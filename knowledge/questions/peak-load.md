---
type: Question
title: How full do buses get, by route and hour?
description: Peak load by route and hour, showing which routes get uncomfortably full and when (answered on 1.8 days).
tags: [load, ridership]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
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

Answered on 1.8 days: `[LOAD]`, in [peak loads](../findings/peak-loads.md).
