---
type: Finding
title: Departures from the first stop
description: 60% of Friday's trips left their first stop on time; the median left 4.2 min late, 40% left 5+ min late, and 1% left early.
tags: [delay, official-feed, departures]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[DEPART]"]
sources:
  - id: q-depart
    resource: ../../analysis.sql
    title: analysis.sql [DEPART]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Part of the evidence for the [late threshold](../decisions/late-threshold.md):
the on-time share of departures is the figure nearest MATA's own.

# Answer

From MATA's feed, 455 Friday trips:[^q-depart][^snapshot]

- **60% left their first stop on time** (≤ 1 min early, ≤ 5 late); median
  4.2 min late; 40% left 5+ min late; 1% early.
- **By route**, worst: 37 (78% of trips left 5+ min late), 50 (66%), 16
  (60%), 28 (57%). Best: 30 (86% on time), 07 (85%), trolley (77%), 53
  (76%), 13 (75%). Small numbers per route (4–35 trips, one day).
- These late starts are where most routes' delay comes from; most then
  recover ([where delay builds up](where-delay-builds.md)).

# Method

Departures come from MATA's [official feed](../feeds/official-gtfs-rt.md),
which keeps a bus at its next trip's first stop
([layovers](layovers.md)). The tracker can't time them: at a line's end it
still shows the finished trip's headsign when the bus leaves, so its log
there is a departure credited to the trip just ended (it made line ends
look 22% early). `arrivals_due` in [analysis.sql](../system/analysis-sql.md)
leaves line ends out for that reason.

[^q-depart]: analysis.sql [DEPART]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
