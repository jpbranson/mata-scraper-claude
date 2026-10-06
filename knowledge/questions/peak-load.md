---
type: Question
title: How full do buses get, by route and hour?
description: Peak load by route and hour, showing which routes get uncomfortably full and when (answered on 12 days).
tags: [load, ridership]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
answer_status: answered
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Peak load by route and hour. Max / percentile of `occupancy_pct`, not the
sum: which routes get uncomfortably full, and when.

Group 2 of the backlog (ridership and crowding). Riders on board are
`occupancy_pct / 2` ([bus capacity](../decisions/bus-capacity.md)).

# Data

The [tracker history](../datasets/positions.md) alone.

# Status

Answered on 12 days (8 weekdays, 2 Saturdays, 2 Sundays): `[LOAD]`, in
[peak loads](../findings/peak-loads.md). The weekday and weekend split and
the weekday busiest hours come from one-off queries (the same query by day
type).
