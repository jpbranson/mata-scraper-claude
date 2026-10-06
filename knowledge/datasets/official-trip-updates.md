---
type: Dataset
title: Official archive - trip updates
description: MATA's official GTFS-RT trip updates every 5 minutes, with per-stop predictions and cancelled trips; from 2026-09-25.
resource: ../../data/official/
tags: [official-feed, missed-service]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: official-code
    resource: ../../official_feed.py
    title: official_feed.py (trip_update_rows, EVERY, Official.update)
  - id: snapshot-1005
    resource: Measured on findings_page/snapshot-2026-10-05 (copy of data/ taken 2026-10-05 22:37 CDT)
    title: Measurements on the 2026-10-05 snapshot (official archive 2026-09-25 05:45 to 2026-10-05 22:33)
---

# Layout

`data/official/dt=YYYY-MM-DD/trip_updates.jsonl.gz` (UTC date of `feed_ts`),
from 2026-09-25 05:45 CDT, saved by the
[official feed archiver](../system/official-feed-archiver.md) every 5
minutes (snapshots a median 304 s apart); every 30 s would be ~150 MB a day
of mostly repeated predictions.[^official-code][^snapshot-1005] Not in git.
Size: see [official vehicles](official-vehicles.md#size); a weekday is
~15k rows and ~10 MB.

As with the vehicles, a poller restart saves the current snapshot again:
the 2026-09-25 21:12:26 snapshot is in twice. Count snapshots with
`count(DISTINCT feed_ts)`.[^snapshot-1005]

# Schema

One row per trip per snapshot, ~67 trips a snapshot on a weekday: the
trips under way and those due soon. Enum values are the GTFS-RT names;
times are Unix seconds.[^official-code]

| Field | Notes |
|---|---|
| `feed_ts` | Feed header time; trip updates carry no per-trip timestamp |
| `trip_id`, `route_id` | `ADDED` trips have IDs made up on the day, in no timetable |
| `trip_status` | `SCHEDULED`, `ADDED` or `CANCELED` |
| `vehicle_id` | Fleet number; null until a bus is assigned, and always null on `CANCELED` trips |
| `stops` | List of `{seq, stop_id, arrival, departure, status}`, one per remaining stop; `status` is `SCHEDULED` or `SKIPPED` (0.3% of entries) |

Only trips with a `vehicle_id` carry real predictions; the rest repeat the
timetable (see the [feed's validation notes](../feeds/official-gtfs-rt.md#validation)).
From 2026-09-25 to 10-05, 150 distinct trip IDs were marked `CANCELED`
and 27 trips were `ADDED`.[^snapshot-1005]

# Examples

DuckDB reads the lists with `unnest`. Every cancelled trip:

```sql
SELECT DISTINCT route_id, trip_id
FROM read_json_auto('data/official/*/trip_updates.jsonl.gz')
WHERE trip_status = 'CANCELED'
```

Most trips that never run are not marked; `trip_service` in
[analysis.sql](../system/analysis-sql.md) finds them (see
[missed service](../findings/missed-service.md)). `off_trip_updates` is the
view over this file.

[^official-code]: official_feed.py (trip_update_rows, EVERY, Official.update)
[^snapshot-1005]: Measurements on the 2026-10-05 snapshot
