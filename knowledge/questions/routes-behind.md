---
type: Question
title: Which routes constantly run behind?
description: Core question 1, ranking routes by how often their buses run 5+ minutes late (answered on 12 days; human sanity check pending).
tags: [core, delay]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
answer_status: answered
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
  - id: flight-log-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FLIGHT_LOG.md
    title: FLIGHT_LOG.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Which routes constantly run behind? The first of the three questions the
project exists to answer (see [project](../project.md)).

# How it's answered

`[Q1]` in [analysis.sql](../system/analysis-sql.md): per route, the share of
bus-polls 5+ minutes late, the median delay, the share early and the share on
time, over the rows worth trusting for delay (the `good` view). On time is at
most 1 minute early and 5 late; see
[late threshold](../decisions/late-threshold.md).

# Data

The [tracker history](../datasets/positions.md) alone.

# Status

Answered on 12 days (8 weekdays, 2 Saturdays, 2 Sundays): `[Q1]`, in
[which routes run behind](../findings/routes-behind.md), with a weekday-only
ranking beside it. Still to do (step 5 of the [project](../project.md)'s
plan): a human sanity check of the ranking against experience of the routes
([next steps](../work/next-steps.md), 3a). Ranking routes on weekends, two
of each so far, needs more weeks.
