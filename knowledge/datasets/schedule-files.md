---
type: Dataset
title: Saved timetables (data/schedule)
description: Each service day's timetable as the pages need it, per stop and per route with its stop patterns; the only record of past days' timetables.
resource: ../../data/schedule/
tags: [timetable, gtfs]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: schedule-code
    resource: ../../schedule.py
    title: schedule.py (patterns, write)
---

# Layout

`data/schedule/<day>/`, written by
[schedule.py](../system/timetable-and-arrivals.md) once per service day (and
at startup) from the [GTFS timetable](../feeds/gtfs-timetable.md). 25 files,
~1 MB a day. Not in git. MATA's GTFS feed only covers today onward, so a day
can be replayed on the [strips](../system/route-strips.md) and
[schematic](../system/schematic-map.md) only if its folder exists
(2026-09-23 has none).

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

# Read by

The [map's](../system/live-map.md) stop and bus panels, the strips and
schematic (`locate` in [transit.js](../system/transit-js.md)), and the
`sched`, `timepoints` and `line_ends` views in
[analysis.sql](../system/analysis-sql.md).

[^schedule-code]: schedule.py (patterns, write)
