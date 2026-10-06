---
type: Question
title: When do drivers change, and what delay does it cause?
description: When and where operators relieve each other on a bus that stays in service, how long the handover holds the bus, and which routes it hurts (partly answered; only the garage reliefs on route 42 are visible).
tags: [delay, reliefs, blocks]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T03:21:00Z }
answer_status: partial
sources:
  - id: user-request
    resource: "The user's question, 2026-10-05, about 22:00 CDT"
    title: "Analyze the bus movement and delay data: when do drivers switch? How long of a delay does that usually cause? Are any routes particularly bad for this kind of delay?"
---

# Question

When do drivers switch, how long a delay does a switch usually cause, and
are some routes particularly bad for it?[^user-request]

# Data

Neither feed names the operator or the run, so changes have to be
inferred: the [GTFS timetable's](../feeds/gtfs-timetable.md) blocks say
which buses must change drivers, the [position
history](../datasets/positions.md) shows where a bus stops and what delay
it gains there, and the [official vehicle
positions](../datasets/official-vehicles.md) say which bus ran each trip
of a block.

# Status

Partly answered on 7 weekdays, 2 Saturdays and 2 Sundays: `[RELIEF]`, in
[driver changes](../findings/driver-changes.md). Route 42's changes at the
garage are clear; everywhere else they happen out of sight, most likely
inside terminal layovers. A run or operator ID from MATA (a run-cut, or the
blocks' relief points) would answer the rest.

[^user-request]: The user's question, 2026-10-05
