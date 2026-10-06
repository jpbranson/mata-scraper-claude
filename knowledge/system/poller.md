---
type: Component
title: Poller
description: cadavl_to_gtfs_rt.py, the one long-running process; every 10 s during service hours it fetches the tracker's vehicles and writes the history, the snapshot, the replay frames and a GTFS-RT feed, and drives the timetable, official-feed and detour modules.
resource: ../../cadavl_to_gtfs_rt.py
tags: [tracker, poller]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:01:00Z }
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
  - id: copy-2026-10-05
    resource: ../../findings_page/snapshot-2026-10-05/
    title: Copy of data/ taken 2026-10-05 22:37 (gaps between stored polls)
  - id: poller-log
    resource: ../../data/poller.log
    title: data/poller.log, 2026-09-30 04:00 crosswalk rebuild (read-only grep)
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

Each poll also hands off to three modules, each in its own `try/except` so a
failure is logged and never costs a poll:

- [timetable and arrivals](timetable-and-arrivals.md) (`schedule.py`): trip
  and arrival matching, every poll, before the history is written, so each
  row carries its `trip_id`;
- [official feed archiver](official-feed-archiver.md) (`official_feed.py`):
  every poll, after the outputs, so a slow official feed never delays
  `latest.json`;
- [detour logger](detour-logger.md) (`cadavl_detours.py`): hourly, last.

The order within a poll: fetch, normalize, timetable, history, replay
frame, `latest.json`, `vehicle_positions.pb`, the log line, official feed,
detours.[^poller-code]

Outside service hours it polls nothing and checks the clock every 5
minutes, so `latest.json` keeps the 23:59:50 poll overnight (usually an
empty vehicle list).

# When a poll fails

A request error on `/topo/vehicules` (timeout, 5xx, connection reset) or an
`OSError` while writing logs `poll failed: ...` and drops the rest of that
poll, the official-feed and detour steps included; the next tick tries
again.[^poller-code]

- The `OSError` case is Windows refusing to replace `latest.json`
  (`[WinError 5] Access is denied`), which the code puts down to
  `http.server` having it open. By then the history rows and the replay
  frame are written, so only `latest.json` (one poll old),
  `vehicle_positions.pb` and that poll's official and detour steps are
  missed.
- The vendor request times out after 10 s, past the next tick, so a timeout
  costs two ticks.

How often each has happened: [failure modes](../operations/failure-modes.md).

# Fixed 10 s clock

Cycles start on a fixed 10 s clock (:00, :10, :20 …), not 10 s after the
last one finished. A cycle takes 1–4 s, so the old sleep-after-poll loop
drifted to 11–14 s apart, and history from before the fix has those gaps.
The fix went live at 2026-09-25 20:12:38 CDT; afterwards 379 of 380 stored
polls were on the 10 s clock (the exception was a restart). From 2026-09-26
to 2026-10-05 every gap between stored polls is a multiple of 10
s.[^copy-2026-10-05] A poll that overruns its tick (a 10 s timeout, a
crosswalk rebuild) skips the next tick rather than crowding it.

# Route mapping and self-repair

- The `idLigne → route` mapping and colors are loaded from
  [`routes.csv`](../datasets/routes-csv.md) at startup (`load_routes`).
- When a poll has buses on lines it doesn't know (stored as
  `cadavl:<id>`), at most every 15 minutes (`TOPO_CHECK_SECONDS = 900`) it
  asks [`/config/version`](../feeds/tracker-config-version.md). If that
  moved past the version recorded in
  [`network.geojson`](../datasets/network-geojson.md) (`topo_version`), it
  rebuilds the crosswalk ([`build_crosswalk.refresh`](crosswalk-builder.md),
  a ~28 MB download), reloads it, re-reads the same poll with it, and has
  `schedule.py` reload the timetable, since stop names may have moved. So a
  renumbering fixes itself on the poll that first sees it, as on 2026-09-30
  04:00 (every line ID changed, rebuilt in 7 s); no `cadavl:<id>` row was
  stored.[^poller-log]
- If the check finds nothing new or the rebuild fails (`crosswalk refresh
  failed: ...`), the next check waits 15 minutes, and rows logged in
  between keep `cadavl:<id>`; [`backfill_routes.py`](backfill-tools.md)
  remaps them later.

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
stamped with the local date and time (live since 2026-09-25 20:12:38). The
stamp is when the line was printed, at the end of the poll, so it can trail
the tick by a few seconds.

[^poller-code]: cadavl_to_gtfs_rt.py
[^copy-2026-10-05]: Copy of data/ taken 2026-10-05 22:37 (gaps between stored polls)
[^poller-log]: data/poller.log, 2026-09-30 04:00 crosswalk rebuild (read-only grep)
