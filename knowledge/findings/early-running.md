---
type: Finding
title: Early running
description: 9% of bus-polls are 2+ min early, clustered at a few timepoints led by route 30 at American Way Transit Center (65%); from the start of a line buses almost never leave early.
tags: [delay, early]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[EARLY]", "[Q1]"]
sources:
  - id: q-early
    resource: ../../analysis.sql
    title: analysis.sql [EARLY]
  - id: q-q1
    resource: ../../analysis.sql
    title: analysis.sql [Q1]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [early running](../questions/early-running.md). Early means 2+ min
early in the vendor's whole minutes ([late threshold](../decisions/late-threshold.md)).

# Answer

- **Overall:** 9% of all bus-polls are 2+ min early,[^q-q1] and 8% of
  departures from mid-route timepoints.[^q-early][^snapshot]
- **By route** (share of polls 2+ min early): the trolley (100) 20%, route
  40 17%, 07, 30, 04 and 57 14–15%.
- **By timepoint**, it clusters at a few: route 30 at American Way Transit
  Center 65% (avg 3.9 min early, at a transfer point), 40 at James Rd @
  Hollywood 40%, the trolley at Main @ Madison 37%, 01 at Union @ Waldran
  32%, 04 at Pendleton @ Ketchum 28%, then 19–22% on 28, 57 (Park @
  Perkins, Lamar @ East Pkwy), 40 (Stage @ Summer), 50 (Poplar @ Cleveland)
  and 69 (Sax Rd @ Mitchell).
- **From the start of a line** buses almost never leave early (1%,
  [departures](departures.md)); they leave late.
- By hour it peaks at night and at 4 a.m. ([when delay goes bad](time-of-day.md)),
  and routes 30, 37, 40, 04, 42, 50 and 57 finish trips well ahead of how
  they started ([where delay builds up](where-delay-builds.md)): their
  schedules have slack.

[^q-early]: analysis.sql [EARLY]
[^q-q1]: analysis.sql [Q1]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
