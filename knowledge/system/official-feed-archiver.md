---
type: Component
title: Official feed archiver
description: official_feed.py fetches MATA's own GTFS-Realtime vehicle positions and alerts every poll, and trip updates every 5 minutes, and appends each new snapshot to data/official/ as flat rows.
resource: ../../official_feed.py
tags: [official-feed, poller]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:01:00Z }
sources:
  - id: data-sizes
    resource: ../../data/official/
    title: data/official/ folder sizes, 2026-09-28 to 2026-10-04 (read-only du)
  - id: copy-2026-10-05
    resource: ../../findings_page/snapshot-2026-10-05/
    title: Copy of data/ taken 2026-10-05 22:37 (duplicate (feed_ts, vehicle) and (feed_ts, trip) rows)
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: official-code
    resource: ../../official_feed.py
    title: official_feed.py, Official.update
---

# Behavior

Every poll, `Official.update` fetches [MATA's own GTFS-RT](../feeds/official-gtfs-rt.md)
vehicle positions and alerts (two small requests), and every 5 minutes its
trip updates, and appends any snapshot it hasn't saved (by header timestamp)
to `data/official/dt=<UTC day>/`, flattened to rows:

- [official vehicles](../datasets/official-vehicles.md) (`vehicles.jsonl.gz`)
- [official trip updates](../datasets/official-trip-updates.md) (`trip_updates.jsonl.gz`)
- [official alerts](../datasets/official-alerts.md) (`alerts.jsonl.gz`), saved only when they change

Trip updates every 30 s would be ~150 MB a day of mostly repeated
predictions, hence 5 minutes. Measured 2026-09-28 to 2026-10-04: 12–14.5
MB a weekday (UTC day; trip updates ~10 MB, vehicles ~3.9 MB, alerts ~50
KB), 6.6–11.6 MB on the weekend days.[^data-sizes] Archived from
2026-09-25.

Every feed's file is rebuilt every 30 s, so most polls fetch a snapshot
already saved and write nothing. What was saved is remembered only in
memory, so after a restart each feed's current snapshot and the alert list
are saved once more.[^official-code] The archive holds the vehicle
snapshots of 2026-09-25 20:12:14 and 21:12:33 and the trip-update snapshot
of 21:12:26 twice (the two restarts that evening); later restarts, all
with no buses out, left none. Count rows per snapshot with that in mind.[^copy-2026-10-05]

# Why keep it

It is an archive only (nothing in the poller reads it), kept for what the
tracker can't give: trip IDs to check `schedule.py`'s against ([trip
matching](../findings/trip-matching.md)), report timestamps, cancelled trips
and missed-trip alerts ([missed service](../findings/missed-service.md)),
and the predictions riders saw ([countdowns](../findings/countdowns.md)).
[`analysis.sql`](analysis-sql.md) reads it as `off_vehicles`,
`off_trip_updates` and `off_alerts`.

# Failures and checks

- A failure is logged per feed (`official <feed> failed: ...`, 5 s
  timeout) and never costs a poll; that feed is fetched again the next
  poll, trip updates included. The archive has a gap and nothing else
  notices. When the tracker poll itself fails, this step is skipped for
  that poll. Five failures from 2026-09-25 to 2026-10-05 ([failure
  modes](../operations/failure-modes.md)).
- `python official_feed.py` fetches each feed once and prints a row.
- `gtfs-realtime-bindings` (in `requirements.txt`) is needed for it.

[^data-sizes]: data/official/ folder sizes, 2026-09-28 to 2026-10-04 (read-only du)
[^official-code]: official_feed.py, Official.update
[^copy-2026-10-05]: Copy of data/ taken 2026-10-05 22:37 (duplicate (feed_ts, vehicle) and (feed_ts, trip) rows)
