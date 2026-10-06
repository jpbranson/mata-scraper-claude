---
type: Finding
title: Countdown accuracy
description: Over 11 days and 2.7 million predictions, MATA's countdowns are good close up (87% within 2 min) and lean late far out; a rider timing their walk to a 20-minute countdown finds the bus already gone 4 times in 10, every day.
tags: [official-feed, predictions]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[PREDICT]"]
sources:
  - id: q-predict
    resource: ../../analysis.sql
    title: analysis.sql [PREDICT]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [are the countdowns riders see honest?](../questions/countdowns.md)

# Answer

2,748,928 predictions in MATA's [official feed](../feeds/official-gtfs-rt.md)
for trips with a bus, Fri 09-25 to Mon 10-05, against when it left the
stop:[^q-predict][^snapshot]

| Made ahead | Within ±2 min | Bus 1+ min *earlier* | Bus 5+ min later |
|---|---|---|---|
| 0–5 min | 87% | 9% | 4% |
| 5–10 | 70% | 29% | 5% |
| 10–20 | 55% | 37% | 8% |
| 20–40 | 43% | 42% | 10% |
| 40+ | 35% | 48% | 13% |

The median error is about 0 (−0.3 to +0.1 min up to 40 min ahead), but
far-out countdowns lean late: **a rider timing their walk to a 20-minute
countdown finds the bus already gone 4 times in 10** (39% of predictions
made 18–22 min ahead).[^one-off] It holds on every day (39–49% of 20–40
min predictions). Weekends lean a little further: 46–47% at 20–40 min
against 41% on weekdays.[^one-off]

[^q-predict]: analysis.sql [PREDICT]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
