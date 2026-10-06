---
type: Finding
title: How many people are riding right now
description: The query works, now after service too (0 buses, 0 riders at 22:37 Monday); at 20:21 on Fri 2026-09-25, 25 buses carried 95 riders, and at 20:21 on the 8 weekdays 21–29 buses carried 82–152.
tags: [ridership, load]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[Q3]"]
sources:
  - id: q-q3
    resource: ../../analysis.sql
    title: analysis.sql [Q3]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: snapshot-0925
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [how many people are riding right now?](../questions/riders-now.md)

# Answer

- At 20:21 on Fri 2026-09-25: 25 buses and 95 riders on
  board.[^q-q3][^snapshot-0925]
- At 22:37 on Mon 2026-10-05, after the last bus left: 0 buses, 0
  riders.[^q-q3][^snapshot] Until 2026-10-05 the query failed after service,
  when the latest poll has no vehicles; it now names its columns and
  works at any hour.
- For scale, from the history at the same time of day, 20:21: on the 8
  weekdays 21–29 buses carried 82–152 riders (median 111); on the two
  Saturdays 9–12 buses carried 22–28; on Sundays service had
  ended.[^one-off]

# Method

Reads the [latest snapshot](../datasets/latest-snapshot.md), leaves out buses
still for 30+ polls, and sums load % ÷ 2: the vendor's 100% is 50 riders
([bus capacity](../decisions/bus-capacity.md)). The history figures are the
same sum over the poll nearest 20:21 each day in the
[position history](../datasets/positions.md).

[^q-q3]: analysis.sql [Q3]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^snapshot-0925]: Data snapshot, Fri 2026-09-25 20:21
[^one-off]: One-off queries, 2026-10-05
