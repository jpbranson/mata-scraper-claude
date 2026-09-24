"""
Build the route and stop crosswalks from CADAVL's /topo payload.

/topo (no suffix) is the full network definition: 25 lines, 3,766 stops,
2,283 deviations. It is ~28 MB and took 14 seconds to serve, so fetch it
ONCE and cache it. /config/version returns a small integer (196203 when
captured) — poll that cheaply and only re-download /topo when it changes.

    python build_crosswalk.py --topo topo.json
    python build_crosswalk.py --fetch          # download it fresh

Writes routes.csv, stops.csv and shapes.geojson next to the script.
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import requests

from cadavl_to_gtfs_rt import BASE, HEADERS

ROUTES_CSV = Path("routes.csv")
STOPS_CSV = Path("stops.csv")
SHAPES_GEOJSON = Path("shapes.geojson")
VERSION_PATH = Path("topo_version.txt")


def fetch_version(session: requests.Session) -> int:
    resp = session.get(f"{BASE}/config/version",
                       params={"_tmp": int(time.time() * 1000)},
                       headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.json()["version"][0]["valeur"]


def fetch_topo(session: requests.Session) -> dict:
    """~28 MB, ~14 s. Do not put this in a polling loop."""
    resp = session.get(f"{BASE}/topo",
                       params={"_tmp": int(time.time() * 1000)},
                       headers=HEADERS, timeout=120)
    resp.raise_for_status()
    return resp.json()


def extract_routes(topo: dict) -> list[dict]:
    return [{
        "line_internal_id": ligne["idLigne"],
        "route_short_name": ligne["nomCommercial"],   # "01", "50", "100"
        "route_long_name": ligne["libCommercial"],    # "UNION", "POPLAR"
        "route_color": (ligne.get("couleur") or "").lstrip("#"),
        "has_alerts": ligne.get("messageIVExiste"),
    } for ligne in topo["topo"][0]["ligne"]]


def extract_stops(topo: dict) -> list[dict]:
    rows = []
    for stop in topo["topo"][0]["pointArret"]:
        loc = stop.get("localisation") or {}
        rows.append({
            "stop_internal_id": stop["idPointArret"],
            "stop_code": stop.get("mnemoPointArret"),   # e.g. "THIEASNN"
            "stop_name": stop.get("nomCommercial"),
            "lat": loc.get("lat"),
            "lon": loc.get("lng"),
            "line_internal_ids": "|".join(
                str(i["idLigne"]) for i in stop.get("infoLigneSwiv", [])),
        })
    return rows


def extract_shapes(topo: dict) -> dict:
    """One MultiLineString per line, for drawing the network on the map.

    Each line has several `itineraire`s (direction/branch variants) made of
    2-point `troncons` that overlap heavily between variants. Segments are
    emitted once per line, chained into runs while consecutive, and rounded
    to 5 decimals (~1 m). About 400 KB for the whole network."""
    features = []
    for ligne in topo["topo"][0]["ligne"]:
        seen: set[int] = set()
        parts: list[list[list[float]]] = []
        for itin in ligne["itineraire"]:
            run: list[list[float]] = []
            for seg in itin["troncons"]:
                if seg["idTroncon"] in seen:
                    if len(run) > 1:
                        parts.append(run)
                    run = []
                    continue
                seen.add(seg["idTroncon"])
                a = [round(seg["debut"]["lng"], 5), round(seg["debut"]["lat"], 5)]
                b = [round(seg["fin"]["lng"], 5), round(seg["fin"]["lat"], 5)]
                if not run or run[-1] != a:
                    if len(run) > 1:
                        parts.append(run)
                    run = [a]
                run.append(b)
            if len(run) > 1:
                parts.append(run)
        features.append({
            "type": "Feature",
            "properties": {"route_id": ligne["nomCommercial"],
                           "name": ligne["libCommercial"]},
            "geometry": {"type": "MultiLineString", "coordinates": parts},
        })
    return {"type": "FeatureCollection", "features": features}


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"wrote {path} ({len(rows)} rows)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--topo", help="path to a saved /topo payload")
    ap.add_argument("--fetch", action="store_true", help="download /topo")
    args = ap.parse_args()

    if args.fetch:
        session = requests.Session()
        version = fetch_version(session)
        print(f"topo version {version} — downloading (~28 MB, be patient)")
        topo = fetch_topo(session)
        Path("topo.json").write_text(json.dumps(topo))
        VERSION_PATH.write_text(str(version))
    elif args.topo:
        topo = json.loads(Path(args.topo).read_text())
    else:
        ap.error("pass --topo PATH or --fetch")

    routes = extract_routes(topo)
    write_csv(ROUTES_CSV, routes)
    write_csv(STOPS_CSV, extract_stops(topo))
    SHAPES_GEOJSON.write_text(json.dumps(extract_shapes(topo), separators=(",", ":")))
    print(f"wrote {SHAPES_GEOJSON} ({SHAPES_GEOJSON.stat().st_size // 1024} KB)")

    print("\nroute crosswalk:")
    for r in routes:
        print(f"  {r['route_short_name']:>4} {r['route_long_name']:<26} "
              f"idLigne={r['line_internal_id']}")

    print("\nNext: confirm route_short_name matches route_id (or route_short_name) "
          "in routes.txt from GTFS_MATA.zip, and check whether stop_code "
          "matches stop_code in stops.txt.")


if __name__ == "__main__":
    main()
