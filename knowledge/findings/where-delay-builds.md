---
type: Finding
title: Where delay builds up
description: Lateness builds most where route 36 leaves American Way Transit Center (46 bus-min a day at American Way @ Getwell, 21 at Getwell @ Allenbrooke), then on 42's Cleveland corridor (25 at Cleveland @ Larkin), 01's Tillman at Johnson and 50's Poplar; most routes start trips 2–4 min late and recover, while on weekdays 13, 01, 08, 28, 02 and 36 lose 0.7–1.5 min a trip.
tags: [delay, routes, stops]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:19:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[WHERE]", "[WHERE_ROUTE]"]
sources:
  - id: q-where
    resource: ../../analysis.sql
    title: analysis.sql [WHERE]
  - id: q-where_route
    resource: ../../analysis.sql
    title: analysis.sql [WHERE_ROUTE]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [where along the route delay accumulates](../questions/where-delay-accumulates.md)
and [whether delay recovers or compounds](../questions/recover-or-compound.md).

# Per stop

Lateness gained since the previous logged stop on the same trip, summed
into bus-minutes lost per day; stops passed 20+ times; line ends left out;
12 days. Early counts as on time, so a bus waiting out being early at a
timepoint gains nothing.[^q-where][^snapshot]

| Route → direction | Stop | Avg gained | Bus-min/day |
|---|---|---|---|
| 36 → Centennial / Hacks Cross | American Way @ Getwell | +2.9 min | 46 |
| 42 → Frayser | Cleveland @ Larkin | +1.6 | 25 |
| 36 → William Hudson | Getwell Rd @ Allenbrooke Cv | +2.5 | 21 |
| 01 → Walnut @ Racine | Tillman at Johnson | +0.7 | 17 |
| 36 → William Hudson | Jefferson @ Pauline | +0.9 | 15 |
| 30 → Riverdale | Getwell Rd @ Allenbrooke Cv | +2.7 | 15 |
| 50 → Exeter | Poplar @ Cleveland, Poplar @ High | +0.8 | 14 each |
| 42 → Airways | Cleveland @ Jefferson, Bellevue @ Central | +0.8–0.9 | 13 each |
| 36 → William Hudson / → Centennial | Winchester @ Kirby Terrace, Lamar @ East Pkwy, Third @ Exchange, Getwell @ Mallory | +0.7–1.5 | 12–13 each |
| 50 → William Hudson | Poplar @ Innsbruck, Poplar @ Claybrook | +0.6 | 11–13 each |

- **Route 36 loses the most, at American Way Transit Center.** Its top two
  stops are the first ones after the transit center, in each direction.
  Buses reach it 3 min late on average and leave about 3 min later still;
  48% of trips toward Centennial are 5+ min late at the next stop. Route 30
  arrives there on time and loses 2.7 min leaving toward Riverdale. 36 has
  7 of the 20 stops in `[WHERE]`.[^q-where][^one-off]
- **Then 42's Cleveland corridor and 50's Poplar.** 42 has 4 of the 20
  (Cleveland @ Larkin, @ Jefferson, @ Monroe and Bellevue @ Central), 50
  has 4 (Poplar @ Cleveland, @ High, @ Innsbruck, @ Claybrook), each
  costing 11–25 bus-min a day.[^q-where]
- 42's Cleveland corridor and 36's stretches are also among the
  [slowest stretches](speed.md).
- Weekdays alone give the same places at the top.[^one-off]
- On 1.8 days the count included early buses waiting at timepoints, which
  put the trolley's Main @ Union near the top; counted as lateness, the
  same corridors (36 at American Way, 42 on Cleveland, 50 on Poplar, 01 at
  Tillman) lead.

# Per trip: recover or compound

Delay at the last logged stop minus the first; line ends aside; trips
logged 20+ min; 5,456 trips.[^q-where_route]

- Most routes **start late and recover**. The median trip starts 3 min late
  and ends on time; 60% end earlier than they started, by 2.2 min on
  average.[^one-off] Median start is 2–4 min late on 22 of 25 routes (01,
  13 and 28 start on time); the median end is on time or early on
  19.[^q-where_route]
- 37, 30, 57 and 40 end 4.8–5.8 min earlier than they started, and 19, 07
  and 04 4.2–4.6: their schedules have slack, which fits their
  [early running](early-running.md).[^q-where_route]
- Only a few **compound**, and by little: over 12 days 13 +1.5 min a trip,
  01 +1.2, 28 +0.6, 08 +0.4, 02 and 36 +0.3; 36 has the most trips gaining
  5+ min (17%).[^q-where_route] On weekdays alone: 13 +1.5, 01 +1.3, 08
  +1.1, 28 +1.0, 02 and 36 +0.7 (36: 19% gaining 5+). On weekends 02, 08,
  28 and 36 recover; 13 and 01 still lose time.[^one-off]
- On 1.8 days route 02 compounded most (+3.8 min a trip). That was mostly
  Fri 09-25 (+5.6); on the other 11 days it was −2.9 to +1.9.[^one-off]
- The late starts come from the terminal: trips leave their first stop a
  median 3.9 min late ([departures](departures.md)), 6.4–6.7 on routes 19
  and 34.

[^q-where]: analysis.sql [WHERE]
[^q-where_route]: analysis.sql [WHERE_ROUTE]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
