---
type: Question
title: Should we compute schedule adherence ourselves?
description: Self-computed schedule adherence instead of the vendor's reported delay, a non-goal unless the vendor's values prove untrustworthy (not planned).
tags: [delay, timetable]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
answer_status: not-planned
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

Self-computed schedule adherence, instead of the vendor's number.

# Status

Not planned: a non-goal of the [project](../project.md). The timetable and
trip matching exist ([timetable and arrivals](../system/timetable-and-arrivals.md)),
and actual − scheduled agreed with the vendor's delay when checked. Only
worth it if the vendor's delay values prove untrustworthy; if ever needed,
the `sched` view in [analysis.sql](../system/analysis-sql.md) makes it a
one-line join.
