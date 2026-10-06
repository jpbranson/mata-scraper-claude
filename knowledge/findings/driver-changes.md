---
type: Finding
title: Driver changes
description: No feed names the driver; long weekday blocks keep one bus all day, so drivers change on the street, and it only shows on route 42 at the garage, where 5 trips a weekday sit ~9 min instead of ~2 and leave 5 min late.
tags: [delay, reliefs, blocks]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:19:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:01:30Z
queries: ["[RELIEF]"]
sources:
  - id: q-relief
    resource: ../../analysis.sql
    title: analysis.sql [RELIEF]
  - id: gtfs
    resource: ../feeds/gtfs-timetable.md
    title: MATA GTFS timetable, trips.txt block_id and stop_times.txt (calendar 2026-10-05 to 2026-11-03)
  - id: one-off
    resource: "One-off DuckDB queries in the session scratchpad, on a copy of data/ taken Mon 2026-10-05 22:01 CDT (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [driver changes](../questions/driver-changes.md).

# Answer

- **No feed says who is driving.** Neither the tracker nor MATA's official
  feed carries an operator or run ID, so driver changes ("reliefs") are
  inferred.
- **Most weekday buses need one, on the street.** 47 of 56 weekday blocks
  run over 10 h (median 15.7 h, none with an hour's break), as do 31 of 46
  Saturday blocks; no Sunday block runs over 10 h.[^gtfs] A block keeps the
  same bus all day on most days (91 mid-day bus changes in 381 weekday
  block-days), so the new driver takes over the bus in service.[^one-off]
- **Route 42 changes drivers at the garage**, on Watkins St at Levee Rd,
  southbound, at the same point on each long block every day:[^q-relief]

  | Block | Trip leaves Frayser | At the garage | Days it showed |
  |---|---|---|---|
  | 4201 | 12:00 | ~12:10 | 4 of 7 |
  | 4202 | 13:00 | ~13:10 | 7 of 7 |
  | 4204 | 14:01 | ~14:15 | 5 of 6 |
  | 4203 | 15:00 | ~15:12 | 6 of 7 |
  | 4204 | 18:00 | ~18:14 | 7 of 7 |

  Saturdays, one per block: 12:27, 13:10–13:22, 14:40–14:51 and 16:53. Sundays:
  none. The one weekday route 42 block without one, 4205, runs 9.6 h.
- **Each costs about 5 minutes.** The bus arrives on time, sits a median
  8.6 min there (middle half 7.2–10.1) where other trips take 2.2, and
  leaves 5 min late with about 5 riders aboard. It is still ~3 min late at
  the next timepoints (Bellevue @ Lamar, Elvis Presley @ Norris, Millbranch
  @ Shelby), where other trips are on time, and the schedule's padding
  absorbs it by Airways Transit Center (1.7 min early, against 3.5 for other
  trips). The bus's next trip leaves about 1 min later than
  usual.[^one-off]
- **Route 08 also passes the garage and never stops there**, so it changes
  drivers somewhere else.
- **Elsewhere it doesn't show.** Other routes most likely change drivers at
  a terminal, inside the layover, where a change can't be told from an
  ordinary layover. Long mid-route stops that cost time are not changes:
  they are as common on Sundays (35 per 100 bus-hours) as on weekdays (28),
  and the ones that recur (route 32 at James Rd @ Hollywood, 69 at Weaver
  Rd @ Fields, 30 and 36 at American Way Transit Center) come on every
  round trip, not once a day.[^one-off]
- **A hint at terminals.** Buses reach the end of the line on time (median
  0.6 min late) but leave late (3.9 min), and late leaving that a late
  arrival didn't force peaks mid-block: on weekday blocks of 14 h+, 24–33%
  of departures 5–9 h into the block leave 7+ min late that way, against
  15–17% 1–2 h in, 8–13% 13–15 h in, and 5–13% on Sundays. That fits handovers at terminals, but it is tangled with time of
  day.[^one-off]
- **Mid-day bus changes cost more.** On the 78 weekday trips where a block
  switched to a different bus, the trip left a median 9.1 min late (half 10+
  min), against 4.0 for the rest. 4 of route 42's 11 fell on its relief
  trips.[^one-off]

# Method

- **Blocks**: a block's span is its first departure to its last arrival in
  the GTFS timetable; shifts are rarely over 10 h, so a longer block needs
  at least one change.[^gtfs]
- **Which bus ran each trip**: the bus MATA's official feed most often
  reports on that trip; a mid-day bus change is a block's trip run by a
  different bus than its previous trip.
- **A relief stop**: a stop mid-trip, not at the route's own line end, where
  the bus sits 3+ min longer than that route and direction usually take,
  gains 3+ min of delay, and leaves 2+ min late. The last condition leaves
  out timepoint holds, where an early bus waits and leaves on time. What
  makes it a driver change rather than a break is the pattern: the same
  trip at the same place most days, once per long block, at the garage, and
  never on Sundays, when no block needs one.
- **Late leaving that a late arrival didn't force**: departure delay minus
  however much of the arrival delay the scheduled layover couldn't absorb,
  for consecutive trips of one block on one bus (official feed).
- Data: tracker history 2026-09-24 to 2026-10-05 22:01 (trip IDs from
  09-25), official feed from 09-25: 7 weekdays, 2 Saturdays and 2 Sundays
  with both. Blocks are from the timetable in force from 2026-10-05; trip
  IDs were the same in September (99% of the official feed's trips match),
  and the relief times hold from 09-25 to 10-05. The one-off figures come
  from a copy taken at 22:01 on 10-05; `[RELIEF]` gives the same trips,
  passes and times on the [full copy](snapshot-2026-10-05.md) taken after
  service, which the findings page's "Changing drivers" section is built
  from (`findings_page/relief_data.py`).

[^q-relief]: analysis.sql [RELIEF]
[^gtfs]: MATA GTFS timetable, trips.txt block_id and stop_times.txt
[^one-off]: One-off queries, 2026-10-05
