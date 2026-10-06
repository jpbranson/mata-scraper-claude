# Update log (Central time)

## 2026-10-06

* **Request**: 00:10 — At the user's request, committed and pushed
  everything from 2026-10-05, including the crosswalk files at topo 198282.
* **Update**: 00:09 — Findings page version 4, rebuilt on the 12-day copy
  at the user's request: a route-by-day grid of trips that never ran, a new
  "Which days are bad" section, weekdays apart from Saturdays and Sundays in
  the hour, riders and fleet charts, a weekday late column in the route
  table, slow stretches measured along the route, and every figure in the
  text from 12 days. `page_data.py` was rewritten for weeks of data (no
  more `FEED_DAY`); see [findings page](system/findings-page.md).

## 2026-10-05

* **Correction**: 23:39 — At the user's request, `backfill_replay.py` fixed:
  it now matches each past day's arrivals to the timetable saved that day
  (`Timetable.saved` in `schedule.py`) instead of today's `gtfs.zip`, which
  has no service on earlier days, and leaves a day with neither alone.
  Tested on a copy: 2026-09-29 rebuilt to the poller's 42,036 arrivals byte
  for byte; see [backfill tools](system/backfill-tools.md).
* **Update**: 23:20 — At the user's request ("verify that project knowledge
  is accurate, comprehensive, and up to date"), the whole bundle was checked
  against the code, `git log`, `poller.log` and the 12-day copy. Every
  finding, its question's status, and the decisions on capacity, ghosts,
  lateness and speed were rerun on 12 days (all four decisions stand); the
  system, operations, feeds and datasets concepts were corrected where the
  code or data disagreed (among them: the official feed is about as fresh as
  the tracker, not a minute behind; the vendor renumbered every line and
  stop on 2026-09-30, topo 198282, and `ops\update.ps1` reverts the
  uncommitted crosswalk; `backfill_replay.py` would strip trips from past
  days; measured sizes, failures since 2026-09-25, and the block structure
  of the timetable). Comments in `official_feed.py`, `cadavl_detours.py`
  and `cadavl_to_gtfs_rt.py` corrected to match; `--sample` still parses 41
  buses. What needs the user is in [next steps](work/next-steps.md).
* **Update**: 23:12 — `analysis.sql` changed where 12 days showed a query
  misleading: `[WHERE]`, `[HOUR]`, `[Q1]`, `[LOAD]`, `[BOARDINGS]`,
  `[FLEET]`, `[MISSED]`, `[MISSED_HOUR]`, `[TRIPMATCH]`, `[LAYOVER]`, the
  `good` view's comment and the header (see
  [analysis.sql](system/analysis-sql.md)). Earlier (22:48), `[Q3]` fixed:
  it failed every night once `latest.json` had no vehicles. The whole file
  runs in about 4 minutes on 12 days.
* **Update**: 22:52 — Findings page version 3: "Changing drivers" rebuilt
  from `findings_page/snapshot-2026-10-05/` (same trips, passes and times)
  instead of the 22:01 scratch copy.
* **Correction**: 22:42 — At 22:38 a `snapshot.py` run copied the live
  `data/` into `findings_page/snapshot/`, over the 2026-09-25 20:21 copy the
  page is built from (an edit to give it a `DEST_DIR` had failed, and the
  command carried on). Rebuilt by keeping records up to the original's last
  poll; `page_data.py` on it reproduces `out/page_data.json` and
  `out/numbers.txt` byte for byte ([snapshot](findings/snapshot-2026-09-25.md)).
  The live `data/` was only read. `snapshot.py` now takes a `DEST_DIR` and
  copies `data/detours/` (without it `page_data.py` had failed since
  2026-09-27); `.gitignore` ignores `findings_page/snapshot*/`.
* **Creation**: 22:37 — The 12-day copy, `findings_page/snapshot-2026-10-05/`
  ([snapshot](findings/snapshot-2026-10-05.md)), taken after Monday's
  service.
* **Update**: 22:37 — At the user's request, the findings page (version 2)
  gained the section "Changing drivers" (`findings_page/relief_data.py`,
  new).
* **Creation**: 22:21 — The user asked when drivers switch, what delay it
  causes and which routes are bad for it. Answered in
  [driver changes](findings/driver-changes.md) (question
  [driver changes](questions/driver-changes.md)), with `[RELIEF]` added to
  analysis.sql, from a copy of data/ taken 22:01 in the session scratchpad
  (7 weekdays, 2 Saturdays, 2 Sundays with both feeds). Not committed.

## 2026-10-04

* **Initialization**: 21:18 — Knowledge moved from DESIGN.md, FINDINGS.md,
  QUESTIONS.md, FLIGHT_LOG.md and findings_page/README.md (as of `2a1b9ab`)
  into this OKF v0.2 bundle; no facts changed. The flight log's plan is now
  [next steps](work/next-steps.md) and its log entries are the 2026-09-25
  entries below.

## 2026-09-27

* **Update**: 20:29 — `2a1b9ab` analysis.sql: rider_messages view, routes
  from the text over MATA's tags.
* **Update**: 19:50 — `f2456f9` DESIGN.md: drop history of the pre-rewrite
  code.
* **Update**: 19:39 — `78456eb` cadavl_detours: drop the --sample mode and
  messages_by_line.
* **Deprecation**: 19:38 — `a5d2cf3` Remove the one-off cadence probe and
  stale ignore entries.

## 2026-09-25

* **Request**: 21:35 — The user's request: committed and pushed
  `findings_page/`, the doc updates and the flight log (`513d93a`).
* **Update**: 21:31 — Page scripts moved to `findings_page/` with a README;
  paths now relative to the repo, the feed day in one constant (`FEED_DAY`).
  Ties now broken in every sort and pick, so two runs on one copy give
  byte-identical output. Tested end to end on a fresh copy (to 21:20, 1 min
  44 s), then rebuilt from the 20:21 copy: same as the published page except
  the 30th delay-map circle (a tie at 13.5 bus-min/day) and six stops drawn
  20–155 m from where they were (several stops share a name). `snapshot/`
  now holds the 20:21 copy and `out/` its build. DESIGN.md, FINDINGS.md and
  QUESTIONS.md updated.
* **Deployment**: 21:15 — Deploy checked, read-only
  (`scratchpad/deploy_check.py`, on copies). Both tasks last started
  21:12:45 (the user's `update.ps1`), but the new code first ran at
  20:12:38: that's the first time-stamped log line, so an earlier restart at
  20:12 had already deployed it. Since 20:12:38: 383 log lines, all stamped,
  no poll errors; 379 of 380 stored polls on the 10 s clock (the exception
  is the restart); `vehicle_positions.pb` carries speed for all 14 vehicles;
  `data/detours/dt=2026-09-26/` has 2 records (route 39's detour and rider
  messages), written 20:12:42 and 21:12:51; the map server sends `map.html`
  with `CAPACITY = 50`.
* **Request**: 21:14 — The user's requests: move the page scripts into the
  repo; check that the poller changes are deployed.
* **Update**: 21:11 — Committed and pushed `99a8b44` (FINDINGS.md refresh,
  `[HEADWAY]` tiebreak, the flight log), as part of step 6.
* **Update**: 21:09 — FINDINGS.md refreshed to the 20:21 copy
  (analysis.sql rerun whole into `scratchpad/full_run_2021.txt`, plus
  `scratchpad/checks.py` for the one-off figures), so the file and the page
  agree.
* **Correction**: 21:07 — analysis.sql `[HEADWAY]`: windows now
  `ORDER BY t, t_sched`. Two buses logged in the same second were ordered at
  random, so the bunched and overtake counts changed between runs (4 or 5
  bunched). Now 6 every time, the same 6 FINDINGS.md already named.
* **Creation**: 21:04 — Page published as a private artifact, "Memphis
  Buses, Measured" (`scratchpad/findings_template.html` + `build_page.py` →
  `findings.html`). Checked with headless Chrome screenshots at 1280 px and
  375 px, light and dark (the in-app browser's screenshots timed out); fixed
  garbled characters (no charset), label collisions, the phone layout (a CSS
  specificity bug kept figures at 55% width).
* **Creation**: 20:26 — Page data: `scratchpad/page_data.py` over a copy of
  data/ taken at 20:21 → `page_data.json` (every number the page draws) +
  `numbers.txt`.
* **Correction**: 20:25 — The times of the entries from 19:16 on were
  corrected from file timestamps; they had first been logged as guessed
  clock times, several hours off.
* **Request**: 20:18 — The user's request: commit and push (done:
  `ef8710c` poller, `bdbfd38` map, `34103dd` analysis.sql, `c658a63`
  FINDINGS.md and DESIGN.md, `e4e3af4` flight log), then publish
  FINDINGS.md as a page.
* **Update**: ~20:09 — All steps worked through. Open: 1 (waiting for a
  week, ~Oct 1), 2c deploy (the user), 3a rerun + sanity check (the user,
  after Oct 1), MATA's on-time window (the user, optional).
* **Correction**: ~20:08 — Found while reviewing FINDINGS.md: at a line's
  end the tracker logs the bus's *departure* credited to the trip just
  finished (headsign flips late), so line-end "arrivals" looked 22% early
  and the "53% on time at first stops" figure was wrong. Fix: `line_ends`
  view, excluded in `arrivals_due` (so `[WHERE]` `[WHERE_ROUTE]` `[EARLY]`
  `[HEADWAY]` `[SPEED_SLOW]` `[LAYOVER]` `[STOP_WAIT]` no longer see them),
  new `[DEPART]` query timing departures from MATA's feed (59% on time,
  median 4.3 min late, 40% 5+ late, 1% early). Reran analysis.sql whole (24
  queries, clean) and updated every affected figure in FINDINGS.md and
  DESIGN.md (late threshold, schedule.py limits, §4 view list). Scratch
  checks: scratchpad/ends.sql, headway_extra.sql.
* **Decision**: ~20:02 — 5b: checked, `vehicle_positions.pb` isn't in the
  way (one small write per poll, no reader); kept, no change.
* **Creation**: ~20:01 — 5a coded: `cadavl_detours.DetourLog` (hourly
  /topo/refresh + /iv/message → data/detours/dt=<UTC>/detours.jsonl.gz when
  changed; stop IDs → stop codes via stops.csv;
  `parse_detours(payload, route_for)`; empty `update` → no detours). Poller:
  lazy `import cadavl_detours` in run_poller (same pattern as
  build_crosswalk), `detours.update(...)` after the official feed, own
  try/except. Tests: py_compile, both `--sample` runs, __main__-then-import
  order, live loop 45 s into scratch (route 39 detour + 3 messages logged,
  1.9 KB; polls still on 10 s ticks). DESIGN.md (architecture, components
  §5, data sources, data model, needs, failure modes), QUESTIONS.md,
  FINDINGS.md updated. Next: 5b.
* **Update**: ~19:57 — analysis.sql reorganized (views, then three
  questions, open questions, QUESTIONS groups 1–5; CRLF kept). Whole file
  runs clean via scratchpad/run_sql.py: 23 tagged queries, 54 s. DESIGN.md
  §4 lists the views. Next: 5a detour logging.
* **Update**: ~19:55 — 4e done as far as 1.8 days allow. analysis.sql:
  `timepoints` view; queries `[DIRECTION]` `[HOUR]` `[EARLY]` `[LOAD]`
  `[LOAD_DELAY]` `[RIDERS_DAY]` `[BOARDINGS]` `[FLEET]` `[SPEED]`
  `[SPEED_SLOW]` `[PREDICT]` `[LAYOVER]` `[STOP_WAIT]` (each run and
  checked; SPEED_SLOW reworked to stop-to-stop segments ≥ 300 m; LAYOVER
  uses first logged stop; STOP_WAIT imputes unlogged departures).
  FINDINGS.md: groups 1–5 written, "not answerable yet" list. Next: tidy
  analysis.sql (views first, queries by group), run it whole, then 5a detour
  logging.
* **Update**: ~19:47 — 4d done: `[TRIPMATCH]` in analysis.sql. 99.8%
  agreement where we name a trip (58,429 reports); disagreements = other
  direction at turnarounds; 2.7% none (no next stop / 1h+). Next: 4e, the
  rest of the QUESTIONS backlog, one question at a time.
* **Update**: ~19:45 — 4b done: analysis.sql `stops` view (stops.csv) +
  `[WHERE]` (delay gained per stop, bus-min/day) + `[WHERE_ROUTE]` (start vs
  end delay per trip; also answers group 1 "recover or compound"). Top:
  route 36 at American Way @ Getwell (+3.1 min/pass). Most routes start 2–6
  min late and recover; 100, 02, 36 compound. FINDINGS.md section written.
* **Update**: ~19:44 — 4a + 4c done (4c done alongside because missed trips
  explained the first headway results). analysis.sql gained views
  `arrivals`, `sched` (flattens data/schedule JSON), `off_vehicles`,
  `off_trip_updates`, `off_alerts`, `arrivals_due`, `trip_service`, and
  queries `[HEADWAY]`, `[MISSED]`, `[MISSED_HOUR]`. Bunching ~nil (5 of
  64,818 pairs); missed trips 13% Thu / 17% Fri; only 27 of 99 Fri misses
  marked CANCELED. Arrivals log catches ~83–85% of stops per trip (checked
  with scratchpad/coverage.sql). Tracker vs official on which trips ran: 434
  of 441. FINDINGS.md sections written. Next: 4d trip matching (row level).
* **Decision**: ~19:36 — 3e done: kept 5 min. Vendor never says "1 min" (on
  time = ±1 min). `[Q1]` gains `share_early` (< -60 s) and `on_time`
  (-60..300 s). On-time 73% of polls, 75% at timepoints, 53% at first-stop
  departures (closest to MATA's published 54–65%). Script
  `scratchpad/otp.py`. DESIGN.md: new known limit (whole minutes, ±1 min on
  time), "Delay is capped" note on old 0-valued rows (still flagged capped,
  so excluded), SQL block Q1, open question. FINDINGS.md section. Step 3
  complete except 3a's week-of-data rerun + the user's sanity check. Next:
  4a bunching/headways.
* **Decision**: ~19:33 — 3d done. All 340,389 load readings are even and
  cover every even value 0–100 → the vendor's 100% is 50 riders on every
  vehicle. MATA's 2012 SRTP (matatransit.com,
  MATA_SRTP_Plan_APPENDICES.pdf, Figure 4-4): 40-ft bus 40 seats / max load
  48. Official occupancy categories are fixed bands (STANDING from ~11
  riders), useless for crowding. Changed: map.html `CAPACITY = 50`
  (+comment), analysis.sql `[Q3]` → `sum(occupancy_pct) // 2` (144 riders
  at 19:10 Fri), DESIGN.md (known limits, map text, data model, SQL block,
  open question), FINDINGS.md. Web research notes: CPTDB fleet wiki 403s;
  the city's OTP data dictionary PDF host (memegis.maps.arcgis.com) was
  refused in the browser. Next: 3e late threshold (research mostly done: no
  published MATA window).
* **Decision**: ~19:24 — 3c done: m/s (official speed == speed_raw in 97%
  of 2,557 moving same-report pairs; distance/(speed×time) = 1.03).
  `cadavl_to_gtfs_rt.py`: `SPEED_UNIT`/`_SPEED_TO_MS` replaced by
  `MAX_SPEED_MS = 40`, feed writes speed (≤ 40). probe_cadence.py
  output/docstring updated. `--sample` OK (41/41 buses carry speed).
  DESIGN.md (known limits, probes, data model, open question), QUESTIONS.md
  (speed profiles), FINDINGS.md updated. Next: 3d capacity.
* **Decision**: ~19:21 — 3b done. Scripts `scratchpad/ghost*.py`. Streaks
  of 30+ still polls are layovers (127/183) and holds (45); dead trackers
  (8) end in a 200 m+ jump and are mostly 1–5 min; official report age
  freezes too. Delay unaffected, route shares ±1.2 pts. Bus 458: 15% ghost
  rows. Added to analysis.sql: `dist_m` macro, `ghost_rows` view, `[GPS]`
  query, tags `[Q1]`–`[Q3]`. DESIGN.md: known-limits wording, map marker,
  data model, SQL block synced (Q2 hours, Q3 unnest), open question marked
  settled. FINDINGS.md section written. Next: 3c speed unit.
* **Update**: ~19:16 — DESIGN.md updated for 2a/2b (fixed clock; stamped
  log lines). 3a: analysis runs from `scratchpad/run_sql.py FILE [TAG]` over
  a copy made by `scratchpad/sync_data.py` (never query the live files).
  Ran analysis.sql unchanged; results in new FINDINGS.md. Changed Q2 to
  show `hours` covered (Wed was a 0.9 h sliver). Next: 3b ghost threshold.
* **Update**: 19:14 — Restart NOT done: auto mode refused the agent's next
  action as "Interfere With Workloads". Leaving the live poller alone; 2c
  goes to human review. Moving on; poller changes from later steps get
  tested the same way (scratchpad copy) and deployed together by the user.
* **Update**: 19:11 — 2a/2b coded. `--sample` check passes. Live test
  (scratchpad copy of the loop, all output paths redirected to
  `scratchpad/testdata`, 75 s): polls at exactly 1790381360, …370, …380 …
  (gaps 10 s after the first), log lines stamped
  `2026-09-25 19:09:20 31 vehicles, 26 moved`. Restart script:
  `scratchpad/restart_poller.ps1` (waits for latest.json to change, +2 s,
  stops task, kills orphan python, starts task).
* **Creation**: 19:07 — Started the [next steps](work/next-steps.md) run.
  Baseline health check: poller running since Wed night; 1.8 service days
  of history (Thu full, Fri so far); official archive since Fri 05:45. Poll
  gaps median 11 s, p90 13–14 s. ~1.5% of polls fail (vendor
  timeouts/5xx). Found this shell can't terminate the task's python
  processes (OpenProcess → access denied), so restarting the poller may
  need an unsandboxed command or the user (`.\ops\update.ps1`).
* **Update**: 06:15 — `5e4cefe` Archive MATA's official GTFS-RT feed
  alongside the tracker history.

## 2026-09-24

* **Update**: 22:42 — `988f633` Strips: load band along each bus's stretch
  of line.
* **Update**: 22:34 — `33b9081` DESIGN: interlined blocks, layover gaps,
  route backfill, replay on strips and schematic, load bands.
* **Creation**: 21:35 — `bcbd380` Add route strips and a subway-style
  schematic, both with live buses.
* **Update**: 20:55 — `208ec8b` DESIGN: trolley marker, bus panel and delay
  chart.
* **Update**: 20:43 — `a966a68` Map: mark the bus garage, trolley barn and
  transit centers.
* **Creation**: 20:23 — `5729825` Add ops/backfill.ps1: pause the poller
  around backfill_replay.py.
* **Update**: 18:19 — `8f90b73` Map: stop schedules, fix 1h+ early colour,
  trails on load, stop contrast.
* **Update**: 09:04 — `b984448` setup.ps1: let the installing account
  start/stop tasks without admin.
* **Update**: 08:43 — `6c9b769` DESIGN: bring up to date with Task
  Scheduler ops, replay and map changes.

## 2026-09-23

* **Update**: 22:46 — `d2a2457` Replay backfill from history; page
  tolerates old pollers; phone layout.
* **Update**: 22:42 — `70a7473` DESIGN: Tailscale serve recipe for phone
  access.
* **Update**: 22:28 — `577edd6` DESIGN: measured storage figures.
* **Update**: 22:15 — `231cd5c` Replay: scrub and play back any recorded
  day; trails from history.
* **Update**: 22:05 — `3b515b0` Map: Inter at 16px minimum, gradient
  trails, stop dots.
* **Creation**: 21:54 — `1d5bb78` Add ops/update.ps1: pull and restart both
  tasks.
* **Update**: 21:50 — `a1e797e` Visual-first live map: delay tiers, load
  size, trails, route shapes.
* **Update**: 21:27 — `45142c6` Target a Windows home machine: Task
  Scheduler setup script.
* **Creation**: 21:20 — `88888f8` Add setup script and home-machine
  deployment notes.
* **Creation**: 20:55 — `12f8945` Implement the lean feed: snapshot writer,
  live map, DuckDB analysis, ops.
* **Creation**: 20:49 — `3b2e6c3` Add backlog of analysis questions.
* **Creation**: 20:44 — `589c810` Add design document.
