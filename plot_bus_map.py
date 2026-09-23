#!/usr/bin/env python3
"""Plot bus positions from data/positions/ on an interactive map.

For each vehicle, draws a trail of its recent positions (fading with age)
and a marker at its most recent known location, colored by route.
"""
import argparse
import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path

import folium

DATA_DIR = Path(__file__).parent / "data" / "positions"
ROUTES_CSV = Path(__file__).parent / "routes.csv"


def load_route_colors():
    colors = {}
    with open(ROUTES_CSV, newline="") as f:
        for row in csv.DictReader(f):
            color = row.get("route_color", "").strip()
            colors[row["line_internal_id"]] = f"#{color}" if color else "#3388ff"
    return colors


def load_positions(max_age_hours):
    vehicles = defaultdict(list)
    cutoff = None
    files = sorted(DATA_DIR.glob("dt=*/positions.jsonl.gz"))
    if not files:
        raise SystemExit(f"No position files found under {DATA_DIR}")

    for path in files:
        with gzip.open(path, "rt") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                vehicles[rec["vehicle_id"]].append(rec)

    for vid, recs in vehicles.items():
        recs.sort(key=lambda r: r["observed_at"])

    if max_age_hours is not None:
        latest_ts = max(
            r["observed_at"] for recs in vehicles.values() for r in recs
        )
        cutoff = latest_ts - max_age_hours * 3600
        vehicles = {
            vid: [r for r in recs if r["observed_at"] >= cutoff]
            for vid, recs in vehicles.items()
        }
        vehicles = {vid: recs for vid, recs in vehicles.items() if recs}

    return vehicles


def build_map(vehicles, route_colors, max_trail_points, out_path):
    all_lats = [r["lat"] for recs in vehicles.values() for r in recs]
    all_lons = [r["lon"] for recs in vehicles.values() for r in recs]
    center = [sum(all_lats) / len(all_lats), sum(all_lons) / len(all_lons)]

    m = folium.Map(location=center, zoom_start=12, tiles="OpenStreetMap")

    for vid, recs in vehicles.items():
        trail = recs[-max_trail_points:]
        route_id = trail[-1].get("line_internal_id") or trail[-1].get("route_id")
        color = route_colors.get(str(route_id), "#3388ff")

        n = len(trail)
        for i in range(n - 1):
            age_frac = (n - 1 - i) / max(n - 1, 1)
            opacity = max(0.08, 1.0 - age_frac * 0.9)
            seg = [
                (trail[i]["lat"], trail[i]["lon"]),
                (trail[i + 1]["lat"], trail[i + 1]["lon"]),
            ]
            folium.PolyLine(
                seg,
                color=color,
                weight=3,
                opacity=opacity,
            ).add_to(m)

        latest = trail[-1]
        popup = (
            f"Vehicle {vid}<br>Route {latest.get('route_id')}<br>"
            f"Dest: {latest.get('destination', '')}<br>"
            f"Delay: {latest.get('delay_raw', '')}"
        )
        folium.CircleMarker(
            location=(latest["lat"], latest["lon"]),
            radius=5,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=1.0,
            opacity=1.0,
            popup=popup,
        ).add_to(m)

    m.save(out_path)
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-o", "--output", default="bus_map.html", help="Output HTML file path"
    )
    parser.add_argument(
        "--max-age-hours",
        type=float,
        default=None,
        help="Only include positions within this many hours of the latest observation",
    )
    parser.add_argument(
        "--max-trail-points",
        type=int,
        default=30,
        help="Max number of past positions to draw per vehicle trail",
    )
    args = parser.parse_args()

    route_colors = load_route_colors()
    vehicles = load_positions(args.max_age_hours)
    out_path = build_map(vehicles, route_colors, args.max_trail_points, args.output)
    print(f"Wrote map with {len(vehicles)} vehicles to {out_path}")


if __name__ == "__main__":
    main()
