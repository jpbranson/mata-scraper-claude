"""
Rebuild replay frames, stop arrivals and stop schedules from the full
position history.

The poller writes data/replay/<day>.jsonl and data/arrivals/<day>/ as it
goes, but only while it is running the current code. This regenerates
them from data/positions/ (one row per bus per 10 s), one frame per 30 s,
so any recorded day can be replayed in map.html and its stops show when
buses came.

    python backfill_replay.py                # every day in data/positions/
    python backfill_replay.py 2026-09-24     # one day (local date)

On the way it repairs two things older pollers got wrong: rows on lines
routes.csv didn't know yet (`cadavl:<id>`, mapped with today's routes.csv
where the ID is in it; backfill_routes.py fixes the history itself) and
"1h+" delays, which were stored as 0.

Files for the days touched are rewritten from scratch. Stop the poller
first if you rebuild today, or its next writes will land in the rebuilt
files out of order.
"""

from __future__ import annotations

import gzip
import json
import sys
from datetime import date, datetime

import requests

from backfill_routes import fix_route
from cadavl_to_gtfs_rt import (OUT_DIR, POLL_SECONDS, REPLAY_EVERY, parse_delay, replay_frame,
                               replay_path)
from schedule import GTFS_PATH, Arrivals, Timetable, append_arrivals, fetch_gtfs

FRAME_S = POLL_SECONDS * REPLAY_EVERY


def main(only_day: str | None) -> None:
    files = sorted(OUT_DIR.glob("positions/dt=*/positions.jsonl.gz"))
    if not files:
        sys.exit(f"no history under {OUT_DIR / 'positions'}")

    if not GTFS_PATH.exists():
        fetch_gtfs(requests.Session())
    written: dict[str, int] = {}
    arrived: dict[str, list] = {}
    detector = Arrivals()
    timetable = None
    open_paths = set()
    poll: list[dict] = []
    poll_t = None
    last_bin = None

    def flush() -> None:
        nonlocal last_bin, timetable
        if not poll:
            return
        day = datetime.fromtimestamp(poll_t).strftime("%Y-%m-%d")
        if only_day and day != only_day:
            return
        if timetable is None or timetable.day.isoformat() != day:
            timetable = Timetable(GTFS_PATH, date.fromisoformat(day))
            timetable.write()       # the stop panel needs the day's schedule too
        arrived.setdefault(day, []).extend(detector.update(timetable, poll))
        if poll_t // FRAME_S == last_bin:
            return
        path = replay_path(poll_t)
        path.parent.mkdir(parents=True, exist_ok=True)
        mode = "a" if path in open_paths else "w"     # first touch truncates
        open_paths.add(path)
        with path.open(mode, encoding="utf-8") as fh:
            fh.write(replay_frame(poll, poll_t))
        written[day] = written.get(day, 0) + 1
        last_bin = poll_t // FRAME_S

    # Rows are appended in time order, so one pass groups them into polls.
    for f in files:
        with gzip.open(f, "rt", encoding="utf-8") as fh:
            for line in fh:
                r = json.loads(line)
                if r["observed_at"] != poll_t:
                    flush()
                    poll, poll_t = [], r["observed_at"]
                r.setdefault("unchanged_polls", 0)
                fix_route(r)
                if r.get("delay_raw"):
                    r["delay_seconds"], r["delay_capped"] = parse_delay(r["delay_raw"])
                poll.append(r)
    flush()

    for day, found in sorted(arrived.items()):
        append_arrivals(found, mode="w")
        print(f"{day}: {len(found)} arrivals -> {OUT_DIR / 'arrivals' / day}")
    for day, n in sorted(written.items()):
        print(f"{day}: {n} frames -> {OUT_DIR / 'replay' / (day + '.jsonl')}")
    if not written:
        print("nothing written" + (f" for {only_day}" if only_day else ""))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
