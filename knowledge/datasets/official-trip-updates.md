---
type: Dataset
title: Official archive - trip updates
description: MATA's official GTFS-RT trip updates every 5 minutes, with per-stop predictions and cancelled trips; from 2026-09-25.
resource: ../../data/official/
tags: [official-feed, missed-service]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
---

# Layout

`data/official/dt=YYYY-MM-DD/trip_updates.jsonl.gz` (UTC date of `feed_ts`),
from 2026-09-25, saved by the
[official feed archiver](../system/official-feed-archiver.md) every 5
minutes; every 30 s would be ~150 MB a day of mostly repeated predictions.
Not in git. Size: see [official vehicles](official-vehicles.md#size).

# Schema

One row per trip per snapshot. Enum values are the GTFS-RT names; times are
Unix seconds.

| Field | Notes |
|---|---|
| `feed_ts` | Feed header time; trip updates carry no per-trip timestamp |
| `trip_id`, `route_id` | |
| `trip_status` | `SCHEDULED`, `CANCELED`, … |
| `vehicle_id` | Fleet number; null until a bus is assigned |
| `stops` | List of `{seq, stop_id, arrival, departure, status}` |

Only trips with a `vehicle_id` carry real predictions; the rest repeat the
timetable (see the [feed's validation notes](../feeds/official-gtfs-rt.md#validation)).

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
