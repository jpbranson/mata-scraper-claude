---
type: Finding
title: Peak loads
description: Buses are rarely full; routes average 1.7–9.9 riders on board, and every seat is taken (40+ riders) on 0.9% of route 50's polls, 0.2% of 42's and under 0.1% anywhere else, never on a Sunday.
tags: [load, ridership, crowding]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[LOAD]"]
sources:
  - id: q-load
    resource: ../../analysis.sql
    title: analysis.sql [LOAD]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [peak load by route and hour](../questions/peak-load.md). Riders =
load % ÷ 2, and 40 riders (80%) is every seat taken
([bus capacity](../decisions/bus-capacity.md)).

# Answer

- **Average** 1.7–9.9 riders on board by route over the 12 days, highest
  on 52, 42, 36 and 50 (9–10); the 95th percentile 23–27 on those four and
  21 or under elsewhere.[^q-load][^snapshot] Weekdays are fuller: 6.7
  riders a bus, against 5.5 on Saturdays and 5.2 on Sundays, with weekday
  95th percentiles of 29 on 50 and 25–26 on 52, 42 and 36.[^one-off]
- **Every seat taken** (40+): route 50 on 0.9% of its polls (on 10 of 12
  days) and 42 on 0.2% (6 days); 36, 11, 52 and 08 under 0.1%, on 2–5 days
  each. On Saturdays only route 50 got there, and no bus on a
  Sunday.[^one-off] On 1.8 days only 50, 42 and 36 had; 11, 52 and 08 now
  have too, for a few minutes at a time.
- **Busiest hours (weekdays)** are mostly mid-afternoon: 50 and 36 at 15,
  52 at 14, 11 and 08 at 16, 42 at 17. Route 50 is nearly as full from 9 to
  13 (11–12 riders on average, against 13.8 at 15).[^one-off] On 1.8 days
  route 50's busiest hour was 9.
- **The fullest:** readings of 96%+ (MATA's maximum load) are nearly all
  route 50 on Poplar (689 polls): heading out to Exeter Rd between 08:40
  and 14:00 on 7 of the 12 days (e.g. bus 21212 Fri 09-25 from 09:25 and
  Fri 10-02 from 09:20), and heading in to William Hudson on Wed 09-30 and
  Thu 10-01 (bus 4017 at 96–100% from 15:27 to 15:59). Elsewhere only a
  few minutes: 42 (bus 22608 Thu 10-01 at 12:49), 08 and 11.[^one-off]
- **One stuck counter:** bus 22609 on route 39 read 100% for 53 minutes on
  Wed 09-30 (16:15–17:08), jumping from 0 in one poll and back to 0 at
  Second @ Market. That is all of route 39's 40+ readings in `[LOAD]`
  (share 0.003), so route 39 is left out above.[^one-off]

[^q-load]: analysis.sql [LOAD]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
