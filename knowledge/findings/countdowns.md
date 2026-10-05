---
type: Finding
title: Countdown accuracy
description: MATA's countdowns are good close up and optimistic far out; a rider timing their walk to a 20-minute countdown finds the bus already gone 4 times in 10.
tags: [official-feed, predictions]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[PREDICT]"]
sources:
  - id: q-predict
    resource: ../../analysis.sql
    title: analysis.sql [PREDICT]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [are the countdowns riders see honest?](../questions/countdowns.md)

# Answer

250,024 predictions in MATA's [official feed](../feeds/official-gtfs-rt.md)
for trips with a bus, against when it left the stop:[^q-predict][^snapshot]

| Made ahead | Within ±2 min | Bus 1+ min *earlier* | Bus 5+ min later |
|---|---|---|---|
| 0–5 min | 87% | 9% | 4% |
| 5–10 | 70% | 29% | 5% |
| 10–20 | 54% | 37% | 8% |
| 20–40 | 41% | 42% | 12% |
| 40+ | 33% | 45% | 15% |

The median error is about 0, but far-out countdowns lean late: **a rider
timing their walk to a 20-minute countdown finds the bus already gone 4
times in 10.**

[^q-predict]: analysis.sql [PREDICT]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
