---
type: GTFS Feed
title: MATA GTFS timetable (GTFS_MATA.zip)
description: MATA's published timetable from the tracker's vendor, rebuilt nightly; it lines up exactly with the tracker and is the base for trip matching, stop schedules and the schematic.
resource: https://gtfs.mata.cadavl.com/MATA/GTFS/GTFS_MATA.zip
tags: [gtfs, timetable]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: schedule-code
    resource: ../../schedule.py
    title: schedule.py docstring
  - id: gtfs-rt-validator
    resource: https://github.com/MobilityData/gtfs-realtime-validator
    title: MobilityData GTFS-Realtime validator
  - id: gtfs-1005
    resource: Measured on findings_page/snapshot-2026-10-05/data/gtfs.zip (downloaded by the poller 2026-10-05 04:00 CDT)
    title: The timetable of 2026-10-05 (calendar.txt, trips.txt, stop_times.txt, stops.txt)
  - id: snapshot-1005
    resource: Measured on findings_page/snapshot-2026-10-05 (copy of data/ taken 2026-10-05 22:37 CDT)
    title: Measurements on the 2026-10-05 snapshot (official feed trip IDs 2026-09-25 to 10-05)
  - id: poller-log
    resource: ../../data/poller.log
    title: poller.log, "timetable for <day>" lines 2026-09-24 to 10-05
---

# What it is

MATA's published timetable as GTFS (a zip of CSVs), from the same vendor
that runs the [tracker](swiv-tracker.md). ~1.5 MB, rebuilt nightly. It only
covers today onward, so a past day's timetable exists only if the poller
saved it ([schedule files](../datasets/schedule-files.md)).

The copy of 2026-10-05 has a calendar from that day to 2026-11-03, three
services (`0_Weekday`, `2-Sat`, `3-Sun`) and no `calendar_dates`
exceptions. It holds 25 routes, 1,398 trips (651 weekday, 454 Saturday, 293
Sunday) and 118,795 stop times: 55,953 on a weekday, 39,065 on a Saturday
and 23,777 on a Sunday, the same counts the poller has loaded every day
since 2026-09-24.[^gtfs-1005][^poller-log] Five routes (12, 19, 34, 37, 69)
don't run on Sundays.

# Used for

- [schedule.py](../system/timetable-and-arrivals.md) downloads it once per
  service day when the server's copy is newer than the cached
  `data/gtfs.zip`, and uses it for stop schedules and trip matching.
- [build_schematic.py](../system/schematic-map.md) builds the subway-style
  layout from it.
- The [official GTFS-RT feed](official-gtfs-rt.md)'s trip and stop IDs are
  this feed's.

# Alignment with the tracker

It lines up with the tracker exactly (confirmed against live traffic):[^schedule-code]

- GTFS `stop_id` is `"0:"` + the tracker's stop code (`mnemoPointArret`,
  `stop_code` in [stops.csv](../datasets/stops-csv.md)).
- `route_id` is the route number.
- `trip_headsign` is the bus's `destination`, trailing spaces and all.
- The vendor's delay is measured against this timetable (checked: a bus
  "8 min late" at LAMAR @LAPALOMA at 18:01 is the 17:52:59 trip).

# Trip IDs

Trip IDs look like `0_Weekday731683` and stay the same when the timetable is
rebuilt. Every scheduled trip MATA's official feed reported from 2026-09-25
to 10-05 is in the 2026-10-05 timetable: 99.4% of its trip-days in the
vehicle positions and 99.6% in the trip updates. The rest are `ADDED` trips,
whose IDs are made up on the day (`0_Weekday2026-09-25-14-04-17-569-714529`)
and are in no timetable. All 1,397 trips the poller matched buses to are in
it too.[^snapshot-1005]

# Stop times

`arrival_time` equals `departure_time` on all 118,795 calls: the timetable
has no dwell, and a layover is only the gap between one trip's last stop
and the next trip's first. 9,117 calls are timepoints
(`timepoint` = 1).[^gtfs-1005]

# Blocks and interlining

`trips.txt` carries `block_id` (the tracker doesn't, and the
[schedule files](../datasets/schedule-files.md) don't keep it). A block's
span is its first departure to its last arrival:[^gtfs-1005]

| Service | Blocks | Over 10 h | Median span | Longest |
|---|---|---|---|---|
| Weekday | 56 | 47 | 15.7 h | 17.8 h |
| Saturday | 46 | 31 | 11.8 h | 14.8 h |
| Sunday | 37 | 0 | 8.8 h | 9.95 h |

No block has a gap of an hour or more between consecutive trips (the
longest is 26 min), so a block over 10 h needs a driver change in service
(see [driver changes](../findings/driver-changes.md)).

A few blocks interline: weekday and Saturday blocks 4001 and 4002, and
Sunday blocks 1301 and 1302, alternate a route 13 round trip with a route
40 one from William Hudson, so those buses change route every couple of
hours. That's real, not mislabelling; follow a bus by `vehicle_id` and split
its day at each route or headsign change.

# Static validation

MobilityData's validator[^gtfs-rt-validator] (2026-09-25, run alongside the
[realtime check](official-gtfs-rt.md#validation)) reported ~14,000 static
problems, nearly all false: it claims every trip and 7,588 stops lack
coordinates; they don't. Real but harmless, and still so in the copy of
2026-10-05:[^gtfs-1005]

- `stops.txt` lists nearly every stop twice, under `0:` (3,849) and `1:`
  (3,739) prefixes. Trips only use `0:` IDs, and so do we.
- 3,988 stops are used by no trip.

[^schedule-code]: schedule.py docstring
[^gtfs-rt-validator]: MobilityData GTFS-Realtime validator
[^gtfs-1005]: The timetable of 2026-10-05
[^snapshot-1005]: Measurements on the 2026-10-05 snapshot
[^poller-log]: poller.log, "timetable for <day>" lines 2026-09-24 to 10-05
