---
type: GTFS-Realtime Feed
title: MATA official GTFS-Realtime feed
description: MATA's own GTFS-RT vehicle positions, trip updates and alerts from the tracker's vendor; it has trip IDs, report times and cancellations the tracker lacks, but no delay, and positions only every 30 s.
resource: https://gtfsrt.mata.cadavl.com/ProfilGtfsRt2_0RSProducer-MATA/
tags: [official-feed, gtfs]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: official-code
    resource: ../../official_feed.py
    title: official_feed.py docstring
  - id: transitland
    resource: "Transitland feed registry: MATA's GTFS-RT listing, looked up 2026-09-25"
    title: Transitland feed listing
  - id: gtfs-rt-validator
    resource: https://github.com/MobilityData/gtfs-realtime-validator
    title: MobilityData GTFS-Realtime validator
  - id: snapshot-1005
    resource: Measured on findings_page/snapshot-2026-10-05 (copy of data/ taken 2026-10-05 22:37 CDT)
    title: Measurements on the 2026-10-05 snapshot (official archive 2026-09-25 05:45 to 2026-10-05 22:33, positions over the same days)
  - id: gtfs-rt-spec
    resource: https://gtfs.org/realtime/reference/
    title: GTFS Realtime reference (VehicleDescriptor, TripDescriptor)
---

# What it is

Standard GTFS-Realtime from the [tracker's](swiv-tracker.md) vendor,
unauthenticated. Not linked from matatransit.com; found via
Transitland[^transitland] on 2026-09-25. It's presumably what GO901, Transit
and Google Maps show. All three files are rebuilt every 30 s (measured
2026-09-25;[^official-code] the vehicle snapshots archived since are a
median 30 s apart, 90% within 38 s[^snapshot-1005]):

| File | Size | Holds |
|---|---|---|
| `VehiclePosition.pb` | ~3 KB | Each bus: `trip_id`, report time, next `stop_id`, occupancy as a category |
| `TripUpdate.pb` | ~120 KB | Predicted time at each remaining stop of each trip; `CANCELED` trips |
| `Alert.pb` | ~1 KB | Rider alerts, mostly missed trips ("Route 50 is not running from Exeter @ Poplar at 5:30a") |

Vehicle IDs are fleet numbers (our `equipment_no`); trip and stop IDs are
the [GTFS timetable's](gtfs-timetable.md).

Trip status is `SCHEDULED` or `ADDED` in the vehicle positions, and also
`CANCELED` in the trip updates; a stop in a trip update is `SCHEDULED` or
`SKIPPED`. `ADDED` trips (36 from 2026-09-25 to 10-05) carry IDs made up on
the day, like `0_Weekday2026-09-25-14-04-17-569-714529`, that are in no
timetable.[^snapshot-1005] Like the tracker, it names no driver, run or
block: GTFS-RT has no field for them.[^gtfs-rt-spec]

# Compared with the tracker

Compared live, it has what the tracker lacks, and lacks what our three
questions need:

| | Official GTFS-RT | Tracker ([`/topo/vehicules`](tracker-vehicles.md)) |
|---|---|---|
| Vehicle ID | Fleet number (`equipment_no`) | Vendor ID and fleet number |
| Trip | `trip_id` from the timetable | None; `schedule.py` infers it (agreed 27 of 27) |
| Timestamp | Each bus's report time | None |
| Freshness | A report every ~30 s per bus, a median 5 s older than the feed | Every 10 s |
| Load | Category (`FEW_SEATS_AVAILABLE`) | Percent |
| Delay | None; predicted times per stop | The vendor's "5 min late" |
| Missed service | `CANCELED` trips; alerts like "Route 50 is not running from Exeter @ Poplar at 5:30a" | None |
| Layovers | Keeps the bus, at its next trip's first stop | Drops the bus until ~5 min before its next trip |

The positions are the same GPS fixes as the tracker's, just fewer: an
official report matches the tracker's row a median 9 s later, to within a
metre (moving buses, 2026-10-02).[^snapshot-1005] The predictions don't reproduce the tracker's delay
(next-stop prediction − timetable ranged from 9 min more to 10 min less
than the tracker's figure, 27 buses at 05:30), so the tracker stays the
source for positions, delay and load. The feed fills the tracker's missing
timestamps and trip IDs in its own archive, not in our rows.

It keeps each bus through the day. From 2026-09-25 to 10-05 a bus's
consecutive snapshots were more than 2 minutes apart 291 times in 558
bus-days, 3% of bus time; the tracker dropped buses for over 2 minutes
4,299 times in 621 bus-days, 13% of bus time, mostly at
layovers.[^snapshot-1005]

Its occupancy categories are fixed bands of the tracker's rider count, not
a crowding measure (see [bus capacity](../decisions/bus-capacity.md)); its
speed is m/s by the spec (see [speed unit](../decisions/speed-unit.md)).

# Validation

Checked with MobilityData's GTFS-RT validator[^gtfs-rt-validator]
(2026-09-25, 13 snapshots of each feed against `GTFS_MATA.zip`): every trip
and stop ID resolves, no stale feeds, one trivial error (two consecutive
stops of one trip predicted at the same second). What its warnings mean for
analysis:

- **Only trips with a `vehicle_id` carry real predictions.** Trips no bus
  has started yet are listed with the timetable's times unchanged
  (predicted − scheduled is exactly 0). Filter on `vehicle_id` before
  judging prediction accuracy, or the copies make it look perfect.
- **The official positions include buses at layover.** A bus waiting at the
  first stop of its next trip (11 of 34 at 06:10) is in the positions with
  that trip's ID, while the tracker drops it and its trip update has no
  vehicle yet. That fills most of the layover gaps in our own history.
- **Buses at the garage show their first trip.** MATA's garage is off
  Watkins St at Levee Rd (about 35.178, -90.011). A bus parked there
  before pulling out is in the positions, standing still, with its first
  trip's ID and that trip's first stop as next stop, most often William
  Hudson (`0:2`).[^snapshot-1005]
- **Trip updates carry no per-trip timestamp**; use `feed_ts`.

The static timetable check is under [GTFS timetable](gtfs-timetable.md#static-validation).

# Used for

The [official feed archiver](../system/official-feed-archiver.md) saves it
beside our history: [vehicles](../datasets/official-vehicles.md),
[trip updates](../datasets/official-trip-updates.md) and
[alerts](../datasets/official-alerts.md).

[^official-code]: official_feed.py docstring
[^transitland]: Transitland feed listing
[^gtfs-rt-validator]: MobilityData GTFS-Realtime validator
[^snapshot-1005]: Measurements on the 2026-10-05 snapshot
[^gtfs-rt-spec]: GTFS Realtime reference (VehicleDescriptor, TripDescriptor)
