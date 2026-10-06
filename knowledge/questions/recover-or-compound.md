---
type: Question
title: Does delay recover or compound?
description: Whether a bus late at the start of a trip catches up or falls further behind, telling wrong schedules from stuck buses (answered on 12 days).
tags: [delay]
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

Does delay recover or compound? Follow one bus through a run: does a bus
5 min late at the start end 5 min late or 15? Wrong schedules vs buses
getting stuck.

A run ends where the route or headsign changes: buses on routes 13 and 40
alternate between them all day (GTFS blocks 4001/4002, see
[GTFS timetable](../feeds/gtfs-timetable.md)), and the delay resets at each
handoff.

# Data

Planned from the [tracker history](../datasets/positions.md); answered per
trip from the [arrivals log](../datasets/arrivals-log.md), line ends left
out.

# Status

Answered on 12 days (8 weekdays, 2 Saturdays, 2 Sundays): `[WHERE_ROUTE]`
(delay at a trip's last logged stop minus its first), in
[where delay builds up](../findings/where-delay-builds.md).
