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
| `/horaires/pta/<stop id>` | The tracker's own stop popup: next one or two times per route | small | Nothing (no CORS, so the page can't call it; kept as a cross-check) |
| `gtfs.mata.cadavl.com/MATA/GTFS/GTFS_MATA.zip` | MATA's published timetable (GTFS), same vendor | ~1.5 MB, rebuilt nightly | Stop schedules and trip matching (`schedule.py`) |

The GTFS feed lines up with the tracker exactly: GTFS `stop_id` is `"0:"` +
the tracker's stop code (`mnemoPointArret`, `stop_code` in `stops.csv`),
`route_id` is the route number, and `trip_headsign` is the bus's
`destination`, trailing spaces and all. The vendor's delay is measured
against this timetable (checked: a bus "8 min late" at LAMAR @LAPALOMA at
18:01 is the 17:52:59 trip).

Known limits of the vehicle payload, which shape the design:

- **No server timestamp.** `observed_at` is *our* fetch time. A bus whose
  coordinates don't change across many polls is a dropped GPS feed (a "ghost"),
  not a parked bus; `unchanged_polls` counts that.
- **No trip or block ID.** We know the route and headsign, not which scheduled
  trip a bus is on; `schedule.py` infers it (see below). Delay is whatever
  the vendor reports (`avanceRetard`), not something we compute. The GTFS
  timetable does carry `block_id`, and a few blocks interline: weekday
  blocks 4001 and 4002 (and their weekend twins) alternate a route 13 round
  trip with a route 40 one from William Hudson, so those buses change route
  every couple of hours. That's real, not mislabelling; follow a bus by
  `vehicle_id` and split its day at each route or headsign change.
- **Buses leave the feed at layovers.** At the end of a line a bus often
  drops out of the payload for 5–25 minutes and comes back on its return
  trip (bus 10015 at Walnut @ Racine: 20:10–20:19). Those gaps are in the
  history too; they're most of the breaks in the map's delay chart.
- **Delay is capped.** `"1h+ late"` / `"1h+ early"` mean "at least an hour",
  stored as ±3600 and flagged `delay_capped`. Those rows are usually
  misassigned buses; exclude them. (Pollers before 2026-09-24 stored them as
  0; `backfill_replay.py` re-parses `delay_raw`.)
- **Line and stop IDs are opaque and unstable.** Internal `idLigne` (e.g.
  111302) maps to route "36" only by lookup, and every ID changes when the
  vendor publishes a new topo version — which happened twice in September
  2026, days apart. Stop codes (`LAMLAPEN`) and route numbers are stable;
  key everything on those.
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
                                      ├─▶ data/schedule/YYYY-MM-DD/, data/arrivals/YYYY-MM-DD/  timetable + when buses came (schedule.py)
                                      └─▶ data/vehicle_positions.pb                         GTFS-RT feed
 GTFS_MATA.zip ── once a day ──▶ poller (schedule.py)
 /topo ── when line IDs change ──▶ poller (build_crosswalk.py) ──▶ routes.csv, stops.csv, network.geojson

 map.html  ── data/latest.json every 10 s + the day's replay file + stop files on click ──▶  live map, replay, stop times  (served by python -m http.server)
 strips.html, schematic.html ── data/latest.json every 10 s + route files ──▶  route strips, subway-style map
 schematic.json ── built by build_schematic.py with LOOM (occasionally, on Linux/WSL) ──▶  the schematic layout
 analysis.sql ── DuckDB reads data/positions/*/*.jsonl.gz ──▶  the three questions
 routes.csv / stops.csv / network.geojson ── built by build_crosswalk.py ──▶  names, colors, route lines
```

Five files do the work: the poller, its timetable module, the map page,
the SQL file, and the crosswalk builder. Everything else in the repo is
optional, a one-off tool (`backfill_replay.py`, `backfill_routes.py`, `cadavl_detours.py`,
`probe_cadence.py`), or one of the two extra views (`strips.html`,
`schematic.html`, sharing `transit.js` and `pages.css`, with
`build_schematic.py` making the schematic's layout).

## Components

### 1. Poller — `cadavl_to_gtfs_rt.py`

Runs forever as a scheduled task (see Running it). Each cycle, during
service hours (04:00–24:00 local): fetch `/topo/vehicules`, normalize each
bus into a flat row, then write four things.

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
6–9 GB/year. The replay frames add ~7 MB/day (~2.5 GB/year) and the log
~0.3 MB/day. Acceptable on any disk. If it ever matters, compact old days to
Parquet with one DuckDB `COPY` — not now.

**Snapshot — `data/latest.json`.** The same rows for the current poll plus
`fetched_at`, written atomically (tmp file + rename). The map reads this; so
does the "right now" query. Each bus also carries `trail`, its last ten
replay positions (one per 30 s), held in memory and seeded from the replay
file when the poller starts, so the map draws full trails the moment it
opens without waiting for the multi-MB replay file.

**Replay — `data/replay/<local day>.jsonl`.** Every third poll (30 s) one
compact line: the poll time and, per bus, `[id, route, lat, lon, bearing,
delay_seconds, delay_capped, occupancy_pct, unchanged_polls, destination,
next_stop_name, equipment_no]`. The last three (from 2026-09-25) let the
strips and schematic place a replayed bus on its stop pattern; older frames
stop at `unchanged_polls` and still load. ~110 B per bus per frame, ~7 MB
for a full day. `python backfill_replay.py [day]` rebuilds these (and the
day's arrivals) from the full history — for days recorded before this
existed, after any gap, or to bring old frames up to the current format.
Each page loads the viewed day's file once; it drives the replay scrubber
(and on the map, the trails while replaying).

**GTFS-RT — `data/vehicle_positions.pb`.** Already implemented; ~30 lines and
one dependency. Kept because it is the standard interchange format, but
nothing in this project consumes it. Delete it and `gtfs-realtime-bindings`
if it ever gets in the way.

The `idLigne → route` mapping and colors are loaded from `routes.csv` at
startup (`load_routes`). When a poll has buses on lines it doesn't know
(`cadavl:<id>`), at most every 15 minutes it asks `/config/version`; if
that moved past the version recorded in `network.geojson`, it rebuilds the
crosswalk (`build_crosswalk.refresh`, a ~28 MB download) and reloads, so
a renumbering fixes itself within a poll or two. `StaleTracker` does ghost
detection; `parse_delay` turns the vendor's text into seconds.

**Timetable and arrivals — `schedule.py`.** Once per service day (and at
startup) the poller downloads `GTFS_MATA.zip` if the server's copy is newer
than `data/gtfs.zip`, loads today's trips, and writes for the map:

- `data/schedule/<day>/stops.json` — stop code → routes scheduled there
  (from the timetable, not `/topo`, which lists lines that pass without
  stopping).
- `data/schedule/<day>/<route>.json` — that route's trips (id, headsign)
  and, per stop, seconds after local midnight (`t0`); plus its stop
  `patterns`: per headsign, each stop sequence that is a real branch
  (≥ a fifth of its trips and sharing < 80% of stops with the main one:
  route 36 via Lamar or via Kimball), stops in order with name, position,
  median seconds from the first stop, and timepoint flag. 25 files,
  ~1 MB a day.

Every poll it then does two matches:

- **Trip.** The trip a bus is running is the one of its route and headsign
  due at its next stop closest to *now + ETA − reported delay*, within 20
  minutes. Stored as `trip_id` on the row. Needs an uncapped delay.
- **Arrival.** When a bus's next stop changes away from A, it has served A,
  at the time of the last poll that still showed A (±10 s). The stop is the
  one named A on that route and direction nearest the bus (names repeat
  across the street), and the trip is matched as above. Skipped if the bus
  was over 300 m away or the polls were over two minutes apart. Appended
  to `data/arrivals/<day>/<route>.jsonl` as `{t, stop, vehicle, trip,
  delay}` — ~40k a day, ~2.5 MB, split by route so the map fetches only
  the routes at a clicked stop.

Checked live: every arrival's actual − scheduled time agreed with the
vendor's reported delay to within a minute. A failure here is logged and
never costs a poll.

### 2. Crosswalk — `build_crosswalk.py`

The poller runs it when line IDs change (above); by hand,
`python build_crosswalk.py --fetch`. Commit the results when convenient —
`ops/update.ps1` discards the poller's local copies before pulling, and the
poller rebuilds again if the pulled ones are stale.

Besides `routes.csv` and `stops.csv` it writes `network.geojson`: one
MultiLineString per route, built from the 2-point segments in `/topo`,
de-duplicated across a route's direction/branch variants and rounded to 5
decimals, plus one Point per stop with its name and code, and the topo
version it was built from (`topo_version`). Just under 1 MB; the map draws
it as the background.

### 3. Live map — `map.html`

One static page, Leaflet from a CDN, no build step. It fetches
`data/latest.json` every 10 s, the day's `data/replay/` file once (in the
background; the live view doesn't wait for it), `network.geojson` once,
and a clicked stop's schedule and arrival files. Visual-first: the
picture carries the information and text is confined to a tooltip and a
three-number strip. All text is Inter (Google Fonts) at 16 px (12 pt) or
larger, including the route numbers inside the markers.

Encodings, per bus:

- **Fill = schedule adherence**, in tiers: early (blue), on time (grey, so
  problems stand out), 5+ / 10+ / 20+ min late (yellow → orange → red, the
  status palette). `"1h+"` capped values count as 20+ late or early,
  matching their direction.
- **Size = passenger load** (`occupancy_pct`), radius 13–19 px (16–22 px
  for three-character route numbers, so the digits fit).
- **Number = route**, a wedge on the rim = heading. **Shape = mode**: the
  trolley (route 100) is a diamond, buses are circles. The vendor types
  every vehicle "Bus", so the route is the only tell.
- **Trail** = the last ten positions, 30 s apart (live, from `latest.json`;
  replaying, from the frames), in the tier color, one segment per pair: bright,
  thick and solid where the bus just was, darker, thinner and fainter as it
  ages.
- **Ghost** (`unchanged_polls` ≥ 30) = dashed hollow circle, no wedge.
- Late buses are stacked on top of on-time ones.

Around it: the whole network as hairlines and every stop as a small hollow
dot with a high-contrast ring (light on the dark basemap, larger at higher
zoom, hover for its name) — visible but subordinate to the buses. Click a
bus and its route highlights, drawn over the other lines, while every other
route and bus dims (click the bus again or the map to clear), a ring marks
it, and a panel shows its fleet number, delay and load; the last three
stops it served in the past 90 minutes (scheduled vs actual, from the
arrivals log); its next three on its trip (scheduled vs expected =
scheduled + current delay, from the timetable; located by its next stop,
or replaying, by its last arrival); and a line chart of its delay over the
last four hours from the replay frames (tier colors, 0/5/10/20 guides,
"1h+" readings left as gaps, crosshair tooltip). A bus that ran more than
one route in that window (MATA's timetable interlines 13 and 40 in one
block) gets a line at each switch, each stretch's route along the top (the
current one always), and a break in the delay line there. Click a stop
and the routes that stop there highlight, and a panel lists for each route
the last three and next three scheduled trips: when each bus actually came
(with minutes late/early in the tier colors), "not seen" when no arrival
was recorded, and, live, "~time" when a bus on that trip is on its way
(scheduled + its current delay). Replaying, the panel shows the same as of
the viewed moment. Squares mark the four transit centers (hollow; click for
the combined times of all their bays) and the bus garage at 1370 Levee Rd
and trolley barn at 547 N Main St (filled) — hard-coded in `PLACES`, the
transit centers located from where the timetable ends trips headed to them.
Clock times are Memphis time wherever the viewer is. On phones the panel
takes the top of the screen and the map slides the clicked bus or stop
into the clear area below it. Hover for route,
headsign, delay text, load, fleet number. Top-right: buses in service, buses
5+ min late, estimated riders (`CAPACITY = 40`). A dot goes red when the
snapshot is older than 90 s. Bottom-left legend. Bottom bar: play/pause,
a scrubber across the day's frames, the clock, replay speed (10× / 60× /
300× real time), LIVE, and a date picker for earlier days — so any moment
of any recorded day can be revisited and played forward, with the same
encodings and trails. On phones (≤ 720 px wide) the scrubber gets its own
row and the legend moves up out of its way. The OSM basemap is muted
with a CSS filter so the data reads on top; dark mode inverts it and follows
the OS setting.

Served by `python -m http.server` from the repo root — browsers block
`fetch()` on `file://` URLs, so a server is required, but that one command
is all of it. The legend links to the two views below, and a bus's panel
to its route's strip.

### 3b. Route strips and schematic — `strips.html`, `schematic.html`

Two more views of the same data, each with page links, a row of route
chips (bus count on each; one sideways-scrolling row on phones), and the
map's bottom bar — play/pause, scrubber, clock, speed, LIVE, day picker —
replaying the same `data/replay/<day>.jsonl` frames (`transit.js`,
`timeline`). A day can only be replayed here if the poller saved that day's
timetable (`data/schedule/<day>/`); MATA's GTFS feed only covers today
onward, so 2026-09-23 can't be. Both place a bus along its route's stop pattern the same
way (`transit.js`, `locate`): the pattern for its headsign, its next stop
by name (nearest if the name repeats; other patterns if its branch's
isn't the main one), and the fraction between that stop and the one
before by distance. Delay colors are the map's tiers.

**Strips** (`strips.html#36`): one vertical strip per pattern of the
chosen route, stops top to bottom in travel order, evenly spaced and all
named (timepoints bold with a big dot), like the line diagram over a
subway door. Buses sit on the line with a chevron for direction; beside
each, its delay, fleet number and the gap to the bus ahead in scheduled
minutes — bunching and holes read at a glance. Labels shift down rather
than overlap. Branches with the same headsign say "via" their first stop
the others lack.

**Schematic** (`schematic.html#36`): the whole network as a subway map,
drawn with Leaflet on a flat (`CRS.Simple`) plane from `schematic.json`.
Stations are the timetable's timepoints, merged where LOOM merged them
(246 → 143); segments are at 45°/90°; routes that share a street run as
parallel lanes in LOOM's crossing-minimising order. Lines are one neutral
ink so color stays with the buses; route numbers mark each route's ends;
click a line, a bus or a chip to pick a route out (others fade). Lanes
keep a fixed pixel spacing (5 px, halved at a phone's whole-network zoom),
so the offsets are recomputed on zoom. Labels: the transit centers at
overview, every station from zoom 0, placed right or left of their
station and skipped where they would collide. A bus slides along its own
lane between the timepoints before and after it, by scheduled time, using
the edge chain stored for that pair of timepoints. How full it is shows as
a translucent band along that stretch of its lane: the lane's width plus up
to 32 px at 100% (12 px at a phone's overview), drawn under the lines so
the other lanes in a bundle stay visible through it. No band for a bus
with stuck GPS, or for other routes while one is picked out; the tooltip
gives the exact %.

`build_schematic.py` makes `schematic.json` (56 KB, committed) from the
GTFS feed with [LOOM](https://github.com/ad-freiburg/loom) (University of
Freiburg: `gtfs2graph | topo | loom | octi`), cut to timepoints first. LOOM
is C++ and builds on Linux or WSL; the script's docstring has the build
line (build only the four tools — `topo`'s test suite takes most of an
hour to compile). Rerun only when MATA changes its routes; line-ID
renumberings don't matter, since routes are keyed by number and stops by
code.

### 4. Analysis — `analysis.sql`

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
Not required for any of the three questions. If wanted later: an hourly
scheduled task writes `data/detours.geojson`, and `map.html` draws it as a second layer.
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
| `route_id` | str | MATA route number ("01"), or `cadavl:<id>` if unmapped (`backfill_routes.py` fixes these later) |
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
| `trip_id` | str | GTFS trip the bus is inferred to be running; null if unmatched (from 2026-09-24) |

## Running it

An always-on Windows machine at home. Chosen over the cloud free tiers:
Google's e2-micro is free but its external IP is ~$3.65/month, Oracle's is
$0 but has signup and idle-reclamation caveats, and a home box costs a few
dollars a year in power. Needs are tiny: one 12 KB request every 10 s,
~25–30 MB/day of disk (history plus replay frames).

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

After pulling new code, `.\ops\update.ps1` pulls, re-runs
`pip install -r requirements.txt`, and restarts both tasks. It needs no
admin: setup grants the installing account read + execute on both tasks,
which is enough to start and stop them. After the poller has logged
`cadavl:<id>` routes, for days recorded before replay or arrivals existed,
or to bring a day's replay frames up to the current format, run
`.\ops\backfill.ps1` (every day) or `.\ops\backfill.ps1 2026-09-24` (one
day) from your own PowerShell window (a sandboxed shell can't see the
poller's command line, so it can't stop it). It pauses the
poller, runs `backfill_routes.py` (every history file) and
`backfill_replay.py`, and starts the poller again.

The machine's clock is already Central time, so the service-hours check
needs no time-zone setting. Do set Power settings to never sleep (and, on
a laptop, "do nothing" on lid close, plugged in).

Reaching the map away from home: Tailscale (free for personal use) on the
machine and the phone makes a private network between your own devices,
with no router ports opened and nothing exposed to the internet. Phone
browsers force `https://`, which plain `http.server` can't answer
(`ERR_SSL_PROTOCOL_ERROR`), so let Tailscale terminate HTTPS: enable
MagicDNS and HTTPS in the admin console (DNS page), then on the PC run
`tailscale serve --bg 8000` once. The map is then at
`https://<pc-name>.<tailnet>.ts.net/map.html` from any signed-in device.
Don't port-forward 8000 instead; `http.server` is not meant to face the
public internet.

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
- MATA changes routes or renumbers lines → the poller notices unmapped
  lines and rebuilds the crosswalk itself. Rows from before the rebuild
  keep `cadavl:<id>`; `.\ops\backfill.ps1` remaps them in the history
  (`backfill_routes.py`) and rebuilds the replay and arrivals files.
- GTFS feed down → the cached `data/gtfs.zip` is used; with none, stop
  panels say there's no timetable and everything else carries on.
- Vendor changes the JSON shape → `normalize_vehicle` returns nothing useful;
  the `--sample` check against a freshly saved payload is the debugging tool.

## Implementation plan

Steps 1–4 are done. Each left the project working; net line count went down.

1. **Poller.** Read `routes.csv` at startup; write all rows every poll; write
   `latest.json`; delete raw archive, dedupe set, and the two hardcoded dicts.
2. **Map.** Add `map.html`; delete `plot_bus_map.py` and `bus_map.html`.
3. **Analysis.** Add `analysis.sql` with the three queries above.
4. **Ops.** Add `requirements.txt`, `ops/setup.ps1` and `ops/update.ps1`
   (Task Scheduler), and `.gitignore` entries for generated files. Deploy
   and let it run.
5. **After a week of data:** run the queries, sanity-check against personal
   experience of the routes, then decide the open questions below.

## Open questions

- **Bus capacity.** `occupancy_pct` is a percentage of something. A constant
  of 40 riders at 100% is a reasonable first guess for a 40-foot bus; the
  right value may vary by `equipment_no` (fleet number), and the trolley is
  different. Until confirmed, ridership figures are relative, not absolute.
- **Ghost threshold.** 30 unchanged polls (five minutes) is a guess. A bus
  at a layover legitimately sits still that long (when it doesn't drop out
  of the feed altogether); check how many rows the filter drops per route
  before trusting it.
- **Late threshold.** Five minutes is the usual transit-industry cutoff for
  "late". Adjust if MATA publishes its own on-time standard.
- **Speed unit.** Only matters if the GTFS-RT feed gets a consumer.

## Non-goals

- Computing our own delay. The vendor's reported delay is kept as the
  measure; the GTFS timetable is used only to name trips and show stop
  schedules, and actual − scheduled agrees with it anyway.
- Multi-agency support, a REST API, user accounts, alerting, dashboards
  beyond the one map page and the SQL file.
- Unit tests. The offline `--sample` run against `vehicules.json` is the
  regression check; if the parser changes, run it.
