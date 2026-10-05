---
type: Dataset
title: Our GTFS-RT feed (vehicle_positions.pb)
description: A GTFS-Realtime VehiclePosition feed the poller rewrites every poll; fresher than MATA's but without trip IDs, and nothing reads it.
resource: ../../data/vehicle_positions.pb
tags: [gtfs, tracker]
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
---

# What it is

A GTFS-RT VehiclePosition feed of the current poll, written by the
[poller](../system/poller.md) (~30 lines of code). Not in git.

- Since 2026-09-25 20:12 it carries speed (m/s,
  [speed unit](../decisions/speed-unit.md)), skipping readings over 40 m/s
  (`MAX_SPEED_MS`).
- No trip IDs: the [tracker](../feeds/tracker-vehicles.md) has none.

# Status

Nothing in this project consumes it, and MATA publishes an
[official GTFS-RT feed](../feeds/official-gtfs-rt.md) anyway; ours is fresher
but has no trip IDs. Checked 2026-09-25: one small write per poll, no
reader, not in the way, so kept. Delete it if it ever gets in the way
(`gtfs-realtime-bindings` stays, for
[official_feed.py](../system/official-feed-archiver.md)).
