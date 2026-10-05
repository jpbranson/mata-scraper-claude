---
type: Component
title: Analysis SQL
description: analysis.sql, one DuckDB file of views over everything in data/ and a tagged query per question; the findings cite its queries by tag.
resource: ../../analysis.sql
tags: [analysis, duckdb]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: analysis-code
    resource: ../../analysis.sql
    title: analysis.sql
---

# Running it

DuckDB is an in-process analytical database: a single binary (or `pip
install duckdb`) that queries files directly, so there is nothing to load,
no schema to maintain, and no server. It reads the gzipped JSONL partitions
in one call and picks up the `dt=` folder name as a column.

- From the repo root: `duckdb < analysis.sql`.
- On Windows: download the DuckDB CLI (`duckdb.exe`, a single file) and run
  `Get-Content analysis.sql | .\duckdb.exe` from the repo folder.
- The whole file takes about a minute; each query also runs on its own
  after the views.
- Run it on a copy of `data/`, not the live files the poller is writing
  ([working with live data](../operations/working-with-live-data.md)).
  [`findings_page/page_data.py`](findings-page.md) creates these views over
  a snapshot.

Variations (by hour of day, by route × weekday, riders over the day) are
the same queries with a different `GROUP BY`. Add them to the file as they
are needed; don't pre-build them.

# Views

| View | What it is |
|---|---|
| `pos` | All [position history](../datasets/positions.md), with local (Central) time `t`; `dt` from the folder name |
| `good` | Rows worth trusting for delay: a delay was reported, it isn't a "1h+" cap, and the bus hasn't sat still for 30+ polls ([ghost threshold](../decisions/ghost-threshold.md)) |
| `dist_m` (macro) | Metres between two points; exact enough at city scale |
| `ghost_rows` | The positions a dead tracker left behind (a still streak of 6+ polls ending 200 m+ away within 2 min); spatial queries leave them out |
| `arrivals` | The [arrivals log](../datasets/arrivals-log.md): one row per bus per stop served |
| `sched` | The saved [timetables](../datasets/schedule-files.md), one row per scheduled call |
| `stops` | Stop names and positions by stop code ([`stops.csv`](../datasets/stops-csv.md)) |
| `timepoints` | Each route's timepoints, from the saved stop patterns |
| `line_ends` | Where each route's stop patterns begin and end; left out of timing questions ([timetable and arrivals](timetable-and-arrivals.md), Limits) |
| `off_vehicles`, `off_trip_updates`, `off_alerts` | The [official archive](official-feed-archiver.md); `day` is the local date of the snapshot |
| `rider_messages` | The [detour log's](../datasets/detour-log.md) rider messages, each with the routes its text names where MATA's tags disagree (`tagged`, `named`, `routes`, `mismatch`) |
| `arrivals_due` | Each arrival with the time its trip was due (nearest call), leaving out dead-tracker rows and line ends |
| `trip_service` | Each scheduled trip and whether any bus ran it (tracker or official feed), and whether MATA marked it `CANCELED` |

# Queries

After the views come the queries, grouped as in [questions/](../questions/)
and tagged so the findings can cite them:

| Tag | Group | Reported in |
|---|---|---|
| `[Q1]` | The three questions | [Routes that run behind](../findings/routes-behind.md) |
| `[Q2]` | The three questions | [Bad days](../findings/bad-days.md) |
| `[Q3]` | The three questions | [Riders right now](../findings/riders-now.md) |
| `[GPS]` | Open questions | [Ghost trackers](../findings/ghost-trackers.md) |
| `[WHERE]` | 1 Delay | [Where delay builds](../findings/where-delay-builds.md) |
| `[WHERE_ROUTE]` | 1 Delay | [Where delay builds](../findings/where-delay-builds.md) |
| `[DIRECTION]` | 1 Delay | [Direction](../findings/direction.md) |
| `[HOUR]` | 1 Delay | [Time of day](../findings/time-of-day.md) |
| `[EARLY]` | 1 Delay | [Early running](../findings/early-running.md) |
| `[LOAD]` | 2 Ridership | [Peak loads](../findings/peak-loads.md) |
| `[LOAD_DELAY]` | 2 Ridership | [Load vs delay](../findings/load-vs-delay.md) |
| `[RIDERS_DAY]` | 2 Ridership | [Riders per day](../findings/riders-per-day.md) |
| `[BOARDINGS]` | 2 Ridership | [Boardings](../findings/boardings.md) |
| `[HEADWAY]` | 3 Service | [Headways](../findings/headways.md) |
| `[FLEET]` | 3 Service | [Fleet in service](../findings/fleet-in-service.md) |
| `[SPEED]` | 3 Service | [Speed](../findings/speed.md) |
| `[SPEED_SLOW]` | 3 Service | [Speed](../findings/speed.md) |
| `[MISSED]` | 4 Official feed | [Missed service](../findings/missed-service.md) |
| `[MISSED_HOUR]` | 4 Official feed | [Missed service](../findings/missed-service.md) |
| `[PREDICT]` | 4 Official feed | [Countdowns](../findings/countdowns.md) |
| `[DEPART]` | 4 Official feed | [Departures](../findings/departures.md) |
| `[TRIPMATCH]` | 4 Official feed | [Trip matching](../findings/trip-matching.md) |
| `[LAYOVER]` | 4 Official feed | [Layovers](../findings/layovers.md) |
| `[STOP_WAIT]` | 5 Needs more | [Stop waits](../findings/stop-waits.md) |

# Examples

The two base views and the three questions, as in the file (the file is
authoritative):

```sql
-- All history, with local (Central) time.
CREATE VIEW pos AS
SELECT *,
       to_timestamp(observed_at) AT TIME ZONE 'America/Chicago' AS t
FROM read_json_auto('data/positions/*/positions.jsonl.gz', hive_partitioning = true);

-- Rows worth trusting for delay: a delay was reported, it isn't a "1h+"
-- cap, and the bus hasn't sat still for 30+ polls (mostly layovers).
CREATE VIEW good AS
SELECT * FROM pos
WHERE delay_seconds IS NOT NULL AND NOT delay_capped AND unchanged_polls < 30;

-- 1. Which routes constantly run behind?
-- On time = at most 1 min early and 5 min late; in the vendor's whole
-- minutes (it never says "1 min"), early is 2+ min and late 6+ min.
SELECT route_id,
       count(*)                                   AS bus_polls,
       round(median(delay_seconds) / 60, 1)       AS median_min_late,
       round(avg((delay_seconds > 300)::int), 2)  AS share_over_5_min,
       round(avg((delay_seconds < -60)::int), 2)  AS share_early,
       round(avg((delay_seconds BETWEEN -60 AND 300)::int), 2) AS on_time
FROM good
GROUP BY route_id
ORDER BY share_over_5_min DESC;

-- 2. Which days are especially bad?
-- `hours` is first to last bus recorded; a short one is a partial day.
SELECT t::date                                    AS day,
       dayname(t::date)                           AS dow,
       round(date_diff('minute', min(t), max(t)) / 60, 1) AS hours,
       round(median(delay_seconds) / 60, 1)       AS median_min_late,
       round(avg((delay_seconds > 300)::int), 2)  AS share_over_5_min
FROM good
GROUP BY 1, 2
ORDER BY share_over_5_min DESC;

-- 3. How many people are riding right now?
-- The load % is riders out of 50 on every vehicle, so riders = % / 2.
SELECT count(*)                                         AS buses_in_service,
       sum(occupancy_pct) // 2                          AS riders
FROM (SELECT unnest(vehicles, recursive := true)
      FROM read_json_auto('data/latest.json'))
WHERE unchanged_polls < 30;
```

Every cancelled trip in the [official archive](../datasets/official-trip-updates.md):

```sql
SELECT DISTINCT route_id, trip_id
FROM read_json_auto('data/official/*/trip_updates.jsonl.gz')
WHERE trip_status = 'CANCELED';
```

Most trips that never run are not marked; `trip_service` finds them.
