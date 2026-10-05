---
type: Decision
title: "Bus capacity: 100% is 50 riders"
description: The tracker's load % is a rider count out of 50 on every vehicle, trolley included, so riders on board = occupancy_pct / 2.
tags: [load, tracker, ridership]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: snapshot
    resource: ../findings/snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: srtp-2012
    resource: "matatransit.com: MATA_SRTP_Plan_APPENDICES.pdf, Figure 4-4"
    title: MATA 2012 Short Range Transit Plan, service guidelines
  - id: map-html
    resource: ../../map.html
    title: map.html (CAPACITY)
  - id: q-q3
    resource: ../../analysis.sql
    title: analysis.sql [Q3]
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Decision

Settled 2026-09-25: the vendor's 100% is 50 riders, on every vehicle. So
riders on board = `occupancy_pct / 2`, a count as good as the bus's
(presumably automatic) passenger counters, not an estimate from a guessed
capacity. Good as the counters are, no better.

What changed:

- `CAPACITY = 50` in [map.html](../system/live-map.md);[^map-html] the
  map's "riders" figure went up by ~25%.
- `[Q3]` in [analysis.sql](../system/analysis-sql.md) is
  `sum(occupancy_pct) // 2`.[^q-q3]
- The [tracker's known limits](../feeds/tracker-vehicles.md) and the
  [positions schema](../datasets/positions.md) say so.

# Evidence

- **The percentages are all even.** All 351,576 readings (340,389 when
  first settled, on an earlier copy), from every fleet series (4xx,
  20xxx–22xxx, 4xxx, 5004) and the trolley (603), are even, and together
  they take all 51 even values from 0 to 100.[^snapshot] The vendor divides
  a rider count by one fixed 50; a per-bus capacity like 38 or 40 would
  produce odd values.
- **For scale** (MATA's 2012 Short Range Transit Plan, service
  guidelines):[^srtp-2012] a 40-ft bus is planned at 40 seats with a
  48-rider maximum (120% of seats at peak on key corridors, 100%
  otherwise). So on the vendor's scale **80% ≈ every seat taken** (a full
  seated load) and **96–100% ≈ MATA's maximum load**, about the most MATA
  plans to carry. How often buses get there: [peak loads](../findings/peak-loads.md).
- **Ridership is the right scale:** riders per day from this reading match
  MATA's reported ridership ([riding per day](../findings/riders-per-day.md)).
- **The official feed's occupancy categories don't mean what they say.**
  Pairing each official report with the tracker's for the same bus and
  position (5,915 pairs), the middle 90% of each:

  | Official category | Riders (tracker) |
  |---|---|
  | EMPTY | ≈ 0 |
  | MANY_SEATS_AVAILABLE | ≈ 1–5 |
  | FEW_SEATS_AVAILABLE | ≈ 6–10 |
  | STANDING_ROOM_ONLY | ≈ 11–20 |
  | no category | ≈ 21–36 (never above 40) |
  | FULL | ≈ 41+ |

  Fixed bands of the same count; they don't say whether seats are free (a
  bus with 11 riders has plenty). Don't use them for crowding.

[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
[^srtp-2012]: MATA 2012 Short Range Transit Plan, service guidelines
[^map-html]: map.html (CAPACITY)
[^q-q3]: analysis.sql [Q3]
