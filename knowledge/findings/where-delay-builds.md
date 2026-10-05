---
type: Finding
title: Where delay builds up
description: Delay builds on route 36's Getwell / American Way stretch, 50's Poplar corridor and 42's Cleveland corridor; most routes start late and recover, while 02, 28, 01, 13, 36 and 08 compound.
tags: [delay, routes, stops]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[WHERE]", "[WHERE_ROUTE]"]
sources:
  - id: q-where
    resource: ../../analysis.sql
    title: analysis.sql [WHERE]
  - id: q-where_route
    resource: ../../analysis.sql
    title: analysis.sql [WHERE_ROUTE]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [where along the route delay accumulates](../questions/where-delay-accumulates.md)
and [whether delay recovers or compounds](../questions/recover-or-compound.md).

# Per stop

Delay gained since the previous logged stop on the same trip, summed into
bus-minutes lost per day; stops passed 20+ times; line ends left
out.[^q-where][^snapshot]

| Route → direction | Stop | Avg gained | Bus-min/day |
|---|---|---|---|
| 36 → Centennial / Hacks Cross | American Way @ Getwell | +3.1 min | 60 |
| 36 → William Hudson | Getwell Rd @ Allenbrooke Cv | +3.0 | 32 |
| 50 → William Hudson | Poplar @ Claybrook | +1.4 | 29 |
| 01 → Walnut @ Racine | Tillman at Johnson | +1.1 | 26 |
| 42 → Frayser / → Airways | Cleveland @ Larkin, Cleveland @ Jefferson, Bellevue @ Central | +1.6–1.7 | 24–25 each |
| 50 → William Hudson / → Exeter | Poplar @ Innsbruck, @ Kirby Pkwy, @ High | +0.9–1.0 | 20–24 each |
| 100 trolley → Central Station | Main St @ Union Ave | +1.8 | 24 |

Route 36's Getwell / American Way stretch costs time in both directions,
and 50's Poplar corridor and 42's Cleveland corridor add up stop after stop.
The 42 and 50 corridors are also among the [slowest stretches](speed.md).

# Per trip: recover or compound

Delay at the last logged stop minus the first; line ends aside; trips
logged 20+ min.[^q-where_route]

- Most routes **start late and recover**. Median start 2–4 min late on most
  routes (37: 6), and on most the median end is on time or early.
- 30, 37, 40 end 5.6–7.7 min earlier than they started, and 04, 42, 50, 57
  about 4.3: their schedules have slack, which fits their
  [early running](early-running.md).
- Some **compound** instead: 02 +3.8 min per trip (31% of trips gain 5+),
  28 +2.1, 01 +2.0, 13 +1.5, 36 +1.4, 08 +1.2.
- The late starts come from the terminal: trips leave their first stop late
  ([departures](departures.md)), a median 5.7 min on route 50 and 6.8 on 37.

[^q-where]: analysis.sql [WHERE]
[^q-where_route]: analysis.sql [WHERE_ROUTE]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
