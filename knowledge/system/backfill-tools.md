---
type: Component
title: Backfill tools
description: backfill_routes.py remaps history rows stored as cadavl:<id> to route numbers, and backfill_replay.py rebuilds a day's replay frames and arrivals from the full history; ops/backfill.ps1 runs both with the poller paused.
resource: ../../backfill_replay.py
tags: [ops, replay, crosswalk]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:39:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: backfill-replay-code
    resource: ../../backfill_replay.py
    title: backfill_replay.py
  - id: backfill-routes-code
    resource: ../../backfill_routes.py
    title: backfill_routes.py
  - id: backfill-ps1
    resource: ../../ops/backfill.ps1
    title: ops/backfill.ps1
  - id: schedule-code
    resource: ../../schedule.py
    title: schedule.py, Timetable and Timetable.write
---

# The two scripts

One-off tools, optional to the running system.

- **`backfill_routes.py [dt]`** rewrites [history](../datasets/positions.md)
  rows whose `route_id` is `cadavl:<id>` (lines the poller didn't know when
  it saw them, see [poller](poller.md)) with today's
  [`routes.csv`](../datasets/routes-csv.md) (`route_id` and `route_color`);
  rows on lines it doesn't know are left alone and counted. Without an
  argument it does every file in `data/positions/`; with one, the file for
  that `dt=` (a UTC date).
- **`python backfill_replay.py [day]`** rebuilds a day's [replay
  frames](../datasets/replay-frames.md), [arrivals](../datasets/arrivals-log.md)
  and stop schedules from the full history (every day, or one local date):
  for days recorded before those existed, after any gap, or to bring old
  frames up to the current format. On the way it repairs, in what it
  writes, two things older pollers got wrong: `cadavl:<id>` routes (mapped
  with today's `routes.csv`) and "1h+" delays, which pollers until the
  evening of 2026-09-24 stored as 0 (it re-parses `delay_raw`; see [tracker
  known limits](../feeds/tracker-vehicles.md)). Files for the days touched
  are rewritten from scratch.

# Which timetable a day is matched to

MATA's [GTFS feed](../feeds/gtfs-timetable.md) covers only the day it was
fetched onward (the 2026-10-05 copy's `calendar.txt` starts 20261005), so
for an earlier day it has no trip due. `backfill_replay.py` therefore
matches each day's arrivals to the timetable the poller saved that day,
`data/schedule/<day>/` (`Timetable.saved`), and leaves those files as they
are. A day with no saved timetable uses the feed's if it has service that
day (and saves it); with neither, the day's arrivals and schedule files are
left alone and only its replay frames are rebuilt, with a line saying
so.[^backfill-replay-code][^schedule-code]

Until 2026-10-05 it loaded every day from the current `data/gtfs.zip`, so a
past day got 0 stop times due (2026-09-28, against 55,953 for 10-05): its
arrivals would have been rewritten with every `trip` null and its
`stops.json` emptied. No past day was rebuilt that way. Tested on a copy:
`Timetable.saved` for 2026-10-05 equals the feed's timetable for that day
(the same 55,953 stop times, stop patterns and stop-name index), a rebuild
of 2026-09-29 reproduces the poller's 42,036 arrivals byte for byte, and
2026-09-23, which has no saved timetable, is skipped.
`backfill_routes.py` doesn't touch the timetable.

# Running them

Use `.\ops\backfill.ps1` (every day) or `.\ops\backfill.ps1 2026-09-24` (one
day). It pauses the poller, runs `backfill_routes.py` (every history file)
and `backfill_replay.py`, and starts the poller again. Run it when:

- the poller has logged `cadavl:<id>` routes;
- a day was recorded before replay or arrivals existed;
- a day's replay frames should be brought up to the current format.

Run it from your own PowerShell window: a sandboxed shell can't see the
poller's command line, so it can't stop it ([working with live
data](../operations/working-with-live-data.md)).

[^backfill-replay-code]: backfill_replay.py
[^schedule-code]: schedule.py, Timetable, Timetable.saved and Timetable.write
