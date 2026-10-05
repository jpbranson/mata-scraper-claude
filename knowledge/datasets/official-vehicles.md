---
type: Dataset
title: Official archive - vehicle positions
description: MATA's official GTFS-RT vehicle positions, one row per bus per 30 s snapshot, with trip IDs and report times the tracker lacks; from 2026-09-25.
resource: ../../data/official/
tags: [official-feed, gps]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
---

# Layout

`data/official/dt=YYYY-MM-DD/vehicles.jsonl.gz`, from 2026-09-25. `dt` is
the UTC date of `feed_ts`, the feed header's time. Appended by the
[official feed archiver](../system/official-feed-archiver.md) for every
snapshot of the [official feed](../feeds/official-gtfs-rt.md) not already
saved (by header timestamp). Not in git.

# Schema

One row per bus per snapshot (30 s). Enum values are the GTFS-RT names;
times are Unix seconds.

| Field | Notes |
|---|---|
| `feed_ts` | Feed header time |
| `reported_at` | The bus's own report time |
| `vehicle_id` | Fleet number (the tracker's `equipment_no`) |
| `trip_id`, `route_id` | From the [GTFS timetable](../feeds/gtfs-timetable.md) |
| `trip_status` | e.g. `SCHEDULED`, `CANCELED` |
| `lat`, `lon`, `bearing` | |
| `speed` | m/s by the spec |
| `stop_id` | GTFS, `0:<stop code>` |
| `stop_status` | e.g. `IN_TRANSIT_TO` |
| `occupancy` | Category, e.g. `FEW_SEATS_AVAILABLE`; fixed bands of the rider count, not a crowding measure ([bus capacity](../decisions/bus-capacity.md)) |

It includes buses at layover, parked at their next trip's first stop with
that trip's ID, which the tracker drops (see the
[feed's validation notes](../feeds/official-gtfs-rt.md#validation)).

# Size

The whole official archive ([vehicles](official-vehicles.md),
[trip updates](official-trip-updates.md), [alerts](official-alerts.md)) is
~15–25 MB a day, estimated from early-morning snapshots.

# Querying

`off_vehicles` in [analysis.sql](../system/analysis-sql.md).
