---
type: Question
title: Where and how often do buses run early?
description: Early running, which strands riders and is invisible in on-time percentages (answered on 12 days).
tags: [delay]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
answer_status: answered
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Early running: negative `delay_seconds`. Leaving early is worse for riders
than a few minutes late and is invisible in on-time percentages.

# Data

The [tracker history](../datasets/positions.md); departures from a timepoint
come from the [arrivals log](../datasets/arrivals-log.md).

# Status

Answered on 12 days (8 weekdays, 2 Saturdays, 2 Sundays): `[EARLY]`
(timepoints where buses leave early) and `[Q1]`'s `share_early`, in
[early running](../findings/early-running.md).
From the start of a line, see [departures](../findings/departures.md).
