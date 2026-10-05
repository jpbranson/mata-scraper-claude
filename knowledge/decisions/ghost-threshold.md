---
type: Decision
title: "Ghost threshold: keep the 30-poll rule"
description: Rows of a bus still for 30+ polls stay out of delay figures (they are mostly layovers), and spatial queries also drop the dead-tracker rows that ghost_rows finds.
tags: [gps, tracker, data-quality]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
sources:
  - id: ghost-trackers
    resource: ../findings/ghost-trackers.md
    title: Ghost trackers and still buses
  - id: analysis-sql
    resource: ../../analysis.sql
    title: analysis.sql (good, ghost_rows)
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Decision

Settled 2026-09-25, on 1.8 days of data; recheck after a week (hence
`stale_after`).

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

- 30 still polls almost never means a dead tracker: of 191 such streaks
  (183 on the earlier copy first used: 127 layovers, 45 holds, 8 dead),
  130 were layovers at a route's end and 47 holds mid-route (the bus later
  drove off from the same spot); 8 were dead trackers.
- Dead trackers show instead as a still streak, usually 1–5 minutes, that
  ends with the bus reappearing 200 m+ away; the official feed's report
  times freeze over the same stretches.
- The vendor freezes the delay along with the position, so swapping one
  rule for the other moves no route's 5+ min late share by more than 1.4
  points (on the earlier copy, by more than about a point: ±1.2).
- Bus 458 alone has nearly half the ghost rows (15% of its polls).

[^ghost-trackers]: Ghost trackers and still buses
[^analysis-sql]: analysis.sql (good, ghost_rows)
