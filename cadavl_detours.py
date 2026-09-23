"""
CADAVL /topo/refresh -> detour records + GTFS-Realtime Service Alerts.

Despite the name, `refresh` is not a polling-interval endpoint. It is the
current network-deviation state: which line segments are being bypassed, the
replacement geometry, and which stops are affected. In the sample it was
385 KB covering 11 lines, 105 stops, and 14 detour paths.

It changes on the scale of days, not seconds. Poll it hourly at most.

    python cadavl_detours.py --sample refresh.json
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import requests
from google.transit import gtfs_realtime_pb2

from cadavl_to_gtfs_rt import BASE, HEADERS, LINE_TO_ROUTE_ID

REFRESH_SECONDS = 3600


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
    for itinerary in payload["update"][0]["objetsSuppl"]["itineraires"]:
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


def parse_detours(payload: dict) -> list[dict]:
    """One record per affected line."""
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
            "route_id": LINE_TO_ROUTE_ID.get(line_id, f"cadavl:{line_id}"),
            "bypassed_segment_ids": bypassed,
            "affected_stop_ids": stops_by_line.get(line_id, []),
            "detour_paths": [segments_to_linestring(ids, index)
                             for ids in replacement],
        })
    return detours


def detours_to_geojson(detours: list[dict]) -> dict:
    """Drop straight into R via sf::read_sf(), or DuckDB spatial."""
    return {
        "type": "FeatureCollection",
        "features": [
            {"type": "Feature",
             "properties": {"route_id": d["route_id"],
                            "line_internal_id": d["line_internal_id"],
                            "path_index": i},
             "geometry": {"type": "LineString", "coordinates": path}}
            for d in detours for i, path in enumerate(d["detour_paths"])
            if len(path) > 1
        ],
    }


# --------------------------------------------------------------------------
# GTFS-Realtime Service Alerts
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


def messages_by_line(messages: list[dict]) -> dict[int, list[str]]:
    out: dict[int, list[str]] = {}
    for msg in messages:
        text = msg.get("message")
        if not text:
            continue
        for line in msg.get("ligne", []):
            out.setdefault(line["idLigne"], []).append(text)
    return out


def build_alerts_feed(detours: list[dict], header_time: int,
                      texts: dict[int, list[str]] | None = None):
    """Structural detour data from /topo/refresh, with rider-facing text
    from /iv/message when supplied."""
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.header.gtfs_realtime_version = "2.0"
    feed.header.incrementality = gtfs_realtime_pb2.FeedHeader.FULL_DATASET
    feed.header.timestamp = header_time

    for d in detours:
        entity = feed.entity.add()
        entity.id = f"detour-{d['line_internal_id']}"
        alert = entity.alert
        alert.effect = gtfs_realtime_pb2.Alert.DETOUR
        alert.cause = gtfs_realtime_pb2.Alert.UNKNOWN_CAUSE

        informed = alert.informed_entity.add()
        informed.route_id = d["route_id"]

        for text in (texts or {}).get(d["line_internal_id"], []):
            translation = alert.description_text.translation.add()
            translation.text = text
            translation.language = "en"

        for stop_id in d["affected_stop_ids"]:
            # CADAVL stop IDs, not GTFS stop_ids — same crosswalk problem as
            # routes. These are the same IDs the horaires/pta/<id> endpoint
            # uses, so that endpoint is the way to resolve them.
            stop_entity = alert.informed_entity.add()
            stop_entity.route_id = d["route_id"]
            stop_entity.stop_id = f"cadavl:{stop_id}"

    return feed


# --------------------------------------------------------------------------

def run_sample(path: str) -> None:
    payload = json.loads(Path(path).read_text())
    detours = parse_detours(payload)
    now = int(time.time())

    print(f"{len(detours)} lines on detour")
    for d in detours:
        print(f"  {d['route_id']}: {len(d['bypassed_segment_ids'])} segments "
              f"bypassed, {len(d['affected_stop_ids'])} stops affected, "
              f"{len(d['detour_paths'])} detour path(s)")

    gj = detours_to_geojson(detours)
    Path("detours.geojson").write_text(json.dumps(gj))
    print(f"\nwrote detours.geojson: {len(gj['features'])} linestrings")

    feed = build_alerts_feed(detours, now)
    print(f"alerts feed: {len(feed.entity)} alerts, "
          f"{len(feed.SerializeToString())} bytes")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", required=True)
    run_sample(ap.parse_args().sample)
