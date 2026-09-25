"""
MATA's official GTFS-Realtime feeds -> a daily archive beside our own.

The tracker's vendor also publishes standard GTFS-RT, unauthenticated, at
gtfsrt.mata.cadavl.com (not linked from matatransit.com; Transitland lists
it). All three files are rebuilt every 30 s (measured 2026-09-25):

    VehiclePosition.pb  ~3 KB    each bus: trip_id, report time, next stop_id,
                                 occupancy as a category (not a percent)
    TripUpdate.pb       ~120 KB  predicted time at each remaining stop of
                                 each trip; CANCELED trips
    Alert.pb            ~1 KB    rider alerts, mostly missed trips ("Route 50
                                 is not running from Exeter @ Poplar at 5:30a")

Vehicle ids here are fleet numbers (our `equipment_no`), and trip ids are
the GTFS timetable's. Positions run about a minute behind the tracker, and
there is no delay field, so the tracker stays the source for positions,
delay and load; this archive adds what the tracker lacks.

The poller calls `Official.update` every poll. Each snapshot not seen
before is appended to data/official/dt=YYYY-MM-DD/ (UTC date, like the
positions history):

    vehicles.jsonl.gz      one row per bus per snapshot (every 30 s)
    trip_updates.jsonl.gz  one row per trip per snapshot, every 5 min
                           (every 30 s would be ~150 MB a day)
    alerts.jsonl.gz        one row per snapshot whose alerts changed,
                           holding the whole list, so an empty list marks
                           when the last alert cleared

Check it by hand:
    python official_feed.py
"""

from __future__ import annotations

import gzip
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from google.protobuf.message import DecodeError
from google.transit import gtfs_realtime_pb2 as rt

BASE = "https://gtfsrt.mata.cadavl.com/ProfilGtfsRt2_0RSProducer-MATA"
HERE = Path(__file__).parent
OUT_DIR = HERE / "data" / "official"

# Seconds between fetches of each feed; 0 = every poll. A snapshot whose
# header timestamp was already saved is skipped, so polling faster than
# the feed changes costs a small request and nothing on disk.
EVERY = {"VehiclePosition": 0, "Alert": 0, "TripUpdate": 300}

_VP = rt.VehiclePosition
_TD = rt.TripDescriptor
_STU = rt.TripUpdate.StopTimeUpdate


def _text(ts: rt.TranslatedString) -> str | None:
    return ts.translation[0].text if ts.translation else None


def vehicle_rows(feed: rt.FeedMessage) -> list[dict]:
    rows = []
    for e in feed.entity:
        if not e.HasField("vehicle"):
            continue
        v = e.vehicle
        rows.append({
            "feed_ts": feed.header.timestamp,
            "reported_at": v.timestamp or None,        # the bus's own report time
            "vehicle_id": v.vehicle.id or e.id,        # fleet number
            "trip_id": v.trip.trip_id or None,
            "route_id": v.trip.route_id or None,
            "trip_status": _TD.ScheduleRelationship.Name(v.trip.schedule_relationship),
            "lat": v.position.latitude,
            "lon": v.position.longitude,
            "bearing": v.position.bearing if v.position.HasField("bearing") else None,
            "speed": v.position.speed if v.position.HasField("speed") else None,
            "stop_id": v.stop_id or None,
            "stop_status": _VP.VehicleStopStatus.Name(v.current_status),
            "occupancy": (_VP.OccupancyStatus.Name(v.occupancy_status)
                          if v.HasField("occupancy_status") else None),
        })
    return rows


def trip_update_rows(feed: rt.FeedMessage) -> list[dict]:
    """`stops` has one entry per remaining stop, times in Unix seconds or
    null. The vendor's uncertainty is a flat 120 s (or 0), so it isn't
    kept."""
    rows = []
    for e in feed.entity:
        if not e.HasField("trip_update"):
            continue
        u = e.trip_update
        rows.append({
            "feed_ts": feed.header.timestamp,
            "trip_id": u.trip.trip_id or None,
            "route_id": u.trip.route_id or None,
            "trip_status": _TD.ScheduleRelationship.Name(u.trip.schedule_relationship),
            "vehicle_id": u.vehicle.id or None,
            "stops": [{"seq": s.stop_sequence, "stop_id": s.stop_id,
                       "arrival": s.arrival.time or None,
                       "departure": s.departure.time or None,
                       "status": _STU.ScheduleRelationship.Name(s.schedule_relationship)}
                      for s in u.stop_time_update],
        })
    return rows


def alert_rows(feed: rt.FeedMessage) -> list[dict]:
    alerts = []
    for e in feed.entity:
        if not e.HasField("alert"):
            continue
        a = e.alert
        alerts.append({
            "id": e.id,
            "routes": sorted({i.route_id for i in a.informed_entity if i.route_id}),
            "stops": sorted({i.stop_id for i in a.informed_entity if i.stop_id}),
            "active": [[p.start or None, p.end or None] for p in a.active_period],
            "cause": rt.Alert.Cause.Name(a.cause),
            "effect": rt.Alert.Effect.Name(a.effect),
            "header": _text(a.header_text),
            "description": _text(a.description_text),
        })
    return [{"feed_ts": feed.header.timestamp, "alerts": alerts}]


FEEDS = {
    "VehiclePosition": ("vehicles", vehicle_rows),
    "TripUpdate": ("trip_updates", trip_update_rows),
    "Alert": ("alerts", alert_rows),
}


def fetch(session: requests.Session, name: str) -> rt.FeedMessage:
    # Answers in 0.1-0.2 s; a short timeout keeps a hung server from
    # stretching the poll interval.
    resp = session.get(f"{BASE}/{name}.pb", timeout=5)
    resp.raise_for_status()
    feed = rt.FeedMessage()
    feed.ParseFromString(resp.content)
    return feed


def append_rows(stem: str, rows: list[dict], feed_ts: int) -> None:
    day = datetime.fromtimestamp(feed_ts, timezone.utc).strftime("%Y-%m-%d")
    path = OUT_DIR / f"dt={day}/{stem}.jsonl.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "at", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, separators=(",", ":")) + "\n")


class Official:
    """The poller's handle: fetches each feed when it's due and appends
    snapshots it hasn't saved yet. Alerts are saved only when they change."""

    def __init__(self) -> None:
        self.fetched_at: dict[str, float] = {}
        self.feed_ts: dict[str, int] = {}
        self.alerts: list | None = None

    def update(self, session: requests.Session, now: int) -> None:
        for name, (stem, to_rows) in FEEDS.items():
            if now - self.fetched_at.get(name, 0) < EVERY[name]:
                continue
            try:
                feed = fetch(session, name)
            except (requests.RequestException, DecodeError) as exc:
                print(f"official {name} failed: {exc}")
                continue
            self.fetched_at[name] = now
            ts = feed.header.timestamp
            if ts == self.feed_ts.get(name):
                continue
            self.feed_ts[name] = ts
            rows = to_rows(feed)
            if name == "Alert":
                if rows[0]["alerts"] == self.alerts:
                    continue
                self.alerts = rows[0]["alerts"]
            append_rows(stem, rows, ts)


if __name__ == "__main__":
    with requests.Session() as s:
        for name, (stem, to_rows) in FEEDS.items():
            feed = fetch(s, name)
            rows = to_rows(feed)
            print(f"{name}: {len(feed.entity)} entities, "
                  f"{time.time() - feed.header.timestamp:.0f} s old")
            print(json.dumps(rows[0] if rows else None)[:400])
