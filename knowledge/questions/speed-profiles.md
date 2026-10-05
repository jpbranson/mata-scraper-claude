---
type: Question
title: Where and when are buses slow?
description: Speed by route segment and hour, showing where bus lanes or signal priority would help (answered on 1.8 days).
tags: [speed]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
answer_status: answered
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Speed profiles. Average `speed_raw` (metres per second, see
[speed unit](../decisions/speed-unit.md)) by route segment and hour. Slow
segments on a map = where bus lanes or signal priority would help.

# Data

The [tracker history](../datasets/positions.md); stop-to-stop segments from
the [arrivals log](../datasets/arrivals-log.md).

# Status

Answered on 1.8 days: `[SPEED]` (by route, all day and at the peaks) and
`[SPEED_SLOW]` (the slowest stop-to-stop stretches of 300 m+), in
[speed](../findings/speed.md).
