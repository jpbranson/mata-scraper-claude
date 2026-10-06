---
type: Dataset
title: Official archive - vehicle positions
description: MATA's official GTFS-RT vehicle positions, one row per bus per 30 s snapshot, with trip IDs and report times the tracker lacks; from 2026-09-25.
resource: ../../data/official/
tags: [official-feed, gps]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: official-code
    resource: ../../official_feed.py
    title: official_feed.py (vehicle_rows, Official.update, append_rows)
  - id: snapshot-1005
    resource: Measured on findings_page/snapshot-2026-10-05 (copy of data/ taken 2026-10-05 22:37 CDT)
    title: Measurements on the 2026-10-05 snapshot (official archive 2026-09-25 05:45 to 2026-10-05 22:33)
---

# Layout

`data/official/dt=YYYY-MM-DD/vehicles.jsonl.gz`, from 2026-09-25 05:45
CDT. `dt` is the UTC date of `feed_ts`, the feed header's time. Appended by
the [official feed archiver](../system/official-feed-archiver.md) for every
snapshot of the [official feed](../feeds/official-gtfs-rt.md) not already
saved (by header timestamp), checked every poll. Not in git.

The archiver forgets what it saved when the poller restarts, so a restart
saves the current snapshot again: the 2026-09-25 20:12:14 and 21:12:33
snapshots are in twice.[^official-code][^snapshot-1005] Count snapshots
with `count(DISTINCT feed_ts)`, and dedupe on (`vehicle_id`, `feed_ts`)
before counting rows.

# Schema

One row per bus per snapshot, a median 30 s apart (90% within 38 s). Enum
values are the GTFS-RT names; times are Unix seconds.[^official-code][^snapshot-1005]

| Field | Notes |
|---|---|
| `feed_ts` | Feed header time |
| `reported_at` | The bus's own report time; a median 5 s before `feed_ts` |
| `vehicle_id` | Fleet number (the tracker's `equipment_no`) |
| `trip_id`, `route_id` | From the [GTFS timetable](../feeds/gtfs-timetable.md); every row has a trip, as the feed lists only buses assigned to one |
| `trip_status` | `SCHEDULED`, or `ADDED` for a trip added on the day (0.4% of rows); never `CANCELED` here |
| `lat`, `lon`, `bearing` | |
| `speed` | m/s by the spec |
| `stop_id` | GTFS, `0:<stop code>`: the stop the bus is at or heading to |
| `stop_status` | `IN_TRANSIT_TO` or `STOPPED_AT` |
| `occupancy` | `EMPTY`, `MANY_SEATS_AVAILABLE`, `FEW_SEATS_AVAILABLE`, `STANDING_ROOM_ONLY` or `FULL`, null on 4% of rows; fixed bands of the rider count, not a crowding measure ([bus capacity](../decisions/bus-capacity.md)) |

It includes buses at layover, parked at their next trip's first stop with
that trip's ID, which the tracker drops (see the
[feed's validation notes](../feeds/official-gtfs-rt.md#validation)), and
buses waiting at the garage on Watkins St at Levee Rd (about 35.178,
-90.011) before their first trip, most with William Hudson (`0:2`) as their
stop.[^snapshot-1005]

# Size

Measured 2026-09-26 to 10-05, by local day:[^snapshot-1005]

| Day | Vehicle rows | vehicles | trip_updates | alerts | Whole archive |
|---|---|---|---|---|---|
| Weekday | ~78k | ~4 MB | ~10.3 MB | 18–50 KB | ~14.5 MB |
| Saturday | ~57k | ~3 MB | ~8 MB | ~10 KB | ~11 MB |
| Sunday | ~35k | ~1.9 MB | ~4.2 MB | ~6 KB | ~6 MB |

About 4.6 GB a year; 131 MB so far. Vehicle rows are ~51 B gzipped. Each
snapshot is appended as its own gzip member, which costs space the same
way as in the [position history](positions.md#size).

# Querying

`off_vehicles` in [analysis.sql](../system/analysis-sql.md).

[^official-code]: official_feed.py (vehicle_rows, Official.update, append_rows)
[^snapshot-1005]: Measurements on the 2026-10-05 snapshot
