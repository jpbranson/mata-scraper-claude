---
type: Question
title: Where along the route does delay accumulate?
description: Which stops on each route add delay, pinpointing the intersection or segment causing it (answered on 12 days).
tags: [delay]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
answer_status: answered
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
  - id: flight-log-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FLIGHT_LOG.md
    title: FLIGHT_LOG.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Where along the route does delay accumulate? Delay by `next_stop_name` per
route: pinpoints the intersection or segment causing it.

Group 1 of the backlog (delay, deeper than "which routes"). With
[bunching](bunching.md) and [effective headway](effective-headway.md), the
first to take on after [ghost detection](ghost-buses.md).

# Data

Planned from the [tracker history](../datasets/positions.md) alone; answered
from the [arrivals log](../datasets/arrivals-log.md) (the `arrivals_due`
view, line ends left out).

# Status

Answered on 12 days (8 weekdays, 2 Saturdays, 2 Sundays): `[WHERE]`, delay
gained per stop in bus-minutes per day, in
[where delay builds up](../findings/where-delay-builds.md).
