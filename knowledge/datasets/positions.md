---
type: Dataset
title: Position history
description: One row per bus per poll (every 10 s of service), in daily gzipped JSONL partitions; the history every delay and load question is answered from.
resource: ../../data/positions/
tags: [tracker, delay, load, gps]
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

# Layout

`data/positions/dt=YYYY-MM-DD/positions.jsonl.gz`, appended by the
[poller](../system/poller.md) on every poll during service hours (04:00–24:00
local). `dt` is the UTC date of the fetch; convert `observed_at` to local
time in queries rather than renaming partitions. A restart appends to the
day file, never overwrites it. Not in git (`data/` is ignored).

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

| Field | Type | Notes |
|---|---|---|
| `observed_at` | int, Unix seconds | Fetch time, not report time |
| `vehicle_id` | str | Vendor ID; stable per bus |
| `equipment_no` | str | Fleet number painted on the bus |
| `vehicle_type` | str | "Bus"; the vendor types every vehicle "Bus", the trolley included |
| `line_internal_id` | int | Vendor line ID |
| `route_id` | str | MATA route number ("01"), or `cadavl:<id>` if unmapped ([backfill_routes.py](../system/backfill-tools.md) fixes these later) |
| `route_color` | str | Hex from [routes.csv](routes-csv.md); for the map |
| `lat`, `lon` | float | |
| `bearing` | int | Degrees 0–360 |
| `speed_raw` | int | Metres per second, whole numbers; the odd impossible reading ([speed unit](../decisions/speed-unit.md)) |
| `occupancy_pct` | int | Passenger load as a percent of 50 riders, so always even; riders = `occupancy_pct / 2` ([bus capacity](../decisions/bus-capacity.md)) |
| `destination` | str | Headsign |
| `next_stop_name` | str | Display name, not a GTFS stop_id |
| `next_stop_eta_min` | int | |
| `delay_seconds` | int | Positive = late; `0` = "on time"; null if unparseable |
| `delay_raw` | str | Vendor text, e.g. "4 min late" |
| `delay_capped` | bool | True for "1h+" values: a floor, not a measurement |
| `unchanged_polls` | int | Consecutive polls with identical coordinates: parked, or a dead tracker ([ghost threshold](../decisions/ghost-threshold.md)) |
| `trip_id` | str | GTFS trip the bus is inferred to be running ([trip matching](../system/timetable-and-arrivals.md)); null if unmatched (from 2026-09-24) |

Where each field comes from in the vendor payload, and the payload's known
limits: [tracker vehicles](../feeds/tracker-vehicles.md).

# Size

Measured: 68 B per bus-poll gzipped, so a 30-bus average over the 20-hour
service day is ~18 MB/day and a full 41-bus day ~24 MB; call it 6–9 GB/year.
Acceptable on any disk. If it ever matters, compact old days to Parquet with
one DuckDB `COPY`; not now.

# Querying

[analysis.sql](../system/analysis-sql.md) reads it as the `pos` view (local
time as `t`), filters it to `good` rows for delay, and drops `ghost_rows`
for anything spatial.
