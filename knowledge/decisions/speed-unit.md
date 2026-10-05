---
type: Decision
title: "Speed unit: metres per second"
description: The tracker's speed_raw is whole metres per second, confirmed against MATA's official feed and against the distance buses cover.
tags: [speed, tracker, official-feed]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: snapshot
    resource: ../findings/snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
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
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Decision

Settled 2026-09-25: `speed_raw` is metres per second, in whole numbers. Not
needed for any of the three questions; used by the
[speed findings](../findings/speed.md).

What changed: the [poller](../system/poller.md) dropped its `SPEED_UNIT`
switch for `MAX_SPEED_MS = 40` and now writes speed into
[`vehicle_positions.pb`](../datasets/vehicle-positions-pb.md), skipping
readings over 40 m/s.[^poller-code] Live since the poller restart on
2026-09-25 at 20:12.

# Evidence

- **Same report, both feeds.** Matching each official vehicle position to
  the tracker row for the same bus (fleet number) at the identical
  coordinates, i.e. the same report, gave 5,915 pairs; for the 2,751 moving
  ones (2,557 on the earlier copy first used), the official speed (m/s by
  the GTFS-RT spec[^gtfs-rt-spec]) *equals* `speed_raw` 97% of the
  time.[^snapshot]
- **Distance covered.** Over 10,924 five-minute windows of moving buses
  (ghost rows left out), metres covered ÷ (`speed_raw` × seconds) = 1.03
  (middle half 0.98–1.08). mph would give 0.45, km/h 0.28. Slightly over 1
  fits whole-number speeds rounded down.
- **Range.** `speed_raw` is typically 0–21 (40% of polls 0); 295 rows (1 in
  1,200) are impossible (41–347).

[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
[^gtfs-rt-spec]: GTFS-Realtime specification
[^poller-code]: cadavl_to_gtfs_rt.py (MAX_SPEED_MS)
