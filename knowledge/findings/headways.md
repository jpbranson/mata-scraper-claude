---
type: Finding
title: Bunching and headways
description: Buses don't bunch and the ones that run keep their spacing; the gaps riders get are trips that never run.
tags: [headway, missed-service]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[HEADWAY]"]
sources:
  - id: q-headway
    resource: ../../analysis.sql
    title: analysis.sql [HEADWAY]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [bus bunching](../questions/bunching.md) and
[effective headway](../questions/effective-headway.md).

# Answer

- **Headways are long.** Median planned gap between consecutive trips at a
  stop: 45 min on the busiest routes (01, 08, 36, 50), 60–120 on most, 4–6
  hours on 28, 34, 37.
- **Bunching essentially never happens.** Of 65,766 pairs of consecutive
  buses at a stop (line ends aside), 6 came within a quarter of their
  planned gap (5 of them one pair: route 50 buses 32055 and 23023, 20 min
  apart on paper, together Fri 11:18–11:23), and 34 were
  overtakes.[^q-headway][^snapshot]
- **The buses that run keep their spacing.** Gaps over 1.5× plan between
  two buses that ran: ≤ 0.6% (routes 50, 36), otherwise ~0. A rider turning
  up at random waits ≤ 1 min longer than the timetable implies on most
  routes; route 28 +5.6 min (6-hour gaps, 54 pairs), 02 +3.7, 52 +2.3, 37
  +1.8, 53 +1.5.
- The gaps riders actually get are **trips that never run**: see
  [missed service](missed-service.md) and, per stop,
  [what riders get at the stop](stop-waits.md).

# Method

`[HEADWAY]` pairs each bus with the one before it at the stop and compares
against *their two trips'* planned difference. Counting from "the previous
bus seen" instead overstates gaps, because the
[arrivals log](../datasets/arrivals-log.md) catches only ~84% of the stops
on a trip that ran (99% on the trolley).

Two buses logged in the same second are ordered by their timetable, so the
bunched and overtake counts no longer shift from run to run.

[^q-headway]: analysis.sql [HEADWAY]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
