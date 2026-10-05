---
type: Finding
title: Where buses fill
description: Buses fill at the downtown hubs, above all Second @ Jackson (823 riders on per day), the first stop out of William Hudson for seven routes.
tags: [ridership, load, stops]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[BOARDINGS]"]
sources:
  - id: q-boardings
    resource: ../../analysis.sql
    title: analysis.sql [BOARDINGS]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [where do buses fill and empty?](../questions/where-buses-fill.md)

# Answer

Riders on per day:[^q-boardings][^snapshot]

| Stop | On per day | Note |
|---|---|---|
| Second @ Jackson | 823 | the first stop out of William Hudson for 01, 04, 07, 12, 13, 50, 57 |
| Second @ Market | 382 | |
| Third @ Mill | 148 | |
| Airways Blvd @ Winchester | 133 | |
| Directors Row @ Brooks | 129 | |
| AW Willis @ Third | 124 | |
| Getwell @ Mallory | 99 | |

# Method

Each change in a bus's load between polls (up to 30 s apart) goes to the
stop it was serving, its next stop in the earlier poll. Net changes between
polls only, so the figures are floors.

[^q-boardings]: analysis.sql [BOARDINGS]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
