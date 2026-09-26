-- Questions from DESIGN.md and QUESTIONS.md, over data/.
-- Run from the repo root:  duckdb < analysis.sql   (all of it takes about a
-- minute; every query stands alone after the views, so copy out the one
-- you want). Each query is tagged [..]; FINDINGS.md quotes them by tag.

-- ============================================================ views

-- All history, with local (Central) time. `dt` comes from the folder name.
CREATE VIEW pos AS
SELECT *,
       to_timestamp(observed_at) AT TIME ZONE 'America/Chicago' AS t
FROM read_json_auto('data/positions/*/positions.jsonl.gz', hive_partitioning = true);

-- Rows worth trusting for delay: a delay was reported, it isn't a "1h+" cap,
-- and the bus hasn't sat still for 30+ polls (5 min). Those are mostly
-- layovers and holds, not dead GPS, but dropping them or the real ghosts
-- instead moves no route's late share by more than a point ([GPS]).
CREATE VIEW good AS
SELECT * FROM pos
WHERE delay_seconds IS NOT NULL AND NOT delay_capped AND unchanged_polls < 30;

-- Metres between two points; exact enough at city scale.
CREATE MACRO dist_m(lat1, lon1, lat2, lon2) AS
    6371000 * sqrt(pow(radians(lon2 - lon1) * cos(radians((lat1 + lat2) / 2)), 2)
                   + pow(radians(lat2 - lat1), 2));

-- Stuck GPS ("ghosts"): one row per (vehicle_id, observed_at) whose position
-- is stale. A bus's coordinates stop changing either because it is parked
-- (a layover or hold: it later drives off from the same spot) or because its
-- tracker stopped reporting (it reappears far away). A still streak of a
-- minute or more (6+ polls) that ends with the bus 200 m+ away was the
-- latter; the official feed's report times freeze over the same stretches.
-- The vendor freezes the delay too, so delay stats barely notice, but
-- anything spatial (speeds, positions) should leave these rows out.
CREATE VIEW ghost_rows AS
WITH w AS (
    SELECT vehicle_id, observed_at, lat, lon,
           lag(lat) OVER v AS plat, lag(lon) OVER v AS plon, lag(observed_at) OVER v AS pt
    FROM pos WINDOW v AS (PARTITION BY vehicle_id ORDER BY observed_at)),
s AS (
    SELECT *, sum((plat IS NULL OR lat <> plat OR lon <> plon OR observed_at - pt > 120)::int)
                OVER (PARTITION BY vehicle_id ORDER BY observed_at ROWS UNBOUNDED PRECEDING) AS streak
    FROM w),
e AS (
    SELECT vehicle_id, streak, count(*) AS polls, min(observed_at) AS t_first,
           max(observed_at) AS t_last, any_value(lat) AS lat, any_value(lon) AS lon
    FROM s GROUP BY ALL),
x AS (
    SELECT *, lead(t_first) OVER v - t_last AS gap,
           dist_m(lat, lon, lead(lat) OVER v, lead(lon) OVER v) AS jump_m
    FROM e WINDOW v AS (PARTITION BY vehicle_id ORDER BY streak))
SELECT s.vehicle_id, s.observed_at
FROM s JOIN x USING (vehicle_id, streak)
WHERE x.polls >= 6 AND x.gap <= 120 AND x.jump_m > 200;

-- When buses served stops (schedule.py): one row per bus per stop, `t` the
-- last poll that still showed the stop as next, `vehicle` the tracker's ID,
-- `trip` the matched GTFS trip, `delay` the vendor's delay then.
CREATE VIEW arrivals AS
SELECT regexp_extract(filename, '(\d{4}-\d{2}-\d{2})', 1) AS day,
       regexp_extract(filename, '([^/\\]+)\.jsonl$', 1)   AS route,
       t, stop, vehicle, trip, delay
FROM read_json('data/arrivals/*/*.jsonl', filename = true,
               columns = {t: 'BIGINT', stop: 'VARCHAR', vehicle: 'VARCHAR',
                          trip: 'VARCHAR', delay: 'INTEGER'});

-- The timetable the poller saved for each day (schedule.py): one row per
-- scheduled call, `t_sched` in Unix seconds.
CREATE VIEW sched AS
WITH f AS (
    SELECT regexp_extract(filename, '(\d{4}-\d{2}-\d{2})', 1) AS day,
           regexp_extract(filename, '([^/\\]+)\.json$', 1)    AS route,
           t0, trips, stops
    FROM read_json('data/schedule/*/*.json', filename = true,
                   columns = {t0: 'BIGINT', trips: 'JSON', stops: 'JSON'})),
k AS (
    SELECT day, route, t0, trips, stops, unnest(json_keys(stops)) AS stop
    FROM f WHERE route <> 'stops'),
c AS (
    SELECT day, route, t0, trips, stop,
           unnest(json_extract(stops, '$."' || stop || '"')::INTEGER[][]) AS call
    FROM k)
SELECT day, route, stop, t0 + call[1] AS t_sched,
       json_extract_string(trips, '$[' || call[2] || '][0]') AS trip,
       json_extract_string(trips, '$[' || call[2] || '][1]') AS headsign
FROM c;

-- Stop names and positions by stop code (build_crosswalk.py).
CREATE VIEW stops AS
SELECT DISTINCT ON (stop_code) stop_code, stop_name, lat, lon
FROM read_csv_auto('stops.csv');

-- Each route's timepoints (the timetable's major stops), from the stop
-- patterns schedule.py saves.
CREATE VIEW timepoints AS
WITH f AS (
    SELECT regexp_extract(filename, '([^/\\]+)\.json$', 1) AS route, patterns
    FROM read_json('data/schedule/*/*.json', filename = true, columns = {patterns: 'JSON'})),
p AS (
    SELECT route, unnest(json_extract(patterns, '$[*].stops[*]')) AS s
    FROM f WHERE route <> 'stops')
SELECT DISTINCT ON (route, s ->> 0) route, s ->> 0 AS stop, trim(s ->> 1) AS name
FROM p WHERE (s ->> 5)::INTEGER = 1;

-- Where each route's stop patterns begin and end. At a line's end the
-- tracker still shows the finished trip's headsign when the bus leaves,
-- so what the arrivals log records there is a departure credited to the
-- trip that just ended; `arrivals_due` leaves these stops out, and
-- [DEPART] times departures from MATA's feed instead.
CREATE VIEW line_ends AS
WITH f AS (
    SELECT regexp_extract(filename, '([^/\\]+)\.json$', 1) AS route, patterns
    FROM read_json('data/schedule/*/*.json', filename = true, columns = {patterns: 'JSON'})),
p AS (
    SELECT route, unnest(json_extract(patterns, '$[*].stops')) AS stops
    FROM f WHERE route <> 'stops')
SELECT DISTINCT route, json_extract_string(stops, '$[0][0]') AS stop FROM p
UNION
SELECT DISTINCT route, json_extract_string(stops, '$[' || (json_array_length(stops) - 1) || '][0]') FROM p;

-- MATA's official GTFS-RT archive (official_feed.py), from 2026-09-25.
-- `day` is the local date of the snapshot.
CREATE VIEW off_vehicles AS
SELECT *, strftime(to_timestamp(feed_ts) AT TIME ZONE 'America/Chicago', '%Y-%m-%d') AS day
FROM read_json_auto('data/official/*/vehicles.jsonl.gz');

CREATE VIEW off_trip_updates AS
SELECT *, strftime(to_timestamp(feed_ts) AT TIME ZONE 'America/Chicago', '%Y-%m-%d') AS day
FROM read_json_auto('data/official/*/trip_updates.jsonl.gz');

-- One row per alert per snapshot in which the alert list changed.
CREATE VIEW off_alerts AS
SELECT feed_ts, unnest(alerts, max_depth := 2)
FROM read_json_auto('data/official/*/alerts.jsonl.gz');

-- Arrivals with the time their trip was due at that stop (the nearest
-- call, for trips that pass a stop twice), leaving out any a dead
-- tracker timed and the ends of lines (see line_ends).
CREATE VIEW arrivals_due AS
SELECT a.*, s.t_sched, s.headsign
FROM arrivals a
JOIN sched s ON s.day = a.day AND s.route = a.route AND s.stop = a.stop AND s.trip = a.trip
ANTI JOIN ghost_rows g ON g.vehicle_id = a.vehicle AND g.observed_at = a.t
ANTI JOIN line_ends e ON e.route = a.route AND e.stop = a.stop
QUALIFY row_number() OVER (PARTITION BY a.day, a.route, a.stop, a.vehicle, a.t
                           ORDER BY abs(s.t_sched - (a.t - coalesce(a.delay, 0)))) = 1;

-- Scheduled trips, and whether a bus was ever on each: by the tracker (an
-- arrival or position matched to it) or by MATA's own feed (a vehicle on
-- it). `canceled`: MATA's feed marked it CANCELED at some point. On the
-- latest day only trips due over half an hour before the last poll count.
-- Before 2026-09-25 only the tracker counts, and it misses ~2% of trips
-- that do run, so misses read slightly high there.
CREATE VIEW trip_service AS
WITH ran AS (
    SELECT day, trip FROM arrivals WHERE trip IS NOT NULL
    UNION SELECT strftime(t, '%Y-%m-%d'), trip_id FROM pos WHERE trip_id IS NOT NULL
    UNION SELECT day, trip_id FROM off_vehicles WHERE trip_id IS NOT NULL
    UNION SELECT day, trip_id FROM off_trip_updates WHERE vehicle_id IS NOT NULL),
canceled AS (
    SELECT DISTINCT day, trip_id AS trip FROM off_trip_updates WHERE trip_status = 'CANCELED'),
trips AS (
    SELECT day, route, trip, any_value(headsign) AS headsign, min(t_sched) AS due
    FROM sched GROUP BY day, route, trip)
SELECT t.*, r.trip IS NOT NULL AS ran, c.trip IS NOT NULL AS canceled
FROM trips t
LEFT JOIN ran r ON r.day = t.day AND r.trip = t.trip
LEFT JOIN canceled c ON c.day = t.day AND c.trip = t.trip
WHERE t.due < (SELECT max(observed_at) FROM pos) - 1800;

-- ============================================================ the three questions (DESIGN.md)

-- [Q1] 1. Which routes constantly run behind?
-- The usual on-time window is at most 1 min early and 5 min late. The
-- vendor says "on time" within a minute either way and never "1 min", so
-- in its whole minutes, early is 2+ min early and late is 6+ min late.
SELECT route_id,
       count(*)                                   AS bus_polls,
       round(median(delay_seconds) / 60, 1)       AS median_min_late,
       round(avg((delay_seconds > 300)::int), 2)  AS share_over_5_min,
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
SELECT count(*)                                AS buses_in_service,
       sum(occupancy_pct) // 2                 AS riders
FROM (SELECT unnest(vehicles, recursive := true)
      FROM read_json_auto('data/latest.json'))
WHERE unchanged_polls < 30;

-- ============================================================ open questions (DESIGN.md)

-- [GPS] Whose tracker drops out? Share of each bus's rows that were ghosts.
SELECT p.equipment_no,
       count(*)                                        AS rows,
       count(g.vehicle_id)                             AS ghost_rows,
       round(count(g.vehicle_id) / count(*), 3)        AS ghost_share,
       string_agg(DISTINCT p.route_id, ',')            AS routes
FROM pos p LEFT JOIN ghost_rows g USING (vehicle_id, observed_at)
GROUP BY 1
HAVING count(g.vehicle_id) > 0
ORDER BY ghost_share DESC
LIMIT 15;

-- ============================================================ QUESTIONS.md 1: delay

-- [WHERE] Where along a route delay builds up. For each stop, the delay a
-- bus gained since the previous stop logged on its trip (within 15 min),
-- over every trip that passed: `min_per_day` is bus-minutes lost there per
-- day, the places worth fixing first. Negative = buses make time up (or
-- wait out being early at a timepoint).
WITH a AS (
    SELECT day, route, headsign, trip, vehicle, stop, t, delay,
           delay - lag(delay) OVER w AS gained, t - lag(t) OVER w AS secs
    FROM arrivals_due
    WINDOW w AS (PARTITION BY day, trip, vehicle ORDER BY t))
SELECT a.route, s.stop_name, a.headsign,
       count(*)                                          AS passes,
       round(avg(gained) / 60, 2)                        AS avg_min_gained,
       round(sum(gained) / 60 / count(DISTINCT day), 1)  AS min_per_day
FROM a JOIN stops s ON s.stop_code = a.stop
WHERE gained IS NOT NULL AND secs < 900
GROUP BY ALL
HAVING count(*) >= 20
ORDER BY min_per_day DESC
LIMIT 20;

-- [WHERE_ROUTE] Does delay recover or compound? Per trip, delay at the last
-- stop logged minus at the first, ends of lines aside (trips logged 20+
-- minutes), by route.
WITH trips AS (
    SELECT day, route, trip, vehicle,
           arg_min(delay, t) AS first_delay, arg_max(delay, t) AS last_delay,
           (max(t) - min(t)) / 60 AS minutes_logged
    FROM arrivals_due GROUP BY ALL)
SELECT route, count(*) AS trips,
       round(median(first_delay) / 60, 1)                AS med_start,
       round(median(last_delay) / 60, 1)                 AS med_end,
       round(avg(last_delay - first_delay) / 60, 1)      AS avg_gain,
       round(avg((last_delay - first_delay > 300)::int), 2) AS share_gain_5
FROM trips WHERE minutes_logged >= 20
GROUP BY route ORDER BY avg_gain DESC;

-- [DIRECTION] Which direction is worse? Routes whose headsigns differ by
-- 10+ points in their share of bus-polls 5+ min late.
WITH d AS (
    SELECT route_id, destination, count(*) AS polls,
           avg((delay_seconds > 300)::int) AS late
    FROM good GROUP BY ALL HAVING count(*) >= 500),
r AS (SELECT route_id, max(late) - min(late) AS spread FROM d GROUP BY 1)
SELECT d.route_id, d.destination, d.polls, round(d.late, 2) AS share_over_5_min
FROM d JOIN r USING (route_id)
WHERE r.spread >= 0.10
ORDER BY r.spread DESC, d.route_id, d.late DESC;

-- [HOUR] When does it go bad? By hour of day, every route. With weeks of
-- data, add dayname(t) to compare weekdays and weekends.
SELECT hour(t) AS hour, count(*) AS polls,
       round(median(delay_seconds) / 60, 1)        AS median_min_late,
       round(avg((delay_seconds > 300)::int), 2)   AS share_over_5_min,
       round(avg((delay_seconds < -60)::int), 2)   AS share_early
FROM good GROUP BY 1 ORDER BY 1;

-- [EARLY] Early running where it strands riders: buses leaving a timepoint
-- mid-route 2+ min early (someone there on time misses them), by route and
-- timepoint. Leaving a line's end early is in [DEPART].
SELECT a.route, tp.name AS timepoint, count(*) AS departures,
       round(avg((a.delay < -60)::int), 2)                        AS share_early,
       round(avg(a.delay) FILTER (WHERE a.delay < -60) / 60, 1)   AS avg_min_early
FROM arrivals_due a JOIN timepoints tp USING (route, stop)
GROUP BY ALL HAVING count(*) >= 15
ORDER BY share_early DESC
LIMIT 15;

-- ============================================================ QUESTIONS.md 2: ridership and crowding

-- [LOAD] Peak loads by route: riders on board (load % / 2) over its
-- bus-polls, and its fullest hour on average. 40 riders fill a 40-ft
-- bus's seats.
WITH h AS (
    SELECT route_id, hour(t) AS hour, avg(occupancy_pct) AS load
    FROM pos WHERE unchanged_polls < 30 GROUP BY ALL),
peak AS (SELECT route_id, arg_max(hour, load) AS busiest_hour FROM h GROUP BY 1)
SELECT route_id,
       round(avg(occupancy_pct) / 2, 1)              AS avg_riders,
       quantile_disc(occupancy_pct, 0.95) // 2       AS p95_riders,
       max(occupancy_pct) // 2                       AS max_riders,
       round(avg((occupancy_pct >= 80)::int), 3)     AS share_seats_full,
       any_value(busiest_hour)                       AS busiest_hour
FROM pos JOIN peak USING (route_id)
WHERE unchanged_polls < 30
GROUP BY route_id
ORDER BY p95_riders DESC, avg_riders DESC;

-- [LOAD_DELAY] Are the busiest routes the latest? Per route, riders on
-- board against late share (with the correlation across routes), and
-- whether its fuller buses (20+ riders) run later than its emptier ones
-- (under 10); if so, boarding time may be the cause.
WITH r AS (
    SELECT route_id,
           avg(occupancy_pct) / 2                                             AS avg_riders,
           avg((delay_seconds > 300)::int)                                    AS late,
           avg((delay_seconds > 300)::int) FILTER (WHERE occupancy_pct >= 40) AS late_full,
           avg((delay_seconds > 300)::int) FILTER (WHERE occupancy_pct < 20)  AS late_empty
    FROM good GROUP BY 1)
SELECT route_id, round(avg_riders, 1) AS avg_riders, round(late, 2) AS share_over_5_min,
       round(late_full, 2) AS late_20_plus_riders, round(late_empty, 2) AS late_under_10,
       round(corr(avg_riders, late) OVER (), 2) AS corr_across_routes
FROM r ORDER BY avg_riders DESC;

-- [RIDERS_DAY] Riding per day: rider-hours on board (each poll weighted
-- by the time to the next, up to 30 s), the most on board at once, and a
-- floor on boardings (every rise in a bus's count between polls; net
-- changes only). The line to set weather and events against.
WITH polls AS (
    SELECT observed_at, any_value(t) AS t, sum(occupancy_pct) / 2 AS riders
    FROM pos GROUP BY observed_at),
w AS (
    SELECT *, least(coalesce(lead(observed_at) OVER (ORDER BY observed_at) - observed_at, 10), 30) AS secs
    FROM polls),
b AS (
    SELECT t::date AS day,
           greatest(occupancy_pct - lag(occupancy_pct) OVER v, 0) / 2 AS boarded,
           observed_at - lag(observed_at) OVER v AS gap
    FROM pos WINDOW v AS (PARTITION BY vehicle_id ORDER BY observed_at)),
bd AS (SELECT day, sum(boarded) FILTER (WHERE gap <= 30) AS boardings FROM b GROUP BY 1)
SELECT w.t::date AS day, dayname(w.t::date) AS dow,
       round(sum(riders * secs) / 3600)             AS rider_hours,
       max(riders)                                  AS peak_on_board,
       strftime(arg_max(w.t, riders), '%H:%M')      AS peak_at,
       round(any_value(bd.boardings))               AS boardings_floor
FROM w JOIN bd ON bd.day = w.t::date
GROUP BY 1, 2 ORDER BY 1;

-- [BOARDINGS] Where do buses fill and empty? Each change in a bus's load
-- between polls (up to 30 s apart) goes to the stop it was serving, its
-- next stop in the earlier poll: riders on and off per day. Net changes
-- only, so both are floors.
WITH d AS (
    SELECT route_id, t, lag(next_stop_name) OVER v AS stop,
           (occupancy_pct - lag(occupancy_pct) OVER v) / 2 AS change,
           observed_at - lag(observed_at) OVER v AS gap
    FROM pos WINDOW v AS (PARTITION BY vehicle_id ORDER BY observed_at))
SELECT stop, string_agg(DISTINCT route_id, ',' ORDER BY route_id) AS routes,
       round(sum(greatest(change, 0)) / count(DISTINCT t::date))  AS on_per_day,
       round(sum(greatest(-change, 0)) / count(DISTINCT t::date)) AS off_per_day
FROM d WHERE stop IS NOT NULL AND gap <= 30
GROUP BY stop ORDER BY on_per_day DESC
LIMIT 20;

-- ============================================================ QUESTIONS.md 3: service delivered vs promised

-- [HEADWAY] Bunching: are the buses that run evenly spaced? For each two
-- buses in a row at a stop, the time between them against what the
-- timetable plans between their two trips: bunched = under a quarter of
-- it, gap = over 1.5 times it. `excess_wait` is the extra minutes a rider
-- turning up at random waits because the buses come unevenly (average
-- wait is sum(h²) / 2 sum(h), actual minus planned). Trips that never ran
-- don't show here; that's [MISSED].
WITH a AS (
    SELECT *, lag(t) OVER w AS prev_t, lag(t_sched) OVER w AS prev_sched,
           lag(vehicle) OVER w AS prev_vehicle
    FROM arrivals_due
    WINDOW w AS (PARTITION BY day, route, stop ORDER BY t, t_sched)),
pairs AS (
    SELECT route, t - prev_t AS actual, t_sched - prev_sched AS planned
    FROM a
    WHERE prev_t IS NOT NULL AND vehicle <> prev_vehicle AND t_sched > prev_sched)
SELECT route,
       count(*)                                          AS pairs,
       round(median(planned) / 60)                       AS planned_min,
       round(avg((actual < planned / 4)::int), 3)        AS bunched,
       round(avg((actual <= 60)::int), 3)                AS within_1_min,
       round(avg((actual > planned * 1.5)::int), 3)      AS gaps,
       round((sum(actual * actual) / (2 * sum(actual))
              - sum(planned * planned) / (2 * sum(planned))) / 60, 1) AS excess_wait
FROM pairs
GROUP BY route
ORDER BY bunched DESC, gaps DESC;

-- [FLEET] Buses out against buses the timetable needs, at half past each
-- hour: trips in progress then (each needs a bus) against buses in the
-- tracker, averaged over the days recorded. Buses at layover drop out of
-- the tracker and aren't in progress either.
WITH polls AS (SELECT DISTINCT observed_at, t FROM pos),
pick AS (
    SELECT strftime(t, '%Y-%m-%d') AS day, hour(t) AS hour,
           arg_min(observed_at, abs(minute(t) * 60 + second(t) - 1800)) AS at_
    FROM polls GROUP BY ALL),
buses AS (SELECT observed_at, count(*) AS in_tracker FROM pos GROUP BY 1),
trips AS (SELECT day, trip, min(t_sched) AS t0, max(t_sched) AS t1 FROM sched GROUP BY ALL),
need AS (
    SELECT p.day, p.hour, p.at_, count(x.trip) AS scheduled
    FROM pick p JOIN trips x ON x.day = p.day AND p.at_ BETWEEN x.t0 AND x.t1
    GROUP BY ALL)
SELECT n.hour, count(*) AS days,
       round(avg(n.scheduled), 1) AS trips_in_progress, round(avg(b.in_tracker), 1) AS buses_seen,
       round(avg(b.in_tracker - n.scheduled), 1) AS short_by
FROM need n JOIN buses b ON b.observed_at = n.at_
GROUP BY 1 ORDER BY 1;

-- [SPEED] Speed profiles (mph): by route, all day, at the peaks (7-9 and
-- 16-18) and midday (10-15), stops included; dead trackers, long still
-- periods and impossible readings left out.
SELECT route_id,
       round(avg(speed_raw) * 2.237, 1)                                                  AS mph,
       round(avg(speed_raw) FILTER (WHERE hour(t) IN (7, 8, 16, 17)) * 2.237, 1)         AS mph_peak,
       round(avg(speed_raw) FILTER (WHERE hour(t) BETWEEN 10 AND 14) * 2.237, 1)         AS mph_midday,
       round(avg((speed_raw = 0)::int), 2)                                               AS share_stopped
FROM pos ANTI JOIN ghost_rows USING (vehicle_id, observed_at)
WHERE unchanged_polls < 30 AND speed_raw <= 40
GROUP BY 1 ORDER BY mph;

-- [SPEED_SLOW] The slowest stretches: from each stop to the next one
-- logged on the same trip, straight-line distance over the time between
-- the bus leaving each (so the stop at the far end counts; layovers
-- don't), where buses pass 20+ times. Stretches under 300 m are left out:
-- they are mostly two stops at one corner, where the turn and the light
-- are all there is.
WITH a AS (
    SELECT route, trip, vehicle, day, stop, t,
           lag(stop) OVER w AS prev_stop, lag(t) OVER w AS prev_t
    FROM arrivals_due WINDOW w AS (PARTITION BY day, trip, vehicle ORDER BY t)),
seg AS (
    SELECT a.route, s1.stop_name AS from_stop, s2.stop_name AS to_stop,
           dist_m(s1.lat, s1.lon, s2.lat, s2.lon) AS m, a.t - a.prev_t AS secs
    FROM a JOIN stops s1 ON s1.stop_code = a.prev_stop JOIN stops s2 ON s2.stop_code = a.stop
    WHERE a.prev_t IS NOT NULL AND a.t - a.prev_t BETWEEN 10 AND 900)
SELECT route, from_stop, to_stop, count(*) AS passes,
       round(avg(m))                         AS metres,
       round(avg(secs))                      AS avg_secs,
       round(sum(m) / sum(secs) * 2.237, 1)  AS mph
FROM seg
GROUP BY ALL HAVING count(*) >= 20 AND avg(m) >= 300
ORDER BY mph
LIMIT 20;

-- ============================================================ QUESTIONS.md 4: MATA's official feed

-- [MISSED] Trips that never ran, by route and day. Most were never marked
-- canceled; MATA's alerts ("Route 1 is not running from William Hudson at
-- 5:15a") name some of them in free text.
SELECT day, route,
       count(*)                                        AS scheduled,
       count(*) FILTER (WHERE NOT ran)                 AS never_ran,
       round(avg((NOT ran)::int), 2)                   AS share_missed,
       count(*) FILTER (WHERE NOT ran AND canceled)    AS marked_canceled
FROM trip_service
GROUP BY ALL
ORDER BY day, share_missed DESC, route;

-- [MISSED_HOUR] Share of trips that never ran, by the hour they were due
-- to leave, every route.
SELECT hour(to_timestamp(due) AT TIME ZONE 'America/Chicago') AS hour,
       count(*) AS scheduled, count(*) FILTER (WHERE NOT ran) AS never_ran,
       round(avg((NOT ran)::int), 2) AS share_missed
FROM trip_service
GROUP BY 1 ORDER BY 1;

-- [PREDICT] Are the countdowns riders see honest? Each prediction in MATA's
-- trip updates (trips with a bus on them) against when the bus left that
-- stop (arrivals), by how far ahead it was made. `median_off_min` > 0:
-- the bus came later than predicted.
WITH pr AS (
    SELECT day, feed_ts, trip_id AS trip, unnest(stops, max_depth := 2)
    FROM off_trip_updates WHERE vehicle_id IS NOT NULL),
j AS (
    SELECT pr.feed_ts, coalesce(pr.departure, pr.arrival) AS predicted, a.t AS actual
    FROM pr JOIN arrivals a ON a.day = pr.day AND a.trip = pr.trip AND '0:' || a.stop = pr.stop_id
    WHERE coalesce(pr.departure, pr.arrival) >= pr.feed_ts AND a.t >= pr.feed_ts)
SELECT CASE WHEN predicted - feed_ts < 300 THEN 'a  0-5 min'
            WHEN predicted - feed_ts < 600 THEN 'b  5-10 min'
            WHEN predicted - feed_ts < 1200 THEN 'c 10-20 min'
            WHEN predicted - feed_ts < 2400 THEN 'd 20-40 min'
            ELSE 'e 40+ min' END                         AS ahead,
       count(*)                                          AS predictions,
       round(median(actual - predicted) / 60, 1)         AS median_off_min,
       round(avg((abs(actual - predicted) <= 120)::int), 2) AS within_2_min,
       round(avg((actual - predicted < -60)::int), 2)    AS bus_early_by_1_plus,
       round(avg((actual - predicted > 300)::int), 2)    AS bus_late_by_5_plus
FROM j GROUP BY 1 ORDER BY 1;

-- [DEPART] Do trips leave on time? From MATA's feed, which keeps a bus at
-- its trip's first stop until it goes: the first report of the trip's bus
-- after its last one at that stop, against the scheduled start. Reports
-- come every ~30 s, so departures read up to half a minute late.
WITH first_stop AS (
    SELECT day, route, trip, arg_min(stop, t_sched) AS stop, min(t_sched) AS due
    FROM sched GROUP BY ALL),
v AS (
    SELECT DISTINCT day, trip_id AS trip, reported_at, stop_id
    FROM off_vehicles WHERE trip_id IS NOT NULL AND reported_at IS NOT NULL),
at_first AS (
    SELECT v.day, v.trip, max(v.reported_at) AS last_there
    FROM v JOIN first_stop f ON f.day = v.day AND f.trip = v.trip AND v.stop_id = '0:' || f.stop
    GROUP BY ALL),
dep AS (
    SELECT a.day, a.trip, min(v.reported_at) AS left_at
    FROM at_first a JOIN v ON v.day = a.day AND v.trip = a.trip AND v.reported_at > a.last_there
    GROUP BY ALL)
SELECT coalesce(f.route, 'all') AS route, count(*) AS departures,
       round(median(d.left_at - f.due) / 60, 1)                     AS median_min_late,
       round(avg((d.left_at - f.due BETWEEN -60 AND 300)::int), 2)  AS on_time,
       round(avg((d.left_at - f.due > 300)::int), 2)                AS late_over_5,
       round(avg((d.left_at - f.due < -60)::int), 2)                AS early
FROM dep d JOIN first_stop f USING (day, trip)
GROUP BY ROLLUP (f.route)
ORDER BY on_time, departures DESC;

-- [TRIPMATCH] Does schedule.py's trip matching hold up? Each official
-- vehicle report (bus = fleet number) against our row for the same bus
-- nearest in time (within a minute): `same` counts only rows where we
-- named a trip; `ours_none` is how often we didn't.
WITH o AS (
    SELECT DISTINCT vehicle_id AS equipment_no, reported_at, trip_id AS off_trip
    FROM off_vehicles WHERE trip_id IS NOT NULL AND reported_at IS NOT NULL),
m AS (
    SELECT o.*, p.trip_id AS our_trip, p.route_id
    FROM o JOIN pos p ON p.equipment_no = o.equipment_no
                     AND p.observed_at BETWEEN o.reported_at - 60 AND o.reported_at + 60
    QUALIFY row_number() OVER (PARTITION BY o.equipment_no, o.reported_at
                               ORDER BY abs(p.observed_at - o.reported_at)) = 1)
SELECT coalesce(route_id, 'all')                   AS route,
       count(*)                                    AS compared,
       round(avg((our_trip = off_trip)::int), 3)   AS same,
       round(avg((our_trip IS NULL)::int), 3)      AS ours_none
FROM m
GROUP BY ROLLUP (route_id)
ORDER BY same, compared DESC;

-- [LAYOVER] How long buses sit at the start of a trip before leaving, from
-- MATA's feed (the tracker drops them there): time stopped at the trip's
-- first stop, and whether short waits go with late starts (5+ min late at
-- the first stop the tracker logged on the trip; at the first stop itself
-- the tracker still shows the previous trip's headsign).
WITH first_stop AS (
    SELECT day, trip, arg_min(stop, t_sched) AS stop FROM sched GROUP BY ALL),
sat AS (
    SELECT v.day, v.trip_id AS trip, any_value(v.route_id) AS route,
           (max(v.feed_ts) - min(v.feed_ts)) / 60 AS minutes
    FROM off_vehicles v JOIN first_stop f ON f.day = v.day AND f.trip = v.trip_id
                                          AND v.stop_id = '0:' || f.stop
    WHERE v.stop_status = 'STOPPED_AT'
    GROUP BY v.day, v.trip_id),
start AS (SELECT day, trip, arg_min(delay, t) AS delay FROM arrivals_due GROUP BY ALL)
SELECT coalesce(s.route, 'all') AS route, count(*) AS trips,
       round(median(s.minutes)) AS median_min_sat,
       round(avg((s.minutes < 5)::int), 2) AS share_under_5,
       round(avg((d.delay > 300)::int) FILTER (WHERE s.minutes < 5), 2)  AS late_start_after_short,
       round(avg((d.delay > 300)::int) FILTER (WHERE s.minutes >= 5), 2) AS late_start_after_long
FROM sat s LEFT JOIN start d USING (day, trip)
GROUP BY ROLLUP (s.route) ORDER BY trips DESC;

-- ============================================================ QUESTIONS.md 5

-- [STOP_WAIT] What riders get, missed trips included: turn up at a
-- timepoint (mid-route; line ends are in [DEPART]) 2 minutes before the
-- timetable says, and how long until a bus of that route leaves? A trip
-- that ran leaves when the tracker logged it
-- there, or if it didn't, at its scheduled time plus its median delay; a
-- trip that never ran doesn't come. Leaving 2+ min early means waiting
-- for the next. `stranded`: no bus at all for the rest of the day.
WITH trip_delay AS (
    SELECT day, trip, median(delay) AS d FROM arrivals_due GROUP BY ALL),
dep AS (
    SELECT s.day, s.route, s.stop,
           coalesce(a.t, s.t_sched + coalesce(td.d, 0)) AS t_dep
    FROM sched s
    JOIN trip_service ts ON ts.day = s.day AND ts.trip = s.trip AND ts.ran
    LEFT JOIN arrivals_due a ON a.day = s.day AND a.trip = s.trip AND a.stop = s.stop
                            AND a.t_sched = s.t_sched
    LEFT JOIN trip_delay td ON td.day = s.day AND td.trip = s.trip),
calls AS (
    SELECT s.day, s.route, s.stop, s.t_sched
    FROM sched s
    JOIN timepoints tp USING (route, stop)
    ANTI JOIN line_ends e ON e.route = s.route AND e.stop = s.stop
    JOIN trip_service ts ON ts.day = s.day AND ts.trip = s.trip),
w AS (
    SELECT c.route, d.t_dep - (c.t_sched - 120) AS wait
    FROM calls c ASOF LEFT JOIN dep d
      ON d.day = c.day AND d.route = c.route AND d.stop = c.stop AND d.t_dep >= c.t_sched - 120)
SELECT coalesce(route, 'all') AS route, count(*) AS calls,
       round(median(wait) / 60, 1)                  AS median_wait_min,
       round(quantile_cont(wait, 0.9) / 60)         AS p90_wait_min,
       round(avg((wait > 900)::int), 2)             AS over_15_min,
       count(*) FILTER (WHERE wait IS NULL)         AS stranded
FROM w GROUP BY ROLLUP (route) ORDER BY median_wait_min DESC;
