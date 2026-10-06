---
type: API Endpoint
title: Tracker rider messages (/iv/message)
description: The tracker's rider-facing notices, detours and trips out of service alike; saved hourly to the detour log.
resource: https://swiv.mata.cadavl.com/SWIV/MATA/proxy/restWS/iv/message
tags: [tracker, detours, missed-service]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: detours-code
    resource: ../../cadavl_detours.py
    title: cadavl_detours.py (fetch_messages, DetourLog)
  - id: snapshot-1005
    resource: Measured on findings_page/snapshot-2026-10-05 (copy of data/ taken 2026-10-05 22:37 CDT)
    title: Measurements on the 2026-10-05 snapshot (detour log, 2026-09-25 20:12 to 2026-10-05 20:00)
---

# What it is

The [tracker's](swiv-tracker.md) rider notices. Small: up to 28 at a time
from 2026-09-25 to 10-05.[^snapshot-1005] Not only detours: "Route 11 Out
of service Outbound from Thomas & Whitney @ 7:45 PM. The next unit is
scheduled to arrive at 8:39 PM" sits beside "Route 39 diverted. Stops: …".
So the [detour log](../datasets/detour-log.md) also holds missed-trip
notices from the tracker's side.

Each message carries the lines MATA tagged it with, as internal line IDs
the logger turns into route numbers through the crosswalk.[^detours-code]
The tags are occasionally wrong; the `rider_messages` view in
[analysis.sql](../system/analysis-sql.md) prefers the routes its text names.
The `lignes` filter is ignored, so it is called bare.

# Used for

Fetched once an hour with [`/topo/refresh`](tracker-detours.md) by the
[detour logger](../system/detour-logger.md).

[^detours-code]: cadavl_detours.py (fetch_messages, DetourLog)
[^snapshot-1005]: Measurements on the 2026-10-05 snapshot
