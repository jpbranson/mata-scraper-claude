"""The findings page's driver-change section, from a copy of data/ that
covers weeks rather than the page's two days (made like snapshot.py's;
never the live files). Runs analysis.sql's [RELIEF] query for the trips
where route 42 changes drivers at the garage, and times every southbound
route 42 pass of the garage the same way, for the chart.
Writes out/relief.json; build_page.py puts it in the page as D.relief.

    .venv\\Scripts\\python findings_page\\relief_data.py SNAPSHOT_DIR
"""
import json
import os
import pathlib
import re
import sys

import duckdb

HERE = pathlib.Path(__file__).resolve().parent
REPO = HERE.parent
SNAP = pathlib.Path(sys.argv[1]).resolve()
OUT = HERE / "out"

OUT.mkdir(exist_ok=True)
os.chdir(SNAP)          # analysis.sql reads data/... and stops.csv relative to here
con = duckdb.connect()
sql = (REPO / "analysis.sql").read_text(encoding="utf-8")
for chunk in re.split(r";[ \t]*\r?\n", sql):
    body = "\n".join(l for l in chunk.strip().splitlines() if not l.strip().startswith("--")).strip()
    if re.match(r"(?i)create\b", body):
        con.sql(body)
relief_q = re.search(r"-- \[RELIEF\].*?(?=;[ \t]*\r?\n)", sql, re.S).group(0)

# The trips [RELIEF] finds, route 42 southbound (the only ones it finds).
rel = con.sql(relief_q)
relief = [dict(zip(rel.columns, r)) for r in rel.fetchall()]
assert all(r["route"] == "42" and r["destination"] == "AIRWAYS TRANSIT" for r in relief), relief
key = {(r["service"], r["trip_starts"]) for r in relief}

# Every southbound route 42 pass of the garage, timed as [RELIEF] times them.
passes = con.sql("""
    WITH p AS (
        SELECT trip_id, t, observed_at, delay_seconds, occupancy_pct
        FROM pos
        WHERE route_id = '42' AND destination = 'AIRWAYS TRANSIT' AND trip_id IS NOT NULL
          AND NOT delay_capped AND dist_m(lat, lon, 35.1755, -90.0090) < 450),
    starts AS (
        SELECT trip, min(hm) AS hm
        FROM (SELECT trip, strftime(to_timestamp(min(t_sched)) AT TIME ZONE 'America/Chicago', '%H:%M') AS hm
              FROM sched GROUP BY day, trip)
        GROUP BY trip)
    SELECT regexp_extract(p.trip_id, '^(.*?)[0-9]+$', 1) AS service, p.t::date::varchar AS day, s.hm,
           hour(min(p.t)) * 60 + minute(min(p.t))               AS at_min,
           (max(p.observed_at) - min(p.observed_at)) / 60       AS minutes,
           arg_min(p.delay_seconds, p.observed_at) / 60          AS delay_in,
           arg_max(p.delay_seconds, p.observed_at) / 60          AS delay_out,
           median(p.occupancy_pct) / 2                           AS riders
    FROM p LEFT JOIN starts s ON s.trip = p.trip_id
    GROUP BY p.trip_id, p.t::date, s.hm
    ORDER BY 1, 2, 4""").fetchall()

SERVICE = {"0_Weekday": "weekday", "2-Sat": "saturday", "3-Sun": "sunday"}
D = {
    "window": dict(zip(["first", "last"], con.sql(
        "SELECT strftime(min(t), '%Y-%m-%d %H:%M'), strftime(max(t), '%Y-%m-%d %H:%M') FROM pos").fetchone())),
    "days": {SERVICE[s]: len({p[1] for p in passes if p[0] == s}) for s in SERVICE},
    # service, day, trip start, minute of day at the garage, minutes there,
    # delay in and out (min), riders, a driver-change trip
    "passes": [[SERVICE.get(s, s), d, hm, at, round(mi, 1), din, dout, round(rid), (s, hm) in key]
               for s, d, hm, at, mi, din, dout, rid in passes],
    "trips": [{"service": SERVICE.get(r["service"], r["service"]), "starts": r["trip_starts"], "days": r["days"],
               "usual": r["usual_min"], "median": r["median_min"], "gained": r["median_min_gained"],
               "share": r["share_relief"]} for r in relief],
}
(OUT / "relief.json").write_text(json.dumps(D, separators=(",", ":")), encoding="utf-8")
print(f"{OUT / 'relief.json'}: {len(D['passes'])} passes, {len(D['trips'])} driver-change trips, {D['window']}")
