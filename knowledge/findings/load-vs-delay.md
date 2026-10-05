---
type: Finding
title: Busiest vs latest
description: Across routes, load and lateness are barely related (correlation 0.19), but within a route fuller buses are much later.
tags: [load, delay]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[LOAD_DELAY]"]
sources:
  - id: q-load_delay
    resource: ../../analysis.sql
    title: analysis.sql [LOAD_DELAY]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [are the busiest routes the latest?](../questions/busiest-vs-latest.md)

# Answer

- **Across routes, barely related** (correlation 0.19): 42, the busiest, is
  10% late.[^q-load_delay][^snapshot]
- **Within a route, fuller buses are much later** (share 5+ min late):

  | Route | 20+ riders | Under 10 riders |
  |---|---|---|
  | 50 | 46% | 16% |
  | 57 | 42% | 15% |
  | 12 | 40% | 6% |
  | 08 | 58% | 26% |
  | 02 | 62% | 34% |
  | 36 | 39% | 22% |

- Boarding time, or late buses collecting more waiting riders: the data
  can't separate the two.

[^q-load_delay]: analysis.sql [LOAD_DELAY]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
