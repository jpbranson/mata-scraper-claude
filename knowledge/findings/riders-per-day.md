---
type: Finding
title: Riding per day
description: A weekday carries 3,800–4,500 rider-hours and at least 7,900–9,400 boardings, with 370–456 riders on board at the peak; a Saturday about 60% of that and a Sunday about a third, ~7,300 boardings a day over a week, the same scale as MATA's reported ridership.
tags: [ridership, load]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[RIDERS_DAY]"]
sources:
  - id: q-riders_day
    resource: ../../analysis.sql
    title: analysis.sql [RIDERS_DAY]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: mata-ridership-2023-09
    resource: "MATA's reported bus ridership for September 2023 (the document was not recorded)"
    title: MATA bus ridership, September 2023
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers the daily-total part of
[ridership by day, weather and events](../questions/ridership-trend.md).

# Answer

| Day | Rider-hours | Peak on board | Boardings (at least) |
|---|---|---|---|
| Thu 2026-09-24 | 4,064 | 451 at 15:40 | 8,077 |
| Fri 2026-09-25 | 4,063 | 423 at 15:40 | 8,036 |
| Sat 2026-09-26 | 2,393 | 304 at 16:18 | 5,238 |
| Sun 2026-09-27 | 1,443 | 234 at 10:15 | 2,937 |
| Mon 2026-09-28 | 3,861 | 428 at 11:31 | 8,295 |
| Tue 2026-09-29 | 4,212 | 437 at 15:31 | 8,831 |
| Wed 2026-09-30 | 4,322 | 456 at 15:46 | 8,784 |
| Thu 2026-10-01 | 4,308 | 431 at 09:30 | 9,440 |
| Fri 2026-10-02 | 3,811 | 370 at 09:38 | 7,892 |
| Sat 2026-10-03 | 2,531 | 328 at 11:56 | 5,541 |
| Sun 2026-10-04 | 1,320 | 203 at 14:35 | 2,897 |
| Mon 2026-10-05 | 4,480 | 451 at 12:40 | 9,104 |

[^q-riders_day][^snapshot] (The 55 minutes of Wed 09-23 are left out.)

| Day type | Rider-hours | Boardings (at least) | Share of a weekday |
|---|---|---|---|
| Weekday (8) | 4,140 | 8,560 | |
| Saturday (2) | 2,460 | 5,390 | ~60% |
| Sunday (2) | 1,380 | 2,920 | ~one third |

- **Weekdays** run 3,811–4,480 rider-hours; the lowest were Fri 10-02 and
  Mon 09-28. The peak on board (370–456) came at 15:30–15:46 on four of
  the eight and mid-morning or midday on the others. On average the most
  on board is at 15:30–16:00 (~380), with ~250–350 from 07:30 to
  17:30.[^one-off] On 1.8 days both peaks fell at 15:40; that was not the
  rule.
- **Saturdays** hold ~185–260 on board from 08:30 to 16:30, **Sundays**
  ~130–185 from 08:30 to 16:00, before service winds down to its end
  about 18:40.[^one-off]

A week at these rates is at least ~51,000 boardings, ~7,300 a day. MATA
reported ~230,600 bus riders in September 2023 (~7,700 a
day),[^mata-ridership-2023-09] the same scale, which also supports reading
the load as riders out of 50 ([bus capacity](../decisions/bus-capacity.md)).

Two of each weekend day and one or two of each weekday are enough to
separate weekdays from weekends, not to compare one weekday with another.
Weather and events need weeks of data plus outside data.

# Method

As the query's comment says: rider-hours weight each poll's riders on
board (load % ÷ 2) by the time to the next poll, up to 30 s; boardings are
every rise in a bus's count between polls, net changes only, so a floor
(see [where buses fill](boardings.md)). One stuck counter (bus 22609 at
100% for 53 minutes, see [peak loads](peak-loads.md)) adds about 44
rider-hours to Wed 09-30.

[^q-riders_day]: analysis.sql [RIDERS_DAY]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^mata-ridership-2023-09]: MATA bus ridership, September 2023
[^one-off]: One-off queries, 2026-10-05
