---
type: Decision
title: "Speed unit: metres per second"
description: The tracker's speed_raw is whole metres per second, confirmed against MATA's official feed (equal in 97% of 33,269 moving same-report pairs on 11 days) and against the distance buses cover (ratio 1.03).
tags: [speed, tracker, official-feed]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: snapshot
    resource: ../findings/snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
  - id: gtfs-rt-spec
    resource: "GTFS-Realtime specification (VehiclePosition speed in metres per second)"
    title: GTFS-Realtime specification
  - id: poller-code
    resource: ../../cadavl_to_gtfs_rt.py
    title: cadavl_to_gtfs_rt.py (MAX_SPEED_MS)
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
---

# Decision

Settled 2026-09-25: `speed_raw` is metres per second, in whole numbers. Not
needed for any of the three questions; used by the
[speed findings](../findings/speed.md). Rechecked 2026-10-05 on 12 days of
data: nothing contradicts it.

What changed: the [poller](../system/poller.md) dropped its `SPEED_UNIT`
switch for `MAX_SPEED_MS = 40` and now writes speed into
[`vehicle_positions.pb`](../datasets/vehicle-positions-pb.md), skipping
readings over 40 m/s.[^poller-code] Live since the poller restart on
2026-09-25 at 20:12.

# Evidence

- **Same report, both feeds.** Matching each official vehicle position to
  the tracker row for the same bus (fleet number) at the identical
  coordinates, i.e. the same report, gave 67,487 pairs over 11 days; for
  the 33,269 moving ones (2,557 on the earlier copy first used), the
  official speed (m/s by the GTFS-RT spec[^gtfs-rt-spec]) *equals*
  `speed_raw` 97% of the time.[^snapshot][^one-off]
- **Distance covered.** Over 63,065 five-minute windows of moving buses
  (ghost rows left out), metres covered ÷ (`speed_raw` × seconds) = 1.03
  (middle half 0.99–1.08). mph would give 0.45, km/h 0.28. Slightly over 1
  fits whole-number speeds rounded down.[^one-off]
- **Range.** `speed_raw` is typically 0–21 (99th percentile 21; 40% of
  polls 0); 2,199 rows (about 1 in 1,000) are impossible (41–1,542).

[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
[^gtfs-rt-spec]: GTFS-Realtime specification
[^poller-code]: cadavl_to_gtfs_rt.py (MAX_SPEED_MS)
