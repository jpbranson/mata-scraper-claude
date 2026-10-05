---
type: Plan
title: Next steps (started 2026-09-25)
description: Status of the "next steps" run (poller fixes, open questions, the question backlog, detour logging, findings page), and what still needs a human.
tags: [plan]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: flight-log-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FLIGHT_LOG.md
    title: FLIGHT_LOG.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# How to use this plan

Working plan for the "next steps" list (the table below). **To resume after
an interruption:** read this concept, check the Status table, and pick up at
the first step that isn't DONE. The run's log is in the
[update log](../log.md) under 2026-09-25 (newest first); its latest entry
says what was last in hand.

Status key: TODO · IN PROGRESS · DONE · WAITING (time-gated) · BLOCKED (needs a human)

Nothing is committed to git unless the user asks; uncommitted work is listed
under "Uncommitted changes".

# Plan and status

| # | Step | Status |
|---|---|---|
| 1 | Let the poller collect a week of data (until ~2026-10-01) | WAITING |
| 2a | Poller: poll on a fixed 10 s clock (was 10 s sleep *after* each poll → 11–14 s) | DONE — live since 20:12:38; verified (379 of 380 polls on the 10 s clock) |
| 2b | Poller: timestamp every `poller.log` line | DONE — live since 20:12:38; verified |
| 2c | Deploy 2a/2b (restart `mata-poller`), verify cadence + log in live data | DONE — you restarted at 20:12:38 (and again at 21:12:45); verified 21:15 |
| 3a | Run `analysis.sql`, record results (re-run after a week; human sanity check) | Ran + recorded in FINDINGS.md; WAITING (week of data) + needs your sanity check |
| 3b | Open question: ghost threshold (226xx buses, layover vs dead GPS) | DONE (on 1.8 days; recheck with a week) |
| 3c | Open question: speed unit (tracker `speed_raw` vs official feed / computed speed) | DONE (m/s); speed in our feed since 20:12, verified |
| 3d | Open question: bus capacity (40 at 100%?) | DONE (100% = 50 riders; riders = pct / 2) |
| 3e | Open question: late threshold (MATA's own on-time standard?) | DONE (kept 5 min; MATA window not public → human check) |
| 4a | QUESTIONS: bunching and effective headways | DONE (on 1.8 days) |
| 4b | QUESTIONS: where along a route delay accumulates | DONE (on 1.8 days) |
| 4c | QUESTIONS: missed service (cancelled trips, alerts) | DONE (on 1.8 days; by weekday needs weeks) |
| 4d | QUESTIONS: does our trip matching hold up vs official trip IDs | DONE (99.8% agree; 1 day of official data) |
| 4e | QUESTIONS: the rest of groups 1–4 (and group 5's stop-level waits) as the data allows | DONE for what 1.8 days allow; weekday/weather/events WAITING (weeks); detour impact after 5a + weeks |
| 5a | Deferred: detour logging (needed for "detour impact") | DONE — logging since 20:12:42 (`data/detours/`); verified |
| 5b | Deferred: our own `vehicle_positions.pb` — delete only if it gets in the way | DONE — checked, not in the way; kept, nothing changed |
| 6 | (Your request, 20:18) Commit + push; publish FINDINGS.md as a page | DONE — pushed; page published (private until you share it); FINDINGS.md refreshed to the same 20:21 snapshot |
| 7 | (Your request, 21:14) Move the page scripts into the repo; check the deploy | DONE — `findings_page/` committed and pushed; deploy verified |

The table is as the run left it on 2026-09-25 (times are CDT). FINDINGS.md
and QUESTIONS.md are now the [findings](../findings/index.md) and
[questions](../questions/index.md) in this bundle.

# For human review

(Items that need the user: decisions, things the agent couldn't do, sanity
checks.)

- ~~Deploy the poller changes (2c).~~ Done: you ran `.\ops\update.ps1` at
  20:12 (and again at 21:12); checked at 21:15, all four changes are live.
- **Sanity-check the route ranking (3a)** in
  [which routes run behind](../findings/routes-behind.md) against your own
  experience of the routes (step 5 of the [project](../project.md)'s plan),
  and rerun `analysis.sql` after a full week (~Oct 1).
- ~~Review and commit.~~ Done: committed and pushed to `main` at your
  request (2026-09-25, 20:18).
- **The findings page** ("Memphis Buses, Measured", listed under
  `/artifacts` in Claude Code or at claude.ai/code/artifacts) is private
  until you share it from its Share menu. It and the findings use data up to
  Fri 20:21, two hours before Friday's service ended; rebuild both from a
  fresh copy (see [findings page](../system/findings-page.md)) if you want
  Friday whole.
- **MATA's on-time window (3e).** Not public anywhere the agent could
  reach. The city's data hub page for "MATA On Time Performance"
  (data.memphistn.gov/datasets/mata-on-time-performance-1/about) links a
  "Data Dictionary" PDF on memegis.maps.arcgis.com that the browser pane
  refused; if you can open it (or ask MATA), and the window isn't "≤1 min
  early, ≤5 min late", change the two numbers in `[Q1]` of
  [analysis.sql](../../analysis.sql). See
  [late threshold](../decisions/late-threshold.md).

# Uncommitted changes

(none: everything up to the 21:35 entry of 2026-09-25 is committed and
pushed)
