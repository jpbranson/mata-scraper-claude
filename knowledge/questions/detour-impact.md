---
type: Question
title: What do detours do to delay and ridership?
description: Delay and ridership on detoured vs normal days (waiting for weeks of the detour log, kept since 2026-09-25 20:12; by 2026-10-05 it held 19 short route detours, too few to answer).
tags: [detours, delay, ridership]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:55Z }
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
  - id: snapshot
    resource: ../findings/snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
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

Waiting: needs weeks of the detour log. By Mon 10-05 20:00 it held 19
route detours, most a few hours long: 39 from Fri 09-25 evening to Sun
09-27, 42 and the trolley Thu 10-01 evening (42 again Fri 10-02 morning),
seven routes Fri 10-02 evening, six to eight routes Sat 10-03 morning,
and 02 from Sat 10-03 noon to Sun 10-04 noon.[^snapshot] A first look,
each detour's share of polls 5+ min late against the same route at the
same hours on other days of its type, goes both ways: 57 on Fri 10-02
evening 36% against 7%, but 02 on Sat 10-03 15% against 46%, with only
one other Saturday to compare with.[^one-off] It needs
several detours per route and more ordinary days to compare against.

[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
