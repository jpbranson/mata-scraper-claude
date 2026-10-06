---
type: Decision
title: "Bus capacity: 100% is 50 riders"
description: The tracker's load % is a rider count out of 50 on every vehicle, trolley included, so riders on board = occupancy_pct / 2; rechecked on 12 days, where all 2.2 million readings are even.
tags: [load, tracker, ridership]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: snapshot
    resource: ../findings/snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
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
---

# Decision

Settled 2026-09-25: the vendor's 100% is 50 riders, on every vehicle. So
riders on board = `occupancy_pct / 2`, a count as good as the bus's
(presumably automatic) passenger counters, not an estimate from a guessed
capacity. Good as the counters are, no better. Rechecked 2026-10-05 on 12
days of data: nothing contradicts it.

What changed:

- `CAPACITY = 50` in [map.html](../system/live-map.md);[^map-html] the
  map's "riders" figure went up by ~25%.
- `[Q3]` in [analysis.sql](../system/analysis-sql.md) is
  `sum(occupancy_pct) // 2`.[^q-q3]
- The [tracker's known limits](../feeds/tracker-vehicles.md) and the
  [positions schema](../datasets/positions.md) say so.

# Evidence

- **The percentages are all even.** All 2,217,872 readings over 12 days
  (340,389 when first settled, on an earlier copy), from every fleet series
  (4xx, 20xxx–22xxx, 4xxx, 2006, 5004) and both trolleys (603, 607), are
  even, and together they take all 51 even values from 0 to
  100.[^snapshot][^one-off] The vendor divides a rider count by one fixed
  50; a per-bus capacity like 38 or 40 would produce odd values.
- **For scale** (MATA's 2012 Short Range Transit Plan, service
  guidelines):[^srtp-2012] a 40-ft bus is planned at 40 seats with a
  48-rider maximum (120% of seats at peak on key corridors, 100%
  otherwise). So on the vendor's scale **80% ≈ every seat taken** (a full
  seated load) and **96–100% ≈ MATA's maximum load**, about the most MATA
  plans to carry. How often buses get there: [peak loads](../findings/peak-loads.md).
- **Ridership is the right scale:** riders per day from this reading, at
  least ~7,300 boardings a day over a week, match MATA's reported ridership
  of ~7,700 a day ([riding per day](../findings/riders-per-day.md)).
- **The official feed's occupancy categories don't mean what they say.**
  Pairing each official report with the tracker's for the same bus and
  position (67,487 pairs over 11 days), the middle 90% of each:[^one-off]

  | Official category | Riders (tracker) |
  |---|---|
  | EMPTY | ≈ 0 |
  | MANY_SEATS_AVAILABLE | ≈ 1–5 |
  | FEW_SEATS_AVAILABLE | ≈ 6–10 |
  | STANDING_ROOM_ONLY | ≈ 11–20 |
  | no category | ≈ 21–36 |
  | FULL | ≈ 41–50 |

  Fixed bands of the same count; they don't say whether seats are free (a
  bus with 11 riders has plenty). Don't use them for crowding.

[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
[^srtp-2012]: MATA 2012 Short Range Transit Plan, service guidelines
[^map-html]: map.html (CAPACITY)
[^q-q3]: analysis.sql [Q3]
