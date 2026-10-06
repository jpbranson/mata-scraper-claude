---
type: Finding
title: Departures from the first stop
description: 60% of 5,011 trips over 11 days left their first stop on time (58% on weekdays, 75% on Sundays); the median left 3.9 min late, 39% left 5+ min late, and 1% left early; routes 19 and 34 are worst (64–65% 5+ min late).
tags: [delay, official-feed, departures]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[DEPART]"]
sources:
  - id: q-depart
    resource: ../../analysis.sql
    title: analysis.sql [DEPART]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Part of the evidence for the [late threshold](../decisions/late-threshold.md):
the on-time share of departures is the figure nearest MATA's own.

# Answer

From MATA's feed, 5,011 trips from Fri 09-25 to Mon 10-05, 91% of the
5,532 that ran:[^q-depart][^snapshot][^one-off]

- **60% left their first stop on time** (≤ 1 min early, ≤ 5 late); median
  3.9 min late; 39% left 5+ min late; 1% early.
- **By day type**: weekdays 58% on time (3,715 trips; each of the 7
  weekdays 54–61%), Saturdays 60%, Sundays 75% (median 2.8 min
  late).[^one-off]
- **By route**, worst: 19 (65% of trips left 5+ min late), 34 (64%), 69
  (55%), 37 (53%), 30 (52%). Best: 13 (75% on time), 07 (74%), trolley
  (73%), 53 (71%), 32 (67%). 53–379 trips a route.
- On Fri 09-25 alone (the 1.8-day copy) route 30 was the best (86% on
  time) and 37, 50, 16 and 28 the worst. Over 11 days 30 is among the
  worst (46%), 37 still is, and 28 is better than average (64%).
- These late starts are where most routes' delay comes from; most then
  recover ([where delay builds up](where-delay-builds.md)). Buses reach the
  end of the line about on time and leave the next trip late;
  [driver changes](driver-changes.md) looks at why.

# Method

Departures come from MATA's [official feed](../feeds/official-gtfs-rt.md),
which keeps a bus at its next trip's first stop
([layovers](layovers.md)). The tracker can't time them: at a line's end it
still shows the finished trip's headsign when the bus leaves, so its log
there is a departure credited to the trip just ended (it makes 21% of line
ends look 2+ min early). `arrivals_due` in
[analysis.sql](../system/analysis-sql.md) leaves line ends out for that
reason.[^one-off]

[^q-depart]: analysis.sql [DEPART]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
