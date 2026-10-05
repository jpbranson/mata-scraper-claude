---
type: Finding
title: Which days are bad
description: Not answerable yet; of the two days recorded, Friday had 19% of bus-polls 5+ min late and Thursday 17%.
tags: [delay, days]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[Q2]"]
sources:
  - id: q-q2
    resource: ../../analysis.sql
    title: analysis.sql [Q2]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [which days are especially bad?](../questions/bad-days.md)

# Answer

| Day | 5+ min late | Hours covered |
|---|---|---|
| Fri 2026-09-25 | 19% | 16.4 (to 20:21) |
| Thu 2026-09-24 | 17% | full day |

Two days can't say which days are bad.[^q-q2][^snapshot] It needs weeks of
data, weekends included.

The query also shows `hours`, first to last bus recorded, so partial days
are obvious (Wed: 0.9 h).

[^q-q2]: analysis.sql [Q2]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
