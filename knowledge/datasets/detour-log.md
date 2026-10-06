---
type: Dataset
title: Detour log
description: The tracker's detours and rider messages, one line each time either changed (checked hourly); from 2026-09-25 20:12, for the detour-impact question.
resource: ../../data/detours/
tags: [detours, tracker]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: flight-log-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FLIGHT_LOG.md
    title: FLIGHT_LOG.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
  - id: detours-code
    resource: ../../cadavl_detours.py
    title: cadavl_detours.py (DetourLog, stop_codes, build_segment_index)
  - id: poller-log
    resource: ../../data/poller.log
    title: poller.log, "detour log failed" lines 2026-09-25 22:12 to 09-27 19:00
  - id: fix-commit
    resource: https://github.com/jpbranson/mata-scraper-claude/commit/8de1cc1
    title: "8de1cc1 cadavl_detours: treat a null objetsSuppl as no itineraries"
  - id: snapshot-1005
    resource: Measured on findings_page/snapshot-2026-10-05 (copy of data/ taken 2026-10-05 22:37 CDT)
    title: Measurements on the 2026-10-05 snapshot (data/detours, 2026-09-25 20:12 to 2026-10-05 20:00)
---

# Layout

`data/detours/dt=YYYY-MM-DD/detours.jsonl.gz` (UTC date of `fetched_at`),
written by the [detour logger](../system/detour-logger.md) from its first
poller restart after 2026-09-25 (logging since 20:12:42 CDT that day). One
line whenever the [detours](../feeds/tracker-detours.md) or the tracker's
[rider messages](../feeds/tracker-messages.md) changed since the last one
saved (checked hourly, and once at every start). Not in git.

2 to 17 lines and 4–107 KB a day; 120 lines and 196 KB from 2026-09-25 to
10-05.[^snapshot-1005]

# Schema

| Field | Notes |
|---|---|
| `fetched_at` | Unix seconds |
| `detours` | One per line on detour: `route_id`, `stops` (stop codes it skips; `cadavl:<id>` for a stop missing from [stops.csv](stops-csv.md)), `bypassed_segments` (count), `paths` (replacement geometry, lists of `[lon, lat]`); 0 to 8 at a time so far, often none |
| `messages` | Every rider message, up to 28 at a time so far: `routes` MATA tagged it with (occasionally wrong; `rider_messages` in [analysis.sql](../system/analysis-sql.md) prefers the routes its text names), `text` |

A route's detour runs from the first line that lists it to the first that
doesn't.

# Gaps and flaws

- **No checks from 2026-09-26 22:00 to 09-27 19:38.** When no line was
  detoured the vendor sent `objetsSuppl` null, and the logger failed on it:
  19 times, at 2026-09-25 22:12 and 23:12 and every hour from 09-26 23:00 to
  09-27 19:00.[^poller-log] Fixed in 8de1cc1, live from the 19:38
  restart.[^fix-commit] Changes in that window are lost.
- **Routes and stops need a current crosswalk.** The logger maps the
  tracker's internal IDs with routes.csv and stops.csv. After
  `ops/update.ps1` reset them to the committed topo 198256 at 2026-10-01
  23:09, with no bus out to trigger a rebuild, that start's line tagged 5
  messages with `cadavl:<id>` routes. All five name their route in the
  text, so `rider_messages` recovers them.[^detours-code][^snapshot-1005]

# Used for

The [detour impact](../questions/detour-impact.md) question, once weeks of
it exist. Not drawn on the map.

[^detours-code]: cadavl_detours.py (DetourLog, stop_codes, build_segment_index)
[^poller-log]: poller.log, "detour log failed" lines 2026-09-25 22:12 to 09-27 19:00
[^fix-commit]: 8de1cc1 cadavl_detours: treat a null objetsSuppl as no itineraries
[^snapshot-1005]: Measurements on the 2026-10-05 snapshot
