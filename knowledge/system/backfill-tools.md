---
type: Component
title: Backfill tools
description: backfill_routes.py remaps history rows stored as cadavl:<id> to route numbers, and backfill_replay.py rebuilds a day's replay frames and arrivals from the full history; ops/backfill.ps1 runs both with the poller paused.
resource: ../../backfill_replay.py
tags: [ops, replay, crosswalk]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
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
