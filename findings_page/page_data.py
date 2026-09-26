"""Everything the findings page draws, and every number FINDINGS.md quotes,
from one copy of data/ (made by snapshot.py; never the live files).
Writes out/page_data.json (for the page) and out/numbers.txt (for the text).

    .venv\\Scripts\\python findings_page\\page_data.py [SNAPSHOT_DIR]
"""
import json
import math
import os
import pathlib
import re
import sys
from collections import defaultdict

import duckdb

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
SNAP = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE / "snapshot"
OUT = HERE / "out"
# The day MATA's official feed covers in full: trips it saw, and its alerts,
# are counted on this day. The page is laid out for this day and the one
# before it (DAYS in template.html).
FEED_DAY = "2026-09-25"

OUT.mkdir(exist_ok=True)
os.chdir(SNAP)          # analysis.sql reads data/... and stops.csv relative to here
con = duckdb.connect()
for chunk in re.split(r";[ \t]*\r?\n", (REPO / "analysis.sql").read_text(encoding="utf-8")):
    body = "\n".join(l for l in chunk.strip().splitlines() if not l.strip().startswith("--")).strip()
    if re.match(r"(?i)create\b", body):
        con.sql(body)


def rows(q):
    return con.sql(q).fetchall()


def one(q):
    return con.sql(q).fetchone()


def r1(x, n=1):
    return None if x is None else round(float(x), n)


D = {}          # page data
N = []          # numbers for FINDINGS.md, as text lines


def note(*a):
    N.append(" ".join(str(x) for x in a))


# ---------------------------------------------------------------- meta
m = one("""SELECT count(*), count(DISTINCT observed_at), count(DISTINCT vehicle_id),
                  strftime(min(t), '%Y-%m-%d %H:%M'), strftime(max(t), '%Y-%m-%d %H:%M')
           FROM pos""")
o = one("""SELECT count(DISTINCT feed_ts),
                  strftime(to_timestamp(min(feed_ts)) AT TIME ZONE 'America/Chicago', '%Y-%m-%d %H:%M'),
                  strftime(to_timestamp(max(feed_ts)) AT TIME ZONE 'America/Chicago', '%Y-%m-%d %H:%M')
           FROM off_vehicles""")
days = rows("""SELECT t::date::varchar, strftime(min(t), '%H:%M'), strftime(max(t), '%H:%M'), count(*)
               FROM pos GROUP BY 1 ORDER BY 1""")
D["meta"] = {"rows": m[0], "polls": m[1], "buses": m[2], "first": m[3], "last": m[4],
             "official_snapshots": o[0], "official_first": o[1], "official_last": o[2],
             "days": [{"day": d, "first": f, "last": l, "rows": n} for d, f, l, n in days]}
note("META", D["meta"])

# ---------------------------------------------------------------- Q1, Q2
q1 = rows("""SELECT route_id, count(*), median(delay_seconds) / 60,
                    avg((delay_seconds > 300)::int), avg((delay_seconds < -60)::int),
                    avg((delay_seconds BETWEEN -60 AND 300)::int)
             FROM good GROUP BY 1 ORDER BY 4 DESC, 1""")
D["q1"] = [{"route": r, "polls": n, "median": r1(md), "late": r1(l, 3), "early": r1(e, 3), "on_time": r1(ot, 3)}
           for r, n, md, l, e, ot in q1]
tot = one("""SELECT count(*), avg((delay_seconds > 300)::int), avg((delay_seconds < -60)::int),
                    avg((delay_seconds BETWEEN -60 AND 300)::int),
                    (SELECT count(*) FROM pos)
             FROM good""")
D["q1_all"] = {"polls": tot[0], "late": r1(tot[1], 3), "early": r1(tot[2], 3), "on_time": r1(tot[3], 3),
               "kept": r1(tot[0] / tot[4], 3)}
capped = one("SELECT avg(delay_capped::int), avg((unchanged_polls >= 30)::int) FROM pos")
D["q1_all"]["capped"] = r1(capped[0], 3)
D["q1_all"]["still30"] = r1(capped[1], 3)
note("Q1", D["q1"])
note("Q1_ALL", D["q1_all"])
q2 = rows("""SELECT t::date::varchar, dayname(t::date), round(date_diff('minute', min(t), max(t)) / 60, 1),
                    avg((delay_seconds > 300)::int)
             FROM good GROUP BY 1, 2 ORDER BY 1""")
D["q2"] = [{"day": d, "dow": w, "hours": h, "late": r1(l, 3)} for d, w, h, l in q2]
note("Q2", D["q2"])

# ---------------------------------------------------------------- ghosts / GPS
con.sql("""CREATE TABLE gs AS
WITH w AS (
    SELECT vehicle_id, equipment_no, observed_at, lat, lon,
           lag(lat) OVER v AS plat, lag(lon) OVER v AS plon, lag(observed_at) OVER v AS pt
    FROM pos WINDOW v AS (PARTITION BY vehicle_id ORDER BY observed_at)),
s AS (
    SELECT *, sum((plat IS NULL OR lat <> plat OR lon <> plon OR observed_at - pt > 120)::int)
                OVER (PARTITION BY vehicle_id ORDER BY observed_at ROWS UNBOUNDED PRECEDING) AS streak
    FROM w),
e AS (
    SELECT vehicle_id, streak, any_value(equipment_no) AS eq, count(*) AS polls,
           min(observed_at) AS t_first, max(observed_at) AS t_last,
           any_value(lat) AS lat, any_value(lon) AS lon
    FROM s GROUP BY vehicle_id, streak)
SELECT *, lead(t_first) OVER v - t_last AS gap,
       dist_m(lat, lon, lead(lat) OVER v, lead(lon) OVER v) AS jump_m
FROM e WINDOW v AS (PARTITION BY vehicle_id ORDER BY streak)""")
con.sql("""CREATE TABLE ends_xy AS
SELECT DISTINCT s.lat::DOUBLE AS lat, s.lon::DOUBLE AS lon FROM line_ends le JOIN stops s ON s.stop_code = le.stop
UNION ALL SELECT * FROM (VALUES (35.17919, -90.01324), (35.15966, -90.04761), (35.15655, -90.0477),
                                (35.13193, -90.05903), (35.06178, -89.99283), (35.07598, -89.93267)) v(lat, lon)""")
con.sql("""CREATE TABLE gs2 AS
SELECT gs.*,
       (SELECT min(dist_m(gs.lat, gs.lon, e.lat, e.lon)) FROM ends_xy e) < 150 AS at_end,
       CASE WHEN gap IS NULL THEN 'end' WHEN gap > 120 THEN 'left' WHEN jump_m > 200 THEN 'dead' ELSE 'drove' END AS how
FROM gs WHERE polls >= 6""")
gt = rows("""SELECT CASE WHEN polls < 10 THEN '6-9' WHEN polls < 20 THEN '10-19' WHEN polls < 30 THEN '20-29' ELSE '30+' END,
                    count(*), count(*) FILTER (WHERE how = 'dead'), count(*) FILTER (WHERE how = 'drove'),
                    count(*) FILTER (WHERE how = 'left'), avg(at_end::int),
                    count(*) FILTER (WHERE how = 'drove' AND at_end), count(*) FILTER (WHERE how = 'drove' AND NOT at_end)
             FROM gs2 GROUP BY 1 ORDER BY min(polls)""")
D["ghost_streaks"] = [{"polls": b, "streaks": n, "dead": d, "drove": dr, "left": lf, "at_end": r1(ae, 2),
                       "layover": lay, "hold": hold} for b, n, d, dr, lf, ae, lay, hold in gt]
note("GHOST_STREAKS", D["ghost_streaks"])
gps = rows("""SELECT p.equipment_no, count(*), count(g.vehicle_id), string_agg(DISTINCT p.route_id, ',' ORDER BY p.route_id)
              FROM pos p LEFT JOIN ghost_rows g USING (vehicle_id, observed_at)
              GROUP BY 1 HAVING count(g.vehicle_id) > 0 ORDER BY count(g.vehicle_id) / count(*) DESC, 1 LIMIT 5""")
gtot = one("""SELECT count(*), (SELECT count(*) FROM pos) FROM ghost_rows""")
D["gps"] = {"top": [{"bus": b, "rows": n, "ghost": g, "routes": rt} for b, n, g, rt in gps],
            "ghost_rows": gtot[0], "rows": gtot[1]}
note("GPS", D["gps"])
# route late share: 30-poll rule vs dropping ghost rows instead
gl = rows("""WITH f AS (SELECT p.*, g.vehicle_id IS NOT NULL AS ghost FROM pos p
                        LEFT JOIN ghost_rows g USING (vehicle_id, observed_at)
                        WHERE delay_seconds IS NOT NULL AND NOT delay_capped)
             SELECT max(abs(a - b)) FROM (
               SELECT route_id, avg((delay_seconds > 300)::int) FILTER (WHERE unchanged_polls < 30) AS a,
                      avg((delay_seconds > 300)::int) FILTER (WHERE NOT ghost) AS b
               FROM f GROUP BY 1)""")
D["gps"]["max_route_diff"] = r1(gl[0][0] * 100, 1)
note("GPS max route diff pts", D["gps"]["max_route_diff"])

# ---------------------------------------------------------------- speed unit, capacity (same-report pairs)
con.sql("""CREATE TABLE pairs AS
SELECT DISTINCT o.vehicle_id, o.reported_at, o.speed AS off_speed, o.occupancy, p.speed_raw, p.occupancy_pct
FROM off_vehicles o JOIN pos p ON p.equipment_no = o.vehicle_id
  AND p.observed_at BETWEEN o.reported_at - 30 AND o.reported_at + 90
  AND abs(p.lat - o.lat) < 1e-6 AND abs(p.lon - o.lon) < 1e-6""")
sp = one("""SELECT count(*), count(*) FILTER (WHERE speed_raw > 0),
                   avg((abs(off_speed - speed_raw) < 0.05)::int) FILTER (WHERE speed_raw > 0)
            FROM pairs WHERE off_speed IS NOT NULL""")
grid = rows("""SELECT speed_raw, round(off_speed)::int, count(*) FROM pairs
               WHERE off_speed IS NOT NULL AND speed_raw BETWEEN 0 AND 25 AND off_speed <= 25
               GROUP BY 1, 2 ORDER BY 1, 2""")
dist = one("""WITH legs AS (
    SELECT p.vehicle_id, p.observed_at, p.observed_at - lag(p.observed_at) OVER v AS dt,
           dist_m(lag(p.lat) OVER v, lag(p.lon) OVER v, p.lat, p.lon) AS m,
           (p.speed_raw + lag(p.speed_raw) OVER v) / 2.0 AS v_raw, p.observed_at // 300 AS win
    FROM pos p ANTI JOIN ghost_rows g USING (vehicle_id, observed_at)
    WINDOW v AS (PARTITION BY p.vehicle_id ORDER BY p.observed_at)),
w AS (SELECT vehicle_id, win, sum(m) AS m, sum(v_raw * dt) AS raw_s
      FROM legs WHERE dt <= 30 GROUP BY ALL HAVING sum(dt) >= 240 AND sum(m) > 500)
SELECT count(*), median(m / raw_s), quantile_cont(m / raw_s, 0.25), quantile_cont(m / raw_s, 0.75) FROM w""")
bad = one("SELECT count(*) FILTER (WHERE speed_raw > 40), count(*), max(speed_raw), quantile_disc(speed_raw, 0.99), avg((speed_raw = 0)::int) FROM pos")
D["speed"] = {"pairs": sp[0], "moving": sp[1], "equal": r1(sp[2], 3), "grid": grid,
              "windows": dist[0], "ratio": r1(dist[1], 3), "ratio_p25": r1(dist[2], 2), "ratio_p75": r1(dist[3], 2),
              "impossible": bad[0], "rows": bad[1], "max": bad[2], "p99": bad[3], "zero": r1(bad[4], 2)}
note("SPEED", {k: v for k, v in D["speed"].items() if k != "grid"})
comb = rows("SELECT occupancy_pct, count(*) FROM pos GROUP BY 1 ORDER BY 1")
odd = one("SELECT count(*) FILTER (WHERE occupancy_pct % 2 = 1), count(*) FROM pos")
cats = rows("""SELECT occupancy, count(*), quantile_disc(occupancy_pct, 0.05), quantile_disc(occupancy_pct, 0.5),
                      quantile_disc(occupancy_pct, 0.95)
               FROM pairs GROUP BY 1 ORDER BY 4, 1""")
D["capacity"] = {"comb": comb, "odd": odd[0], "rows": odd[1],
                 "categories": [{"cat": c or "none", "n": n, "p5": a, "p50": b, "p95": c2} for c, n, a, b, c2 in cats]}
note("CAPACITY", {"odd": odd, "categories": D["capacity"]["categories"]})

# ---------------------------------------------------------------- on-time windows
otp = one("""SELECT avg((delay BETWEEN -60 AND 300)::int), avg((delay > 300)::int), avg((delay < -60)::int), count(*)
             FROM arrivals_due a JOIN timepoints tp USING (route, stop)""")
D["otp_timepoints"] = {"on_time": r1(otp[0], 3), "late": r1(otp[1], 3), "early": r1(otp[2], 3), "n": otp[3]}
note("OTP mid-route timepoints", D["otp_timepoints"])
dep = rows("""WITH first_stop AS (
    SELECT day, route, trip, arg_min(stop, t_sched) AS stop, min(t_sched) AS due FROM sched GROUP BY ALL),
v AS (SELECT DISTINCT day, trip_id AS trip, reported_at, stop_id FROM off_vehicles
      WHERE trip_id IS NOT NULL AND reported_at IS NOT NULL),
at_first AS (SELECT v.day, v.trip, max(v.reported_at) AS last_there
             FROM v JOIN first_stop f ON f.day = v.day AND f.trip = v.trip AND v.stop_id = '0:' || f.stop
             GROUP BY ALL),
d AS (SELECT a.day, a.trip, min(v.reported_at) AS left_at
      FROM at_first a JOIN v ON v.day = a.day AND v.trip = a.trip AND v.reported_at > a.last_there GROUP BY ALL)
SELECT f.route, (d.left_at - f.due) / 60.0 FROM d JOIN first_stop f USING (day, trip) ORDER BY 1, 2""")
D["depart"] = [[r, r1(x, 2)] for r, x in dep]
dd = sorted(x for _, x in dep)
dn = len(dd)
D["depart_all"] = {"n": dn, "median": r1(dd[dn // 2], 1),
                   "on_time": r1(sum(-1 <= x <= 5 for x in dd) / dn, 3),
                   "late5": r1(sum(x > 5 for x in dd) / dn, 3), "early": r1(sum(x < -1 for x in dd) / dn, 3)}
note("DEPART", D["depart_all"])

# ---------------------------------------------------------------- where delay builds up
wh = rows("""WITH a AS (
    SELECT day, route, headsign, trip, vehicle, stop, t, delay,
           delay - lag(delay) OVER w AS gained, t - lag(t) OVER w AS secs
    FROM arrivals_due WINDOW w AS (PARTITION BY day, trip, vehicle ORDER BY t))
SELECT a.route, s.stop_name, a.headsign, count(*), avg(gained) / 60,
       sum(gained) / 60 / count(DISTINCT day), arg_min(s.lat, s.stop_code), arg_min(s.lon, s.stop_code)
FROM a JOIN stops s ON s.stop_code = a.stop
WHERE gained IS NOT NULL AND secs < 900
GROUP BY a.route, s.stop_name, a.headsign HAVING count(*) >= 20
ORDER BY 6 DESC, 1, 2, 3 LIMIT 30""")
D["where"] = [{"route": r, "stop": s, "head": h.strip(), "passes": n, "gain": r1(g, 2), "per_day": r1(pd, 1),
               "lat": la, "lon": lo} for r, s, h, n, g, pd, la, lo in wh]
note("WHERE", D["where"][:10])
se = rows("""WITH trips AS (
    SELECT day, route, trip, vehicle, arg_min(delay, t) AS first_delay, arg_max(delay, t) AS last_delay,
           (max(t) - min(t)) / 60 AS minutes_logged
    FROM arrivals_due GROUP BY ALL)
SELECT route, count(*), avg(first_delay) / 60, avg(last_delay) / 60, median(first_delay) / 60,
       median(last_delay) / 60, avg(last_delay - first_delay) / 60, avg((last_delay - first_delay > 300)::int)
FROM trips WHERE minutes_logged >= 20 GROUP BY route ORDER BY 7 DESC, 1""")
D["start_end"] = [{"route": r, "trips": n, "start": r1(a), "end": r1(b), "med_start": r1(c), "med_end": r1(d_),
                   "gain": r1(g), "gain5": r1(g5, 2)} for r, n, a, b, c, d_, g, g5 in se]
note("START_END", D["start_end"])

# ---------------------------------------------------------------- direction, hour
dr = rows("""SELECT route_id, trim(destination), count(*), avg((delay_seconds > 300)::int)
             FROM good GROUP BY ALL HAVING count(*) >= 500 ORDER BY 1, 3 DESC, 2""")
by = defaultdict(lambda: {"in": [0, 0.0], "out": [0, 0.0], "heads": []})
for r, h, n, l in dr:
    k = "in" if h.startswith("WILLIAM HUDSON") else "out"
    by[r][k][0] += n
    by[r][k][1] += l * n
    by[r]["heads"].append([h, n, r1(l, 3)])
D["direction"] = [{"route": r, "in": r1(v["in"][1] / v["in"][0], 3) if v["in"][0] else None,
                   "out": r1(v["out"][1] / v["out"][0], 3) if v["out"][0] else None,
                   "in_polls": v["in"][0], "out_polls": v["out"][0], "heads": v["heads"]}
                  for r, v in sorted(by.items())]
note("DIRECTION", [(d["route"], d["in"], d["out"]) for d in D["direction"]])
hr = rows("""SELECT hour(t), count(*), avg((delay_seconds > 300)::int), avg((delay_seconds < -60)::int),
                    median(delay_seconds) / 60
             FROM good GROUP BY 1 ORDER BY 1""")
D["hour"] = [{"h": h, "polls": n, "late": r1(l, 3), "early": r1(e, 3), "median": r1(md)} for h, n, l, e, md in hr]
hrr = rows("""SELECT route_id, hour(t), count(*), avg((delay_seconds > 300)::int)
              FROM good GROUP BY 1, 2 HAVING count(*) >= 60 ORDER BY 1, 2""")
hr_route = defaultdict(list)
for r, h, n, l in hrr:
    hr_route[r].append([h, n, r1(l, 3)])
D["hour_route"] = hr_route
note("HOUR", [(d["h"], d["late"], d["early"]) for d in D["hour"]])

# ---------------------------------------------------------------- early running mid-route
er = rows("""SELECT a.route, tp.name, count(*), avg((a.delay < -60)::int),
                    avg(a.delay) FILTER (WHERE a.delay < -60) / 60
             FROM arrivals_due a JOIN timepoints tp USING (route, stop)
             GROUP BY ALL HAVING count(*) >= 15 ORDER BY 4 DESC, 1, 2 LIMIT 12""")
D["early"] = [{"route": r, "tp": n, "deps": c, "share": r1(s, 3), "avg": r1(a)} for r, n, c, s, a in er]
note("EARLY", D["early"])

# ---------------------------------------------------------------- loads, riders, boardings
ld = rows("""SELECT route_id, avg(occupancy_pct) / 2, quantile_disc(occupancy_pct, 0.25) / 2,
                    quantile_disc(occupancy_pct, 0.5) / 2, quantile_disc(occupancy_pct, 0.75) / 2,
                    quantile_disc(occupancy_pct, 0.95) / 2, max(occupancy_pct) / 2, avg((occupancy_pct >= 80)::int)
             FROM pos WHERE unchanged_polls < 30 GROUP BY 1 ORDER BY 6 DESC, 2 DESC, 1""")
D["loads"] = [{"route": r, "avg": r1(a), "p25": p25, "p50": p50, "p75": p75, "p95": p95, "max": mx,
               "full": r1(f, 4)} for r, a, p25, p50, p75, p95, mx, f in ld]
note("LOADS", D["loads"])
full = rows("""SELECT route_id, trim(destination), strftime(min(t), '%a %H:%M'), strftime(max(t), '%a %H:%M'),
                      count(*), string_agg(DISTINCT equipment_no, ',' ORDER BY equipment_no)
               FROM pos WHERE occupancy_pct >= 96 GROUP BY 1, 2 ORDER BY 5 DESC, 1, 2""")
D["fullest"] = [list(x) for x in full]
note("FULLEST", D["fullest"])
lde = rows("""SELECT route_id, avg(occupancy_pct) / 2, avg((delay_seconds > 300)::int),
                     avg((delay_seconds > 300)::int) FILTER (WHERE occupancy_pct >= 40),
                     avg((delay_seconds > 300)::int) FILTER (WHERE occupancy_pct < 20),
                     count(*) FILTER (WHERE occupancy_pct >= 40)
              FROM good GROUP BY 1 ORDER BY 2 DESC, 1""")
D["load_delay"] = [{"route": r, "riders": r1(a), "late": r1(l, 3), "late_full": r1(lf, 3), "late_empty": r1(le, 3),
                    "n_full": nf} for r, a, l, lf, le, nf in lde]
cor = one("""SELECT corr(a, l) FROM (SELECT avg(occupancy_pct) AS a, avg((delay_seconds > 300)::int) AS l
                                      FROM good GROUP BY route_id)""")
D["load_delay_corr"] = r1(cor[0], 2)
note("LOAD_DELAY", D["load_delay"], "corr", D["load_delay_corr"])
rd = rows("""WITH polls AS (SELECT observed_at, any_value(t) AS t, sum(occupancy_pct) / 2 AS riders, count(*) AS buses
                           FROM pos GROUP BY observed_at)
             SELECT t::date::varchar, (hour(t) * 60 + minute(t)) // 5 * 5, avg(riders), avg(buses)
             FROM polls GROUP BY 1, 2 ORDER BY 1, 2""")
rdd = defaultdict(list)
for d, mnt, rv, bv in rd:
    rdd[d].append([mnt, r1(rv, 0), r1(bv, 1)])
D["riders_curve"] = rdd
rday = rows("""WITH polls AS (
    SELECT observed_at, any_value(t) AS t, sum(occupancy_pct) / 2 AS riders FROM pos GROUP BY observed_at),
w AS (SELECT *, least(coalesce(lead(observed_at) OVER (ORDER BY observed_at) - observed_at, 10), 30) AS secs FROM polls),
b AS (SELECT t::date AS day, greatest(occupancy_pct - lag(occupancy_pct) OVER v, 0) / 2 AS boarded,
             observed_at - lag(observed_at) OVER v AS gap
      FROM pos WINDOW v AS (PARTITION BY vehicle_id ORDER BY observed_at)),
bd AS (SELECT day, sum(boarded) FILTER (WHERE gap <= 30) AS boardings FROM b GROUP BY 1)
SELECT w.t::date::varchar, dayname(w.t::date), round(sum(riders * secs) / 3600), max(riders),
       strftime(arg_max(w.t, riders), '%H:%M'), round(any_value(bd.boardings)),
       strftime(min(w.t), '%H:%M'), strftime(max(w.t), '%H:%M')
FROM w JOIN bd ON bd.day = w.t::date GROUP BY 1, 2 ORDER BY 1""")
D["riders_day"] = [{"day": d, "dow": w, "rider_hours": rh, "peak": pk, "peak_at": pa, "boardings": bo,
                    "from": f, "to": t} for d, w, rh, pk, pa, bo, f, t in rday]
note("RIDERS_DAY", D["riders_day"])
bo = rows("""WITH d AS (
    SELECT route_id, t, lag(next_stop_name) OVER v AS stop,
           (occupancy_pct - lag(occupancy_pct) OVER v) / 2 AS change, observed_at - lag(observed_at) OVER v AS gap
    FROM pos WINDOW v AS (PARTITION BY vehicle_id ORDER BY observed_at))
SELECT stop, string_agg(DISTINCT route_id, ',' ORDER BY route_id),
       sum(greatest(change, 0)) / count(DISTINCT t::date), sum(greatest(-change, 0)) / count(DISTINCT t::date)
FROM d WHERE stop IS NOT NULL AND gap <= 30 GROUP BY stop ORDER BY 3 DESC, 1 LIMIT 12""")
D["boardings"] = [{"stop": s, "routes": r, "on": r1(a, 0), "off": r1(b, 0)} for s, r, a, b in bo]
note("BOARDINGS", D["boardings"])

# ---------------------------------------------------------------- fleet
fl = rows("""WITH polls AS (SELECT observed_at, any_value(t) AS t, count(*) AS buses FROM pos GROUP BY observed_at),
slots AS (SELECT t::date::varchar AS day, (hour(t) * 60 + minute(t)) // 15 * 15 AS slot,
                 arg_min(observed_at, (abs((hour(t) * 60 + minute(t)) % 15 * 60 + second(t) - 450), observed_at)) AS at_,
                 arg_min(buses, (abs((hour(t) * 60 + minute(t)) % 15 * 60 + second(t) - 450), observed_at)) AS buses
          FROM polls GROUP BY ALL),
trips AS (SELECT day, trip, min(t_sched) AS t0, max(t_sched) AS t1 FROM sched GROUP BY ALL)
SELECT s.day, s.slot, s.buses, count(x.trip)
FROM slots s LEFT JOIN trips x ON x.day = s.day AND s.at_ BETWEEN x.t0 AND x.t1
GROUP BY ALL ORDER BY 1, 2""")
fld = defaultdict(list)
for d, sl, b, sch in fl:
    fld[d].append([sl, b, sch])
D["fleet"] = fld

# ---------------------------------------------------------------- speed
spd = rows("""SELECT route_id, avg(speed_raw) * 2.237,
                     avg(speed_raw) FILTER (WHERE hour(t) IN (7, 8, 16, 17)) * 2.237,
                     avg(speed_raw) FILTER (WHERE hour(t) BETWEEN 10 AND 14) * 2.237, avg((speed_raw = 0)::int)
              FROM pos ANTI JOIN ghost_rows USING (vehicle_id, observed_at)
              WHERE unchanged_polls < 30 AND speed_raw <= 40 GROUP BY 1 ORDER BY 2, 1""")
D["speed_route"] = [{"route": r, "mph": r1(a), "peak": r1(p), "midday": r1(md), "stopped": r1(s, 2)}
                    for r, a, p, md, s in spd]
note("SPEED_ROUTE", D["speed_route"])
sl = rows("""WITH a AS (
    SELECT route, trip, vehicle, day, stop, t, lag(stop) OVER w AS prev_stop, lag(t) OVER w AS prev_t
    FROM arrivals_due WINDOW w AS (PARTITION BY day, trip, vehicle ORDER BY t)),
seg AS (
    SELECT a.route, s1.stop_name AS from_stop, s2.stop_name AS to_stop, a.prev_stop AS c1, a.stop AS c2,
           s1.lat AS la1, s1.lon AS lo1, s2.lat AS la2, s2.lon AS lo2,
           dist_m(s1.lat, s1.lon, s2.lat, s2.lon) AS m, a.t - a.prev_t AS secs
    FROM a JOIN stops s1 ON s1.stop_code = a.prev_stop JOIN stops s2 ON s2.stop_code = a.stop
    WHERE a.prev_t IS NOT NULL AND a.t - a.prev_t BETWEEN 10 AND 900)
SELECT route, from_stop, to_stop, count(*), avg(m), avg(secs), sum(m) / sum(secs) * 2.237,
       arg_min(la1, c1), arg_min(lo1, c1), arg_min(la2, c2), arg_min(lo2, c2)
FROM seg GROUP BY route, from_stop, to_stop HAVING count(*) >= 20 AND avg(m) >= 300
ORDER BY 7, 1, 2, 3 LIMIT 15""")
D["slow"] = [{"route": r, "from": f, "to": t, "passes": n, "m": r1(m_, 0), "secs": r1(s, 0), "mph": r1(v),
              "a": [la1, lo1], "b": [la2, lo2]} for r, f, t, n, m_, s, v, la1, lo1, la2, lo2 in sl]
note("SLOW", [(d["route"], d["from"], d["to"], d["mph"]) for d in D["slow"]])

# ---------------------------------------------------------------- headways
hw = one("""WITH a AS (
    SELECT *, lag(t) OVER w AS prev_t, lag(t_sched) OVER w AS prev_sched, lag(vehicle) OVER w AS prev_vehicle
    FROM arrivals_due WINDOW w AS (PARTITION BY day, route, stop ORDER BY t, t_sched))
SELECT count(*) FILTER (WHERE prev_sched IS NOT NULL),
       count(*) FILTER (WHERE t_sched < prev_sched AND vehicle <> prev_vehicle),
       count(*) FILTER (WHERE prev_t IS NOT NULL AND vehicle <> prev_vehicle AND t_sched > prev_sched
                          AND t - prev_t < (t_sched - prev_sched) / 4),
       count(*) FILTER (WHERE prev_t IS NOT NULL AND vehicle <> prev_vehicle AND t_sched > prev_sched
                          AND t - prev_t > (t_sched - prev_sched) * 1.5),
       count(*) FILTER (WHERE prev_t IS NOT NULL AND vehicle <> prev_vehicle AND t_sched > prev_sched)
FROM a""")
D["headway"] = {"pairs": hw[0], "overtakes": hw[1], "bunched": hw[2], "gaps": hw[3], "valid_pairs": hw[4]}
hwr = rows("""WITH a AS (
    SELECT *, lag(t) OVER w AS prev_t, lag(t_sched) OVER w AS prev_sched, lag(vehicle) OVER w AS prev_vehicle
    FROM arrivals_due WINDOW w AS (PARTITION BY day, route, stop ORDER BY t, t_sched)),
pairs AS (SELECT route, t - prev_t AS actual, t_sched - prev_sched AS planned FROM a
          WHERE prev_t IS NOT NULL AND vehicle <> prev_vehicle AND t_sched > prev_sched)
SELECT route, count(*), median(planned) / 60, avg((actual > planned * 1.5)::int),
       (sum(actual * actual) / (2 * sum(actual)) - sum(planned * planned) / (2 * sum(planned))) / 60
FROM pairs GROUP BY route ORDER BY 5 DESC, 1""")
D["headway_route"] = [{"route": r, "pairs": n, "planned": r1(p, 0), "gaps": r1(g, 3), "excess": r1(e)}
                      for r, n, p, g, e in hwr]
note("HEADWAY", D["headway"], D["headway_route"])

# ---------------------------------------------------------------- missed service
bar = rows("""SELECT day, route, hour(to_timestamp(due) AT TIME ZONE 'America/Chicago') * 60
                                + minute(to_timestamp(due) AT TIME ZONE 'America/Chicago'),
                     ran::int, canceled::int, trim(headsign)
              FROM trip_service ORDER BY 1, 2, 3, 6, 4, 5""")
D["barcode"] = [list(x) for x in bar]
mt = rows("""SELECT day, count(*), count(*) FILTER (WHERE NOT ran), count(*) FILTER (WHERE NOT ran AND canceled),
                    count(*) FILTER (WHERE ran AND canceled),
                    strftime(to_timestamp(max(due)) AT TIME ZONE 'America/Chicago', '%H:%M')
             FROM trip_service GROUP BY 1 ORDER BY 1""")
D["missed_days"] = [{"day": d, "scheduled": s, "never": n, "canceled": c, "ran_canceled": rc, "due_by": db}
                    for d, s, n, c, rc, db in mt]
note("MISSED_DAYS", D["missed_days"])
mr = rows("""SELECT day, route, count(*), count(*) FILTER (WHERE NOT ran), count(*) FILTER (WHERE NOT ran AND canceled)
             FROM trip_service GROUP BY ALL ORDER BY 1, 4 DESC, 2""")
note("MISSED_ROUTES", mr)
mh = rows("""SELECT hour(to_timestamp(due) AT TIME ZONE 'America/Chicago'), count(*), count(*) FILTER (WHERE NOT ran)
             FROM trip_service GROUP BY 1 ORDER BY 1""")
D["missed_hour"] = [[h, s, n] for h, s, n in mh]
note("MISSED_HOUR", D["missed_hour"])
ag = one(f"""WITH ours AS (
    SELECT DISTINCT trip FROM arrivals WHERE day = '{FEED_DAY}' AND trip IS NOT NULL
    UNION SELECT DISTINCT trip_id FROM pos WHERE trip_id IS NOT NULL AND strftime(t, '%Y-%m-%d') = '{FEED_DAY}'),
official AS (
    SELECT DISTINCT trip_id AS trip FROM off_vehicles WHERE day = '{FEED_DAY}' AND trip_id IS NOT NULL
    UNION SELECT DISTINCT trip_id FROM off_trip_updates WHERE day = '{FEED_DAY}' AND vehicle_id IS NOT NULL),
t AS (SELECT trip FROM trip_service WHERE day = '{FEED_DAY}'
      AND due >= (SELECT min(feed_ts) FROM off_vehicles) + 900)
SELECT count(*), count(*) FILTER (WHERE o.trip IS NOT NULL),
       count(*) FILTER (WHERE o.trip IS NOT NULL AND u.trip IS NOT NULL),
       count(*) FILTER (WHERE o.trip IS NULL AND u.trip IS NOT NULL)
FROM t LEFT JOIN ours u USING (trip) LEFT JOIN official o USING (trip)""")
D["agree"] = {"scheduled": ag[0], "official_ran": ag[1], "both": ag[2], "ours_only": ag[3]}
note("AGREE", D["agree"])
al = one(f"""SELECT count(DISTINCT id), count(DISTINCT routes) FROM off_alerts
            WHERE strftime(to_timestamp(feed_ts) AT TIME ZONE 'America/Chicago', '%Y-%m-%d') = '{FEED_DAY}'""")
D["alerts"] = {"alerts": al[0]}
note("ALERTS", al)

# ---------------------------------------------------------------- trip matching, coverage
tm = rows("""WITH o AS (
    SELECT DISTINCT vehicle_id AS equipment_no, reported_at, trip_id AS off_trip
    FROM off_vehicles WHERE trip_id IS NOT NULL AND reported_at IS NOT NULL),
m AS (
    SELECT o.*, p.trip_id AS our_trip, p.route_id, p.next_stop_name, p.delay_capped
    FROM o JOIN pos p ON p.equipment_no = o.equipment_no
                     AND p.observed_at BETWEEN o.reported_at - 60 AND o.reported_at + 60
    QUALIFY row_number() OVER (PARTITION BY o.equipment_no, o.reported_at ORDER BY abs(p.observed_at - o.reported_at)) = 1)
SELECT count(*), avg((our_trip = off_trip)::int), avg((our_trip IS NULL)::int),
       count(*) FILTER (WHERE our_trip <> off_trip),
       count(*) FILTER (WHERE our_trip IS NULL AND next_stop_name IS NULL),
       count(*) FILTER (WHERE our_trip IS NULL AND delay_capped)
FROM m""")[0]
D["tripmatch"] = {"compared": tm[0], "same": r1(tm[1], 4), "none": r1(tm[2], 3), "different": tm[3],
                  "none_no_next": tm[4], "none_capped": tm[5]}
note("TRIPMATCH", D["tripmatch"])
cov = one("""WITH ran AS (
    SELECT day, route, trip, min(t_sched) AS first_due, max(t_sched) AS last_due, count(DISTINCT stop) AS logged
    FROM arrivals_due GROUP BY ALL),
due AS (
    SELECT r.day, r.trip, r.logged, count(DISTINCT s.stop) AS scheduled
    FROM ran r JOIN sched s ON s.day = r.day AND s.route = r.route AND s.trip = r.trip
                           AND s.t_sched BETWEEN r.first_due AND r.last_due
    GROUP BY ALL)
SELECT sum(logged) / sum(scheduled) FROM due""")
D["coverage"] = r1(cov[0], 3)
note("COVERAGE", D["coverage"])

# ---------------------------------------------------------------- stop wait, predictions, layovers
sw = rows("""WITH trip_delay AS (SELECT day, trip, median(delay) AS d FROM arrivals_due GROUP BY ALL),
dep AS (
    SELECT s.day, s.route, s.stop, coalesce(a.t, s.t_sched + coalesce(td.d, 0)) AS t_dep
    FROM sched s
    JOIN trip_service ts ON ts.day = s.day AND ts.trip = s.trip AND ts.ran
    LEFT JOIN arrivals_due a ON a.day = s.day AND a.trip = s.trip AND a.stop = s.stop AND a.t_sched = s.t_sched
    LEFT JOIN trip_delay td ON td.day = s.day AND td.trip = s.trip),
calls AS (
    SELECT s.day, s.route, s.stop, s.t_sched FROM sched s
    JOIN timepoints tp USING (route, stop)
    ANTI JOIN line_ends e ON e.route = s.route AND e.stop = s.stop
    JOIN trip_service ts ON ts.day = s.day AND ts.trip = s.trip),
w AS (
    SELECT c.route, d.t_dep - (c.t_sched - 120) AS wait
    FROM calls c ASOF LEFT JOIN dep d
      ON d.day = c.day AND d.route = c.route AND d.stop = c.stop AND d.t_dep >= c.t_sched - 120)
SELECT coalesce(route, 'all'), count(*), median(wait) / 60, quantile_cont(wait, 0.25) / 60,
       quantile_cont(wait, 0.75) / 60, quantile_cont(wait, 0.9) / 60, avg((wait > 900)::int),
       count(*) FILTER (WHERE wait IS NULL)
FROM w GROUP BY ROLLUP (route) ORDER BY 3 DESC, 1""")
D["wait"] = [{"route": r, "calls": n, "median": r1(md), "p25": r1(a), "p75": r1(b), "p90": r1(c, 0),
              "over15": r1(o15, 3), "stranded": st} for r, n, md, a, b, c, o15, st in sw]
note("WAIT", D["wait"])
pf = rows("""WITH pr AS (
    SELECT day, feed_ts, trip_id AS trip, unnest(stops, max_depth := 2)
    FROM off_trip_updates WHERE vehicle_id IS NOT NULL),
j AS (
    SELECT pr.feed_ts, coalesce(pr.departure, pr.arrival) AS predicted, a.t AS actual
    FROM pr JOIN arrivals a ON a.day = pr.day AND a.trip = pr.trip AND '0:' || a.stop = pr.stop_id
    WHERE coalesce(pr.departure, pr.arrival) >= pr.feed_ts AND a.t >= pr.feed_ts)
SELECT (predicted - feed_ts) // 300 AS b, count(*),
       quantile_cont(actual - predicted, [0.1, 0.25, 0.5, 0.75, 0.9]),
       avg((abs(actual - predicted) <= 120)::int), avg((actual - predicted < -60)::int),
       avg((actual - predicted > 300)::int)
FROM j WHERE predicted - feed_ts < 3600 GROUP BY 1 ORDER BY 1""")
D["predict"] = [{"lead": int(b) * 5 + 2.5, "n": n, "q": [r1(x / 60, 2) for x in q], "within2": r1(w2, 3),
                 "early1": r1(e1, 3), "late5": r1(l5, 3)} for b, n, q, w2, e1, l5 in pf]
pb = rows("""WITH pr AS (
    SELECT day, feed_ts, trip_id AS trip, unnest(stops, max_depth := 2)
    FROM off_trip_updates WHERE vehicle_id IS NOT NULL),
j AS (
    SELECT pr.feed_ts, coalesce(pr.departure, pr.arrival) AS predicted, a.t AS actual
    FROM pr JOIN arrivals a ON a.day = pr.day AND a.trip = pr.trip AND '0:' || a.stop = pr.stop_id
    WHERE coalesce(pr.departure, pr.arrival) >= pr.feed_ts AND a.t >= pr.feed_ts)
SELECT CASE WHEN predicted - feed_ts < 300 THEN '0-5' WHEN predicted - feed_ts < 600 THEN '5-10'
            WHEN predicted - feed_ts < 1200 THEN '10-20' WHEN predicted - feed_ts < 2400 THEN '20-40' ELSE '40+' END,
       count(*), avg((abs(actual - predicted) <= 120)::int), avg((actual - predicted < -60)::int),
       avg((actual - predicted > 300)::int), median(actual - predicted) / 60
FROM j GROUP BY 1 ORDER BY min(predicted - feed_ts)""")
D["predict_buckets"] = [{"bucket": b, "n": n, "within2": r1(w, 3), "early1": r1(e, 3), "late5": r1(l, 3),
                         "median": r1(md, 1)} for b, n, w, e, l, md in pb]
note("PREDICT", D["predict_buckets"])
lo = rows("""WITH first_stop AS (SELECT day, trip, arg_min(stop, t_sched) AS stop FROM sched GROUP BY ALL),
sat AS (
    SELECT v.day, v.trip_id AS trip, (max(v.feed_ts) - min(v.feed_ts)) / 60 AS minutes
    FROM off_vehicles v JOIN first_stop f ON f.day = v.day AND f.trip = v.trip_id AND v.stop_id = '0:' || f.stop
    WHERE v.stop_status = 'STOPPED_AT' GROUP BY v.day, v.trip_id),
start AS (SELECT day, trip, arg_min(delay, t) AS delay FROM arrivals_due GROUP BY ALL)
SELECT count(*), median(s.minutes), avg((s.minutes < 5)::int),
       avg((d.delay > 300)::int) FILTER (WHERE s.minutes < 5), avg((d.delay > 300)::int) FILTER (WHERE s.minutes >= 5)
FROM sat s LEFT JOIN start d USING (day, trip)""")[0]
D["layover"] = {"trips": lo[0], "median": r1(lo[1], 0), "under5": r1(lo[2], 2), "late_short": r1(lo[3], 2),
                "late_long": r1(lo[4], 2)}
note("LAYOVER", D["layover"])

# ---------------------------------------------------------------- map: network, simplified, in metres
LAT0, LON0 = 35.12, -89.95
KX, KY = math.cos(math.radians(LAT0)) * 111320, 110540


def xy(lon, lat):
    return (round((lon - LON0) * KX), round((lat - LAT0) * KY))


g = json.loads((REPO / "network.geojson").read_text(encoding="utf-8"))
segs = set()
for f in g["features"]:
    if f["geometry"]["type"] != "MultiLineString":
        continue
    for line in f["geometry"]["coordinates"]:
        pts = [xy(*c) for c in line]
        for a, b in zip(pts, pts[1:]):
            if a != b:
                segs.add((min(a, b), max(a, b)))
adj = defaultdict(set)
for a, b in segs:
    adj[a].add(b)
    adj[b].add(a)
used = set()
lines = []


def walk(a, b):
    path = [a, b]
    used.add((min(a, b), max(a, b)))
    while len(adj[path[-1]]) == 2:
        nxt = [n for n in adj[path[-1]] if (min(path[-1], n), max(path[-1], n)) not in used]
        if not nxt:
            break
        used.add((min(path[-1], nxt[0]), max(path[-1], nxt[0])))
        path.append(nxt[0])
    return path


for node in list(adj):
    if len(adj[node]) != 2:
        for n in adj[node]:
            if (min(node, n), max(node, n)) not in used:
                lines.append(walk(node, n))
for a, b in segs:
    if (a, b) not in used:
        lines.append(walk(a, b))


def dp(pts, tol):
    if len(pts) < 3:
        return pts
    (x1, y1), (x2, y2) = pts[0], pts[-1]
    dx, dy = x2 - x1, y2 - y1
    den = math.hypot(dx, dy) or 1
    best, bi = -1, 0
    for i in range(1, len(pts) - 1):
        d = abs(dy * (pts[i][0] - x1) - dx * (pts[i][1] - y1)) / den
        if d > best:
            best, bi = d, i
    if best <= tol:
        return [pts[0], pts[-1]]
    return dp(pts[:bi + 1], tol)[:-1] + dp(pts[bi:], tol)


net = []
npts = 0
for ln in lines:
    s = dp(ln, 12)
    npts += len(s)
    net.append([c for p in s for c in p])
D["network"] = net
D["map_origin"] = [LAT0, LON0, KX, KY]
note("NETWORK lines", len(net), "points", npts)

# ---------------------------------------------------------------- route table
routes = sorted({d["route"] for d in D["q1"]}, key=lambda r: int(r))
missed_by_route = defaultdict(lambda: [0, 0])
for day, route, s, nr, c in mr:
    missed_by_route[route][0] += s
    missed_by_route[route][1] += nr
dep_by_route = defaultdict(list)
for r, x in dep:
    dep_by_route[r].append(x)
q1m = {d["route"]: d for d in D["q1"]}
waitm = {d["route"]: d for d in D["wait"]}
loadm = {d["route"]: d for d in D["loads"]}
tab = []
for r in routes:
    dl = dep_by_route.get(r, [])
    tab.append({"route": r, "scheduled": missed_by_route[r][0], "never": missed_by_route[r][1],
                "late": q1m[r]["late"], "early": q1m[r]["early"], "on_time": q1m[r]["on_time"],
                "dep_n": len(dl), "dep_on_time": r1(sum(-1 <= x <= 5 for x in dl) / len(dl), 3) if dl else None,
                "wait": waitm.get(r, {}).get("median"), "wait_over15": waitm.get(r, {}).get("over15"),
                "riders": loadm[r]["avg"], "p95": loadm[r]["p95"]})
D["route_table"] = tab
names = {f["properties"]["route_id"]: f["properties"]["name"] for f in g["features"]
         if f["geometry"]["type"] == "MultiLineString"}
D["route_names"] = names

(OUT / "page_data.json").write_text(json.dumps(D, separators=(",", ":")), encoding="utf-8")
(OUT / "numbers.txt").write_text("\n\n".join(N), encoding="utf-8")
print(f"{OUT / 'page_data.json'}: {(OUT / 'page_data.json').stat().st_size // 1024} KB; {len(N)} number blocks")
