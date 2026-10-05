---
type: API Endpoint
title: Tracker stop popup (/horaires/pta)
description: The tracker's own stop popup, the next one or two times per route at a stop; unused, kept as a cross-check.
resource: https://swiv.mata.cadavl.com/SWIV/MATA/proxy/restWS/horaires/pta/<stop id>
tags: [tracker, timetable]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
---

# What it is

`/horaires/pta/<stop id>`: what the [tracker](swiv-tracker.md) shows when a
rider clicks a stop, the next one or two times per route. Small.

# Used for

Nothing. It sends no CORS headers, so the [map](../system/live-map.md)
can't call it; stop times there come from the
[GTFS timetable](gtfs-timetable.md) and the
[arrivals log](../datasets/arrivals-log.md). Kept as a cross-check.
