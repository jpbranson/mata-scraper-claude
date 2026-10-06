---
type: Question
title: When does it go bad?
description: Delay by hour of day and weekday, separating rush-hour congestion from always (by hour for weekdays, Saturdays and Sundays answered on 12 days; one weekday against another waits for more weeks).
tags: [delay]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
answer_status: partial
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

When does it go bad? Delay by hour of day × weekday. Separates rush-hour
congestion from "always".

# Data

The [tracker history](../datasets/positions.md), over weeks for the weekday
part.

# Status

Partial. By hour of day for weekdays, Saturdays and Sundays, answered on 12
days (8 weekdays, 2 Saturdays, 2 Sundays): `[HOUR]` with the day type added
to the `GROUP BY`, in [time of day](../findings/time-of-day.md). One
weekday against another (one or two of each so far) needs more weeks;
`[HOUR]` + `dayname` is ready for it.
