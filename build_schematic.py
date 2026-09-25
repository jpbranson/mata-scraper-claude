"""
Build schematic.json: the subway-style network layout schematic.html draws.

The layout comes from LOOM (https://github.com/ad-freiburg/loom, University
of Freiburg), which turns a GTFS feed into an octilinear transit map: lines
bundled where they share a street, their order chosen to minimise crossings,
and every segment snapped to 45°/90°. LOOM is C++ and builds on Linux or WSL:

    git clone --recurse-submodules https://github.com/ad-freiburg/loom
    cd loom && mkdir build && cd build && cmake .. && make -j gtfs2graph topo loom octi

(`make` of everything also compiles topo's test suite, which takes a very
long time; the four targets above are all this needs.) Then, from here:

    python build_schematic.py --loom path/to/loom/build

Only the timetable's timepoints (its major, timed stops, plus each trip's
first and last stop) become stations; all 3,600 stops would be unreadable.
LOOM merges stations that sit close together, so each timepoint code maps
to the station it merged into. For each route and each pair of consecutive
timepoints it also stores the chain of schematic edges between them, which
is how the page slides live buses along the right line.

Rerun when MATA changes its routes. A renumbering of line IDs doesn't
matter: routes are keyed by number and stops by code.
"""

from __future__ import annotations

import argparse
import csv
import heapq
import io
import json
import math
import subprocess
import tempfile
import zipfile
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import requests

from schedule import GTFS_PATH, STOPS_CSV, dist_m, fetch_gtfs

HERE = Path(__file__).parent
OUT = HERE / "schematic.json"
MERGE_M = 400      # a timepoint this close to a station merged into it


def timepoint_feed(zip_path: Path, out_dir: Path) -> dict[str, list]:
    """Copy the feed with stop_times cut to timepoints (and each trip's ends).
    Returns trip -> [(code, route)] of the kept stops, in order."""
    with zipfile.ZipFile(zip_path) as z:
        z.extractall(out_dir)
        trips = {r["trip_id"]: r["route_id"] for r in
                 csv.DictReader(io.TextIOWrapper(z.open("trips.txt"), "utf-8-sig"))}
        rows = list(csv.DictReader(io.TextIOWrapper(z.open("stop_times.txt"), "utf-8-sig")))
    by_trip: dict[str, list] = defaultdict(list)
    for r in rows:
        by_trip[r["trip_id"]].append(r)
    keep, seqs = [], {}
    for trip, rs in by_trip.items():
        rs.sort(key=lambda r: int(r["stop_sequence"]))
        kept = [r for i, r in enumerate(rs) if r.get("timepoint") == "1" or i in (0, len(rs) - 1)]
        keep += kept
        seqs[trip] = [(r["stop_id"].split(":", 1)[-1], trips[trip]) for r in kept]
    with (out_dir / "stop_times.txt").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(keep)
    return seqs


def run_loom(bin_dir: Path, feed: Path) -> tuple[dict, dict]:
    """gtfs2graph | topo -> geographic graph; | loom | octi -> octilinear."""
    def tool(name, *args, stdin=None):
        return subprocess.run([str(bin_dir / name), *args], input=stdin, capture_output=True,
                              check=True).stdout
    geo = tool("topo", stdin=tool("gtfs2graph", "-m", "bus", str(feed)))
    octi = tool("octi", stdin=tool("loom", stdin=geo))
    return json.loads(geo), json.loads(octi)


def mercator(lon: float, lat: float) -> tuple[float, float]:
    return (math.radians(lon) * 6378137,
            math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * 6378137)


def build(geo: dict, octi: dict, seqs: dict[str, list]) -> dict:
    with STOPS_CSV.open(encoding="utf-8") as fh:
        stops = {r["stop_code"]: r for r in csv.DictReader(fh)}
    feats = octi["features"]
    points = [f for f in feats if f["geometry"]["type"] == "Point"]
    lines = [f for f in feats if f["geometry"]["type"] == "LineString"]

    # Coordinates: Web Mercator, 10 m per unit, origin top-left, y down.
    merc = [mercator(*c) for f in feats for c in
            ([f["geometry"]["coordinates"]] if f["geometry"]["type"] == "Point" else f["geometry"]["coordinates"])]
    x0, y1 = min(m[0] for m in merc), max(m[1] for m in merc)
    def xy(c):
        mx, my = mercator(*c)
        return [round((mx - x0) / 10, 1), round((y1 - my) / 10, 1)]

    index, nodes = {}, []
    for f in points:
        p = f["properties"]
        code = (p.get("station_id") or "").split(":", 1)[-1] or None
        name = stops[code]["stop_name"].strip() if code in stops else (p.get("station_label") or None)
        index[p["id"]] = len(nodes)
        nodes.append([*xy(f["geometry"]["coordinates"]), code, name])
    edges = []
    for f in lines:
        p = f["properties"]
        edges.append([index[p["from"]], index[p["to"]],
                      [xy(c) for c in f["geometry"]["coordinates"]],
                      [ln["label"] for ln in p["lines"]]])

    # Every timepoint code -> the station node it is (or merged into): by
    # code, else the nearest station on the geographic graph within MERGE_M.
    by_code = {n[2]: i for i, n in enumerate(nodes) if n[2]}
    geo_st = [((f["geometry"]["coordinates"][1], f["geometry"]["coordinates"][0]),
               f["properties"]["station_id"].split(":", 1)[-1])
              for f in geo["features"]
              if f["geometry"]["type"] == "Point" and f["properties"].get("station_id")]
    stations = {}
    for code in {c for seq in seqs.values() for c, _ in seq}:
        if code in by_code:
            stations[code] = by_code[code]
            continue
        s = stops.get(code)
        if not s or not s["lat"]:
            continue
        d, near = min((dist_m(float(s["lat"]), float(s["lon"]), la, lo), c)
                      for (la, lo), c in geo_st)
        if d <= MERGE_M and near in by_code:
            stations[code] = by_code[near]

    # Legs: per route, consecutive timepoints -> shortest chain of edges
    # carrying that route, as [edge index, +1 along / -1 against].
    adj: dict[int, list] = defaultdict(list)
    for ei, (a, b, pts, lns) in enumerate(edges):
        length = sum(math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1))
        adj[a].append((b, ei, 1, length, set(lns)))
        adj[b].append((a, ei, -1, length, set(lns)))

    def path(route: str, s: int, t: int) -> list | None:
        dist, prev, heap = {s: 0.0}, {}, [(0.0, s)]
        while heap:
            d, u = heapq.heappop(heap)
            if u == t:
                out = []
                while u != s:
                    u, ei, sign = prev[u]
                    out.append([ei, sign])
                return out[::-1]
            if d > dist[u]:
                continue
            for v, ei, sign, length, lns in adj[u]:
                if route in lns and d + length < dist.get(v, math.inf):
                    dist[v], prev[v] = d + length, (u, ei, sign)
                    heapq.heappush(heap, (d + length, v))
        return None

    legs: dict[str, dict] = defaultdict(dict)
    missing = 0
    for seq in seqs.values():
        for (a, route), (b, _) in zip(seq, seq[1:]):
            key = f"{a}>{b}"
            if key in legs[route] or a not in stations or b not in stations:
                continue
            p = [] if stations[a] == stations[b] else path(route, stations[a], stations[b])
            if p is None:
                missing += 1
            else:
                legs[route][key] = p
    print(f"{len(nodes)} nodes, {len(edges)} edges, {len(stations)} timepoints mapped, "
          f"{sum(map(len, legs.values()))} legs ({missing} without a path)")
    return {"built": datetime.now().isoformat(timespec="seconds"),
            "nodes": nodes, "edges": edges, "stations": stations, "legs": legs}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--loom", required=True, type=Path, help="LOOM build directory")
    args = ap.parse_args()
    if not GTFS_PATH.exists():
        fetch_gtfs(requests.Session())
    with tempfile.TemporaryDirectory() as tmp:
        seqs = timepoint_feed(GTFS_PATH, Path(tmp))
        geo, octi = run_loom(args.loom, Path(tmp))
    OUT.write_text(json.dumps(build(geo, octi, seqs), separators=(",", ":")))
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
