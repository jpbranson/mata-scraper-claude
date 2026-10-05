---
type: Question
title: How does ridership vary by day of week, weather and events?
description: Daily rider-minutes as one trend line, where games and storms would show as spikes or dips (per-day totals answered; day of week, weather and events wait for weeks of data).
tags: [ridership]
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

Ridership by day of week / weather / events. Daily rider-minutes as one
trend line; games and storms show as spikes or dips.

# Data

The [tracker history](../datasets/positions.md) over weeks; weather and
events also need outside data.

# Status

Partial. Riding per day (rider-hours, peak on board, boardings) is answered
for Thursday and Friday: `[RIDERS_DAY]`, in
[riders per day](../findings/riders-per-day.md). Day of week needs weeks of
data; weather and events need weeks plus outside data. `[RIDERS_DAY]` is
ready for it.
