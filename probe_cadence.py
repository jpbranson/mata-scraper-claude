"""
Probe the CADAVL feed's true update cadence and settle the `vitesse` unit.

The payload has no timestamps, so the only way to learn how often the server
actually refreshes is to poll fast and watch when positions change.

Run for a couple of minutes during service hours:

    python probe_cadence.py --seconds 180 --interval 5

Outputs:
  1. How often each vehicle's position changes -> the real refresh cadence.
     Poll no faster than this; anything faster is wasted requests.
  2. Implied speed (metres moved / seconds elapsed) against the reported
     `vitesse` for the same vehicle -> tells you whether vitesse is mph,
     km/h, or m/s. The ratio implied_ms / vitesse lands near 0.45 for mph,
     0.28 for km/h, 1.0 for m/s.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics as st
import time
from collections import defaultdict
from pathlib import Path

import requests

from cadavl_to_gtfs_rt import BASE, HEADERS, iter_raw_vehicles

UNIT_HINTS = {"mph": 0.44704, "km/h": 0.27778, "m/s": 1.0}


def haversine_m(lat1, lon1, lat2, lon2) -> float:
    r = 6371000.0
    dlat, dlon = math.radians(lat2 - lat1), math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2
         + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2))
         * math.sin(dlon / 2) ** 2)
    return 2 * r * math.asin(math.sqrt(a))


def probe(seconds: int, interval: int) -> None:
    session = requests.Session()
    samples: list[tuple[float, dict]] = []
    deadline = time.time() + seconds

    while time.time() < deadline:
        t = time.time()
        try:
            payload = session.get(f"{BASE}/topo/vehicules",
                                  params={"_tmp": int(t * 1000)},
                                  headers=HEADERS, timeout=10).json()
            by_id = {str(v["id"]): v for v in iter_raw_vehicles(payload)}
            samples.append((t, by_id))
            print(f"  t+{t - (deadline - seconds):5.1f}s  {len(by_id)} vehicles")
        except requests.RequestException as exc:
            print(f"  fetch failed: {exc}")
        time.sleep(max(0, interval - (time.time() - t)))

    Path("probe_samples.json").write_text(json.dumps(
        [{"t": t, "vehicles": v} for t, v in samples]))
    analyze(samples)


def analyze(samples: list[tuple[float, dict]]) -> None:
    """Per vehicle, find the moments its position changed."""
    change_gaps: list[float] = []
    speed_ratios: dict[str, list[float]] = defaultdict(list)
    unchanged_streaks: dict[str, int] = defaultdict(int)

    vehicle_ids = {vid for _, by_id in samples for vid in by_id}

    for vid in vehicle_ids:
        track = [(t, by_id[vid]) for t, by_id in samples if vid in by_id]
        last_change_t = None
        for (t_prev, v_prev), (t_now, v_now) in zip(track, track[1:]):
            p, q = v_prev["localisation"], v_now["localisation"]
            moved = haversine_m(p["lat"], p["lng"], q["lat"], q["lng"])
            if moved < 1.0:
                unchanged_streaks[vid] += 1
                continue
            if last_change_t is not None:
                change_gaps.append(t_now - last_change_t)
            last_change_t = t_now

            elapsed = t_now - t_prev
            reported = v_now["conduite"].get("vitesse") or 0
            if elapsed > 0 and reported > 0:
                speed_ratios["ratio"].append((moved / elapsed) / reported)

    print("\n--- refresh cadence ---")
    if change_gaps:
        print(f"n position changes: {len(change_gaps)}")
        print(f"median gap between changes: {st.median(change_gaps):.1f}s")
        print(f"min {min(change_gaps):.1f}s / max {max(change_gaps):.1f}s")
        print(f"-> set POLL_SECONDS to about {round(st.median(change_gaps))}")
    else:
        print("no movement observed — run during service hours")

    print("\n--- vitesse unit ---")
    ratios = speed_ratios["ratio"]
    if ratios:
        med = st.median(ratios)
        best = min(UNIT_HINTS, key=lambda u: abs(UNIT_HINTS[u] - med))
        print(f"median implied_ms / reported vitesse = {med:.3f} "
              f"(n={len(ratios)})")
        print(f"closest match: {best} (expected {UNIT_HINTS[best]})")
        print(f"-> set SPEED_UNIT = "
              f"{ {'mph': 'mph', 'km/h': 'kmh', 'm/s': 'ms'}[best]!r}")
    else:
        print("not enough moving vehicles to judge")

    stale = [vid for vid, n in unchanged_streaks.items()
             if n >= len(samples) - 1]
    if stale:
        print(f"\n--- never moved during the probe ({len(stale)}) ---")
        print("  candidates for stale/ghost records:", sorted(stale))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=int, default=180)
    ap.add_argument("--interval", type=int, default=5)
    args = ap.parse_args()
    probe(args.seconds, args.interval)
