---
type: Dataset
title: Arrivals log
description: Each time a bus served a stop, with the trip it was matched to and its delay, split by day and route; ~42k a weekday.
resource: ../../data/arrivals/
tags: [timetable, delay, headway]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:39:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
  - id: schedule-code
    resource: ../../schedule.py
    title: schedule.py (Arrivals.update, Timetable.trip_for, MATCH_WINDOW)
  - id: backfill-replay
    resource: ../../backfill_replay.py
    title: backfill_replay.py (timetable_for, append_arrivals mode "w")
  - id: snapshot-1005
    resource: Measured on findings_page/snapshot-2026-10-05 (copy of data/ taken 2026-10-05 22:37 CDT)
    title: Measurements on the 2026-10-05 snapshot (data/arrivals, 2026-09-23 to 10-05)
---

# Layout

`data/arrivals/<day>/<route>.jsonl` (local day), appended by
[schedule.py](../system/timetable-and-arrivals.md) whenever a bus's next stop
changes (how a stop and trip are matched is there). Split by route so the
[map](../system/live-map.md) fetches only the routes at a clicked stop.
Not in git. From 2026-09-23 (that day rebuilt from the history, without
trips).[^snapshot-1005] [backfill_replay.py](../system/backfill-tools.md)
rebuilds a day's arrivals from the history, but see
[below](#rebuilding-a-past-day).

# Schema

One JSON object per line, these five fields:

| Field | Notes |
|---|---|
| `t` | When the bus served the stop: the last poll that still showed it as next (±10 s), Unix seconds |
| `stop` | Stop code; MATA's GTFS `stop_id` is `0:` + this |
| `vehicle` | The tracker's `vehicle_id`, not the fleet number |
| `trip` | GTFS trip it was matched to; null when the delay was a "1h+" cap, or when no trip of that route and headsign was due at the stop within 20 min of (`t` − delay)[^schedule-code] |
| `delay` | The vendor's reported delay at that poll, seconds; null for "1h+" caps |

From 2026-09-23 to 10-05, 2,133 records had neither trip nor delay (caps)
and 323 had a delay but no trip, 310 of them on 2026-09-23.[^snapshot-1005]

# Size

Measured 2026-09-26 to 10-05, ~90 B a record:[^snapshot-1005]

| Day | Records | Size |
|---|---|---|
| Weekday | 41–44k | 3.7–3.9 MB |
| Saturday | ~30k | 2.6 MB |
| Sunday | 18–20k | 1.6–1.7 MB |

About 1.2 GB a year; 38 MB so far.

# Limits

Measured 2026-09-25:

- It catches ~83–85% of the stops on a trip that ran: buses pass some
  stops between polls, or out of the feed.
- At the end of a line the tracker still shows the finished trip's headsign
  while the bus waits, so what it logs there is the departure, credited to
  the trip that just ended. [analysis.sql](../system/analysis-sql.md) leaves
  line ends out of timing questions (`line_ends`, `arrivals_due`) and times
  departures from the [official feed](official-trip-updates.md) instead
  ([departures](../findings/departures.md)).

# Rebuilding a past day

backfill_replay.py matches a past day's arrivals to the timetable saved
that day ([schedule files](schedule-files.md)); rebuilt that way,
2026-09-29's 42,036 arrivals come out byte for byte as the poller wrote
them. A day with no saved timetable and no service in the current feed
(2026-09-23) keeps its arrivals as they are.[^backfill-replay] See
[backfill tools](../system/backfill-tools.md).

[^schedule-code]: schedule.py (Arrivals.update, Timetable.trip_for, MATCH_WINDOW)
[^backfill-replay]: backfill_replay.py (timetable_for, append_arrivals mode "w")
[^snapshot-1005]: Measurements on the 2026-10-05 snapshot
