---
type: Dataset
title: Detour log
description: The tracker's detours and rider messages, one line each time either changed (checked hourly); from 2026-09-25 20:12, for the detour-impact question.
resource: ../../data/detours/
tags: [detours, tracker]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: flight-log-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FLIGHT_LOG.md
    title: FLIGHT_LOG.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Layout

`data/detours/dt=YYYY-MM-DD/detours.jsonl.gz` (UTC date of `fetched_at`),
written by the [detour logger](../system/detour-logger.md) from its first
poller restart after 2026-09-25 (logging since 20:12:42 CDT that day). One
line whenever the [detours](../feeds/tracker-detours.md) or the tracker's
[rider messages](../feeds/tracker-messages.md) changed since the last one
saved (checked hourly, and once at every start). Days of detours cost a few
KB. Not in git.

# Schema

| Field | Notes |
|---|---|
| `fetched_at` | Unix seconds |
| `detours` | One per line on detour: `route_id`, `stops` (stop codes it skips), `bypassed_segments` (count), `paths` (replacement geometry, lists of `[lon, lat]`) |
| `messages` | Every rider message: `routes` MATA tagged it with (occasionally wrong; `rider_messages` in [analysis.sql](../system/analysis-sql.md) prefers the routes its text names), `text` |

A route's detour runs from the first line that lists it to the first that
doesn't.

# Used for

The [detour impact](../questions/detour-impact.md) question, once weeks of
it exist. Not drawn on the map.
