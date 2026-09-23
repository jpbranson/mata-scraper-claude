"""
CADAVL (MATA SWIV) -> GTFS-Realtime adapter.

Mapping verified against a real /topo/vehicules payload (41 buses, 20 lines).

    pip install requests gtfs-realtime-bindings

Test the parser offline against a saved payload:
    python cadavl_to_gtfs_rt.py --sample vehicules.json

Run the poller:
    python cadavl_to_gtfs_rt.py
"""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from google.transit import gtfs_realtime_pb2

# --------------------------------------------------------------------------
# Config
# --------------------------------------------------------------------------

BASE = "https://swiv.mata.cadavl.com/SWIV/MATA/proxy/restWS"
AGENCY = "MATA"

# Measured from the tracker's own traffic: consecutive vehicules requests
# 10.000 s apart. Server latency was 0.9-3.4 s, so keep timeouts above that.
POLL_SECONDS = 10
SERVICE_HOURS = (4, 24)
OUT_DIR = Path("data")
FEED_PATH = OUT_DIR / "vehicle_positions.pb"

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

# idLigne -> MATA route number, from /topo. NOT derivable: route 01 is
# idLigne 109149 while route 34 is 109134. Rebuild with build_crosswalk.py
# whenever /config/version changes.
LINE_TO_ROUTE_ID: dict[int, str] = {
    109149: "01", 109148: "02", 109147: "04", 109146: "07", 109145: "08",
    109156: "11", 109155: "12", 109158: "13", 109135: "16", 109154: "19",
    109153: "28", 109152: "30", 109143: "32", 109134: "34", 109142: "36",
    109141: "37", 109140: "39", 109144: "40", 109139: "42", 109138: "50",
    109137: "52", 109136: "53", 109151: "57", 109150: "69", 109157: "100",
}

ROUTE_NAMES: dict[str, str] = {
    "01": "UNION", "02": "MADISON", "04": "WALKER", "07": "SHELBY & HOLMES",
    "08": "CHELSEA & HIGHLAND", "11": "FRAYSER", "12": "MALLORY",
    "13": "LAUDERDALE", "16": "SOUTHEAST CIRCULATOR", "19": "VOLLINTINE",
    "28": "AIRPORT", "30": "BROOKS", "32": "HOLLYWOOD & HAWKINS MILL",
    "34": "CENTRAL & WALNUT GROVE", "36": "LAMAR", "37": "PERKINS",
    "39": "SOUTH THIRD", "40": "STAGE & LAUDERDALE", "42": "CROSSTOWN",
    "50": "POPLAR", "52": "JACKSON", "53": "SUMMER", "57": "PARK",
    "69": "WINCHESTER", "100": "TROLLEY MAIN LINE",
}

# `vitesse` units are unconfirmed (observed range 0-20). GTFS-RT wants metres
# per second. Set this once you've measured it, and speed will be emitted.
#   "unknown" -> omit speed from the feed (default, and correct for now)
#   "mph" | "kmh" | "ms"
SPEED_UNIT = "unknown"
_SPEED_TO_MS = {"mph": 0.44704, "kmh": 0.27778, "ms": 1.0}


# --------------------------------------------------------------------------
# Fetching
# --------------------------------------------------------------------------

def encode_lines(route_codes: list[str]) -> str:
    """Base64 of 'MATA:01___MATA:02___...'. The separator is three
    underscores INSIDE the encoded string, not a comma between values —
    confirmed by decoding the tracker's own request.

    In practice you don't need this: the unfiltered call returned every
    vehicle anyway (12,606 bytes unfiltered vs 12,633 filtered)."""
    joined = "___".join(f"{AGENCY}:{c}" for c in route_codes)
    return base64.b64encode(joined.encode()).decode()


def fetch_vehicles(session: requests.Session,
                   route_codes: list[str] | None = None) -> dict:
    """The sample payload contained every line at once, so try the unfiltered
    call first — one request for the whole fleet beats 20 requests."""
    params: dict[str, object] = {"_tmp": int(time.time() * 1000)}
    if route_codes:
        params["lignes"] = encode_lines(route_codes)
    resp = session.get(f"{BASE}/topo/vehicules", params=params,
                       headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------------------------------
# Normalization
# --------------------------------------------------------------------------

_DELAY_RE = re.compile(r"(?:(\d+)\s*h)?\s*(?:(\d+)\s*min)?\s*(late|early)", re.I)


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
        "route_id": LINE_TO_ROUTE_ID.get(line_id, f"cadavl:{line_id}"),
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


def position_key(v: dict) -> tuple:
    """No report timestamp means we can't dedupe on one. Dedupe on the fields
    that change when the bus moves instead."""
    return (v["vehicle_id"], v["lat"], v["lon"],
            v["next_stop_name"], v["delay_raw"])


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
# GTFS-Realtime output
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


def write_feed(feed) -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tmp = FEED_PATH.with_suffix(".pb.tmp")
    tmp.write_bytes(feed.SerializeToString())
    tmp.replace(FEED_PATH)


def archive_raw(payload: dict, fetched_at: int) -> None:
    """Keep the untouched payload forever — the vendor's fields are
    undocumented and you will want to re-parse."""
    day = datetime.fromtimestamp(fetched_at, timezone.utc).strftime("%Y-%m-%d")
    path = OUT_DIR / f"raw/dt={day}/vehicules.jsonl.gz"
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.open(path, "at", encoding="utf-8") as fh:
        fh.write(json.dumps({"fetched_at": fetched_at, "payload": payload}) + "\n")


def archive_positions(rows: list[dict], fetched_at: int) -> None:
    """Deduped, parsed rows — this is the analysis table."""
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
        print(f"\nWARNING: {len(unmapped)} lines have no GTFS route_id: "
              f"{sorted(unmapped)}")


def run_poller() -> None:
    session = requests.Session()
    seen: set[tuple] = set()
    stale = StaleTracker()

    while True:
        if not SERVICE_HOURS[0] <= datetime.now().hour < SERVICE_HOURS[1]:
            time.sleep(300)
            continue

        fetched_at = int(time.time())
        try:
            payload = fetch_vehicles(session)
            archive_raw(payload, fetched_at)

            rows = [r for r in (normalize_vehicle(v, fetched_at)
                                for v in iter_raw_vehicles(payload)) if r]
            for r in rows:
                r["unchanged_polls"] = stale.update(r)

            fresh = [r for r in rows if position_key(r) not in seen]
            seen.update(position_key(r) for r in fresh)
            if len(seen) > 20_000:      # keep the dedupe set from growing forever
                seen = {position_key(r) for r in rows}

            archive_positions(fresh, fetched_at)
            write_feed(build_feed(rows, fetched_at))
            print(f"{len(rows)} vehicles, {len(fresh)} moved")

        except requests.RequestException as exc:
            print(f"fetch failed: {exc}")

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", help="parse a saved payload instead of polling")
    args = ap.parse_args()
    run_sample(args.sample) if args.sample else run_poller()
