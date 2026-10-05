---
type: Finding
title: How many people are riding right now
description: The query works; at 20:21 Friday, 25 buses were in service with 95 riders on board.
tags: [ridership, load]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[Q3]"]
sources:
  - id: q-q3
    resource: ../../analysis.sql
    title: analysis.sql [Q3]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [how many people are riding right now?](../questions/riders-now.md)

# Answer

At 20:21 Friday: 25 buses and 95 riders on board.[^q-q3][^snapshot]

# Method

Reads the [latest snapshot](../datasets/latest-snapshot.md), leaves out buses
still for 30+ polls, and sums load % ÷ 2: the vendor's 100% is 50 riders
([bus capacity](../decisions/bus-capacity.md)).

[^q-q3]: analysis.sql [Q3]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
