---
type: Finding
title: Peak loads
description: Buses are rarely full; average loads are 1–11 riders, and every seat is taken (40+ riders) only on routes 50, 42 and 36, route 50 most.
tags: [load, ridership, crowding]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[LOAD]"]
sources:
  - id: q-load
    resource: ../../analysis.sql
    title: analysis.sql [LOAD]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [peak load by route and hour](../questions/peak-load.md). Riders =
load % ÷ 2, and 40 riders (80%) is every seat taken
([bus capacity](../decisions/bus-capacity.md)).

# Answer

- **Average** 1–11 riders on board; the 95th percentile 25–29 on 50, 42 and
  36 and under 25 elsewhere.[^q-load][^snapshot]
- **Every seat taken** (40+) only on 50 (1.1% of polls), 42 (0.2%), 36
  (0.1%).
- **Busiest hours differ:** 50 at 9, 36 at 15, 42 at 17.
- **The fullest:** every reading of 96%+ (MATA's maximum load) was route 50
  (Poplar) heading out to Exeter Rd, 08:40–13:10, e.g. bus 21212 for 16
  minutes Fri from 09:25.

[^q-load]: analysis.sql [LOAD]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
