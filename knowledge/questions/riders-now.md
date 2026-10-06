---
type: Question
title: How many people are riding right now?
description: Core question 3, counting buses in service and riders on board from the latest poll (answered).
tags: [core, ridership, load]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
answer_status: answered
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

How many people are riding right now? The third of the three questions the
project exists to answer (see [project](../project.md)).

# How it's answered

`[Q3]` in [analysis.sql](../system/analysis-sql.md) reads
[`data/latest.json`](../datasets/latest-snapshot.md): buses in service, and
riders on board as `sum(occupancy_pct) // 2`, leaving out buses still for 30+
polls. The load % is riders out of 50 on every vehicle
([bus capacity](../decisions/bus-capacity.md)). The
[live map](../system/live-map.md) shows the same figure top-right.

# Status

Answered: `[Q3]`, in [riders right now](../findings/riders-now.md). Since
2026-10-05 it also works after service, when the latest poll has no
vehicles (0 buses, 0 riders).
