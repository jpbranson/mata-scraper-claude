---
type: Dataset
title: Saved timetables (data/schedule)
description: Each service day's timetable as the pages need it, per stop and per route with its stop patterns; the only record of past days' timetables.
resource: ../../data/schedule/
tags: [timetable, gtfs]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:39:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: schedule-code
    resource: ../../schedule.py
    title: schedule.py (patterns, write)
  - id: backfill-replay
    resource: ../../backfill_replay.py
    title: backfill_replay.py (timetable_for)
  - id: snapshot-1005
    resource: Measured on findings_page/snapshot-2026-10-05 (copy of data/ taken 2026-10-05 22:37 CDT)
    title: Measurements on the 2026-10-05 snapshot (data/schedule, 2026-09-24 to 10-05)
---

# Layout

`data/schedule/<day>/`, written by
[schedule.py](../system/timetable-and-arrivals.md) once per service day (and
at startup, and after a crosswalk rebuild) from the
[GTFS timetable](../feeds/gtfs-timetable.md). Not in git. MATA's GTFS feed
only covers today onward, so a day can be replayed on the
[strips](../system/route-strips.md) and [schematic](../system/schematic-map.md)
only if its folder exists. Folders exist from 2026-09-24 (2026-09-23 has
none).[^snapshot-1005]

| Day | Files | Size |
|---|---|---|
| Weekday | 26: `stops.json` and 25 routes | 1.04 MB |
| Saturday | 26 | 0.84 MB |
| Sunday | 21 (no 12, 19, 34, 37 or 69) | 0.57 MB |

About 50 MB a year.

# Schema

Times are seconds after the file's `t0` (local midnight).[^schedule-code]

**`stops.json`**: `{t0, stops: {<stop code>: [routes]}}`, the routes
scheduled to stop there. From the timetable, not
[`/topo`](../feeds/tracker-topo.md), which lists lines that pass without
stopping.

**`<route>.json`**: that route's

- `trips`: `[trip_id, headsign]`, indexed by position;
- `stops`: per stop code, `[seconds after t0, trip index]` for each call;
- `patterns`: per headsign, each stop sequence that is a real branch (at
  least a fifth of its trips, and sharing under 80% of its stops with the
  main one: route 36 via Lamar or via Kimball). Each is `{head, dir, trips,
  stops}`, the stops in order as `[code, name, lat, lon, median seconds from
  the first stop, timepoint flag]`.

They hold no `block_id` and no stop times beyond each route's calls:
blocks are only in the timetable's `trips.txt`. Trip IDs have been stable
across timetable rebuilds, so today's timetable's blocks apply to past days
while MATA keeps the same schedule (see
[GTFS timetable](../feeds/gtfs-timetable.md#trip-ids)).

# Rebuilding a past day

[backfill_replay.py](../system/backfill-tools.md) reads a past day's
timetable back from these files (`Timetable.saved`) to match its
[arrivals](arrivals-log.md), and leaves them as they are. Only a day with
no folder here gets one written, from the current `data/gtfs.zip`, and only
if that has service on the day. Until 2026-10-05 it rewrote every day's
folder from the current feed, which would have emptied a past day's
`stops.json`.[^backfill-replay][^schedule-code]

# Read by

The [map's](../system/live-map.md) stop and bus panels, the strips and
schematic (`locate` in [transit.js](../system/transit-js.md)), and the
`sched`, `timepoints` and `line_ends` views in
[analysis.sql](../system/analysis-sql.md).

[^schedule-code]: schedule.py (patterns, write, Timetable.saved)
[^backfill-replay]: backfill_replay.py (timetable_for)
[^snapshot-1005]: Measurements on the 2026-10-05 snapshot
