---
type: Question
title: How long do buses sit at the terminal, and do short layovers make late starts?
description: Layover length at each terminal from MATA's official positions, and whether short layovers predict late departures (answered on one day of official data).
tags: [official-feed, delay]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
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

Answered on Friday's official data, small numbers per route: `[LAYOVER]`,
in [layovers](../findings/layovers.md).
