---
type: API Endpoint
title: Tracker vehicles (/topo/vehicules)
description: Every bus's position, heading, speed, next stop, schedule adherence and passenger load, refreshed every 10 s; the only endpoint polled continuously.
resource: https://swiv.mata.cadavl.com/SWIV/MATA/proxy/restWS/topo/vehicules
tags: [tracker, delay, load, gps]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
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
---

# What it is

Every bus on the [tracker](swiv-tracker.md): position, heading, speed, next
stop, schedule adherence ("4 min late") and passenger load ("30%"). About
12 KB, refreshed every 10 s; the tracker's own page requests it 10.000 s
apart, and the server took 0.9–3.4 s to answer.[^poller-code] The
[poller](../system/poller.md) fetches it every 10 s and stores one
[position row](../datasets/positions.md) per bus. A saved copy is the
[sample payload](../datasets/sample-payload.md).

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

# Known limits

These shape the design, and were confirmed against live traffic. The
[official feed](official-gtfs-rt.md) fills the first two, in its own
archive, not in our rows.

- **No server timestamp.** `observed_at` is *our* fetch time, so a bus whose
  coordinates stop changing is either parked (a layover or hold) or has a
  tracker that stopped reporting (a "ghost"). `unchanged_polls` counts the
  still polls; how the streak ends tells the two apart (see
  [ghost threshold](../decisions/ghost-threshold.md)).
- **No trip or block ID.** We know the route and headsign, not which
  scheduled trip a bus is on; [schedule.py](../system/timetable-and-arrivals.md)
  infers it, and the official feed's `trip_id` is there to
  [check it against](../findings/trip-matching.md). Delay is whatever the
  vendor reports (`avanceRetard`), not something we compute. The timetable
  does carry blocks, and a few interline buses between routes 13 and 40
  (see [GTFS timetable](gtfs-timetable.md)).
- **Buses leave the feed at layovers.** At the end of a line a bus often
  drops out of the payload for 5–25 minutes and comes back on its return
  trip (bus 10015 at Walnut @ Racine: 20:10–20:19). Those gaps are in the
  history too; they're most of the breaks in the
  [map's](../system/live-map.md) delay chart. The official feed keeps such a
  bus, parked at its next trip's first stop.
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
  111302) maps to route "36" only by lookup, and every ID changes when the
  vendor publishes a new [topo](tracker-topo.md) version, which happened
  twice in September 2026, days apart (every ID changed between topo
  versions 198238 and 198256).[^crosswalk-code] Stop codes (`LAMLAPEN`) and
  route numbers are stable; key everything on those.
- **Speed is metres per second**, whole numbers (typically 0–21; about 1
  reading in 1,200 is impossible, up to 347). Settled 2026-09-25: see
  [speed unit](../decisions/speed-unit.md). Not needed for any of the three
  questions.
- **Load is riders out of 50**, presumably from the bus's automatic
  passenger counters: `"30%"` is 15 people, on every vehicle, trolley
  included (see [bus capacity](../decisions/bus-capacity.md)). Good as the
  counters are, no better.

[^poller-code]: cadavl_to_gtfs_rt.py (normalize_vehicle, POLL_SECONDS)
[^crosswalk-code]: build_crosswalk.py docstring
