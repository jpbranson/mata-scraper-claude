---
type: Finding
title: Riding per day
description: About 4,000 rider-hours and at least 7,900–8,100 boardings a day, peaking near 450 riders on board at 15:40, the same scale as MATA's reported ridership.
tags: [ridership, load]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[RIDERS_DAY]"]
sources:
  - id: q-riders_day
    resource: ../../analysis.sql
    title: analysis.sql [RIDERS_DAY]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: mata-ridership-2023-09
    resource: "MATA's reported bus ridership for September 2023 (the document was not recorded)"
    title: MATA bus ridership, September 2023
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers the daily-total part of
[ridership by day, weather and events](../questions/ridership-trend.md).

# Answer

| Day | Rider-hours | Peak on board | Boardings (at least) |
|---|---|---|---|
| Thu 2026-09-24 | 4,064 | 451 at 15:40 | 8,077 |
| Fri 2026-09-25 (to 20:21) | 3,962 | 423 at 15:40 | 7,913 |

[^q-riders_day][^snapshot]

MATA reported ~230,600 bus riders in September 2023 (~7,700 a
day),[^mata-ridership-2023-09] the same scale, which also supports reading
the load as riders out of 50 ([bus capacity](../decisions/bus-capacity.md)).

Trends by day of week, weather and events need weeks of data plus outside
data.

# Method

As the query's comment says: rider-hours weight each poll's riders on
board (load % ÷ 2) by the time to the next poll, up to 30 s; boardings are
every rise in a bus's count between polls, net changes only, so a floor
(see [where buses fill](boardings.md)).

[^q-riders_day]: analysis.sql [RIDERS_DAY]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
[^mata-ridership-2023-09]: MATA bus ridership, September 2023
