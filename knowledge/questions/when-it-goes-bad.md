---
type: Question
title: When does it go bad?
description: Delay by hour of day and weekday, separating rush-hour congestion from always (by hour answered; by weekday waits for weeks of data).
tags: [delay]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
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

Partial. By hour of day, answered on 1.8 days: `[HOUR]`, in
[time of day](../findings/time-of-day.md). Weekday vs weekend needs weeks of
data; `[HOUR]` + `dayname` is ready for it.
