---
type: Finding
title: Speeds and slow stretches
description: Buses average 11.5–18.5 mph including stops on most routes; the slowest stretches are the trolley on Main and route 42 on Cleveland and Bellevue.
tags: [speed, routes]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[SPEED]", "[SPEED_SLOW]"]
sources:
  - id: q-speed
    resource: ../../analysis.sql
    title: analysis.sql [SPEED]
  - id: q-speed_slow
    resource: ../../analysis.sql
    title: analysis.sql [SPEED_SLOW]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [speed profiles](../questions/speed-profiles.md). The tracker's
speed is metres per second ([speed unit](../decisions/speed-unit.md)); the
figures here are mph.

# By route

- Average speed including stops: 11.5–18.5 mph on most routes (01
  slowest), 24 mph on 28, trolley 4.4.[^q-speed][^snapshot]
- Stopped 25–47% of the time (trolley 62%).
- Peak and midday differ by about 1 mph on most routes (28: 3 mph).

# Slowest stretches

Stop-to-stop segments of 300 m or more:[^q-speed_slow]

| Route | Stretch | mph |
|---|---|---|
| 100 trolley | Main, Madison → Union (5 min for 400 m) | 2.9 |
| 42 | Poplar → Jefferson | 3.7 |
| 42 | Bellevue @ Lamar → Carr | 6.2 |
| 42 | Cleveland @ Union → Bellevue @ Carr | 6.3 |
| 50, 01 | Poplar @ Reese → Highland | 6.2–7.0 |
| 36 | Pauline / Jefferson | 6.5–7.0 |
| 36 | Winchester @ Malco → Kirby Terrace | 6.6 |
| 52 | Jackson @ McDavitt → Auction | 6.7 |
| 01 | Summer @ Franklin → Tillman | 6.8 |

The 42 and 50 corridors are also where
[delay builds up](where-delay-builds.md).

[^q-speed]: analysis.sql [SPEED]
[^q-speed_slow]: analysis.sql [SPEED_SLOW]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
