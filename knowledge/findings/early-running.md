---
type: Finding
title: Early running
description: 9% of bus-polls are 2+ min early, clustered at a few timepoints led by the trolley at Main @ Madison (52%) and route 30 at American Way Transit Center (51%); Sundays run early more (11%), and from the start of a line buses almost never leave early (1%).
tags: [delay, early]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:19:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[EARLY]", "[Q1]"]
sources:
  - id: q-early
    resource: ../../analysis.sql
    title: analysis.sql [EARLY]
  - id: q-q1
    resource: ../../analysis.sql
    title: analysis.sql [Q1]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [early running](../questions/early-running.md). Early means 2+ min
early in the vendor's whole minutes ([late threshold](../decisions/late-threshold.md)).

# Answer

- **Overall:** 9% of all bus-polls are 2+ min early,[^q-q1] and 8% of
  24,552 departures from mid-route timepoints, over 12
  days.[^one-off][^snapshot]
- **By route** (share of polls 2+ min early): the trolley (100) 25%, then
  07, 30 and 57 15%, 40 13%, 04 12%, 42 and 50 11%.[^q-q1]
- **By timepoint**, it clusters at a few:[^q-early] the trolley at Main @
  Madison 52% (294 departures, avg 3.4 min early), route 30 at American
  Way Transit Center 51% (avg 4.0 min early, at a transfer point), 40 at
  James Rd @ Hollywood 30%, 52 at Yale Rd @ Austin Peay 24%, 04 at
  Pendleton @ Ketchum 20%, then 14–19% on 57 (Park @ Perkins, Lamar @ East
  Pkwy), 50 (Poplar @ Cleveland), 52 (Jackson @ Watkins), 04 (Vance @
  Fourth), 32 (James Rd @ Hollywood), 30 (Holmes @ Lamar, IRS), 42
  (Bellevue @ Lamar) and 01 (Union @ Waldran).
- **Sundays run early more**: 11% of bus-polls and of timepoint
  departures, against 8–9% on weekdays and Saturdays. The trolley leaves
  Main @ Madison early on 66–68% of weekend passes (45% on
  weekdays).[^one-off]
- On 1.8 days route 30 at American Way led (65%) and the trolley at Main @
  Madison was third (37%); over 12 days the two are level at the top.
- **From the start of a line** buses almost never leave early (1%,
  [departures](departures.md)); they leave late.
- By hour it peaks late in the evening and at 4 a.m.
  ([when delay goes bad](time-of-day.md)), and routes 37, 30, 57, 40, 19,
  07 and 04 finish trips 4.2–5.8 min ahead of how they started
  ([where delay builds up](where-delay-builds.md)): their schedules have
  slack. `[WHERE]` counts early as on time, so an early bus waiting at a
  timepoint doesn't show there as delay gained.

[^q-early]: analysis.sql [EARLY]
[^q-q1]: analysis.sql [Q1]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
