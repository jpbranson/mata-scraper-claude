---
type: Question
title: Which buses' trackers stop reporting?
description: Ghost buses and GPS reliability, to settle before trusting anything else since bad trackers corrupt the delay stats (answered on 1.8 days; recheck after a week).
tags: [gps]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
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

Ghost buses / GPS reliability. Share of polls with high `unchanged_polls`,
by `equipment_no`. Chronically bad trackers corrupt the delay stats, so
settle this before trusting anything else.

The backlog's suggested order puts this first, since it validates everything
else; then [bunching](bunching.md) / [headways](effective-headway.md) and
[where delay accumulates](where-delay-accumulates.md).

# Data

The [tracker history](../datasets/positions.md); the
[official feed's vehicle positions](../datasets/official-vehicles.md) confirm
a dead tracker (their report times freeze too).

# Status

Answered on 1.8 days (recheck with a week of data): `[GPS]`, in
[ghost trackers](../findings/ghost-trackers.md); the rule it settled is the
[ghost threshold](../decisions/ghost-threshold.md).
