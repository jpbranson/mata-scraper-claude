---
type: Dataset
title: Arrivals log
description: Each time a bus served a stop, with the trip it was matched to and its delay, split by day and route; ~40k a day.
resource: ../../data/arrivals/
tags: [timetable, delay, headway]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Layout

`data/arrivals/<day>/<route>.jsonl`, appended by
[schedule.py](../system/timetable-and-arrivals.md) whenever a bus's next stop
changes (how a stop and trip are matched is there). Split by route so the
[map](../system/live-map.md) fetches only the routes at a clicked stop.
Not in git. [backfill_replay.py](../system/backfill-tools.md) rebuilds a
day's arrivals from the history.

# Schema

One JSON object per line:

| Field | Notes |
|---|---|
| `t` | When the bus served the stop: the last poll that still showed it as next (±10 s), Unix seconds |
| `stop` | Stop code; MATA's GTFS `stop_id` is `0:` + this |
| `vehicle` | The tracker's `vehicle_id`, not the fleet number |
| `trip` | GTFS trip it was matched to; null when the delay was a "1h+" cap |
| `delay` | The vendor's reported delay at that poll, seconds; null for "1h+" caps |

# Size

~40k records a day, ~2.5 MB.

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
