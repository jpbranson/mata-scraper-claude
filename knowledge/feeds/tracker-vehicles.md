---
type: API Endpoint
title: Tracker vehicles (/topo/vehicules)
description: Every bus's position, heading, speed, next stop, schedule adherence and passenger load, refreshed every 10 s; the only endpoint polled continuously.
resource: https://swiv.mata.cadavl.com/SWIV/MATA/proxy/restWS/topo/vehicules
tags: [tracker, delay, load, gps]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: poller-code
    resource: ../../cadavl_to_gtfs_rt.py
    title: cadavl_to_gtfs_rt.py (normalize_vehicle, POLL_SECONDS)
  - id: crosswalk-code
    resource: ../../build_crosswalk.py
    title: build_crosswalk.py docstring
  - id: sample
    resource: ../../vehicules.json
    title: Saved /topo/vehicules payload, 2026-09-23 (every field path in its 41 buses)
  - id: snapshot-1005
    resource: Measured on findings_page/snapshot-2026-10-05 (copy of data/ taken 2026-10-05 22:37 CDT)
    title: Measurements on the 2026-10-05 snapshot (positions 2026-09-23 21:38 to 2026-10-05 22:33, GTFS timetable of 2026-10-05)
  - id: poller-log
    resource: ../../data/poller.log
    title: poller.log, crosswalk rebuilds at 2026-09-30 04:00 and 2026-10-02 04:00
---

# What it is

Every bus on the [tracker](swiv-tracker.md): position, heading, speed, next
stop, schedule adherence ("4 min late") and passenger load ("30%"). About
12 KB, refreshed every 10 s; the tracker's own page requests it 10.000 s
apart, and the server took 0.9–3.4 s to answer.[^poller-code] The
[poller](../system/poller.md) fetches it every 10 s and stores one
[position row](../datasets/positions.md) per bus. A saved copy is the
[sample payload](../datasets/sample-payload.md). After the evening's last
bus it returns an empty list.

# Schema

`{"vehicule": [...]}`, one object per bus. How the poller maps it to a
[positions](../datasets/positions.md) row:

| Payload field | Row field | Notes |
|---|---|---|
| `id` | `vehicle_id` | Vendor ID |
| `numeroEquipement` | `equipment_no` | Fleet number painted on the bus |
| `type` | `vehicle_type` | `"Bus"` on every vehicle, the trolley included |
| `localisation.lat`, `localisation.lng` | `lat`, `lon` | |
| `localisation.cap` | `bearing` | Degrees 0–360 |
| `conduite.idLigne` | `line_internal_id`, `route_id` | Route by lookup in [routes.csv](../datasets/routes-csv.md) |
| `conduite.vitesse` | `speed_raw` | Metres per second |
| `conduite.destination` | `destination` | Headsign |
| `conduite.arretSuiv.nomCommercial` | `next_stop_name` | `arretSuiv` is null when the bus is off-route or idle |
| `conduite.arretSuiv.estimationTemps` | `next_stop_eta_min` | |
| `conduite.avanceRetard` | `delay_raw`, `delay_seconds`, `delay_capped` | Vendor text, e.g. "4 min late" |
| `vehiculeLoad` | `occupancy_pct` | e.g. "30%" |

That is the whole payload: the sample's 41 buses have no other
field.[^sample]

# Known limits

These shape the design, and were confirmed against live traffic. The
[official feed](official-gtfs-rt.md) fills the first two, in its own
archive, not in our rows.

- **No server timestamp.** `observed_at` is *our* fetch time, so a bus whose
  coordinates stop changing is either parked (a layover or hold) or has a
  tracker that stopped reporting (a "ghost"). `unchanged_polls` counts the
  still polls; how the streak ends tells the two apart (see
  [ghost threshold](../decisions/ghost-threshold.md)).
- **No trip, block, run or driver.** We know the route and headsign, not
  which scheduled trip a bus is on or who is driving it;[^sample]
  [schedule.py](../system/timetable-and-arrivals.md) infers the trip, and
  the official feed's `trip_id` is there to
  [check it against](../findings/trip-matching.md). Delay is whatever the
  vendor reports (`avanceRetard`), not something we compute. The timetable
  does carry blocks, and a few interline buses between routes 13 and 40
  (see [GTFS timetable](gtfs-timetable.md)). Neither feed names the driver
  ([driver changes](../findings/driver-changes.md)).
- **Buses leave the feed at layovers.** At the end of a line the tracker
  drops the bus and brings it back about 5 minutes before its next trip's
  scheduled start: a median 4.8 min before, and 3–8 min before on 2,981 of
  3,492 such gaps (2026-09-23 to 10-05).[^snapshot-1005] So the gap is the
  layover: a median 4–19 min by route, longest on route 42. On routes 07,
  28 and the trolley (100) buses mostly come back after the next trip was
  due, so late. These gaps are in the history too; they're most of the
  breaks in the [map's](../system/live-map.md) delay chart. The official
  feed keeps such a bus, parked at its next trip's first stop.
- **Mid-trip, a standing bus almost never drops out.** Of the 4,066 gaps
  over 2 minutes in a bus's rows while the feed was up, 91 were mid-trip
  (next stop set, same headsign before and after), and only 19 of those
  came back within 50 m of where they left.[^snapshot-1005]
- **Delay is capped.** `"1h+ late"` / `"1h+ early"` mean "at least an hour",
  stored as ±3600 and flagged `delay_capped`. Those rows are usually
  misassigned buses; exclude them. (Pollers until the evening of 2026-09-24
  stored them as 0, still flagged, so `NOT delay_capped` drops them either
  way; [backfill_replay.py](../system/backfill-tools.md) re-parses
  `delay_raw`.)
- **Delay is in whole minutes, and "on time" spans a minute either way.**
  The vendor never says "1 min": after `"on time"` the next values are
  `"2 min late"` and `"2 min early"`. See
  [late threshold](../decisions/late-threshold.md).
- **Line and stop IDs are opaque and unstable.** Internal `idLigne` (e.g.
  111394) maps to route "36" only by lookup, and every line and stop ID
  changes when the vendor publishes a new [topo](tracker-topo.md) version.
  That happened three times in eight days: topo 198238 (2026-09-23), 198256
  (2026-09-24) and 198282 (2026-09-30) each renumbered every
  ID.[^crosswalk-code][^poller-log] Stop codes (`LAMLAPEN`) and route
  numbers are stable; key everything on those.
- **Speed is metres per second**, whole numbers (0–21 on 99% of rows; about
  1 reading in 1,000 is over 40 m/s and impossible, up to 1,542, from
  2026-09-23 to 10-05).[^snapshot-1005] Settled 2026-09-25: see
  [speed unit](../decisions/speed-unit.md). Not needed for any of the three
  questions.
- **Load is riders out of 50**, presumably from the bus's automatic
  passenger counters: `"30%"` is 15 people, on every vehicle, trolley
  included (see [bus capacity](../decisions/bus-capacity.md)). Good as the
  counters are, no better.

[^poller-code]: cadavl_to_gtfs_rt.py (normalize_vehicle, POLL_SECONDS)
[^crosswalk-code]: build_crosswalk.py docstring
[^sample]: Saved /topo/vehicules payload, 2026-09-23
[^snapshot-1005]: Measurements on the 2026-10-05 snapshot
[^poller-log]: poller.log, crosswalk rebuilds at 2026-09-30 04:00 and 2026-10-02 04:00
