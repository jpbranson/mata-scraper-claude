---
type: Component
title: Poller
description: cadavl_to_gtfs_rt.py, the one long-running process; every 10 s during service hours it fetches the tracker's vehicles and writes the history, the snapshot, the replay frames and a GTFS-RT feed, and drives the timetable, official-feed and detour modules.
resource: ../../cadavl_to_gtfs_rt.py
tags: [tracker, poller]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: flight-log-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FLIGHT_LOG.md
    title: FLIGHT_LOG.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
  - id: poller-code
    resource: ../../cadavl_to_gtfs_rt.py
    title: cadavl_to_gtfs_rt.py
---

# Cycle

Runs forever as a scheduled task (`mata-poller`, see [running
it](../operations/running-it.md)). Each cycle, during service hours
(04:00–24:00 local, `SERVICE_HOURS`): fetch
[`/topo/vehicules`](../feeds/tracker-vehicles.md), normalize each bus into a
flat row (`normalize_vehicle`), then write four things:

| Output | Concept |
|---|---|
| One row per bus per poll, appended | [positions history](../datasets/positions.md) |
| The current poll, written atomically | [latest snapshot](../datasets/latest-snapshot.md) |
| Every third poll (30 s), one compact frame | [replay frames](../datasets/replay-frames.md) |
| Our own GTFS-RT vehicle positions | [`vehicle_positions.pb`](../datasets/vehicle-positions-pb.md) |

Every row represents the same 10 s of bus-time, so plain `AVG()` in SQL is
already time-weighted: no forward-filling, no "was this bus still in the
feed?" logic. "Right now" is just the latest poll.

Each poll then hands off to three modules, each in its own `try/except` so a
failure is logged and never costs a poll:

- [timetable and arrivals](timetable-and-arrivals.md) (`schedule.py`): trip
  and arrival matching, every poll;
- [official feed archiver](official-feed-archiver.md) (`official_feed.py`):
  every poll;
- [detour logger](detour-logger.md) (`cadavl_detours.py`): hourly.

# Fixed 10 s clock

Cycles start on a fixed 10 s clock (:00, :10, :20 …), not 10 s after the
last one finished. A cycle takes 1–4 s, so the old sleep-after-poll loop
drifted to 11–14 s apart, and history from before the fix has those gaps.
The fix went live at 2026-09-25 20:12:38 CDT; afterwards 379 of 380 stored
polls were on the 10 s clock (the exception was a restart).

# Route mapping and self-repair

- The `idLigne → route` mapping and colors are loaded from
  [`routes.csv`](../datasets/routes-csv.md) at startup (`load_routes`).
- When a poll has buses on lines it doesn't know (stored as
  `cadavl:<id>`), at most every 15 minutes (`TOPO_CHECK_SECONDS = 900`) it
  asks [`/config/version`](../feeds/tracker-config-version.md). If that
  moved past the version recorded in
  [`network.geojson`](../datasets/network-geojson.md) (`topo_version`), it
  rebuilds the crosswalk ([`build_crosswalk.refresh`](crosswalk-builder.md),
  a ~28 MB download) and reloads, so a renumbering fixes itself within a
  poll or two.
- Rows from before the rebuild keep `cadavl:<id>`;
  [`backfill_routes.py`](backfill-tools.md) remaps them later.

# Helpers

- `StaleTracker` counts unchanged polls (`unchanged_polls`): consecutive
  polls with identical coordinates.
- `parse_delay` turns the vendor's text ("4 min late", "on time", "1h+
  late") into seconds and a capped flag.
- `MAX_SPEED_MS = 40` (~90 mph): speeds above it are left out of
  `vehicle_positions.pb` ([speed unit](../decisions/speed-unit.md)).

# Offline check

`python cadavl_to_gtfs_rt.py --sample vehicules.json` parses a [saved
payload](../datasets/sample-payload.md) instead of polling. It is the
project's only regression check: if the parser changes, run it. If the
vendor changes the JSON shape, `normalize_vehicle` returns nothing useful,
and the `--sample` check against a freshly saved payload is the debugging
tool ([failure modes](../operations/failure-modes.md)).

# Log

Output goes to [`data\poller.log`](../datasets/poller-log.md), each line
stamped with the local date and time (live since 2026-09-25 20:12:38).
