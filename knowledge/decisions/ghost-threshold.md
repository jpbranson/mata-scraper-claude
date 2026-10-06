---
type: Decision
title: "Ghost threshold: keep the 30-poll rule"
description: Rows of a bus still for 30+ polls stay out of delay figures (they are mostly layovers and holds, 1,196 of 1,332 streaks on 12 days), and spatial queries also drop the dead-tracker rows that ghost_rows finds.
tags: [gps, tracker, data-quality]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
stale_after: 2026-11-04T06:00:00Z
sources:
  - id: ghost-trackers
    resource: ../findings/ghost-trackers.md
    title: Ghost trackers and still buses
  - id: snapshot
    resource: ../findings/snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: analysis-sql
    resource: ../../analysis.sql
    title: analysis.sql (good, ghost_rows)
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
---

# Decision

Settled 2026-09-25 on 1.8 days of data; rechecked 2026-10-05 on 12 days
([data snapshot](../findings/snapshot-2026-10-05.md)), which still support
it.[^snapshot]

- The `good` view keeps `unchanged_polls < 30`.[^analysis-sql]
- Spatial queries drop `ghost_rows`, a view that finds the positions a dead
  tracker left behind ([analysis.sql](../system/analysis-sql.md)).
- The [live map](../system/live-map.md)'s dashed "no GPS movement" marker is
  usually a layover, and is described that way.

The problem it answers: the tracker sends no report time, so a bus whose
coordinates stop changing is either parked (a layover or hold) or has a
tracker that stopped reporting (a "ghost"); see the
[tracker's known limits](../feeds/tracker-vehicles.md).

# Evidence

From [ghost trackers and still buses](../findings/ghost-trackers.md):[^ghost-trackers]

- 30 still polls rarely means a dead tracker: of 1,332 such streaks, 890
  were layovers at a route's end and 306 holds mid-route (the bus later
  drove off from the same spot); 112 (8%) were dead trackers, up from 8 of
  191 on 1.8 days. Most of those weren't one bus: 47 at the start of
  service and 25 in a single fleet-wide freeze (Mon 10-05 16:50).
- Dead trackers show instead as a still streak, usually 1–5 minutes, that
  ends with the bus reappearing 200 m+ away; the official feed's report
  times freeze over the same stretches.
- The vendor freezes the delay along with the position, so swapping one
  rule for the other moves no route's 5+ min late share by more than 1.4
  points, the same as on 1.8 days.
- Bus 458 alone has a quarter of the ghost rows (10.6% of its polls).

[^ghost-trackers]: Ghost trackers and still buses
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^analysis-sql]: analysis.sql (good, ghost_rows)
