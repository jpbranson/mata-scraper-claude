---
type: Finding
title: Ghost trackers and still buses
description: A bus still for 30+ polls is almost always at a layover or a hold; dead trackers are short, don't move delay figures, and one bus (458) has nearly half of them.
tags: [gps, tracker, data-quality]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[GPS]"]
sources:
  - id: q-gps
    resource: ../../analysis.sql
    title: analysis.sql [GPS]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
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
| 1–1.5 min (6–9 polls) | 1,241 | 69 | 1,160 | 37% |
| 2–3.5 min (10–19) | 466 | 53 | 406 | 38% |
| 3.5–5.5 min (20–29) | 170 | 24 | 142 | 55% |
| 5.5+ min (30+) | 191 | 8 | 177 | 69% |

(The rest left the feed, or were still under way when the copy was
taken.)[^snapshot]

- The 30-poll rule mostly catches **layovers** (130 of 191 streaks at a
  route's end) and **holds** (47 mid-route, typically a bus sitting 5–10 min
  while its delay climbs from ~0 to +5…+10, e.g. route 50 on Poplar, route
  57 on Park). Only 8 were dead trackers.
- Dead trackers are mostly **short** (1–5 min) and slip past it. Over those
  stretches the official feed also freezes: same position, report age
  climbing to ~2 min (median), versus ~10 s for parked buses.
- **It doesn't matter for delay.** The vendor freezes delay with position
  (median delay 0 at a ghost's start, end and after the jump), and every
  route's 5+ min late share is within 1.4 points either way. Route 02 is
  late on all its buses (21715: 22%, 450: 31%, 21808: 37%, 458: 44%, 22607:
  50%), not because of a bad tracker.
- **One bad tracker:** bus 458 (routes 19, 02) has 1,002 ghost rows, 15% of
  its polls and nearly half of all 2,148 ghost rows.[^q-gps] Next worst:
  21501 (5%), 21809 (1.5%).

[^q-gps]: analysis.sql [GPS]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
