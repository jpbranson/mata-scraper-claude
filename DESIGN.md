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
| `/topo/refresh` | Current detours (bypassed and replacement segments) | ~150–385 KB, changes over days | Detour log, hourly (`cadavl_detours.py`) |
| `/iv/message` | Rider-facing notices: detours, and trips out of service | small | Detour log, hourly |
| `/horaires/pta/<stop id>` | The tracker's own stop popup: next one or two times per route | small | Nothing (no CORS, so the page can't call it; kept as a cross-check) |
| `gtfs.mata.cadavl.com/MATA/GTFS/GTFS_MATA.zip` | MATA's published timetable (GTFS), same vendor | ~1.5 MB, rebuilt nightly | Stop schedules and trip matching (`schedule.py`) |
| `gtfsrt.mata.cadavl.com/ProfilGtfsRt2_0RSProducer-MATA/{VehiclePosition,TripUpdate,Alert}.pb` | MATA's official GTFS-Realtime, same vendor | ~3 KB / ~120 KB / ~1 KB, rebuilt every 30 s | Archived beside our history (`official_feed.py`) |

The official GTFS-RT feed isn't linked from matatransit.com (found via
Transitland, 2026-09-25); it's presumably what GO901, Transit and Google
Maps show. Compared live with the tracker, it has what the tracker lacks,
and lacks what our three questions need:

| | Official GTFS-RT | Tracker (`/topo/vehicules`) |
|---|---|---|
| Vehicle ID | Fleet number (`equipment_no`) | Vendor ID and fleet number |
| Trip | `trip_id` from the timetable | None; `schedule.py` infers it (agreed 27 of 27) |
| Timestamp | Each bus's report time | None |
| Freshness | Positions ~1 min old | Every 10 s |
| Load | Category (`FEW_SEATS_AVAILABLE`) | Percent |
| Delay | None; predicted times per stop | The vendor's "5 min late" |
| Missed service | `CANCELED` trips; alerts like "Route 50 is not running from Exeter @ Poplar at 5:30a" | None |

The predictions don't reproduce the tracker's delay (next-stop prediction
− timetable ranged from 9 min more to 10 min less than the tracker's
figure, 27 buses at 05:30), so the tracker stays the source for positions, delay and load.

The GTFS feed lines up with the tracker exactly: GTFS `stop_id` is `"0:"` +
the tracker's stop code (`mnemoPointArret`, `stop_code` in `stops.csv`),
`route_id` is the route number, and `trip_headsign` is the bus's
`destination`, trailing spaces and all. The vendor's delay is measured
against this timetable (checked: a bus "8 min late" at LAMAR @LAPALOMA at
18:01 is the 17:52:59 trip).

Known limits of the tracker's vehicle payload, which shape the design
(the official feed fills the first two, in its own archive, not in our
rows):

- **No server timestamp.** `observed_at` is *our* fetch time, so a bus whose
  coordinates stop changing is either parked (a layover or hold) or has a
  tracker that stopped reporting (a "ghost"). `unchanged_polls` counts the
  still polls; how the streak ends tells the two apart (see Open questions,
  ghost threshold).
- **No trip or block ID.** We know the route and headsign, not which scheduled
  trip a bus is on; `schedule.py` infers it (see below), and the official
  feed's `trip_id` is there to check it against. Delay is whatever
  the vendor reports (`avanceRetard`), not something we compute. The GTFS
  timetable does carry `block_id`, and a few blocks interline: weekday
  blocks 4001 and 4002 (and their weekend twins) alternate a route 13 round
  trip with a route 40 one from William Hudson, so those buses change route
  every couple of hours. That's real, not mislabelling; follow a bus by
  `vehicle_id` and split its day at each route or headsign change.
- **Buses leave the feed at layovers.** At the end of a line a bus often
  drops out of the payload for 5–25 minutes and comes back on its return
  trip (bus 10015 at Walnut @ Racine: 20:10–20:19). Those gaps are in the
  history too; they're most of the breaks in the map's delay chart. The
  official feed keeps such a bus, parked at its next trip's first stop
  (see Official feed below).
- **Delay is capped.** `"1h+ late"` / `"1h+ early"` mean "at least an hour",
  stored as ±3600 and flagged `delay_capped`. Those rows are usually
  misassigned buses; exclude them. (Pollers until the evening of 2026-09-24
  stored them as 0, still flagged, so `NOT delay_capped` drops them either
  way; `backfill_replay.py` re-parses `delay_raw`.)
- **Delay is in whole minutes, and "on time" spans a minute either way.**
  The vendor never says "1 min": after `"on time"` the next values are
  `"2 min late"` and `"2 min early"`.
- **Line and stop IDs are opaque and unstable.** Internal `idLigne` (e.g.
  111302) maps to route "36" only by lookup, and every ID changes when the
  vendor publishes a new topo version — which happened twice in September
  2026, days apart. Stop codes (`LAMLAPEN`) and route numbers are stable;
  key everything on those.
- **Speed is metres per second**, whole numbers (typically 0–21; about 1
  reading in 1,200 is impossible, up to 347). Settled 2026-09-25; see Open
  questions. Not needed for any of the three questions.
- **Load is riders out of 50**, presumably from the bus's automatic
  passenger counters: `"30%"` is 15 people, on every vehicle, trolley
  included (see Open questions). Good as the counters are, no better.

## Architecture

```
                 every 10 s
 CADAVL ───────────────────▶  cadavl_to_gtfs_rt.py  (poller, one process)
                                      │
                                      ├─▶ data/positions/dt=YYYY-MM-DD/positions.jsonl.gz   history (append)
                                      ├─▶ data/latest.json                                  current snapshot
                                      ├─▶ data/replay/YYYY-MM-DD.jsonl                       one frame per 30 s, for replay
                                      ├─▶ data/schedule/YYYY-MM-DD/, data/arrivals/YYYY-MM-DD/  timetable + when buses came (schedule.py)
                                      ├─▶ data/official/dt=YYYY-MM-DD/                      official GTFS-RT archive (official_feed.py)
                                      ├─▶ data/detours/dt=YYYY-MM-DD/detours.jsonl.gz        detours + rider messages, when changed (cadavl_detours.py)
                                      └─▶ data/vehicle_positions.pb                         GTFS-RT feed
 GTFS_MATA.zip ── once a day ──▶ poller (schedule.py)
 official GTFS-RT ── every 30 s (trip updates every 5 min) ──▶ poller (official_feed.py)
 /topo/refresh, /iv/message ── hourly ──▶ poller (cadavl_detours.py)
 /topo ── when line IDs change ──▶ poller (build_crosswalk.py) ──▶ routes.csv, stops.csv, network.geojson

 map.html  ── data/latest.json every 10 s + the day's replay file + stop files on click ──▶  live map, replay, stop times  (served by python -m http.server)
 strips.html, schematic.html ── data/latest.json every 10 s + route files ──▶  route strips, subway-style map
 schematic.json ── built by build_schematic.py with LOOM (occasionally, on Linux/WSL) ──▶  the schematic layout
 analysis.sql ── DuckDB reads data/ (history, arrivals, timetables, official archive) ──▶  the three questions and the backlog (FINDINGS.md)
 routes.csv / stops.csv / network.geojson ── built by build_crosswalk.py ──▶  names, colors, route lines
```

Five files do the work: the poller, its timetable module, the map page,
the SQL file, and the crosswalk builder. The poller's other two modules,
`official_feed.py` and `cadavl_detours.py`, only archive. Everything else
in the repo is optional, a one-off tool (`backfill_replay.py`,
`backfill_routes.py`, `probe_cadence.py`), or one of the two extra views (`strips.html`,
`schematic.html`, sharing `transit.js` and `pages.css`, with
`build_schematic.py` making the schematic's layout).

## Components

### 1. Poller — `cadavl_to_gtfs_rt.py`

Runs forever as a scheduled task (see Running it). Each cycle, during
service hours (04:00–24:00 local): fetch `/topo/vehicules`, normalize each
bus into a flat row, then write four things. Cycles start on a fixed 10 s
clock (:00, :10, :20 …), not 10 s after the last one finished; a cycle takes
1–4 s, so the old sleep-after-poll loop drifted to 11–14 s apart, and
history from before the fix has those gaps.

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

**GTFS-RT — `data/vehicle_positions.pb`.** Already implemented; ~30 lines.
Nothing in this project consumes it, and MATA publishes an official
GTFS-RT feed anyway (see Data source); ours is fresher but has no trip IDs.
Delete it if it ever gets in the way (`gtfs-realtime-bindings` stays, for
`official_feed.py`).

**Official feed — `official_feed.py`.** Every poll, `Official.update`
fetches MATA's own GTFS-RT vehicle positions and alerts (two small
requests), and every 5 minutes its trip updates, and appends any snapshot
it hasn't saved (by header timestamp) to `data/official/dt=<UTC day>/`,
flattened to rows (see Data model). Trip updates every 30 s would be
~150 MB a day of mostly repeated predictions, hence 5 minutes; alerts are
saved only when they change. It is an archive only — nothing reads it
yet — kept for what the tracker can't give: trip IDs to check
`schedule.py`'s against, report timestamps, cancelled trips and
missed-trip alerts, and the predictions riders saw. ~15–25 MB a day,
estimated from early-morning snapshots. A failure is logged and never
costs a poll. `python official_feed.py` fetches each feed once and prints
a row.

Checked with MobilityData's GTFS-RT validator (2026-09-25, 13 snapshots
of each feed against `GTFS_MATA.zip`): every trip and stop ID resolves,
no stale feeds, one trivial error (two consecutive stops of one trip
predicted at the same second). What its warnings mean for analysis:

- **Only trips with a `vehicle_id` carry real predictions.** Trips no bus
  has started yet are listed with the timetable's times unchanged
  (predicted − scheduled is exactly 0). Filter on `vehicle_id` before
  judging prediction accuracy, or the copies make it look perfect.
- **The official positions include buses at layover.** A bus waiting at
  the first stop of its next trip (11 of 34 at 06:10) is in
  `vehicles.jsonl.gz` with that trip's ID, while the tracker drops it and
  its trip update has no vehicle yet. That fills most of the layover gaps
  in our own history.
- **Trip updates carry no per-trip timestamp**; use `feed_ts`.

The validator's static check reported ~14,000 problems, nearly all false
(it claims every trip and 7,588 stops lack coordinates; they don't). Real
but harmless: `stops.txt` lists nearly every stop twice, under `0:`
(3,849) and `1:` (3,739) prefixes, and 3,988 are used by no trip. We
only use `0:` IDs.

The `idLigne → route` mapping and colors are loaded from `routes.csv` at
startup (`load_routes`). When a poll has buses on lines it doesn't know
(`cadavl:<id>`), at most every 15 minutes it asks `/config/version`; if
that moved past the version recorded in `network.geojson`, it rebuilds the
crosswalk (`build_crosswalk.refresh`, a ~28 MB download) and reloads, so
a renumbering fixes itself within a poll or two. `StaleTracker` counts
unchanged polls; `parse_delay` turns the vendor's text into seconds.

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

Two limits, measured 2026-09-25. The log catches ~83–85% of the stops on
a trip that ran (buses pass some stops between polls, or out of the
feed). And at the end of a line the tracker still shows the finished
trip's headsign while the bus waits, so what it logs there is the
departure, credited to the trip that just ended; `analysis.sql` leaves
line ends out of timing questions and times departures from the
official feed instead.

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
- **Still 5+ minutes** (`unchanged_polls` ≥ 30) = dashed hollow circle, no
  wedge, "no GPS movement for N min" in the tooltip. The code calls it a
  ghost, but it is usually a bus at layover; a dead tracker can't be told
  apart until the bus reappears somewhere else.
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
5+ min late, riders on board (load % × `CAPACITY = 50`). A dot goes red when the
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
than overlap. Load is the schematic's band: the line between the timepoints
before and after a bus, widened by up to 24 px at 100% full (so it stays
short of the stop names), drawn under the line and stops; hover a bus for
the exact %. Branches with the same headsign say "via" their first stop
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

The file also defines views over the rest of `data/`: `ghost_rows` (the
positions a dead tracker left behind, for anything spatial), `arrivals`,
`sched` (the saved timetables, one row per scheduled call), `timepoints`,
`line_ends`, `stops`, the official archive (`off_vehicles`, `off_trip_updates`,
`off_alerts`), and two joins of them, `arrivals_due` (each arrival with
the time its trip was due) and `trip_service` (each scheduled trip and
whether any bus ran it). After the views come the queries behind
`FINDINGS.md`, grouped as in `QUESTIONS.md` and tagged (`[Q1]`, `[GPS]`,
`[MISSED]`, …) so the findings can cite them. The whole file takes about
a minute; each query also runs on its own after the views.

Variations (by hour of day, by route × weekday, riders over the day) are the
same queries with a different `GROUP BY`. Add them to the file as they are
needed; don't pre-build them.

### 5. Detours — `cadavl_detours.py`

The "detour impact" question (`QUESTIONS.md`) needs a record of which
routes were detoured when, so the poller keeps one, like the official
archive: once an hour `DetourLog.update` fetches `/topo/refresh` (~150 KB)
and `/iv/message`, and when either changed since the last save, appends a
line to `data/detours/dt=<UTC day>/detours.jsonl.gz` (see Data model). Days
of detours cost a few KB. A failure is logged and never costs a poll; it
waits for the next hour.

`/iv/message` is the tracker's rider notices, and not only detours: "Route
11 Out of service Outbound from Thomas & Whitney @ 7:45 PM. The next unit is
scheduled to arrive at 8:39 PM" sits beside "Route 39 diverted. Stops: …".
So the log also holds missed-trip notices from the tracker's side.

Still not drawn on the map. `python cadavl_detours.py --sample refresh.json`
parses a saved payload into `detours.geojson` and a GTFS-RT alerts feed, if
a map layer is ever wanted.

### 6. Probes — `probe_cadence.py`

One-off diagnostic: polls fast for a few minutes to measure how often
positions really change, and cross-checks the speed unit (settled as m/s
from the archives, so there is nothing to set).

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
| `speed_raw` | int | Metres per second, whole numbers; the odd impossible reading |
| `occupancy_pct` | int | Passenger load as a percent of 50 riders, so always even; riders = `occupancy_pct / 2` |
| `destination` | str | Headsign |
| `next_stop_name` | str | Display name, not a GTFS stop_id |
| `next_stop_eta_min` | int | |
| `delay_seconds` | int | Positive = late; `0` = "on time"; null if unparseable |
| `delay_raw` | str | Vendor text, e.g. "4 min late" |
| `delay_capped` | bool | True for "1h+" values — a floor, not a measurement |
| `unchanged_polls` | int | Consecutive polls with identical coordinates: parked, or a dead tracker |
| `trip_id` | str | GTFS trip the bus is inferred to be running; null if unmatched (from 2026-09-24) |

The official feed's archive, from 2026-09-25, is in
`data/official/dt=YYYY-MM-DD/` (UTC date of `feed_ts`, the feed header's
time). Enum values are the GTFS-RT names (`SCHEDULED`, `CANCELED`,
`IN_TRANSIT_TO`, `FEW_SEATS_AVAILABLE`, …); times are Unix seconds.

| File | One row per | Fields |
|---|---|---|
| `vehicles.jsonl.gz` | bus per snapshot (30 s) | `feed_ts`, `reported_at`, `vehicle_id` (fleet number), `trip_id`, `route_id`, `trip_status`, `lat`, `lon`, `bearing`, `speed` (m/s by the spec), `stop_id` (GTFS, `0:<stop code>`), `stop_status`, `occupancy` |
| `trip_updates.jsonl.gz` | trip per snapshot (5 min) | `feed_ts`, `trip_id`, `route_id`, `trip_status`, `vehicle_id` (null until a bus is assigned), `stops`: list of `{seq, stop_id, arrival, departure, status}` |
| `alerts.jsonl.gz` | snapshot whose alerts changed | `feed_ts`, `alerts`: list of `{id, routes, stops, active: [[start, end]], cause, effect, header, description}`; an empty list means none |

DuckDB reads the lists with `unnest`. Every cancelled trip:
`SELECT DISTINCT route_id, trip_id FROM read_json_auto('data/official/*/trip_updates.jsonl.gz') WHERE trip_status = 'CANCELED'`.
(Most trips that never run are not marked; `trip_service` in
`analysis.sql` finds them.)

The detour log, from its first poller restart after 2026-09-25, is
`data/detours/dt=YYYY-MM-DD/detours.jsonl.gz` (UTC date of `fetched_at`):
one line whenever the detours or the tracker's rider messages changed
since the last one saved (checked hourly, and once at every start).

| Field | Notes |
|---|---|
| `fetched_at` | Unix seconds |
| `detours` | One per line on detour: `route_id`, `stops` (stop codes it skips), `bypassed_segments` (count), `paths` (replacement geometry, lists of `[lon, lat]`) |
| `messages` | Every rider message: `routes` it names, `text` |

A route's detour runs from the first line that lists it to the first
that doesn't.

## Running it

An always-on Windows machine at home. Chosen over the cloud free tiers:
Google's e2-micro is free but its external IP is ~$3.65/month, Oracle's is
$0 but has signup and idle-reclamation caveats, and a home box costs a few
dollars a year in power. Needs are tiny: one 12 KB request every 10 s
(plus the official feed's two of ~2 KB, ~120 KB every 5 minutes, and the
detour check's ~150 KB an hour), ~40–55 MB/day of disk (history, replay
frames, official archive; the detour log adds a few KB).

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
  `data\poller.log`, each line stamped with the local date and time (a few
  hundred KB per day; delete it whenever).
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
- Official GTFS-RT down → logged per feed; its archive has a gap and
  nothing else notices.
- Detour endpoints down → logged; tried again the next hour.
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
   experience of the routes, then decide the open questions below. Started
   early (2026-09-25, on 1.8 days): the open questions are settled on that
   data, `QUESTIONS.md` is worked through, results in `FINDINGS.md`. Still
   to do: rerun on a full week and the sanity check.

## Open questions

- **Bus capacity — settled 2026-09-25: 100% is 50 riders, on every
  vehicle.** Every one of 340,389 readings, from every fleet series and
  the trolley, is an even percentage, and together they take all 51 even
  values from 0 to 100: the vendor divides a rider count by 50. (A per-bus
  capacity like 38 or 40 would give odd values.) So riders on board =
  `occupancy_pct / 2`, a count as good as the counters, not an estimate
  from a guessed capacity; `CAPACITY = 50` in `map.html`. For scale, MATA's
  own loading guideline (2012 Short Range Transit Plan) gives a 40-foot
  bus 40 seats and a 48-rider maximum (120% of seats at peak): 80% is a
  full seated load, 100% about the most MATA plans to carry. The official
  feed's occupancy categories are fixed bands of the same number
  (standing room only from ~11 riders, "full" from ~41) and don't say
  whether seats are free; don't use them for crowding.
- **Ghost threshold — settled 2026-09-25** (on 1.8 days; recheck after a
  week). 30 still polls almost never means a dead tracker: of 183 such
  streaks, 127 were layovers at a route's end and 45 were holds mid-route
  (the bus later drove off from the same spot); 8 were dead trackers.
  Dead trackers show instead as a still streak, usually 1–5 minutes, that
  ends with the bus reappearing 200 m+ away; the official feed's report
  times freeze over the same stretches. `ghost_rows` in `analysis.sql`
  finds them. The vendor freezes the delay along with the position, so
  swapping one rule for the other moves no route's late share by more than
  a point: `good` keeps the 30-poll rule, and spatial queries drop
  `ghost_rows`. Bus 458 alone has nearly half the ghost rows (15% of its
  polls). Details in `FINDINGS.md`.
- **Late threshold — kept at 5 minutes (2026-09-25).** MATA has a
  Board-adopted on-time standard (its 2014 service standards, checked in
  the Title VI monitoring reports) and publishes monthly fixed-route
  on-time figures (Memphis Open Data Hub, "MATA On Time Performance":
  roughly 45–70% since 2015), but the minute window wasn't found in
  anything public; the data hub's data dictionary PDF may have it.
  So `[Q1]` uses the usual window, at most 1 minute early and 5 late,
  and reports `on_time` and `share_early` beside `share_over_5_min`. On
  it, 73% of bus-polls are on time, 75% of departures from mid-route
  timepoints, and 59% of departures from a trip's first stop (`[DEPART]`,
  from MATA's feed: 40% leave 5+ min late), the figure nearest MATA's
  own. If MATA's definition turns up, change the two numbers in `[Q1]`.
- **Speed unit — settled 2026-09-25: metres per second.** Paired with the
  official feed (m/s by the spec) on fleet number and identical position,
  i.e. the same report, the two speeds are equal in 97% of 2,557 moving
  pairs. Independently, the distance buses cover over 5-minute windows is
  1.03 × `speed_raw` × time (mph would give 0.45, km/h 0.28). Our
  `vehicle_positions.pb` now carries speed, skipping readings over 40 m/s.

## Non-goals

- Computing our own delay. The vendor's reported delay is kept as the
  measure; the GTFS timetable is used only to name trips and show stop
  schedules, and actual − scheduled agrees with it anyway.
- Multi-agency support, a REST API, user accounts, alerting, dashboards
  beyond the one map page and the SQL file.
- Unit tests. The offline `--sample` run against `vehicules.json` is the
  regression check; if the parser changes, run it.
