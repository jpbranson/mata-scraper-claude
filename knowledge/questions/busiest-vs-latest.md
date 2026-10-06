---
type: Question
title: Are the busiest routes the latest routes?
description: Crowding against delay by route, a hint whether boarding time causes delay (answered on 12 days).
tags: [load, delay]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
answer_status: answered
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Are the busiest routes the latest routes? Crowding vs delay by route. If
they coincide, dwell time (boarding) may be the delay cause.

# Data

The [tracker history](../datasets/positions.md) alone.

# Status

Answered on 12 days (8 weekdays, 2 Saturdays, 2 Sundays): `[LOAD_DELAY]`,
in [load vs delay](../findings/load-vs-delay.md). Whether boarding time
causes the delay, or late buses collect more riders, the data can't tell.
