---
type: Question
title: How long do buses sit at the terminal, and do short layovers make late starts?
description: Layover length at each terminal from MATA's official positions, and whether short layovers predict late departures (answered on 11 days of official data).
tags: [official-feed, delay]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:17:00Z }
answer_status: answered
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Layover length. The official positions keep a bus parked at its next trip's
first stop while the tracker drops it: how long buses actually sit at each
terminal, and whether short layovers predict late departures.

# Data

The [official vehicle positions](../datasets/official-vehicles.md).

# Status

Answered on 11 days of MATA's official feed (7 weekdays, 2 Saturdays, 2
Sundays), 51–377 trips per route: `[LAYOVER]`, counted from when the bus
stopped moving, in [layovers](../findings/layovers.md).
