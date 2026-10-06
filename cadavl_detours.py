"""
CADAVL /topo/refresh -> detour records.

Despite the name, `refresh` is not a polling-interval endpoint. It is the
current network-deviation state: which line segments are being bypassed, the
replacement geometry, and which stops are affected. In the sample it was
385 KB covering 11 lines, 105 stops, and 14 detour paths.

It changes on the scale of days, not seconds. Poll it hourly at most.

The poller does, through `DetourLog`: once an hour it saves the detours and
the tracker's rider messages (/iv/message: "Route 11 Out of service
Outbound from Thomas & Whitney @ 7:45 PM...") to
data/detours/dt=YYYY-MM-DD/detours.jsonl.gz whenever they changed, so
detour impact can be studied later.
"""

from __future__ import annotations

import csv
import gzip
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

from cadavl_to_gtfs_rt import BASE, HEADERS, route_id_for

REFRESH_SECONDS = 3600
HERE = Path(__file__).parent
STOPS_CSV = HERE / "stops.csv"
LOG_DIR = HERE / "data" / "detours"


def fetch_refresh(session: requests.Session) -> dict:
    resp = session.get(f"{BASE}/topo/refresh",
                       params={"_tmp": int(time.time() * 1000)},
                       headers=HEADERS, timeout=30)  # large payload
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------------------------------
# Parsing
# --------------------------------------------------------------------------

def build_segment_index(payload: dict) -> dict[int, dict]:
    """idTroncon -> {start: (lat, lng), end: (lat, lng)}.

    Geometry lives in objetsSuppl.itineraires, which carries no line ID of its
    own. The link back to a line is by segment ID: each entry in a line's
    tronconsDeviation list is exactly a subset of one itineraire's segments
    (verified — every detour matched a single itineraire at 100%)."""
    index: dict[int, dict] = {}
    # objetsSuppl is null when no line is detoured (seen from 2026-09-25).
    suppl = payload["update"][0].get("objetsSuppl") or {}
    for itinerary in suppl.get("itineraires") or []:
        for seg in itinerary["troncons"]:
            index[seg["idTroncon"]] = {
                "start": (seg["debut"]["lat"], seg["debut"]["lng"]),
                "end": (seg["fin"]["lat"], seg["fin"]["lng"]),
            }
    return index


def segments_to_linestring(segment_ids: list[int],
                           index: dict[int, dict]) -> list[list[float]]:
    """Chain segment endpoints into one coordinate list, GeoJSON order
    (lng, lat). Segments arrive in path order, so this is a simple walk."""
    coords: list[list[float]] = []
    for sid in segment_ids:
        seg = index.get(sid)
        if not seg:
            continue
        for lat, lng in (seg["start"], seg["end"]):
            point = [lng, lat]
            if not coords or coords[-1] != point:
                coords.append(point)
    return coords


def parse_detours(payload: dict, route_for=route_id_for) -> list[dict]:
    """One record per affected line. `route_for` maps a line ID to its
    route; the poller passes its own, which follows crosswalk rebuilds."""
    if not payload.get("update"):
        return []
    update = payload["update"][0]
    index = build_segment_index(payload)

    # Stops are listed once each, with the lines they belong to.
    stops_by_line: dict[int, list[int]] = {}
    for stop in update.get("pointArret", []):
        for info in stop.get("infoLigneSwiv", []):
            stops_by_line.setdefault(info["idLigne"], []).append(
                stop["idPointArret"])

    detours = []
    for line in update.get("ligne", []):
        line_id = line["idLigne"]
        bypassed = [sid for grp in line.get("tronconsDevies", [])
                    for sid in grp["idTroncons"]]
        replacement = [grp["idTroncons"]
                       for grp in line.get("tronconsDeviation", [])]
        detours.append({
            "line_internal_id": line_id,
            "route_id": route_for(line_id),
            "bypassed_segment_ids": bypassed,
            "affected_stop_ids": stops_by_line.get(line_id, []),
            "detour_paths": [segments_to_linestring(ids, index)
                             for ids in replacement],
        })
    return detours


# --------------------------------------------------------------------------
# Rider messages
# --------------------------------------------------------------------------

def fetch_messages(session: requests.Session) -> list[dict]:
    """/iv/message carries the rider-facing wording, e.g.
    "Routes 12, 34, 13, 57, 04, 39, 07, 40 diverted. Stops: ... will not be
    served." Each message lists the affected lines with full names.

    The `lignes` filter appears to be ignored — filtered and unfiltered
    responses were byte-identical — so just call it bare."""
    resp = session.get(f"{BASE}/iv/message", headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()


# --------------------------------------------------------------------------
# The poller's detour log
# --------------------------------------------------------------------------

def stop_codes() -> dict[int, str]:
    """CADAVL stop ID -> stop code (stops.csv). Codes survive the vendor's
    renumberings; IDs don't."""
    with STOPS_CSV.open(encoding="utf-8") as fh:
        return {int(r["stop_internal_id"]): r["stop_code"] for r in csv.DictReader(fh)}


class DetourLog:
    """The poller's handle. Once an hour: the lines on detour (route, the
    stops they skip as stop codes, how many segments are bypassed, the
    replacement paths) and every rider message with the routes it names,
    appended to data/detours/dt=YYYY-MM-DD/detours.jsonl.gz (UTC date) only
    when that differs from the last one saved. A restart saves once more."""

    def __init__(self) -> None:
        self.due = 0
        self.last: dict | None = None

    def update(self, session: requests.Session, now: int, route_for=route_id_for) -> None:
        if now < self.due:
            return
        self.due = now + REFRESH_SECONDS    # after a failure too: detours change over days
        codes = stop_codes()
        state = {
            "detours": [{"route_id": d["route_id"],
                         "stops": [codes.get(s, f"cadavl:{s}") for s in d["affected_stop_ids"]],
                         "bypassed_segments": len(d["bypassed_segment_ids"]),
                         "paths": d["detour_paths"]}
                        for d in parse_detours(fetch_refresh(session), route_for)],
            "messages": [{"routes": sorted({route_for(line["idLigne"]) for line in m.get("ligne", [])}),
                          "text": m["message"].strip()}
                         for m in fetch_messages(session) if (m.get("message") or "").strip()],
        }
        if state == self.last:
            return
        self.last = state
        day = datetime.fromtimestamp(now, timezone.utc).strftime("%Y-%m-%d")
        path = LOG_DIR / f"dt={day}" / "detours.jsonl.gz"
        path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(path, "at", encoding="utf-8") as fh:
            fh.write(json.dumps({"fetched_at": now, **state}, separators=(",", ":")) + "\n")
