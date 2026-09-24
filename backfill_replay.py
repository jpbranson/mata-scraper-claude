"""
Rebuild replay frames from the full position history.

The poller writes data/replay/<day>.jsonl as it goes, but only while it is
running the current code. This regenerates those files from
data/positions/ (one row per bus per 10 s), one frame per 30 s, so any
recorded day can be replayed in map.html.

    python backfill_replay.py                # every day in data/positions/
    python backfill_replay.py 2026-09-24     # one day (local date)

Replay files for the days touched are rewritten from scratch. Stop the
poller first if you rebuild today, or its next frame will land in the
rebuilt file out of order (harmless for the map, but untidy).
"""

from __future__ import annotations

import gzip
import json
import sys
from datetime import datetime

from cadavl_to_gtfs_rt import OUT_DIR, POLL_SECONDS, REPLAY_EVERY, replay_frame, replay_path

FRAME_S = POLL_SECONDS * REPLAY_EVERY


def main(only_day: str | None) -> None:
    files = sorted(OUT_DIR.glob("positions/dt=*/positions.jsonl.gz"))
    if not files:
        sys.exit(f"no history under {OUT_DIR / 'positions'}")

    written: dict[str, int] = {}
    open_paths = set()
    poll: list[dict] = []
    poll_t = None
    last_bin = None

    def flush() -> None:
        nonlocal last_bin
        if not poll or poll_t // FRAME_S == last_bin:
            return
        day = datetime.fromtimestamp(poll_t).strftime("%Y-%m-%d")
        if only_day and day != only_day:
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
                poll.append(r)
    flush()

    for day, n in sorted(written.items()):
        print(f"{day}: {n} frames -> {OUT_DIR / 'replay' / (day + '.jsonl')}")
    if not written:
        print("nothing written" + (f" for {only_day}" if only_day else ""))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)
