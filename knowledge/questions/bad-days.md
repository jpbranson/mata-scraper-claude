---
type: Question
title: Which days are especially bad?
description: Core question 2, comparing whole service days by how late buses ran (partial on 12 days; Sundays are the good days, weekdays and Saturdays alike; one weekday against another, weather and events wait for more weeks).
tags: [core, delay]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
answer_status: partial
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Which days are especially bad? The second of the three questions the project
exists to answer (see [project](../project.md)). Includes weekday vs weekend.

# How it's answered

`[Q2]` in [analysis.sql](../system/analysis-sql.md): per day, the hours
covered (first to last bus recorded; a short one is a partial day), the median
delay and the share of bus-polls 5+ minutes late.

# Data

The [tracker history](../datasets/positions.md), over many days.

# Status

Partial. Weekday vs weekend is answered on 12 days (8 weekdays, 2
Saturdays, 2 Sundays): `[Q2]`, in [bad days](../findings/bad-days.md).
Sundays are the good days; weekdays and Saturdays are alike, and a bad day
is a few routes' bad day. Still waiting: one weekday against another (one
or two of each so far) needs several weeks; `[Q2]` and `[HOUR]` + `dayname`
are ready for it. Weather and events: see
[ridership trend](ridership-trend.md).
