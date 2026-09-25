"""
Put route numbers on history rows recorded while routes.csv was stale.

When MATA renumbers its lines, the poller writes `cadavl:<idLigne>` as the
route until it notices and rebuilds routes.csv. Those rows are still in
data/positions/, where analysis.sql groups by route_id and misses them.
This rewrites them with today's routes.csv (route_id and route_color);
rows on lines it doesn't know are left alone and counted.

    python backfill_routes.py                 # every file in data/positions/
    python backfill_routes.py 2026-09-24      # one file (its dt=, a UTC date)

Each file is rewritten to a temp file and swapped in only if it has the
same number of rows; files with nothing to fix aren't touched. The poller
appends to the current UTC day's file, so stop it first (ops/backfill.ps1
does, then rebuilds the replay and arrivals files from the fixed rows).
"""

from __future__ import annotations

import gzip
import json
import sys
from collections import Counter

from cadavl_to_gtfs_rt import OUT_DIR, ROUTES


def fix_route(r: dict) -> bool:
    """Map a `cadavl:<id>` row to its route in place; True if it changed."""
    line = ROUTES.get(r.get("line_internal_id"))
    if not r["route_id"].startswith("cadavl:") or line is None:
        return False
    r["route_id"], r["route_color"] = line["route_id"], line["color"]
    return True


def backfill(path) -> None:
    rows, fixed, unknown = [], 0, Counter()
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            if fix_route(r):
                fixed += 1
            elif r["route_id"].startswith("cadavl:"):
                unknown[r.get("line_internal_id")] += 1
            rows.append(r)
    left = f", {sum(unknown.values())} left on unknown lines {sorted(unknown)}" if unknown else ""
    print(f"{path.parent.name}: {fixed} of {len(rows)} rows remapped{left}")
    if not fixed:
        return

    tmp = path.with_suffix(".tmp")
    with gzip.open(tmp, "wt", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r) + "\n")
    with gzip.open(tmp, "rt", encoding="utf-8") as fh:
        written = sum(1 for _ in fh)
    if written != len(rows):
        tmp.unlink()
        sys.exit(f"{path}: wrote {written} rows, expected {len(rows)}; original kept")
    tmp.replace(path)


def main(only_day: str | None) -> None:
    if not ROUTES:
        sys.exit("routes.csv is missing; run build_crosswalk.py first")
    pattern = f"positions/dt={only_day or '*'}/positions.jsonl.gz"
    files = sorted(OUT_DIR.glob(pattern))
    if not files:
        sys.exit(f"no history matching {OUT_DIR / pattern}")
    for f in files:
        backfill(f)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
