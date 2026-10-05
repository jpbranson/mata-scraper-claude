---
type: Question
title: How many buses are out, against what the schedule needs?
description: Buses in service by hour against the trips the timetable has running, since dropped runs never show up as late (answered on 1.8 days).
tags: [missed-service]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
answer_status: answered
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Fleet in service by hour. Buses per route over the day vs what the schedule
implies. Dropped runs never show up as "late" (group 4 has MATA's own record
of them: see [missed service](missed-service.md)).

# Data

The [tracker history](../datasets/positions.md) and the
[saved timetables](../datasets/schedule-files.md).

# Status

Answered on 1.8 days: `[FLEET]`, in
[fleet in service](../findings/fleet-in-service.md).
