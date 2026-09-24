# MATA bus feed — design

## Purpose

Continuously record where every MATA (Memphis) bus is, show it on a live map,
and keep enough history to answer questions like:

1. Which routes constantly run behind?
2. Which days are especially bad?
3. How many people are riding right now?

Guiding rule: **the fewest moving parts that answer those questions.** One
process collects, one folder stores, one HTML page shows, one SQL file
analyzes. No database server, no web framework, no build step, no test suite
beyond the existing `--sample` offline check.

## Data source

MATA's public bus tracker (the "SWIV" site) is fed by a vendor system called
CADAVL. Its JSON endpoints are unauthenticated and stateless — no cookies,
tokens, or keys. Everything below was confirmed against live traffic; details
live in the docstrings of the scripts.

| Endpoint | What it is | Size / cadence | Used for |
|---|---|---|---|
| `/topo/vehicules` | Every bus: position, heading, speed, next stop, schedule adherence ("4 min late"), passenger load ("30%") | ~12 KB, refreshes every 10 s | The poller — the only thing hit continuously |
| `/topo` | Full network: 25 lines, ~3,700 stops | ~28 MB, changes rarely | `routes.csv` / `stops.csv` crosswalk |
| `/config/version` | Integer that bumps when `/topo` changes | tiny | Know when to rebuild the crosswalk |
| `/topo/refresh` | Current detours (bypassed and replacement segments) | ~385 KB, changes over days | Optional detour overlay |
| `/iv/message` | Rider-facing alert text | small | Optional detour overlay |

Known limits of the vehicle payload, which shape the design:

- **No server timestamp.** `observed_at` is *our* fetch time. A bus whose
  coordinates don't change across many polls is a dropped GPS feed (a "ghost"),
  not a parked bus; `unchanged_polls` counts that.
- **No trip or block ID.** We know the route and headsign, not which scheduled
  trip a bus is on. Delay is whatever the vendor reports (`avanceRetard`), not
  something we compute.
- **Delay is capped.** `"1h+ late"` means "at least an hour", flagged
  `delay_capped`. Those rows are usually misassigned buses; exclude them.
- **Line IDs are opaque.** Internal `idLigne` (e.g. 109149) maps to route
  "01" only by lookup, and the lookup changes when MATA restructures service.
- **Speed unit unknown.** `vitesse` ranges 0–20; `probe_cadence.py` can settle
  whether it's mph or km/h. Not needed for any of the three questions.
- **Load is a percentage** of an unknown capacity, presumably from the bus's
  automatic passenger counters. Treat rider counts as estimates.

## Architecture

```
                 every 10 s
 CADAVL ───────────────────▶  cadavl_to_gtfs_rt.py  (poller, one process)
                                      │
                                      ├─▶ data/positions/dt=YYYY-MM-DD/positions.jsonl.gz   history (append)
                                      ├─▶ data/latest.json                                  current snapshot
                                      ├─▶ data/replay/YYYY-MM-DD.jsonl                       one frame per 30 s, for replay
                                      └─▶ data/vehicle_positions.pb                         GTFS-RT feed

 map.html  ── fetches data/latest.json every 10 s ──▶  live map      (served by python -m http.server)
 analysis.sql ── DuckDB reads data/positions/*/*.jsonl.gz ──▶  the three questions
 routes.csv / stops.csv ── built once by build_crosswalk.py ──▶  names and colors
```

Four files do the work: the poller, the map page, the SQL file, and the
crosswalk builder. Everything else in the repo is optional or a one-off probe.

## Components

### 1. Poller — `cadavl_to_gtfs_rt.py`

Runs forever under systemd. Each cycle, during service hours (04:00–24:00
local): fetch `/topo/vehicules`, normalize each bus into a flat row, then
write three things.

**History — one row per bus per poll.** This is a change from the current
code, which archives the raw payload separately and writes a position row only
when something changed. The simpler model wins on every axis:

- Every row represents the same 10 s of bus-time, so plain `AVG()` in SQL is
  already time-weighted. No forward-filling, no "was this bus still in the
  feed?" logic.
- "Right now" is just the latest poll.
- The raw archive and the dedupe set (`seen`, `position_key`) are deleted —
  the normalized row already keeps every field the vendor sends.

Cost (measured): 68 B per bus-poll gzipped, so a 30-bus average over the
20-hour service day is ~18 MB/day and a full 41-bus day ~24 MB; call it
6–9 GB/year. The replay frames add ~5–7 MB/day (~2 GB/year) and the log
~0.3 MB/day. Acceptable on any disk. If it ever matters, compact old days to
Parquet with one DuckDB `COPY` — not now.

**Snapshot — `data/latest.json`.** The same rows for the current poll plus
`fetched_at`, written atomically (tmp file + rename). The map reads this; so
does the "right now" query.

**Replay — `data/replay/<local day>.jsonl`.** Every third poll (30 s) one
compact line: the poll time and, per bus, `[id, route, lat, lon, bearing,
delay_seconds, delay_capped, occupancy_pct, unchanged_polls]`. 59 B per bus
per frame, ~5–7 MB for a full day. The map loads the viewed day's file once; it drives both the
replay scrubber and the trails (so trails are there the moment the page
opens, not five minutes after the poller starts).

**GTFS-RT — `data/vehicle_positions.pb`.** Already implemented; ~30 lines and
one dependency. Kept because it is the standard interchange format, but
nothing in this project consumes it. Delete it and `gtfs-realtime-bindings`
if it ever gets in the way.

Small cleanups to make while touching the file:

- Load the `idLigne → route` mapping and colors from `routes.csv` at startup
  instead of the hardcoded `LINE_TO_ROUTE_ID` / `ROUTE_NAMES` dicts, so a
  crosswalk rebuild is the only step when MATA changes service.
- Keep `StaleTracker` (ghost detection) and `parse_delay` as they are.

### 2. Crosswalk — `build_crosswalk.py`

Run `python build_crosswalk.py --fetch` when the poller starts logging
`route_id = cadavl:<n>` (an unmapped line), which is the signal that
`/config/version` bumped. Commit the results. No scheduler needed; MATA
restructures a few times a year (every line ID changed between August and
September 2026).

Besides `routes.csv` and `stops.csv` it writes `network.geojson`: one
MultiLineString per route, built from the 2-point segments in `/topo`,
de-duplicated across a route's direction/branch variants and rounded to 5
decimals, plus one Point per stop with its name. Just under 1 MB; the map
draws it as the background.

### 3. Live map — `map.html`

One static page, Leaflet from a CDN, no build step. It fetches
`data/latest.json` every 10 s, the day's `data/replay/` file once, and
`network.geojson` once. Visual-first: the
picture carries the information and text is confined to a tooltip and a
three-number strip. All text is Inter (Google Fonts) at 16 px (12 pt) or
larger, including the route numbers inside the markers.

Encodings, per bus:

- **Fill = schedule adherence**, in tiers: early (blue), on time (grey, so
  problems stand out), 5+ / 10+ / 20+ min late (yellow → orange → red, the
  status palette). `"1h+"` capped values count as 20+.
- **Size = passenger load** (`occupancy_pct`), radius 9–16 px.
- **Number = route**, a wedge on the rim = heading.
- **Trail** = the five minutes of positions before the viewed moment (from
  the replay frames), in the tier color, one segment per pair: bright,
  thick and solid where the bus just was, darker, thinner and fainter as it
  ages.
- **Ghost** (`unchanged_polls` ≥ 30) = dashed hollow circle, no wedge.
- Late buses are stacked on top of on-time ones.

Around it: the whole network as hairlines and every stop as a small hollow
dot (larger at higher zoom, hover for its name) — visible but clearly
subordinate to the buses; click a bus and its route highlights while the
rest dims (click the map to clear). Hover for route,
headsign, delay text, load, fleet number. Top-right: buses in service, buses
5+ min late, estimated riders (`CAPACITY = 40`). A dot goes red when the
snapshot is older than 90 s. Bottom-left legend. Bottom bar: play/pause,
a scrubber across the day's frames, the clock, replay speed (10× / 60× /
300× real time), LIVE, and a date picker for earlier days — so any moment
of any recorded day can be revisited and played forward, with the same
encodings and trails. The OSM basemap is muted
with a CSS filter so the data reads on top; dark mode inverts it and follows
the OS setting.

Served by `python -m http.server` from the repo root — browsers block
`fetch()` on `file://` URLs, so a server is required, but that one command
is all of it.

### 4. Analysis — `analysis.sql` (new)

DuckDB is an in-process analytical database: a single binary (or `pip install
duckdb`) that queries files directly, so there is nothing to load, no schema
to maintain, and no server. It reads the gzipped JSONL partitions in one
call and picks up the `dt=` folder name as a column. Run with
`duckdb < analysis.sql`.

```sql
-- All history, with local (Central) time.
CREATE VIEW pos AS
SELECT *,
       to_timestamp(observed_at) AT TIME ZONE 'America/Chicago' AS t
FROM read_json_auto('data/positions/*/positions.jsonl.gz', hive_partitioning = true);

-- Rows worth trusting: a delay was reported, it isn't a "1h+" cap,
-- and the GPS fix has moved in the last five minutes.
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
-- CAPACITY is a placeholder; see open questions.
SELECT count(*)                                         AS buses_in_service,
       round(sum(occupancy_pct) / 100.0 * 40)           AS riders_est
FROM read_json_auto('data/latest.json')
WHERE unchanged_polls < 30;
```

Variations (by hour of day, by route × weekday, riders over the day) are the
same queries with a different `GROUP BY`. Add them to the file as they are
needed; don't pre-build them.

### 5. Detours — `cadavl_detours.py` (optional, deferred)

Already parses `/topo/refresh` into GeoJSON lines and a GTFS-RT alerts feed.
Not required for any of the three questions. If wanted later: hourly cron
writes `data/detours.geojson`, and `map.html` draws it as a second layer.
Nothing to do now.

### 6. Probes — `probe_cadence.py`

One-off diagnostic. Run it once during service hours to settle the speed
unit, set `SPEED_UNIT`, and forget about it.

## Data model

One row per bus per poll in `data/positions/dt=YYYY-MM-DD/positions.jsonl.gz`
(`dt` is the UTC date of the fetch; convert `observed_at` to local time in
queries rather than renaming partitions).

| Field | Type | Notes |
|---|---|---|
| `observed_at` | int, Unix seconds | Fetch time, not report time |
| `vehicle_id` | str | Vendor ID; stable per bus |
| `equipment_no` | str | Fleet number painted on the bus |
| `vehicle_type` | str | "Bus"; trolleys may differ |
| `line_internal_id` | int | Vendor line ID |
| `route_id` | str | MATA route number ("01"), or `cadavl:<id>` if unmapped |
| `route_color` | str | Hex from `routes.csv`; for the map |
| `lat`, `lon` | float | |
| `bearing` | int | Degrees 0–360 |
| `speed_raw` | int | Unit unconfirmed |
| `occupancy_pct` | int | Passenger load, percent of unknown capacity |
| `destination` | str | Headsign |
| `next_stop_name` | str | Display name, not a GTFS stop_id |
| `next_stop_eta_min` | int | |
| `delay_seconds` | int | Positive = late; `0` = "on time"; null if unparseable |
| `delay_raw` | str | Vendor text, e.g. "4 min late" |
| `delay_capped` | bool | True for "1h+" values — a floor, not a measurement |
| `unchanged_polls` | int | Consecutive polls with identical coordinates; ghost signal |

## Running it

An always-on Windows machine at home. Chosen over the cloud free tiers:
Google's e2-micro is free but its external IP is ~$3.65/month, Oracle's is
$0 but has signup and idle-reclamation caveats, and a home box costs a few
dollars a year in power. Needs are tiny: one 12 KB request every 10 s,
~15 MB/day of disk.

Everything runs natively (Python, `http.server`, DuckDB); only "keep it
running" is Windows-specific, and Task Scheduler does that. Install once
from an administrator PowerShell in the repo folder, with Python 3.10+ on
PATH:

    Set-ExecutionPolicy -Scope Process Bypass
    .\ops\setup.ps1

It makes the venv from `requirements.txt` (`requests`,
`gtfs-realtime-bindings`, `duckdb`), registers two scheduled tasks that
start at boot with nobody logged in and restart a minute after any crash,
and opens port 8000 to the home LAN and Tailscale only:

- `mata-poller` — `python -u cadavl_to_gtfs_rt.py`, output appended to
  `data\poller.log` (a few hundred KB per day; delete it whenever).
- `mata-web` — `python -m http.server 8000`; the map is at
  `http://localhost:8000/map.html`.

After pulling new code, `.\ops\update.ps1` (same admin PowerShell) pulls,
reinstalls requirements if they changed, and restarts both tasks.

The machine's clock is already Central time, so the service-hours check
needs no time-zone setting. Do set Power settings to never sleep (and, on
a laptop, "do nothing" on lid close, plugged in).

Reaching the map away from home: install Tailscale (free for personal use)
on the machine and your phone. It makes a private network between your own
devices, so `http://<machine-name>:8000/map.html` works anywhere with no
router ports opened and nothing exposed to the internet. Don't port-forward
8000 instead; `http.server` is not meant to face the public internet.

Analysis on Windows: download the DuckDB CLI (`duckdb.exe`, a single file)
and run `Get-Content analysis.sql | .\duckdb.exe` from the repo folder.

Git tracks code, the crosswalk outputs (`routes.csv`, `stops.csv`,
`network.geojson`), `vehicules.json` (the sample payload for `--sample`), and
this document. `data/` and the raw `topo.json` are ignored.

Failure modes and the response to each:

- Vendor down or slow → the poller logs and retries next cycle. Gaps in the
  history are just missing rows.
- Machine reboots → Task Scheduler restarts both tasks; the day file is appended,
  not overwritten.
- MATA changes routes → unmapped lines show as `cadavl:<id>`; rebuild the
  crosswalk. Old rows keep their old `route_id`, which is correct.
- Vendor changes the JSON shape → `normalize_vehicle` returns nothing useful;
  the `--sample` check against a freshly saved payload is the debugging tool.

## Implementation plan

Steps 1–4 are done. Each left the project working; net line count went down.

1. **Poller.** Read `routes.csv` at startup; write all rows every poll; write
   `latest.json`; delete raw archive, dedupe set, and the two hardcoded dicts.
2. **Map.** Add `map.html`; delete `plot_bus_map.py` and `bus_map.html`.
3. **Analysis.** Add `analysis.sql` with the three queries above.
4. **Ops.** Add `requirements.txt`, the two unit files under `ops/`, and
   `.gitignore` entries for generated files. Deploy and let it run.
5. **After a week of data:** run the queries, sanity-check against personal
   experience of the routes, then decide the open questions below.

## Open questions

- **Bus capacity.** `occupancy_pct` is a percentage of something. A constant
  of 40 riders at 100% is a reasonable first guess for a 40-foot bus; the
  right value may vary by `equipment_no` (fleet number), and the trolley is
  different. Until confirmed, ridership figures are relative, not absolute.
- **Ghost threshold.** 30 unchanged polls (five minutes) is a guess. A bus
  at a layover legitimately sits still that long; check how many rows the
  filter drops per route before trusting it.
- **Late threshold.** Five minutes is the usual transit-industry cutoff for
  "late". Adjust if MATA publishes its own on-time standard.
- **Speed unit.** Only matters if the GTFS-RT feed gets a consumer.

## Non-goals

- Schedule comparison (matching buses to GTFS trips). The vendor already
  reports delay; computing our own would need the static GTFS and a lot of
  code for a marginally better number.
- Multi-agency support, a REST API, user accounts, alerting, dashboards
  beyond the one map page and the SQL file.
- Unit tests. The offline `--sample` run against `vehicules.json` is the
  regression check; if the parser changes, run it.
