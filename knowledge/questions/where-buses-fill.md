---
type: Question
title: Where do buses fill and empty?
description: A rough boarding and alighting map from changes in load between polls, without passenger-count data (answered on 12 days).
tags: [load, ridership]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
answer_status: answered
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Where do buses fill and empty? Change in `occupancy_pct` between consecutive
polls, grouped by `next_stop_name`: a rough boarding/alighting map without
passenger-count data.

# Data

The [tracker history](../datasets/positions.md) alone.

# Status

Answered on 12 days (8 weekdays, 2 Saturdays, 2 Sundays): `[BOARDINGS]`,
in [boardings](../findings/boardings.md). The per-weekday, Saturday and
Sunday figures, and the boardings at William Hudson split from the first
stop out, come from one-off queries.
