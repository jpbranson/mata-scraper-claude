---
type: Question
title: Which direction is worse?
description: Whether a route's buses run later one way than the other (answered on 12 days).
tags: [delay]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
answer_status: answered
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Which direction is worse? Group by `destination` (headsign) within a route.
Inbound mornings and outbound evenings often differ a lot.

# Data

The [tracker history](../datasets/positions.md) alone.

# Status

Answered on 12 days (8 weekdays, 2 Saturdays, 2 Sundays): `[DIRECTION]`,
in [direction](../findings/direction.md), split by time of day and day type
there.
