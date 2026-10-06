---
type: Question
title: Does our trip matching hold up?
description: How often the trip schedule.py infers for a bus is the trip MATA's official feed names (answered on 11 days of official data).
tags: [official-feed, timetable]
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

Does our trip matching hold up? `schedule.py`'s `trip_id` (see
[timetable and arrivals](../system/timetable-and-arrivals.md)) vs the
official one for the same bus (fleet number = `equipment_no`), across whole
days rather than one snapshot.

# Data

The [tracker history](../datasets/positions.md) and the
[official vehicle positions](../datasets/official-vehicles.md).

# Status

Answered on 11 days of official data, Fri 09-25 to Mon 10-05 (99.7% agree,
99.8% leaving out the trips MATA's dispatch adds): `[TRIPMATCH]`, in
[trip matching](../findings/trip-matching.md).
