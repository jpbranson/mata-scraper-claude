---
type: Component
title: Official feed archiver
description: official_feed.py fetches MATA's own GTFS-Realtime vehicle positions and alerts every poll, and trip updates every 5 minutes, and appends each new snapshot to data/official/ as flat rows.
resource: ../../official_feed.py
tags: [official-feed, poller]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: official-code
    resource: ../../official_feed.py
    title: official_feed.py
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
predictions, hence 5 minutes. ~15–25 MB a day in all, estimated from
early-morning snapshots. Archived from 2026-09-25.

# Why keep it

It is an archive only (nothing in the poller reads it), kept for what the
tracker can't give: trip IDs to check `schedule.py`'s against ([trip
matching](../findings/trip-matching.md)), report timestamps, cancelled trips
and missed-trip alerts ([missed service](../findings/missed-service.md)),
and the predictions riders saw ([countdowns](../findings/countdowns.md)).
[`analysis.sql`](analysis-sql.md) reads it as `off_vehicles`,
`off_trip_updates` and `off_alerts`.

# Failures and checks

- A failure is logged per feed and never costs a poll; the archive has a gap
  and nothing else notices.
- `python official_feed.py` fetches each feed once and prints a row.
- `gtfs-realtime-bindings` (in `requirements.txt`) is needed for it.
