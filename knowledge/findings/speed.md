---
type: Finding
title: Speeds and slow stretches
description: Buses average 11–19 mph including stops on most routes over 12 days (01 slowest, 28 25 mph, trolley 4.6), with peak and midday within about 1 mph; the slowest stretches are the trolley on Main, route 42 on Cleveland and Bellevue, and buses leaving American Way Transit Center.
tags: [speed, routes]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:55Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[SPEED]", "[SPEED_SLOW]"]
sources:
  - id: q-speed
    resource: ../../analysis.sql
    title: analysis.sql [SPEED]
  - id: q-speed_slow
    resource: ../../analysis.sql
    title: analysis.sql [SPEED_SLOW]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [speed profiles](../questions/speed-profiles.md). The tracker's
speed is metres per second ([speed unit](../decisions/speed-unit.md)); the
figures here are mph.

# By route

- Average speed including stops: 11.2–18.7 mph on most routes (01
  slowest, then 13 and 50 at 12.1), 24.8 mph on 28, trolley
  4.6.[^q-speed][^snapshot]
- Stopped 33–46% of the time (28: 24%, trolley 61%).
- Peak and midday differ by about 1 mph or less on every route. Weekends
  are a little faster than weekdays (14.6 against 14.1 mph overall), most
  on 42 and 02 (about 2 mph).[^one-off]

# Slowest stretches

Stop-to-stop segments of 300 m or more, passed 20+ times in 12 days, with
the distance measured along the route (the timetable's shape
distances):[^one-off]

| Route | Stretch | mph |
|---|---|---|
| 100 trolley | Main, Madison → Union (5 min for 400 m) | 2.9 |
| 30, 36 | Leaving American Way Transit Center, to Getwell @ Allenbrooke, American Way @ Getwell or Lamar (520–1,080 m in 5–7 min) | 3.2–5.5 |
| 42 | Cleveland, Poplar → Jefferson | 4.4 |
| 39 | Third, Brooks → Peebles | 5.5 |
| 37 | Covington Pike, Covington Way → Elmore | 5.6 |
| 42 | Cleveland, Washington → Larkin | 6.5 |
| 42 | Bellevue, Lamar → Carr | 6.5 |
| 57 | Park, White Station → Mt Moriah | 6.8 |
| 53 | Summer, Old Summer → White Station | 6.9 |
| 36 | Winchester, Malco → Kirby Terrace | 6.9 |
| 36 | Pauline @ Madison → Jefferson | 7.2 |
| 52 | Jackson @ McDavitt → Auction | 7.2 |

`[SPEED_SLOW]` uses straight-line distance, which puts route 30's Brooks
@ Gill → Brooks Rd @ South Center first at 2.0 mph; the route runs 2.8 km
between those stops, not 378 m, so buses there do 14.6
mph.[^q-speed_slow] Its Airways @ Brooks → Brooks @ Airways reads slow
for the same reason. Poplar @ Reese → Highland (50, 01), on the 1.8-day
list at 6.2–7.0 mph, is 8.9–9.8 mph over 12 days.

Route 42 on Cleveland and Bellevue, and the stretches out of American Way
Transit Center, are also where [delay builds up](where-delay-builds.md).

[^q-speed]: analysis.sql [SPEED]
[^q-speed_slow]: analysis.sql [SPEED_SLOW]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
