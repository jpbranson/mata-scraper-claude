---
type: Question
title: Are the countdowns riders see honest?
description: How MATA's official arrival predictions compare with when the bus actually came, by how far ahead they were made (answered on 11 days of official data).
tags: [official-feed]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
answer_status: answered
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Are the countdowns riders see honest? Compare each prediction in
`trip_updates.jsonl.gz` with when the bus actually came (`data/arrivals/`),
by how far ahead it was made.

# Method notes

- Join on trip and stop: the official `stop_id` = `0:` + the arrival's
  `stop`.
- The arrival's `vehicle` is the tracker's ID, not the fleet number.
- Only trips with a `vehicle_id` carry real predictions; the rest are the
  timetable.

# Data

The [official trip updates](../datasets/official-trip-updates.md) and the
[arrivals log](../datasets/arrivals-log.md).

# Status

Answered on 11 days of official data, Fri 09-25 to Mon 10-05 (2.7 million
predictions): `[PREDICT]`, in [countdowns](../findings/countdowns.md).
