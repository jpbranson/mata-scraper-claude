---
type: Finding
title: Ghost trackers and still buses
description: A bus still for 30+ polls is nearly always at a layover or a hold (1,196 of 1,332 streaks); dead trackers are short, don't move delay figures, and bus 458 has a quarter of the ghost rows, while a third come at the start of service and some from fleet-wide freezes.
tags: [gps, tracker, data-quality]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[GPS]"]
sources:
  - id: q-gps
    resource: ../../analysis.sql
    title: analysis.sql [GPS]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [ghost buses and GPS reliability](../questions/ghost-buses.md). The
rule this settled is the [ghost threshold](../decisions/ghost-threshold.md).

# Method

A still streak is a run of polls where a bus's coordinates don't change
(`unchanged_polls`). How it *ends* says what it was:

- the bus then drives off from the same spot (first move ≤ 200 m): it was
  really there;
- it reappears 200 m+ away within two minutes: its tracker had stopped and
  the bus was moving all along (a dead tracker).

# Answer

| Still for | Streaks | Dead tracker | Drove off | At a route end |
|---|---|---|---|---|
| 1–1.5 min (6–9 polls) | 8,894 | 287 | 8,570 | 39% |
| 2–3.5 min (10–19) | 3,009 | 270 | 2,706 | 40% |
| 3.5–5.5 min (20–29) | 1,117 | 175 | 924 | 45% |
| 5.5+ min (30+) | 1,332 | 112 | 1,196 | 68% |

(The rest left the feed, or were still under way when the copy was
taken.)[^one-off][^snapshot]

- The 30-poll rule mostly catches **layovers** (890 of 1,332 streaks at a
  route's end) and **holds** (306 mid-route, a median 6.5 min while the
  delay climbs a median 6 min; routes 50, 42, 30, 39 and 57 have the
  most).
- **112 were dead trackers** (8%, against 8 of 191 on 1.8 days), and most
  weren't one bus's fault: 47 at the start of service (04:00–05:59, a bus
  still for 15–20 min that then appears 2–4 km away) and 25 in one
  fleet-wide freeze, Mon 10-05 16:50–17:00, when 26 buses stopped moving
  on the feed at once. 40 were single buses later in the day.
- Dead trackers are mostly **short** (79% last 1–5 min, median 2.3) and
  slip past the rule. Over those stretches the official feed also freezes:
  same position, report age a median ~3 min, against 5 s for parked
  buses.
- **Ghost rows bunch in time.** A third of the 17,966 ghost rows are at
  04:00–05:59, as buses pull out, and later in the day 196 dead streaks
  come in bursts of 4+ buses starting within 10 minutes (30 buses Thu
  10-01 at 12:54, 20 Tue 09-29 at 06:10).
- **It doesn't matter for delay.** The vendor freezes delay with position
  (median delay 0 at a ghost's start, end and after the jump; unchanged in
  88% of streaks), and every route's 5+ min late share is within 1.4 points
  either way (route 02: 25.5% against 24.1%). Route 02 is 25% late without
  bus 458 too (458 alone: 33%), so its lateness isn't a bad tracker.
- **One bad tracker:** bus 458 has 4,670 ghost rows, 10.6% of its polls and
  a quarter of all ghost rows, 4–20% of its polls every day but Mon 10-05
  (1%).[^q-gps] On 1.8 days it had nearly half. Next: 21807 (5.9%, nearly
  all on Mon 09-28, 37% of its polls that day) and 21711 (4.6%, on Fri
  10-02 and Mon 10-05).

[^q-gps]: analysis.sql [GPS]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
