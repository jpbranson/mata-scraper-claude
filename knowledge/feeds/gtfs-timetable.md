---
type: GTFS Feed
title: MATA GTFS timetable (GTFS_MATA.zip)
description: MATA's published timetable from the tracker's vendor, rebuilt nightly; it lines up exactly with the tracker and is the base for trip matching, stop schedules and the schematic.
resource: https://gtfs.mata.cadavl.com/MATA/GTFS/GTFS_MATA.zip
tags: [gtfs, timetable]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
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
---

# What it is

MATA's published timetable as GTFS (a zip of CSVs), from the same vendor
that runs the [tracker](swiv-tracker.md). ~1.5 MB, rebuilt nightly. It only
covers today onward, so a past day's timetable exists only if the poller
saved it ([schedule files](../datasets/schedule-files.md)).

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

# Blocks and interlining

The timetable carries `block_id` (the tracker doesn't), and a few blocks
interline: weekday blocks 4001 and 4002 (and their weekend twins) alternate
a route 13 round trip with a route 40 one from William Hudson, so those
buses change route every couple of hours. That's real, not mislabelling;
follow a bus by `vehicle_id` and split its day at each route or headsign
change.

# Static validation

MobilityData's validator[^gtfs-rt-validator] (2026-09-25, run alongside the
[realtime check](official-gtfs-rt.md#validation)) reported ~14,000 static
problems, nearly all false: it claims every trip and 7,588 stops lack
coordinates; they don't. Real but harmless:

- `stops.txt` lists nearly every stop twice, under `0:` (3,849) and `1:`
  (3,739) prefixes. We only use `0:` IDs.
- 3,988 stops are used by no trip.

[^schedule-code]: schedule.py docstring
[^gtfs-rt-validator]: MobilityData GTFS-Realtime validator
