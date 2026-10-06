---
type: Finding
title: Where buses fill
description: Buses fill at William Hudson Transit Center, ~1,770 riders on a weekday (a fifth of all boardings), which [BOARDINGS] credits to the first stop out (Second @ Jackson 828 a weekday); away from downtown the busiest stops take 110–140 a weekday.
tags: [ridership, load, stops]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:19:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[BOARDINGS]"]
sources:
  - id: q-boardings
    resource: ../../analysis.sql
    title: analysis.sql [BOARDINGS]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [where do buses fill and empty?](../questions/where-buses-fill.md)

# Answer

**William Hudson Transit Center**, downtown, is where buses fill. While a
bus sits there the tracker already shows the first stop out as its next
stop, so `[BOARDINGS]` puts these riders under that stop: Second @ Jackson
(828 on a weekday, 286 a weekend day) and Second @ Market (422 and 211) top
it, as they did on 1.8 days.[^q-boardings][^snapshot] Splitting out the buses
within 150 m of the transit center, riders on:[^one-off]

| At William Hudson, next stop | First stop out for | Weekday | Saturday | Sunday |
|---|---|---|---|---|
| Second @ Jackson | 01, 04, 12, 13, 50, 57 | 733 | 342 | 153 |
| Second @ Market | 02, 34, 36, 39 | 365 | 271 | 87 |
| AW Willis @ Third | 52 | 159 | 147 | 59 |
| Auction @ Third | 08 | 154 | 117 | 77 |
| Third @ Mill | 11, 40 | 150 | 92 | 48 |
| Auction @ Fifth | 19, 53 | 123 | 93 | 30 |
| All | | 1,769 | 1,114 | 493 |

That is 21% of all boardings on weekdays and Saturdays, 17% on Sundays
([riding per day](riders-per-day.md)).

Elsewhere, riders on:[^one-off]

| Stop | Routes | Weekday | Saturday | Sunday |
|---|---|---|---|---|
| Getwell Rd @ Mallory | 08, 36, 37 | 138 | 100 | 57 |
| Directors Row @ Brooks | 04, 12, 28, 30, 32 | 127 | 60 | 42 |
| Airways Blvd @ Winchester | 16, 28, 42 | 127 | 93 | 48 |
| Poplar @ Claybrook | 50 | 111 | 68 | 49 |
| Second @ Jackson (at the stop) | 01, 04, 07, 12, 13, 39, 50, 57 | 95 | 54 | 23 |
| Frayser Plaza | 11, 32, 42 | 87 | 53 | 35 |
| Covington Pike @ Austin Peay | 52 | 75 | 82 | 42 |
| Cleveland @ Jefferson | 42 | 74 | 47 | 29 |

Riders get off more spread out: 343 a weekday at the transit center, and
no other stop over ~125 (Second @ Jackson 124, Third @ Exchange 96, Poplar
@ Cleveland 90).[^one-off]

# Method

Each change in a bus's load between polls (up to 30 s apart) goes to the
stop it was serving, its next stop in the earlier poll. Net changes between
polls only, so the figures are floors. Per day here is per weekday (8),
Saturday (2) or Sunday (2); `[BOARDINGS]` averages all days together. "At
William Hudson" is the bus within 150 m of the transit center at the
earlier poll; first stops out are from the timetable in force from
2026-10-05.

[^q-boardings]: analysis.sql [BOARDINGS]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
