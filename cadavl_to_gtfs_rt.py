"""
CADAVL (MATA SWIV) -> position history, live snapshot, GTFS-Realtime feed.
Also archives MATA's official GTFS-RT feeds (official_feed.py).

Mapping verified against a real /topo/vehicules payload (41 buses, 20 lines).

Test the parser offline against a saved payload:
    python cadavl_to_gtfs_rt.py --sample vehicules.json

Run the poller:
    python cadavl_to_gtfs_rt.py
"""

from __future__ import annotations

import argparse
import csv
import gzip
import json
import re
import time
from collections import deque
from datetime import datetime, timezone
from pathlib import Path

import requests
from google.transit import gtfs_realtime_pb2

from official_feed import Official
from schedule import Schedule

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

BASE = "https://swiv.mata.cadavl.com/SWIV/MATA/proxy/restWS"

# Measured from the tracker's own traffic: consecutive vehicules requests
# 10.000 s apart. Server latency was 0.9-3.4 s, so keep timeouts above that.
POLL_SECONDS = 10
REPLAY_EVERY = 3            # one replay frame per 30 s
TRAIL_POINTS = 10           # replay positions per bus sent in latest.json
TOPO_CHECK_SECONDS = 900    # at most this often, while lines are unmapped
SERVICE_HOURS = (4, 24)
HERE = Path(__file__).parent
OUT_DIR = HERE / "data"
FEED_PATH = OUT_DIR / "vehicle_positions.pb"
LATEST_PATH = OUT_DIR / "latest.json"
ROUTES_CSV = HERE / "routes.csv"

# Taken from a working browser request. Note what is NOT here: no cookie, no
# token, no API key. The endpoints are stateless, so no session handling is
# needed. `x-requested-with` and `referer` are the two most likely to be
# checked by the proxy — keep them.
HEADERS = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://swiv.mata.cadavl.com/SWIV/MATA",
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "mata-position-archiver/0.1 (personal research; you@example.com)",
}

# `vitesse` units are unconfirmed (observed range 0-20). GTFS-RT wants metres
# per second. Set this once you've measured it, and speed will be emitted.
#   "unknown" -> omit speed from the feed (default, and correct for now)
#   "mph" | "kmh" | "ms"
SPEED_UNIT = "unknown"
_SPEED_TO_MS = {"mph": 0.44704, "kmh": 0.27778, "ms": 1.0}


# --------------------------------------------------------------------------
# Route crosswalk
# --------------------------------------------------------------------------

def load_routes(path: Path = ROUTES_CSV) -> dict[int, dict]:
    """idLigne -> {route_id, color}, from routes.csv (build_crosswalk.py).

    NOT derivable: route 01 is idLigne 109149 while route 34 is 109134. It
    changes whenever MATA restructures service; rebuild when the poller
    starts printing `cadavl:<id>` route ids."""
    if not path.exists():
        return {}
    with path.open(encoding="utf-8") as fh:
        return {
            int(r["line_internal_id"]): {
                "route_id": r["route_short_name"],
                "color": f"#{r['route_color']}" if r["route_color"] else "#3388ff",
            }
            for r in csv.DictReader(fh)
        }


ROUTES = load_routes()


def route_id_for(line_id: int | None) -> str:
    return ROUTES.get(line_id, {}).get("route_id", f"cadavl:{line_id}")


# --------------------------------------------------------------------------
# Fetching
# --------------------------------------------------------------------------

def fetch_vehicles(session: requests.Session) -> dict:
    """The unfiltered call returns every vehicle at once (the `lignes` filter
    changes nothing), so one request covers the whole fleet."""
    resp = session.get(f"{BASE}/topo/vehicules",
                       params={"_tmp": int(time.time() * 1000)},
                       headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------------------------------
# Normalization
# --------------------------------------------------------------------------

# The "+" after "1h" must be allowed for, or the hours are skipped and
# "1h+ early" parses as 0 s.
_DELAY_RE = re.compile(r"(?:(\d+)\s*h\+?)?\s*(?:(\d+)\s*min)?\s*(late|early)", re.I)


def parse_delay(text: str | None) -> tuple[int | None, bool]:
    """'4 min late' -> (240, False); '2 min early' -> (-120, False);
    'on time' -> (0, False); '1h+ late' -> (3600, True) where True means the
    value is a floor, not a measurement. Treat capped rows as suspect: a bus
    reading '1h+ early' is more likely misassigned than genuinely early."""
    if not text:
        return None, False
    if text.strip().lower() == "on time":
        return 0, False
    m = _DELAY_RE.search(text)
    if not m:
        return None, False
    hours, minutes, direction = m.groups()
    seconds = int(hours or 0) * 3600 + int(minutes or 0) * 60
    if direction.lower() == "early":
        seconds = -seconds
    return seconds, "+" in text


def parse_occupancy(text: str | None) -> int | None:
    """'48%' -> 48."""
    if not text:
        return None
    try:
        return int(str(text).strip().rstrip("%"))
    except ValueError:
        return None


def iter_raw_vehicles(payload: dict) -> list[dict]:
    """Root key is singular: {"vehicule": [...]}."""
    if isinstance(payload, dict):
        for key in ("vehicule", "vehicules", "vehicles"):
            if isinstance(payload.get(key), list):
                return payload[key]
    if isinstance(payload, list):
        return payload
    raise ValueError(f"Unrecognized payload shape: {list(payload)[:5]}")


def normalize_vehicle(raw: dict, fetched_at: int) -> dict | None:
    loc = raw.get("localisation") or {}
    drive = raw.get("conduite") or {}
    if loc.get("lat") is None or loc.get("lng") is None:
        return None

    next_stop = drive.get("arretSuiv")  # null when the bus is off-route/idle
    delay_seconds, delay_capped = parse_delay(drive.get("avanceRetard"))
    line_id = drive.get("idLigne")

    return {
        # There is NO server-supplied timestamp anywhere in the payload, so
        # this is our fetch time, not the vehicle's report time. It bounds
        # staleness from above only.
        "observed_at": fetched_at,
        "vehicle_id": str(raw.get("id")),
        "equipment_no": raw.get("numeroEquipement"),   # fleet number on the bus
        "vehicle_type": raw.get("type"),               # "Bus"; trolleys may differ
        "line_internal_id": line_id,
        "route_id": route_id_for(line_id),
        "route_color": ROUTES.get(line_id, {}).get("color", "#3388ff"),
        "lat": float(loc["lat"]),
        "lon": float(loc["lng"]),
        "bearing": loc.get("cap"),                     # degrees, 0-360
        "speed_raw": drive.get("vitesse"),             # units unconfirmed
        "occupancy_pct": parse_occupancy(raw.get("vehiculeLoad")),
        "destination": drive.get("destination"),       # headsign, not a trip id
        "next_stop_name": (next_stop or {}).get("nomCommercial"),
        "next_stop_eta_min": (next_stop or {}).get("estimationTemps"),
        "delay_seconds": delay_seconds,
        "delay_raw": drive.get("avanceRetard"),
        "delay_capped": delay_capped,
    }


class StaleTracker:
    """Confirmed in the wild: vehicle 10059 held identical coordinates, next
    stop, and ETA across a multi-minute gap while flagged '1h+ late'. With no
    server timestamp, counting unchanged polls is the only staleness signal
    available. High counts during service hours mean a dropped GPS feed, not a
    parked bus."""

    def __init__(self) -> None:
        self._last: dict[str, tuple] = {}
        self._count: dict[str, int] = {}

    def update(self, v: dict) -> int:
        vid = v["vehicle_id"]
        here = (v["lat"], v["lon"])
        if self._last.get(vid) == here:
            self._count[vid] = self._count.get(vid, 0) + 1
        else:
            self._count[vid] = 0
        self._last[vid] = here
        return self._count[vid]


# --------------------------------------------------------------------------
# Outputs
# --------------------------------------------------------------------------

def build_feed(vehicles: list[dict], header_time: int):
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET
    feed.header.timestamp = header_time

    for v in vehicles:
        entity = feed.entity.add()
        entity.id = v["vehicle_id"]
        vp = entity.vehicle
        vp.vehicle.id = v["vehicle_id"]
        if v.get("equipment_no"):
            vp.vehicle.label = str(v["equipment_no"])

        # No course/run id exists in the payload, so trip_id must stay unset.
        # route_id alone is a valid VehiclePosition.
        vp.trip.route_id = v["route_id"]

        vp.position.latitude = v["lat"]
        vp.position.longitude = v["lon"]
        if v.get("bearing") is not None:
            vp.position.bearing = float(v["bearing"])
        if SPEED_UNIT in _SPEED_TO_MS and v.get("speed_raw") is not None:
            vp.position.speed = float(v["speed_raw"]) * _SPEED_TO_MS[SPEED_UNIT]

        if v.get("occupancy_pct") is not None:
            vp.occupancy_percentage = v["occupancy_pct"]

        vp.timestamp = v["observed_at"]

        # stop_id deliberately omitted: arretSuiv gives a display name
        # ("MTMORIAH RD @CLARKE"), not a GTFS stop_id. Setting a bad stop_id
        # is worse than setting none.

    return feed


def write_atomic(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)


def write_latest(rows: list[dict], fetched_at: int, trails: Trails) -> None:
    """Current snapshot for map.html and the "right now" query. `day` is the
    poller's local service day, which names the replay file. Each bus
    carries its `trail` so the map can draw it without the replay file."""
    write_atomic(LATEST_PATH, json.dumps(
        {"fetched_at": fetched_at, "day": datetime.fromtimestamp(fetched_at).strftime("%Y-%m-%d"),
         "vehicles": [{**r, "trail": trails.get(r["vehicle_id"])} for r in rows]}).encode())


def replay_path(t: int) -> Path:
    """One replay file per local service day."""
    return OUT_DIR / f"replay/{datetime.fromtimestamp(t).strftime('%Y-%m-%d')}.jsonl"


def replay_frame(rows: list[dict], t: int) -> str:
    """Compact frame for the pages' replay, one line: the poll time and, per
    bus, the fields they need. The last three (headsign, next stop, fleet
    number) let the strips and schematic place a bus on its stop pattern;
    frames from before 2026-09-25 lack them. ~110 bytes per bus."""
    return json.dumps({"t": t, "v": [
        [r["vehicle_id"], r["route_id"], round(r["lat"], 5), round(r["lon"], 5),
         r["bearing"], r["delay_seconds"], r["delay_capped"], r["occupancy_pct"],
         r["unchanged_polls"], r.get("destination"), r.get("next_stop_name"), r.get("equipment_no")]
        for r in rows]}, separators=(",", ":")) + "\n"


def write_replay_frame(rows: list[dict], fetched_at: int) -> None:
    """One frame per REPLAY_EVERY polls (~7 MB/day). The page builds trails
    from these too, so they show the moment it opens. backfill_replay.py
    rebuilds a day's file from the full history if this ever has gaps."""
    path = replay_path(fetched_at)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(replay_frame(rows, fetched_at))


class Trails:
    """Each bus's last TRAIL_POINTS replay positions (one per 30 s), kept in
    memory and seeded from today's replay file on startup, so a restart
    doesn't blank the trails either."""

    def __init__(self) -> None:
        self._pts: dict[str, deque] = {}
        path = replay_path(int(time.time()))
        if path.exists():
            with path.open(encoding="utf-8") as fh:
                tail = deque(fh, maxlen=TRAIL_POINTS)
            for line in tail:
                f = json.loads(line)
                if time.time() - f["t"] < TRAIL_POINTS * POLL_SECONDS * REPLAY_EVERY:
                    for v in f["v"]:
                        self._add(v[0], v[2], v[3])

    def _add(self, vid: str, lat: float, lon: float) -> None:
        self._pts.setdefault(vid, deque(maxlen=TRAIL_POINTS)).append([lat, lon])

    def add(self, rows: list[dict]) -> None:
        for r in rows:
            self._add(r["vehicle_id"], round(r["lat"], 5), round(r["lon"], 5))

    def get(self, vid: str) -> list:
        return list(self._pts.get(vid, ()))


def archive_positions(rows: list[dict], fetched_at: int) -> None:
    """One row per vehicle per poll, so every row stands for the same
    POLL_SECONDS of bus-time and plain averages are time-weighted."""
    day = datetime.fromtimestamp(fetched_at, timezone.utc).strftime("%Y-%m-%d")
    path = OUT_DIR / f"positions/dt={day}/positions.jsonl.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "at", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row) + "\n")


# --------------------------------------------------------------------------
# Entry points
# --------------------------------------------------------------------------

def run_sample(path: str) -> None:
    payload = json.loads(Path(path).read_text())
    now = int(time.time())
    rows = [r for r in (normalize_vehicle(v, now)
                        for v in iter_raw_vehicles(payload)) if r]
    feed = build_feed(rows, now)
    print(f"parsed {len(rows)} vehicles, "
          f"{len({r['line_internal_id'] for r in rows})} lines")
    print(f"feed serializes to {len(feed.SerializeToString())} bytes")
    print(json.dumps(rows[0], indent=2))
    unmapped = {r["line_internal_id"] for r in rows
                if r["route_id"].startswith("cadavl:")}
    if unmapped:
        print(f"\nWARNING: {len(unmapped)} lines have no route_id: "
              f"{sorted(unmapped)} — rebuild routes.csv")


def refresh_crosswalk(session: requests.Session) -> bool:
    """MATA renumbers every line now and then; when buses show up on unknown
    lines and /config/version has moved, rebuild routes.csv, stops.csv and
    network.geojson (~28 MB download) and reload. True if rebuilt."""
    global ROUTES
    import build_crosswalk      # imports this module; avoid the cycle at load
    try:
        if not build_crosswalk.refresh(session):
            return False
    except (requests.RequestException, ValueError) as exc:
        print(f"crosswalk refresh failed: {exc}")
        return False
    ROUTES = load_routes()
    return True


def run_poller() -> None:
    session = requests.Session()
    stale = StaleTracker()
    trails = Trails()
    schedule = Schedule()
    official = Official()
    polls = 0
    topo_checked = 0

    while True:
        if not SERVICE_HOURS[0] <= datetime.now().hour < SERVICE_HOURS[1]:
            time.sleep(300)
            continue

        fetched_at = int(time.time())
        try:
            payload = fetch_vehicles(session)
            rows = [r for r in (normalize_vehicle(v, fetched_at)
                                for v in iter_raw_vehicles(payload)) if r]
            if (any(r["route_id"].startswith("cadavl:") for r in rows)
                    and fetched_at - topo_checked > TOPO_CHECK_SECONDS):
                topo_checked = fetched_at
                if refresh_crosswalk(session):
                    schedule.reload_stops()
                    rows = [r for r in (normalize_vehicle(v, fetched_at)
                                        for v in iter_raw_vehicles(payload)) if r]
            for r in rows:
                r["unchanged_polls"] = stale.update(r)
            try:
                schedule.update(session, rows, fetched_at)
            except Exception as exc:    # the timetable is extra; never lose a poll to it
                print(f"schedule update failed: {exc!r}")

            archive_positions(rows, fetched_at)
            polls += 1
            if polls % REPLAY_EVERY == 1:
                write_replay_frame(rows, fetched_at)
                trails.add(rows)
            write_latest(rows, fetched_at, trails)
            write_atomic(FEED_PATH, build_feed(rows, fetched_at).SerializeToString())
            print(f"{len(rows)} vehicles, "
                  f"{sum(r['unchanged_polls'] == 0 for r in rows)} moved")

            # Last, so a slow official feed never delays latest.json.
            try:
                official.update(session, fetched_at)
            except Exception as exc:    # an extra archive; never lose a poll to it
                print(f"official feed archive failed: {exc!r}")

        except (requests.RequestException, OSError) as exc:
            # OSError covers Windows refusing to replace latest.json while
            # http.server has it open; the next poll rewrites it anyway.
            print(f"poll failed: {exc}")

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", help="parse a saved payload instead of polling")
    args = ap.parse_args()
    run_sample(args.sample) if args.sample else run_poller()
