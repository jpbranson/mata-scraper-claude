---
type: Question
title: How long do riders actually wait at the stop?
description: Stop-level wait times riders experience, missed trips included, against the timetable's promised gaps (answered on 12 days).
tags: [headway, missed-service]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:55Z }
answer_status: answered
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Stop-level wait times riders actually experience. The arrivals log
(`data/arrivals/`) has stop codes and times, so this is the
[headway](effective-headway.md) analysis run per stop, against the
timetable's promised gaps.

# Data

The [arrivals log](../datasets/arrivals-log.md) and the
[saved timetables](../datasets/schedule-files.md).

# Status

Answered on 12 days (8 weekdays, 2 Saturdays, 2 Sundays):
`[STOP_WAIT]`, in [stop waits](../findings/stop-waits.md).
