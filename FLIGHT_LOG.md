# Flight log: next steps (started 2026-09-25)

Working log for the "next steps" list (see the plan below). **To resume after
an interruption:** read this file, check the Status table, and pick up at the
first step that isn't DONE. The Log at the bottom says what was last in hand.

Status key: TODO · IN PROGRESS · DONE · WAITING (time-gated) · BLOCKED (needs a human)

Nothing is committed to git unless the user asks; uncommitted work is listed
under "Uncommitted changes".

## Plan and status

| # | Step | Status |
|---|---|---|
| 1 | Let the poller collect a week of data (until ~2026-10-01) | WAITING |
| 2a | Poller: poll on a fixed 10 s clock (was 10 s sleep *after* each poll → 11–14 s) | Code written + live-tested; NOT deployed (see 2c) |
| 2b | Poller: timestamp every `poller.log` line | Code written + live-tested; NOT deployed (see 2c) |
| 2c | Deploy 2a/2b (restart `mata-poller`), verify cadence + log in live data | BLOCKED (needs you: run `.\ops\update.ps1`) |
| 3a | Run `analysis.sql`, record results (re-run after a week; human sanity check) | Ran + recorded in FINDINGS.md; WAITING (week of data) + needs your sanity check |
| 3b | Open question: ghost threshold (226xx buses, layover vs dead GPS) | DONE (on 1.8 days; recheck with a week) |
| 3c | Open question: speed unit (tracker `speed_raw` vs official feed / computed speed) | DONE (m/s); poller change NOT deployed (see 2c) |
| 3d | Open question: bus capacity (40 at 100%?) | DONE (100% = 50 riders; riders = pct / 2) |
| 3e | Open question: late threshold (MATA's own on-time standard?) | DONE (kept 5 min; MATA window not public → human check) |
| 4a | QUESTIONS: bunching and effective headways | DONE (on 1.8 days) |
| 4b | QUESTIONS: where along a route delay accumulates | DONE (on 1.8 days) |
| 4c | QUESTIONS: missed service (cancelled trips, alerts) | DONE (on 1.8 days; by weekday needs weeks) |
| 4d | QUESTIONS: does our trip matching hold up vs official trip IDs | DONE (99.8% agree; 1 day of official data) |
| 4e | QUESTIONS: the rest of groups 1–4 (and group 5's stop-level waits) as the data allows | DONE for what 1.8 days allow; weekday/weather/events WAITING (weeks); detour impact after 5a + weeks |
| 5a | Deferred: detour logging (needed for "detour impact") | Code written + live-tested; NOT deployed (see 2c) |
| 5b | Deferred: our own `vehicle_positions.pb` — delete only if it gets in the way | DONE — checked, not in the way; kept, nothing changed |
| 6 | (Your request, 20:18) Commit + push; publish FINDINGS.md as a page | DONE — pushed; page published (private until you share it); FINDINGS.md refreshed to the same 20:21 snapshot |

## For human review

(Items that need you: decisions, things I couldn't do, sanity checks.)

- **Deploy the poller changes (2c).** The running poller still has the old
  code (Python loaded it at 05:45). I can't restart it: this shell gets
  "access denied" on the task's processes, and auto mode refused the attempt
  as interfering with a running workload. From your own PowerShell in the
  repo folder: `.\ops\update.ps1` (restarts both tasks; a few seconds of
  data lost). Then check `data\poller.log` ends in lines like
  `2026-09-25 19:09:20 31 vehicles, 26 moved`, 10 s apart. All the poller
  changes (2a, 2b, 3c speed in the feed, 5a detour log) are in, so one
  restart deploys them all; `data\detours\` should appear within a minute.
- **Sanity-check the route ranking (3a)** in FINDINGS.md against your own
  experience of the routes (DESIGN step 5), and rerun `analysis.sql` after
  a full week (~Oct 1).
- ~~Review and commit.~~ Done: committed and pushed to `main` at your
  request (2026-09-25, 20:18).
- **The findings page** ("Memphis Buses, Measured", listed under
  `/artifacts` in Claude Code or at claude.ai/code/artifacts) is private
  until you share it from its Share menu. It and FINDINGS.md use data up to Fri 20:21,
  two hours before Friday's service ended; rebuild both from a fresh copy
  (scratchpad `page_data.py` + `build_page.py`) if you want Friday whole.
- **MATA's on-time window (3e).** Not public anywhere I could reach. The
  city's data hub page for "MATA On Time Performance"
  (data.memphistn.gov/datasets/mata-on-time-performance-1/about) links a
  "Data Dictionary" PDF on memegis.maps.arcgis.com that the browser pane
  refused; if you can open it (or ask MATA), and the window isn't "≤1 min
  early, ≤5 min late", change the two numbers in `[Q1]` of analysis.sql.

## Uncommitted changes

(none yet)

## Log (newest last)

(Times from 19:16 on were corrected at 20:25 from file timestamps; I had
first logged guessed clock times, several hours off.)

- 2026-09-25 19:07 CDT — Started. Baseline health check: poller running since
  Wed night; 1.8 service days of history (Thu full, Fri so far); official
  archive since Fri 05:45. Poll gaps median 11 s, p90 13–14 s. ~1.5% of polls
  fail (vendor timeouts/5xx). Found this shell can't terminate the task's
  python processes (OpenProcess → access denied), so restarting the poller
  may need an unsandboxed command or you (`.\ops\update.ps1`).
- 19:11 — 2a/2b coded. `--sample` check passes. Live test (scratchpad copy of
  the loop, all output paths redirected to `scratchpad/testdata`, 75 s): polls
  at exactly 1790381360, …370, …380 … (gaps 10 s after the first), log lines
  stamped `2026-09-25 19:09:20 31 vehicles, 26 moved`. Restart script:
  `scratchpad/restart_poller.ps1` (waits for latest.json to change, +2 s,
  stops task, kills orphan python, starts task).
- 19:14 — Restart NOT done: auto mode refused my next action as "Interfere
  With Workloads". Leaving the live poller alone; 2c goes to human review.
  Moving on; poller changes from later steps get tested the same way
  (scratchpad copy) and deployed together by you.
- ~19:16 — DESIGN.md updated for 2a/2b (fixed clock; stamped log lines).
  3a: analysis runs from `scratchpad/run_sql.py FILE [TAG]` over a copy made
  by `scratchpad/sync_data.py` (never query the live files). Ran
  analysis.sql unchanged; results in new FINDINGS.md. Changed Q2 to show
  `hours` covered (Wed was a 0.9 h sliver). Next: 3b ghost threshold.
- ~19:21 — 3b done. Scripts `scratchpad/ghost*.py`. Streaks of 30+ still polls
  are layovers (127/183) and holds (45); dead trackers (8) end in a 200 m+
  jump and are mostly 1–5 min; official report age freezes too. Delay
  unaffected, route shares ±1.2 pts. Bus 458: 15% ghost rows. Added to
  analysis.sql: `dist_m` macro, `ghost_rows` view, `[GPS]` query, tags
  [Q1]–[Q3]. DESIGN.md: known-limits wording, map marker, data model, SQL
  block synced (Q2 hours, Q3 unnest), open question marked settled.
  FINDINGS.md section written. Next: 3c speed unit.
- ~19:24 — 3c done: m/s (official speed == speed_raw in 97% of 2,557 moving
  same-report pairs; distance/(speed×time) = 1.03). `cadavl_to_gtfs_rt.py`:
  `SPEED_UNIT`/`_SPEED_TO_MS` replaced by `MAX_SPEED_MS = 40`, feed writes
  speed (≤ 40). probe_cadence.py output/docstring updated. `--sample` OK
  (41/41 buses carry speed). DESIGN.md (known limits, probes, data model,
  open question), QUESTIONS.md (speed profiles), FINDINGS.md updated.
  Next: 3d capacity.
- ~19:33 — 3d done. All 340,389 load readings are even and cover every even
  value 0–100 → the vendor's 100% is 50 riders on every vehicle. MATA's
  2012 SRTP (matatransit.com, MATA_SRTP_Plan_APPENDICES.pdf, Figure 4-4):
  40-ft bus 40 seats / max load 48. Official occupancy categories are
  fixed bands (STANDING from ~11 riders), useless for crowding.
  Changed: map.html `CAPACITY = 50` (+comment), analysis.sql [Q3] →
  `sum(occupancy_pct) // 2` (144 riders at 19:10 Fri), DESIGN.md (known
  limits, map text, data model, SQL block, open question), FINDINGS.md.
  Web research notes: CPTDB fleet wiki 403s; the city's OTP data
  dictionary PDF host (memegis.maps.arcgis.com) was refused in the browser.
  Next: 3e late threshold (research mostly done: no published MATA window).
- ~19:36 — 3e done: kept 5 min. Vendor never says "1 min" (on time = ±1 min).
  [Q1] gains `share_early` (< -60 s) and `on_time` (-60..300 s). On-time
  73% of polls, 75% at timepoints, 53% at first-stop departures (closest
  to MATA's published 54–65%). Script `scratchpad/otp.py`. DESIGN.md: new
  known limit (whole minutes, ±1 min on time), "Delay is capped" note on
  old 0-valued rows (still flagged capped, so excluded), SQL block Q1,
  open question. FINDINGS.md section. Step 3 complete except 3a's
  week-of-data rerun + your sanity check. Next: 4a bunching/headways.
- ~19:44 — 4a + 4c done (4c done alongside because missed trips explained
  the first headway results). analysis.sql gained views `arrivals`,
  `sched` (flattens data/schedule JSON), `off_vehicles`,
  `off_trip_updates`, `off_alerts`, `arrivals_due`, `trip_service`, and
  queries [HEADWAY], [MISSED], [MISSED_HOUR]. Bunching ~nil (5 of 64,818
  pairs); missed trips 13% Thu / 17% Fri; only 27 of 99 Fri misses marked
  CANCELED. Arrivals log catches ~83–85% of stops per trip (checked with
  scratchpad/coverage.sql). Tracker vs official on which trips ran: 434 of
  441. FINDINGS.md sections written. Next: 4d trip matching (row level).
- ~19:45 — 4b done: analysis.sql `stops` view (stops.csv) + [WHERE] (delay
  gained per stop, bus-min/day) + [WHERE_ROUTE] (start vs end delay per
  trip; also answers group 1 "recover or compound"). Top: route 36 at
  American Way @ Getwell (+3.1 min/pass). Most routes start 2–6 min late
  and recover; 100, 02, 36 compound. FINDINGS.md section written.
- ~19:47 — 4d done: [TRIPMATCH] in analysis.sql. 99.8% agreement where we
  name a trip (58,429 reports); disagreements = other direction at
  turnarounds; 2.7% none (no next stop / 1h+). Next: 4e, the rest of the
  QUESTIONS backlog, one question at a time.
- ~19:55 — 4e done as far as 1.8 days allow. analysis.sql: `timepoints` view;
  queries [DIRECTION] [HOUR] [EARLY] [LOAD] [LOAD_DELAY] [RIDERS_DAY]
  [BOARDINGS] [FLEET] [SPEED] [SPEED_SLOW] [PREDICT] [LAYOVER] [STOP_WAIT]
  (each run and checked; SPEED_SLOW reworked to stop-to-stop segments ≥
  300 m; LAYOVER uses first logged stop; STOP_WAIT imputes unlogged
  departures). FINDINGS.md: groups 1–5 written, "not answerable yet" list.
  Next: tidy analysis.sql (views first, queries by group), run it whole,
  then 5a detour logging.
- ~19:57 — analysis.sql reorganized (views, then three questions, open
  questions, QUESTIONS groups 1–5; CRLF kept). Whole file runs clean via
  scratchpad/run_sql.py: 23 tagged queries, 54 s. DESIGN.md §4 lists the
  views. Next: 5a detour logging.
- ~20:01 — 5a coded: `cadavl_detours.DetourLog` (hourly /topo/refresh +
  /iv/message → data/detours/dt=<UTC>/detours.jsonl.gz when changed; stop
  IDs → stop codes via stops.csv; `parse_detours(payload, route_for)`;
  empty `update` → no detours). Poller: lazy `import cadavl_detours` in
  run_poller (same pattern as build_crosswalk), `detours.update(...)` after
  the official feed, own try/except. Tests: py_compile, both `--sample`
  runs, __main__-then-import order, live loop 45 s into scratch (route 39
  detour + 3 messages logged, 1.9 KB; polls still on 10 s ticks). DESIGN.md
  (architecture, components §5, data sources, data model, needs, failure
  modes), QUESTIONS.md, FINDINGS.md updated. Next: 5b.
- ~20:02 — 5b: checked, `vehicle_positions.pb` isn't in the way (one small
  write per poll, no reader); kept, no change.
- ~20:08 — Correction found while reviewing FINDINGS.md: at a line's end the
  tracker logs the bus's *departure* credited to the trip just finished
  (headsign flips late), so line-end "arrivals" looked 22% early and the
  "53% on time at first stops" figure was wrong. Fix: `line_ends` view,
  excluded in `arrivals_due` (so [WHERE] [WHERE_ROUTE] [EARLY] [HEADWAY]
  [SPEED_SLOW] [LAYOVER] [STOP_WAIT] no longer see them), new [DEPART]
  query timing departures from MATA's feed (59% on time, median 4.3 min
  late, 40% 5+ late, 1% early). Reran analysis.sql whole (24 queries,
  clean) and updated every affected figure in FINDINGS.md and DESIGN.md
  (late threshold, schedule.py limits, §4 view list). Scratch checks:
  scratchpad/ends.sql, headway_extra.sql.
- ~20:09 — All steps worked through. Open: 1 (waiting for a week, ~Oct 1),
  2c deploy (you), 3a rerun + sanity check (you, after Oct 1), MATA's
  on-time window (you, optional).
- 20:18 — Your request: commit and push (done), then publish FINDINGS.md
  as a page. Log times above corrected from file timestamps.
- 20:26 — Page data: `scratchpad/page_data.py` over a copy of data/ taken at
  20:21 → `page_data.json` (every number the page draws) + `numbers.txt`.
- 21:04 — Page published as a private artifact, "Memphis Buses, Measured"
  (`scratchpad/findings_template.html` + `build_page.py` → `findings.html`).
  Checked with headless Chrome screenshots at 1280 px and 375 px, light and
  dark (the in-app browser's screenshots timed out); fixed garbled
  characters (no charset), label collisions, the phone layout (a CSS
  specificity bug kept figures at 55% width).
- 21:07 — analysis.sql `[HEADWAY]`: windows now `ORDER BY t, t_sched`. Two
  buses logged in the same second were ordered at random, so the bunched
  and overtake counts changed between runs (4 or 5 bunched). Now 6 every
  time, the same 6 FINDINGS.md already named.
- 21:09 — FINDINGS.md refreshed to the 20:21 copy (analysis.sql rerun whole
  into `scratchpad/full_run_2021.txt`, plus `scratchpad/checks.py` for the
  one-off figures), so the file and the page agree.
