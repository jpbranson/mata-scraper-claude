---
type: GTFS-Realtime Feed
title: MATA official GTFS-Realtime feed
description: MATA's own GTFS-RT vehicle positions, trip updates and alerts from the tracker's vendor; it has trip IDs, report times and cancellations the tracker lacks, but no delay and staler positions.
resource: https://gtfsrt.mata.cadavl.com/ProfilGtfsRt2_0RSProducer-MATA/
tags: [official-feed, gtfs]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
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
---

# What it is

Standard GTFS-Realtime from the [tracker's](swiv-tracker.md) vendor,
unauthenticated. Not linked from matatransit.com; found via
Transitland[^transitland] on 2026-09-25. It's presumably what GO901, Transit
and Google Maps show. All three files are rebuilt every 30 s (measured
2026-09-25):[^official-code]

| File | Size | Holds |
|---|---|---|
| `VehiclePosition.pb` | ~3 KB | Each bus: `trip_id`, report time, next `stop_id`, occupancy as a category |
| `TripUpdate.pb` | ~120 KB | Predicted time at each remaining stop of each trip; `CANCELED` trips |
| `Alert.pb` | ~1 KB | Rider alerts, mostly missed trips ("Route 50 is not running from Exeter @ Poplar at 5:30a") |

Vehicle IDs are fleet numbers (our `equipment_no`); trip and stop IDs are
the [GTFS timetable's](gtfs-timetable.md).

# Compared with the tracker

Compared live, it has what the tracker lacks, and lacks what our three
questions need:

| | Official GTFS-RT | Tracker ([`/topo/vehicules`](tracker-vehicles.md)) |
|---|---|---|
| Vehicle ID | Fleet number (`equipment_no`) | Vendor ID and fleet number |
| Trip | `trip_id` from the timetable | None; `schedule.py` infers it (agreed 27 of 27) |
| Timestamp | Each bus's report time | None |
| Freshness | Positions ~1 min old | Every 10 s |
| Load | Category (`FEW_SEATS_AVAILABLE`) | Percent |
| Delay | None; predicted times per stop | The vendor's "5 min late" |
| Missed service | `CANCELED` trips; alerts like "Route 50 is not running from Exeter @ Poplar at 5:30a" | None |

The predictions don't reproduce the tracker's delay (next-stop prediction −
timetable ranged from 9 min more to 10 min less than the tracker's figure,
27 buses at 05:30), so the tracker stays the source for positions, delay
and load. The feed fills the tracker's missing timestamps and trip IDs in
its own archive, not in our rows.

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
