---
type: Finding
title: Busiest vs latest
description: Across routes, load and lateness are barely related (correlation 0.15), but within a route fuller buses are much later, 31% against 18% 5+ min late at the same route and hour on weekdays; route 42 is the exception.
tags: [load, delay]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[LOAD_DELAY]"]
sources:
  - id: q-load_delay
    resource: ../../analysis.sql
    title: analysis.sql [LOAD_DELAY]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [are the busiest routes the latest?](../questions/busiest-vs-latest.md)

# Answer

- **Across routes, barely related** (correlation 0.15; 0.05 on weekdays
  alone): 52, the busiest (10 riders on average), is 18% late, 42 (9.5)
  13%, while 36 (9.3) is among the latest at 26%.[^q-load_delay][^snapshot]
- **Within a route, fuller buses are much later** (share 5+ min late):

  | Route | 20+ riders | Under 10 riders | Polls with 20+ |
  |---|---|---|---|
  | 52 | 37% | 12% | 12,589 |
  | 36 | 38% | 21% | 21,908 |
  | 50 | 36% | 14% | 26,496 |
  | 08 | 34% | 17% | 5,823 |
  | 12 | 42% | 15% | 2,338 |
  | 57 | 59% | 13% | 2,114 |
  | 01 | 59% | 18% | 3,003 |
  | 02 | 60% | 22% | 1,112 |
  | 42 | 15% | 13% | 22,468 |

  Route 42, with the most full buses after 50, is the exception: its fuller
  buses are barely later. Routes with a few hundred 20+ polls or fewer
  (19, 32, 13, 07, 100) are too thin to read.
- **It isn't time of day.** Comparing fuller and emptier buses on the same
  route in the same hour on weekdays, 31% of the fuller ones are 5+ min late
  against 18% of the emptier ones.[^one-off]
- Boarding time, or late buses collecting more waiting riders: the data
  can't separate the two.

[^q-load_delay]: analysis.sql [LOAD_DELAY]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
