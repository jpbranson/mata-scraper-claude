---
type: Finding
title: When delay goes bad
description: The afternoon; 26–32% of bus-polls are 5+ min late at 15:00–17:59 against 5–7% before 7 a.m., and early running peaks at night.
tags: [delay, hours]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[HOUR]"]
sources:
  - id: q-hour
    resource: ../../analysis.sql
    title: analysis.sql [HOUR]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers the hour-of-day half of [when does it go bad?](../questions/when-it-goes-bad.md)

# Answer

- Share 5+ min late climbs from 5–7% before 7 a.m. to 17–20% through midday
  and **26–32% at 15:00–17:59**; median delay is 2 min only in those three
  hours.[^q-hour][^snapshot]
- Early running peaks at night (27% at 21:00, 40% at 22:00) and 4 a.m.
  (16%): evening schedules are slack. See [early running](early-running.md).
- Weekday vs weekend needs more weeks of data.

[^q-hour]: analysis.sql [HOUR]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
