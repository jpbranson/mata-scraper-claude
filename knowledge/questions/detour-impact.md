---
type: Question
title: What do detours do to delay and ridership?
description: Delay and ridership on detoured vs normal days (waiting for weeks of the detour log, kept since 2026-09-25 20:12).
tags: [detours, delay, ridership]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
answer_status: waiting
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Detour impact. Delay and ridership on detoured vs normal days.

Group 5 of the backlog (needs more than the original design).

# Data

A record of which routes were detoured when: the poller now logs detours
hourly ([detour logger](../system/detour-logger.md),
[detour log](../datasets/detour-log.md) in `data/detours/`), since
2026-09-25 at 20:12. Plus the [tracker history](../datasets/positions.md)
for delay and load.

# Status

Waiting: needs weeks of the detour log.
