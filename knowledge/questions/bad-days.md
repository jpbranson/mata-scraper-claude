---
type: Question
title: Which days are especially bad?
description: Core question 2, comparing whole service days by how late buses ran (waiting for weeks of data; two weekdays can't say which days are bad).
tags: [core, delay]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
answer_status: waiting
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

Waiting. The query runs ([bad days](../findings/bad-days.md)), but two
weekdays can't say which days are bad. Weekday vs weekend needs weeks of data;
the queries for it (`[Q2]`, `[HOUR]` + `dayname`, `[RIDERS_DAY]`) are ready.
Weather and events: see [ridership trend](ridership-trend.md).
