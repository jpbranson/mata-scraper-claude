---
type: Dataset
title: Position history
description: One row per bus per poll (every 10 s of service), in daily gzipped JSONL partitions; the history every delay and load question is answered from.
resource: ../../data/positions/
tags: [tracker, delay, load, gps]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
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
    title: cadavl_to_gtfs_rt.py (normalize_vehicle, archive_positions)
  - id: backfill-routes
    resource: ../../backfill_routes.py
    title: backfill_routes.py (rewrites a day file in one gzip stream)
  - id: snapshot-1005
    resource: Measured on findings_page/snapshot-2026-10-05 (copy of data/ taken 2026-10-05 22:37 CDT)
    title: Measurements on the 2026-10-05 snapshot (positions 2026-09-23 21:38 to 2026-10-05 22:33)
---

# Layout

`data/positions/dt=YYYY-MM-DD/positions.jsonl.gz`, appended by the
[poller](../system/poller.md) on every poll during service hours (04:00–24:00
local). `dt` is the UTC date of the fetch, so a partition holds 19:00 to
19:00 local; convert `observed_at` to local time in queries rather than
renaming partitions. A restart appends to the day file, never overwrites
it. A poll with no buses (late evening, after the last one) adds no rows.
Not in git (`data/` is ignored). From 2026-09-23 21:38 CDT.[^snapshot-1005]

# Design

- One row per bus per poll. Every row represents the same 10 s of bus-time,
  so plain `AVG()` in SQL is already time-weighted. No forward-filling, no
  "was this bus still in the feed?" logic.
- "Right now" is just the latest poll (also in the
  [live snapshot](latest-snapshot.md)).
- Polls before the poller's fixed 10 s clock went live (2026-09-25 20:12
  CDT) are 11–14 s apart.
- Gaps (vendor down, buses dropping out at layovers) are just missing rows.

# Schema

20 fields per row:[^poller-code]

| Field | Type | Notes |
|---|---|---|
| `observed_at` | int, Unix seconds | Fetch time, not report time |
| `vehicle_id` | str | Vendor ID; stable per bus |
| `equipment_no` | str | Fleet number painted on the bus |
| `vehicle_type` | str | "Bus" on every row; the vendor types every vehicle "Bus", the trolley included |
| `line_internal_id` | int | Vendor line ID; changes with each [topo version](../feeds/tracker-topo.md#versions) |
| `route_id` | str | MATA route number ("01"), or `cadavl:<id>` if unmapped ([backfill_routes.py](../system/backfill-tools.md) fixes these later; none are left) |
| `route_color` | str | Hex from [routes.csv](routes-csv.md); for the map |
| `lat`, `lon` | float | |
| `bearing` | int | Degrees 0–359 |
| `speed_raw` | int | Metres per second, whole numbers; the odd impossible reading ([speed unit](../decisions/speed-unit.md)) |
| `occupancy_pct` | int | Passenger load as a percent of 50 riders, so always even; riders = `occupancy_pct / 2` ([bus capacity](../decisions/bus-capacity.md)) |
| `destination` | str | Headsign |
| `next_stop_name` | str | Display name, not a GTFS stop_id; null on ~1% of rows (off-route or idle) |
| `next_stop_eta_min` | int | |
| `delay_seconds` | int | Positive = late; `0` = "on time"; null if unparseable (never so far) |
| `delay_raw` | str | Vendor text, e.g. "4 min late" |
| `delay_capped` | bool | True for "1h+" values: a floor, not a measurement |
| `unchanged_polls` | int | Consecutive polls with identical coordinates: parked, or a dead tracker ([ghost threshold](../decisions/ghost-threshold.md)) |
| `trip_id` | str | GTFS trip the bus is inferred to be running ([trip matching](../system/timetable-and-arrivals.md)); null if unmatched (from 2026-09-24; 98% of rows have one since) |

Where each field comes from in the vendor payload, and the payload's known
limits: [tracker vehicles](../feeds/tracker-vehicles.md).

# Size

Measured over 2026-09-23 to 10-05, at ~78 B a row gzipped:[^snapshot-1005]

| Day | Rows | Buses at once (mean) | Size |
|---|---|---|---|
| Weekday | ~225k | ~33 | ~17.5 MB |
| Saturday | ~160k | ~30 | ~13 MB |
| Sunday | ~95k | ~25 | ~8 MB |

About 5.6 GB a year; 166 MB so far. 72 buses have appeared. Each poll
appends its own gzip member, which costs about three times one stream:
dt=2026-09-24, rewritten in one stream by backfill_routes.py, is 28 B a
row.[^backfill-routes] So if size ever matters, rewriting old days in one
stream, or to Parquet with one DuckDB `COPY`, cuts them to about a third.
Not now.

# Querying

[analysis.sql](../system/analysis-sql.md) reads it as the `pos` view (local
time as `t`), filters it to `good` rows for delay, and drops `ghost_rows`
for anything spatial.

[^poller-code]: cadavl_to_gtfs_rt.py (normalize_vehicle, archive_positions)
[^backfill-routes]: backfill_routes.py (rewrites a day file in one gzip stream)
[^snapshot-1005]: Measurements on the 2026-10-05 snapshot
