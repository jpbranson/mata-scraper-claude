---
type: Finding
title: Missed service
description: 13–16% of scheduled trips never ran (Thu 84 of 651, Fri 101 of 618), in every hour of the day, and MATA's own feed marked only 27 of Friday's 101 canceled.
tags: [missed-service, official-feed, routes]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[MISSED]", "[MISSED_HOUR]"]
sources:
  - id: q-missed
    resource: ../../analysis.sql
    title: analysis.sql [MISSED]
  - id: q-missed_hour
    resource: ../../analysis.sql
    title: analysis.sql [MISSED_HOUR]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [missed service](../questions/missed-service.md).

# Method

A trip never ran if no bus was ever on it: none in the tracker (no arrival
or position matched to it) and, from Friday, none in MATA's
[official feed](../feeds/official-gtfs-rt.md). The two agree: of 471 Friday
trips (06:00–19:50) the official feed saw running, the tracker saw 464, and
it saw none the official feed didn't. Counted with the `trip_service` view
([analysis.sql](../system/analysis-sql.md)) against the saved timetables.

# Answer

- **Thu: 84 of 651 scheduled trips (13%) never ran. Fri: 101 of 618
  (16%)** (trips due by 19:50).[^q-missed][^snapshot]
- **Worst:** Fri route 01, 31 of 40: no bus at all until 12:46, then one
  (Thu it ran two all day). Thu route 69, 13 of 17 (no bus before 14:00);
  53, 19 of 31; 37, 5 of 10 (13:00–17:00 only); 02, 14 of 30; 32, 9 of 23.
  Fri: 16 and 30 lost about half, 02 43%, 34 40%, 52 28%.
- Routes 04, 07, 13, 40 and the trolley lost nothing either day; 50 and 11
  one trip in two days; 36 four on Thursday, none Friday.
- **Every hour:** 11–23% of trips missed from 5 a.m. to 6 p.m., worst at
  6 a.m. (23%).[^q-missed_hour]
- **MATA's own records undercount it.** Of Friday's 101 unrun trips, its
  feed marked 27 CANCELED (and 5 trips it marked canceled did run). Its
  alerts are dispatchers' free text, 34 on Friday ("Route 1 is not running
  from William Hudson at 5:15a. The next bus is expected at 6:00a"), with
  "back in service" notes, route tags that are sometimes wrong ("Route 1
  back in service" tagged route 2, route 34 tagged 304), and active periods
  that never end. Counting missed service takes the timetable against buses
  seen, as `[MISSED]` does.
- Missed trips belong beside [which routes run behind](routes-behind.md):
  route 02 is both the latest (39% of polls 5+ min late) and among the most
  missed (43–47% of its trips).

Related: the [fleet in service](fleet-in-service.md) shortfall is the same
gap seen as buses, and it is what riders feel as
[long waits](stop-waits.md), since the buses that run keep their spacing
([headways](headways.md)). Trip-level agreement between the two feeds is
also in [trip matching](trip-matching.md).

[^q-missed]: analysis.sql [MISSED]
[^q-missed_hour]: analysis.sql [MISSED_HOUR]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
