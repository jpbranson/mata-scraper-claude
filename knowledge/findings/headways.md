---
type: Finding
title: Bunching and headways
description: Buses don't bunch (231 of 306,716 pairs at a stop in 12 days, nearly all in seven episodes) and the ones that run keep their spacing; the gaps riders get are trips that never run.
tags: [headway, missed-service]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:55Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[HEADWAY]"]
sources:
  - id: q-headway
    resource: ../../analysis.sql
    title: analysis.sql [HEADWAY]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [bus bunching](../questions/bunching.md) and
[effective headway](../questions/effective-headway.md).

# Answer

- **Headways are long.** Median planned gap between consecutive buses at
  a stop: 45 min on the busiest routes (01, 08, 36, 50), 60–120 on most,
  3–6 hours on 07, 16, 28, 34, 37.[^q-headway][^snapshot]
- **Bunching essentially never happens.** Of 306,716 pairs of consecutive
  buses at a stop in 12 days (line ends aside), 231 (0.08%) came within a
  quarter of their planned gap, and 211 of those were seven episodes of
  two buses running together. The longest: route 50 buses 10056 and
  10019, 25 min apart on paper, ran 2–3 min apart for 53 stops, Thu 10-01
  13:30–16:02. Others: 01 Wed 09-30 10:32–11:09, 50 Sat 10-03 17:09–17:54,
  02 Tue 09-29 12:21–12:47. 126 pairs were overtakes.[^one-off]
- **The buses that run keep their spacing.** Gaps over 1.5× plan between
  two buses that ran: 0.6% at most (01, 36, 42). A rider turning up at
  random waits ≤ 1 min longer than the timetable implies on every route
  but 07 (+1.8 min, 62 pairs) and 28 (+1.5, 281 pairs). On 1.8 days 28, 02
  and 52 looked 2–6 min worse; with 12 days they even out.
- The gaps riders actually get are **trips that never run**: see
  [missed service](missed-service.md) and, per stop,
  [what riders get at the stop](stop-waits.md).

# Method

`[HEADWAY]` pairs each bus with the one before it at the stop and compares
against *their two trips'* planned difference. Counting from "the previous
bus seen" instead overstates gaps, because the
[arrivals log](../datasets/arrivals-log.md) catches only ~87% of the stops
on a trip that ran (99% on the trolley).[^one-off]

Two buses logged in the same second are ordered by their timetable, so the
bunched and overtake counts no longer shift from run to run.

[^q-headway]: analysis.sql [HEADWAY]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
