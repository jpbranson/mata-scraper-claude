---
type: Plan
title: Next steps (started 2026-09-25)
description: Status of the "next steps" run (poller fixes, open questions, the question backlog, detour logging, findings page, the 12-day rerun, driver changes), and what still needs a human.
tags: [plan]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T05:18:00Z }
sources:
  - id: flight-log-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FLIGHT_LOG.md
    title: FLIGHT_LOG.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
  - id: update-log
    resource: ../log.md
    title: Update log, 2026-10-05
---

# How to use this plan

Working plan for the "next steps" list (the table below). **To resume after
an interruption:** read this concept, check the Status table, and pick up at
the first step that isn't DONE. The run's log is in the
[update log](../log.md) (newest first); its latest entry says what was last
in hand.

Status key: TODO · IN PROGRESS · DONE · WAITING (time-gated) · BLOCKED (needs a human)

Nothing is committed to git unless the user asks; uncommitted work is listed
under "Uncommitted changes".

# Plan and status

| # | Step | Status |
|---|---|---|
| 1 | Let the poller collect a week of data (until ~2026-10-01) | DONE — 12 service days by 2026-10-05 (8 weekdays, 2 Saturdays, 2 Sundays) |
| 2a | Poller: poll on a fixed 10 s clock (was 10 s sleep *after* each poll → 11–14 s) | DONE — live since 2026-09-25 20:12:38; verified |
| 2b | Poller: timestamp every `poller.log` line | DONE — live since 2026-09-25 20:12:38; verified |
| 2c | Deploy 2a/2b (restart `mata-poller`), verify cadence + log in live data | DONE — you restarted at 20:12:38 (and again at 21:12:45); verified 21:15 |
| 3a | Run `analysis.sql`, record results (re-run after a week; human sanity check) | DONE — rerun 2026-10-05 on 12 days ([snapshot](../findings/snapshot-2026-10-05.md)), every finding refreshed; BLOCKED on your sanity check |
| 3b | Open question: ghost threshold (226xx buses, layover vs dead GPS) | DONE — rechecked on 12 days, kept |
| 3c | Open question: speed unit (tracker `speed_raw` vs official feed / computed speed) | DONE — rechecked on 12 days (m/s) |
| 3d | Open question: bus capacity (40 at 100%?) | DONE — rechecked on 12 days (100% = 50 riders) |
| 3e | Open question: late threshold (MATA's own on-time standard?) | DONE — rechecked on 12 days, kept 5 min; MATA's window not public → human check |
| 4a | QUESTIONS: bunching and effective headways | DONE (12 days) |
| 4b | QUESTIONS: where along a route delay accumulates | DONE (12 days) |
| 4c | QUESTIONS: missed service (cancelled trips, alerts) | DONE (12 days, weekdays vs weekends); one weekday against another WAITING (weeks) |
| 4d | QUESTIONS: does our trip matching hold up vs official trip IDs | DONE (99.8% agree over 11 days of official data) |
| 4e | QUESTIONS: the rest of groups 1–4 (and group 5's stop-level waits) as the data allows | DONE for 12 days; one weekday against another, weather and events WAITING (weeks); detour impact WAITING (more detours) |
| 5a | Deferred: detour logging (needed for "detour impact") | DONE — logging since 2026-09-25 20:12:42 (`data/detours/`); verified |
| 5b | Deferred: our own `vehicle_positions.pb` — delete only if it gets in the way | DONE — checked, not in the way; kept, nothing changed |
| 6 | (Your request, 2026-09-25 20:18) Commit + push; publish FINDINGS.md as a page | DONE — pushed; page published (private until you share it) |
| 7 | (Your request, 2026-09-25 21:14) Move the page scripts into the repo; check the deploy | DONE — `findings_page/` committed and pushed; deploy verified |
| 8 | (Your request, 2026-10-05) When do drivers switch, what delay does it cause, which routes | DONE — [driver changes](../findings/driver-changes.md), `[RELIEF]` |
| 9 | (Your request, 2026-10-05) Add driver changes to the findings page | DONE — "Changing drivers" section, page versions 2 and 3 |
| 10 | (Your request, 2026-10-05) Verify the knowledge is accurate, comprehensive and up to date | DONE — every directory audited against the code and data, findings and decisions rerun on 12 days, `analysis.sql` fixed where 12 days showed it misleading |
| 11 | (Your request, 2026-10-05) Fix the backfill | DONE — `backfill_replay.py` matches past days to the timetable saved that day (`Timetable.saved`); tested on a copy |
| 12 | (Your request, 2026-10-05) Rebuild the findings page on the 12 days | DONE — version 4, published 2026-10-06 00:09 |
| 13 | (Your request, 2026-10-05) Commit and push | DONE — 2026-10-06, see `git log` |

# For human review

(Items that need the user: decisions, things the agent couldn't do, sanity
checks.)

- **Sanity-check the route ranking (3a)** in
  [which routes run behind](../findings/routes-behind.md) against your own
  experience of the routes: over 12 days routes 36 and 02 are the latest
  (26% of bus-polls 5+ min late), not 02 alone.
- **The findings page** is private until you share it from its Share
  menu ([findings page](../system/findings-page.md)).
- **MATA's on-time window (3e).** Not public anywhere the agent could
  reach. The city's data hub page for "MATA On Time Performance"
  (data.memphistn.gov/datasets/mata-on-time-performance-1/about) links a
  "Data Dictionary" PDF on memegis.maps.arcgis.com that the browser pane
  refused; if you can open it (or ask MATA), and the window isn't "≤1 min
  early, ≤5 min late", change the two numbers in `[Q1]` of
  [analysis.sql](../../analysis.sql). See
  [late threshold](../decisions/late-threshold.md).
- ~~Deploy with `.\ops\update.ps1`.~~ Done: you ran it at 00:16 on
  2026-10-06; both tasks restarted and the crosswalk stayed at topo 198282.
  Still to confirm: the 04:00 "timetable for 2026-10-06" line in
  `poller.log`, the first time the new `schedule.py` runs.

# Open data questions

From the 12-day rerun; none is needed for the core questions.

- Why route 42 was late all day on Sat 2026-10-03 (46% of bus-polls), with
  no rider message ([bad days](../findings/bad-days.md)).
- Why route 28 had three bad weekdays (09-25, 09-30, 10-02).
- `[SPEED_SLOW]` measures stretches in a straight line, which misreads
  loops; the timetable's route distances would fix it once the poller saves
  `stop_times.txt` beside `data/gtfs.zip` ([analysis.sql](../system/analysis-sql.md)).
  The findings page already measures them along the route, reading
  `gtfs.zip` from its copy.
- A stuck-counter filter for loads (bus 22609 sat at 100% for 53 minutes
  on 2026-09-30), and whether the 04:00–05:59 pull-out freezes should count
  as ghosts ([ghost trackers](../findings/ghost-trackers.md)).
- Trips MATA's dispatch adds (36 ad-hoc trip IDs) aren't in the timetable,
  so `trip_service` may count the scheduled trips they cover as never run
  ([missed service](../findings/missed-service.md)).

# Uncommitted changes

(none: everything up to the 2026-10-06 00:17 deployment entry is committed and pushed)
