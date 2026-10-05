---
type: Finding
title: Which direction is worse
description: Leaving downtown; on 10 of the 17 bus routes that reach William Hudson, the trip away from it is 5+ min late at least 10 points more often.
tags: [delay, routes]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[DIRECTION]"]
sources:
  - id: q-direction
    resource: ../../analysis.sql
    title: analysis.sql [DIRECTION]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [which direction is worse?](../questions/which-direction.md)

# Answer

On 10 of the 17 bus routes that reach William Hudson, the trip *away* from
it is 5+ min late at least 10 points more often:[^q-direction][^snapshot]

| Route | Outbound (away from William Hudson) | Inbound |
|---|---|---|
| 52 (to Methodist Hospital) | 42% | 11% |
| 57 | 32% | 5% |
| 34 | 32% | 4% |
| 02 | 51–54% | 26% |
| 39 | 18–41% | 14% |
| 13 | 28% | 6% |
| 11 | 21% | 5% |
| 01 | 30% | 13% |

Only 28 and 40 lean the other way.

[^q-direction]: analysis.sql [DIRECTION]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
