---
type: Question
title: What headway do riders actually get?
description: Time between successive buses at a stop against the timetable's promised frequency (answered on 12 days).
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

Effective headway. Time between successive buses passing the same
`next_stop_name` in the same direction: actual frequency vs the timetable's
promised frequency.

# Data

Planned from the [tracker history](../datasets/positions.md) alone; answered
from the [arrivals log](../datasets/arrivals-log.md) against the
[saved timetables](../datasets/schedule-files.md).

# Status

Answered on 12 days (8 weekdays, 2 Saturdays, 2 Sundays): `[HEADWAY]`,
in [headways and bunching](../findings/headways.md). Run per stop, it
becomes [stop-level waits](stop-waits.md).
