---
type: Question
title: Do buses bunch?
description: Whether buses of a route and direction run close together and leave long gaps behind them, the thing riders feel most (answered on 12 days).
tags: [headway]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:55Z }
answer_status: answered
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Bus bunching. Two buses on the same route and direction within a minute of
each other means a long gap behind them. Detectable from positions alone;
the thing riders feel most.

Group 3 of the backlog (service delivered vs promised). With
[effective headway](effective-headway.md) and
[where delay accumulates](where-delay-accumulates.md), the first to take on
after [ghost detection](ghost-buses.md).

# Data

Planned from the [tracker history](../datasets/positions.md) alone; answered
from the [arrivals log](../datasets/arrivals-log.md) against the
[saved timetables](../datasets/schedule-files.md).

# Status

Answered on 12 days (8 weekdays, 2 Saturdays, 2 Sundays): `[HEADWAY]`,
in [headways and bunching](../findings/headways.md).
