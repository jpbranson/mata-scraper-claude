---
type: Project
title: MATA bus feed
description: Continuously record where every MATA (Memphis) bus is, show it on a live map, and keep enough history to answer which routes run behind, which days are bad, and how many people are riding.
resource: https://github.com/jpbranson/mata-scraper-claude
tags: [tracker, map, analysis]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
---

# Purpose

Continuously record where every MATA (Memphis) bus is, show it on a live map,
and keep enough history to answer questions like:

1. [Which routes constantly run behind?](questions/routes-behind.md)
2. [Which days are especially bad?](questions/bad-days.md)
3. [How many people are riding right now?](questions/riders-now.md)

The wider backlog of questions the data could answer is in
[questions/](questions/), and what the data says so far in
[findings/](findings/).

# Guiding rule

**The fewest moving parts that answer those questions.** One process
collects, one folder stores, one HTML page shows, one SQL file analyzes. No
database server, no web framework, no build step, no test suite beyond the
existing `--sample` offline check.

How the parts fit: [architecture](system/architecture.md). Where the data
comes from: [the SWIV tracker](feeds/swiv-tracker.md), [MATA's GTFS
timetable](feeds/gtfs-timetable.md) and [MATA's official
GTFS-Realtime feed](feeds/official-gtfs-rt.md). How it runs:
[running it](operations/running-it.md).

# Implementation plan

Steps 1–4 (poller, map, analysis, ops) are done.

5. **After a week of data:** run the queries, sanity-check against personal
   experience of the routes, then decide the open questions. Started early
   (2026-09-25, on 1.8 days): the open questions are settled on that data
   ([bus capacity](decisions/bus-capacity.md), [ghost
   threshold](decisions/ghost-threshold.md), [late
   threshold](decisions/late-threshold.md), [speed
   unit](decisions/speed-unit.md)), the question backlog is worked through,
   results in [findings/](findings/). Still to do: rerun on a full week and
   the sanity check. Tracked in [next steps](work/next-steps.md).

# Non-goals

- Computing our own delay. The vendor's reported delay is kept as the
  measure; the GTFS timetable is used only to name trips and show stop
  schedules, and actual − scheduled agrees with it anyway (see
  [self-computed schedule adherence](questions/self-computed-adherence.md)).
- Multi-agency support, a REST API, user accounts, alerting, dashboards
  beyond the one map page and the SQL file.
- Unit tests. The offline `--sample` run against
  [`vehicules.json`](datasets/sample-payload.md) is the regression check; if
  the parser changes, run it.
