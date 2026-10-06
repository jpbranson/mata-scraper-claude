---
type: Component
title: Analysis SQL
description: analysis.sql, one DuckDB file of views over everything in data/ and a tagged query per question; the findings cite its queries by tag.
resource: ../../analysis.sql
tags: [analysis, duckdb]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:19:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: analysis-code
    resource: ../../analysis.sql
    title: analysis.sql
  - id: snapshot-py
    resource: ../../findings_page/snapshot.py
    title: findings_page/snapshot.py
  - id: update-log
    resource: ../log.md
    title: Update log, 2026-10-05 ([Q3] fix, timing of a full run)
---

# Running it

DuckDB is an in-process analytical database: a single binary (or `pip
install duckdb`) that queries files directly, so there is nothing to load,
no schema to maintain, and no server. It reads the gzipped JSONL partitions
in one call and picks up the `dt=` folder name as a column.

- Every path in the file is relative (`data/...`, `stops.csv`), so run it
  from a folder that holds a copy of `data/` and `stops.csv`, such as one
  made by [`findings_page/snapshot.py`](findings-page.md)[^snapshot-py], not
  from the repo root, where `data/` is the live folder the poller is writing
  ([working with live data](../operations/working-with-live-data.md)).
- With the DuckDB CLI (`duckdb.exe`, a single file to download; not on the
  home machine's PATH): from inside the copy's folder, such as
  `findings_page\snapshot-2026-10-05\`, run
  `Get-Content ..\..\analysis.sql | <path to>\duckdb.exe`. Without it, the
  venv's Python `duckdb` can run it statement by statement, as
  [`findings_page/page_data.py`](findings-page.md) does to create the views.
- The copy needs every folder a view reads (`positions`, `official`,
  `arrivals`, `schedule`, `detours`) and `latest.json`: views are bound when
  they are created, so a missing folder fails with "No files found that
  match the pattern".
- The whole file over 12 days (`findings_page/snapshot-2026-10-05/`) takes
  about 4 minutes; `[STOP_WAIT]` alone is ~60 s, `[MISSED]` and
  `[MISSED_HOUR]` ~20 s each. On the first 1.8 days it took about a
  minute.[^update-log] Each query also runs on its own after the views.
- A script that runs the file statement by statement stops at the first
  error; the DuckDB CLI reports it and carries on.

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
| `off_vehicles`, `off_trip_updates`, `off_alerts` | The [official archive](official-feed-archiver.md); on the first two, `day` is the local date of the snapshot; `off_alerts` is one row per alert per snapshot in which the alert list changed |
| `rider_messages` | The [detour log's](../datasets/detour-log.md) rider messages, each with the routes its text names where MATA's tags disagree (`tagged`, `named`, `routes`, `mismatch`) |
| `arrivals_due` | Each arrival with the time its trip was due (nearest call), leaving out dead-tracker rows and line ends |
| `trip_service` | Each scheduled trip and whether any bus ran it (tracker or official feed), and whether MATA marked it `CANCELED`; only trips due over half an hour before the copy's last poll |

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
| `[RELIEF]` | 1 Delay | [Driver changes](../findings/driver-changes.md) |
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
-- All history, with local (Central) time. `dt` comes from the folder name.
CREATE VIEW pos AS
SELECT *,
       to_timestamp(observed_at) AT TIME ZONE 'America/Chicago' AS t
FROM read_json_auto('data/positions/*/positions.jsonl.gz', hive_partitioning = true);

-- Rows worth trusting for delay: a delay was reported, it isn't a "1h+" cap,
-- and the bus hasn't sat still for 30+ polls (5 min). Those are mostly
-- layovers and holds, not dead GPS, but dropping them or the real ghosts
-- instead moves no route's late share by more than 1.4 points ([GPS]).
CREATE VIEW good AS
SELECT * FROM pos
WHERE delay_seconds IS NOT NULL AND NOT delay_capped AND unchanged_polls < 30;

-- [Q1] 1. Which routes constantly run behind?
-- The usual on-time window is at most 1 min early and 5 min late. The
-- vendor says "on time" within a minute either way and never "1 min", so
-- in its whole minutes, early is 2+ min early and late is 6+ min late.
-- `weekday_over_5_min` compares routes on the days they all run: quiet
-- Sundays pull down only the routes that run on Sundays.
SELECT route_id,
       count(*)                                   AS bus_polls,
       round(median(delay_seconds) / 60, 1)       AS median_min_late,
       round(avg((delay_seconds > 300)::int), 2)  AS share_over_5_min,
       round(avg((delay_seconds > 300)::int) FILTER (WHERE dayofweek(t) BETWEEN 1 AND 5), 2) AS weekday_over_5_min,
       round(avg((delay_seconds < -60)::int), 2)  AS share_early,
       round(avg((delay_seconds BETWEEN -60 AND 300)::int), 2) AS on_time
FROM good
GROUP BY route_id
ORDER BY share_over_5_min DESC;

-- [Q2] 2. Which days are especially bad?
-- `hours` is first to last bus recorded; a short one is a partial day.
SELECT t::date                                    AS day,
       dayname(t::date)                           AS dow,
       round(date_diff('minute', min(t), max(t)) / 60, 1) AS hours,
       round(median(delay_seconds) / 60, 1)       AS median_min_late,
       round(avg((delay_seconds > 300)::int), 2)  AS share_over_5_min
FROM good
GROUP BY 1, 2
ORDER BY share_over_5_min DESC;

-- [Q3] 3. How many people are riding right now?
-- The load % is riders out of 50 on every vehicle, so riders = % / 2.
-- The columns are named because after service the vehicle list is empty,
-- and there is nothing to infer them from.
SELECT count(*)                                AS buses_in_service,
       coalesce(sum(occupancy_pct), 0) // 2    AS riders
FROM (SELECT unnest(vehicles, recursive := true)
      FROM read_json('data/latest.json',
                     columns = {vehicles: 'STRUCT(occupancy_pct INTEGER, unchanged_polls INTEGER)[]'}))
WHERE unchanged_polls < 30;
```

`[Q3]` read `latest.json` with `read_json_auto` until 2026-10-05. After
service ends the file holds an empty vehicle list (the poller keeps
rewriting it until midnight), so every night it failed with "Referenced column
unchanged_polls not found". It now names the columns and returns 0 buses
and 0 riders after service.[^update-log]

# Changed for 12 days of data (2026-10-05)

When the findings were rerun on 12 days, queries that assumed two weekdays
or counted something misleading were changed:[^update-log]

- `[WHERE]` counts lateness gained: early counts as on time, so a bus
  waiting out being early at a timepoint no longer shows as delay gained at
  the next stop (the trolley at Main @ Union and route 30's rows did).
- `[HOUR]`, `[FLEET]` and `[MISSED_HOUR]` split weekdays from Saturdays and
  Sundays (`day_type`); `[LOAD]`'s busiest hour is the busiest weekday hour;
  `[Q1]` adds `weekday_over_5_min`, since routes with no Sunday service
  aren't pulled down by quiet Sundays.
- `[BOARDINGS]` divides by whole days (6+ hours of service; the 55 minutes
  on Wed 09-23 counted as a day for some stops) and gives weekdays and
  weekend days apart; its comment says riders boarding at a transit center
  show under the first stop out.
- `[MISSED]` adds each day's total (route `all`) and leaves
  `marked_canceled` blank before 2026-09-25, when there was no official
  feed.
- `[TRIPMATCH]` leaves trips MATA's dispatch adds (in no timetable) out of
  `same` and counts them as `adhoc`.
- `[LAYOVER]` measures from when the bus last moved 50 m+, since the feed
  marks a bus `STOPPED_AT` its next trip's first stop only from about 5
  minutes before the trip is due; it adds `slack`, the minutes before due.
- `[Q3]` names `latest.json`'s columns (above).

Proposed but not made: `[SPEED_SLOW]` measures stretches in a straight line,
which misreads loops (route 30 from Brooks @ Gill to South Center is 378 m
straight but 2,810 m of route); the timetable's `shape_dist_traveled` would
fix it, but DuckDB can't read a file inside `data/gtfs.zip`, so the poller
would first have to save `stop_times.txt` beside it.
[Speed](../findings/speed.md) uses route distances from a one-off query.

Every cancelled trip in the [official archive](../datasets/official-trip-updates.md):

```sql
SELECT DISTINCT route_id, trip_id
FROM read_json_auto('data/official/*/trip_updates.jsonl.gz')
WHERE trip_status = 'CANCELED';
```

Most trips that never run are not marked; `trip_service` finds them.

[^snapshot-py]: findings_page/snapshot.py
[^update-log]: Update log, 2026-10-05 ([Q3] fix, timing of a full run)
