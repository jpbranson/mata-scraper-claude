---
type: Finding
title: Missed service
description: 9% of scheduled trips never ran over 12 days (603 of 6,702; weekdays 9.8%, Saturdays 5.6%, Sundays 7.3%; worst day 16%), mostly a bus missing for hours, and MATA's feed marked only 126 of 519 canceled.
tags: [missed-service, official-feed, routes]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:17:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[MISSED]", "[MISSED_HOUR]"]
sources:
  - id: q-missed
    resource: ../../analysis.sql
    title: analysis.sql [MISSED]
  - id: q-missed_hour
    resource: ../../analysis.sql
    title: analysis.sql [MISSED_HOUR]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [missed service](../questions/missed-service.md).

# Method

A trip never ran if no bus was ever on it: none in the tracker (no arrival
or position matched to it) and, from Fri 09-25, none in MATA's
[official feed](../feeds/official-gtfs-rt.md). The two agree: of 5,484
trips the official feed saw running (Fri 09-25 06:00 to Mon 10-05), the
tracker saw 5,402 (98.5%), and it saw 2 the official feed didn't.[^one-off]
Counted with the `trip_service` view ([analysis.sql](../system/analysis-sql.md))
against the saved timetables, all 12 service days in full. Thu 09-24 (and
Fri 09-25 before 06:00) has only the tracker, so it reads slightly high.

# Answer

- **603 of 6,702 scheduled trips (9.0%) never ran in 12 days** (its day
  totals summed). Weekdays 509 of 5,208 (9.8%), Saturdays 51 of 908
  (5.6%), Sundays 43 of 586 (7.3%).[^q-missed][^snapshot] Weekends lost less, but two of each is
  few: Sun 09-27 (8.9%) lost more than three of the weekdays.
- **By day:** weekdays Thu 09-24 12.9%, Fri 09-25 16.4% (107 of 651), Mon
  09-28 11.4%, Tue 09-29 6.6%, Wed 09-30 9.2%, Thu 10-01 6.0%, Fri 10-02
  5.8%, Mon 10-05 9.8%. Saturdays 6.4% and 4.8%, Sundays 8.9% and 5.8%.
  The first two days were the worst of the twelve, so the 1.8-day figure
  (13–16%) was the high end, not the norm. One or two of each weekday
  can't say which weekday is worst.
- **By route** (its rows summed): 01 lost 98 of 412 trips (24%, on 9 of
  the 12 days), 34 21%, 53 19%, 02 18%, 30 16%, 69 16%. The trolley lost
  1 trip, 07 2, 40 4, 13 5; every route lost at least one.[^q-missed]
- **Worst route-days:** Fri 09-25 route 01, 35 of 45 (no bus most of the
  day); Sun 09-27 route 16, 8 of 8 (no bus at all); Wed 09-30 route 34, 9
  of 10; Thu 09-24 route 69, 13 of 17; Mon 09-28 route 52, 21 of 35; Wed
  09-30 route 53, 18 of 31; Thu 10-01 route 04, 13 of 25; Mon 10-05 route
  50, 17 of 51.
- **It's buses missing for hours, not single trips dropped.** On most bad
  route-days every second or third trip is gone all day (one of the
  route's buses never came out), or a run of trips is (route 01 lost its
  19:30–21:54 trips on Mon 09-28, Tue 09-29, Wed 09-30 and Mon 10-05). By
  the timetable's blocks (one bus's day of work; `trips.txt` in the copy's
  `gtfs.zip`, whose trip IDs cover all 12 days), 30% of missed trips were
  on a block that never ran at all that day, and 88% on one that lost 3 or
  more trips.[^one-off]
- **Every hour, worst late in the evening.** Weekdays: 5–13% of trips
  missed in every hour from 4 a.m. to 6 p.m. (6 a.m. 13%), then 13% at 7
  p.m., 16% at 8 and 23% at 9. Saturdays 1–4% until 1 p.m. and 7–14%
  after; Sundays 4–14%, most at 4 p.m.[^q-missed_hour] Half the misses
  after 8 p.m. are route 01's.[^one-off] The 1.8-day version counted only
  trips due by 19:50, so it couldn't see this.
- **MATA's own records undercount it.** On the 11 days its feed covers,
  it marked 126 of 519 unrun trips CANCELED (24%; by day from 0 to
  47%),[^q-missed] and 36 trips it marked canceled did run.[^one-off] Its
  alerts are
  dispatchers' free text, 194 in 11 days (about 22 a weekday, 4–19 a
  weekend day): "Route 1 is not running from William Hudson at 5:15a. The
  next bus is expected at 6:00a", with "back in service" notes. 11 of the
  190 that name a route are tagged with another route or none ("Route 1
  back in service" tagged 2, route 34 tagged 304, route 36 tagged 42), and
  190 of 194 active periods are a fixed 8 or 10.5 hours, not the length of
  the outage. Counting missed service takes the timetable against buses
  seen, as `[MISSED]` does.
- Missed trips belong beside [which routes run behind](routes-behind.md),
  and the two go together only loosely (r = 0.38 over 25 routes): 02 is
  tied for the latest (26% of polls 5+ min late) and loses 18% of its
  trips, 01 is 22% late and loses 24%, but 36, also 26% late, loses
  6%.[^one-off]

Related: the [fleet in service](fleet-in-service.md) shortfall is the same
gap seen as buses, and it is what riders feel as
[long waits](stop-waits.md), since the buses that run keep their spacing
([headways](headways.md)). Trip-level agreement between the two feeds is
also in [trip matching](trip-matching.md).

[^q-missed]: analysis.sql [MISSED]
[^q-missed_hour]: analysis.sql [MISSED_HOUR]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
