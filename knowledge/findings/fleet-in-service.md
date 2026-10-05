---
type: Finding
title: Fleet in service
description: For most of the day 3–8.5 fewer buses are out than trips in progress, the same shortfall as the missed trips.
tags: [missed-service, fleet]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[FLEET]"]
sources:
  - id: q-fleet
    resource: ../../analysis.sql
    title: analysis.sql [FLEET]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [fleet in service by hour](../questions/fleet-in-service.md).

# Answer

At half past each hour, buses seen vs trips in progress:[^q-fleet][^snapshot]

- Short by 3–8.5 buses most of the day, e.g. 08:30: 49 trips, 40.5 buses;
  13:30–15:30: 48–49 trips, 40–41 buses.
- About even 16:30–17:30.

The same shortfall as the [missed trips](missed-service.md).

[^q-fleet]: analysis.sql [FLEET]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
