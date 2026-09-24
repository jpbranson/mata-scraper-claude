-- The three questions from DESIGN.md, over data/positions/.
-- Run from the repo root:  duckdb < analysis.sql

-- All history, with local (Central) time. `dt` comes from the folder name.
CREATE VIEW pos AS
SELECT *,
       to_timestamp(observed_at) AT TIME ZONE 'America/Chicago' AS t
FROM read_json_auto('data/positions/*/positions.jsonl.gz', hive_partitioning = true);

-- Rows worth trusting: a delay was reported, it isn't a "1h+" cap, and the
-- GPS fix has moved in the last five minutes.
CREATE VIEW good AS
SELECT * FROM pos
WHERE delay_seconds IS NOT NULL AND NOT delay_capped AND unchanged_polls < 30;

-- 1. Which routes constantly run behind?
SELECT route_id,
       count(*)                                   AS bus_polls,
       round(median(delay_seconds) / 60, 1)       AS median_min_late,
       round(avg((delay_seconds > 300)::int), 2)  AS share_over_5_min
FROM good
GROUP BY route_id
ORDER BY share_over_5_min DESC;

-- 2. Which days are especially bad?
SELECT t::date                                    AS day,
       dayname(t::date)                           AS dow,
       round(median(delay_seconds) / 60, 1)       AS median_min_late,
       round(avg((delay_seconds > 300)::int), 2)  AS share_over_5_min
FROM good
GROUP BY 1, 2
ORDER BY share_over_5_min DESC;

-- 3. How many people are riding right now?
-- 40 riders at 100% load is a placeholder capacity (see DESIGN.md).
SELECT count(*)                                AS buses_in_service,
       round(sum(occupancy_pct) / 100.0 * 40)  AS riders_est
FROM (SELECT unnest(vehicles, recursive := true)
      FROM read_json_auto('data/latest.json'))
WHERE unchanged_polls < 30;
