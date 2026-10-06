---
type: Finding
title: Which direction is worse
description: Leaving downtown; on 11 of the 17 bus routes that reach William Hudson, the trip away from it is 5+ min late at least 10 points more often (02 40% against 12%), on weekdays from 6:00 to 18:00, and only 28 and 40 lean the other way.
tags: [delay, routes]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[DIRECTION]"]
sources:
  - id: q-direction
    resource: ../../analysis.sql
    title: analysis.sql [DIRECTION]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [which direction is worse?](../questions/which-direction.md)

# Answer

On 11 of the 17 bus routes that reach William Hudson, the trip *away* from
it is 5+ min late at least 10 points more often (share of bus-polls 5+ min
late, 12 days):[^q-direction][^snapshot]

| Route | Outbound (away from William Hudson) | Inbound |
|---|---|---|
| 02 | 39–43% | 12% |
| 52 (to Methodist Hospital) | 31% | 7% |
| 34 | 34% | 11% |
| 57 | 29% | 7% |
| 19 | 32% | 11% |
| 12 | 31% | 11% |
| 13 | 30% | 11% |
| 01 | 28% | 12% |
| 50 | 25% | 10% |
| 11 | 20% | 5% |
| 36 | 31% | 21% |

- 08 (24% against 14%) and 39 (13–29% against 12%) just miss the 10
  points. Only 28 (17% out, 25% in) and 40 (6% against 14%) lean the other
  way.[^one-off]
- **On weekdays it holds from the morning peak on**, not just in the
  evening rush: across these 17 routes, outbound trips are 24% late at
  6:00–8:59 against 9% inbound, 33% against 10% at 9:00–14:59, and 40%
  against 22% at 15:00–17:59. After 18:00 the two are close (15% and
  13%). Saturdays lean the same way (15–23% against 10–13%); Sundays
  don't (4–16% both ways).[^one-off]
- Routes that don't reach William Hudson differ by direction too: 69 is
  27% late toward Weaver Rd and 5% toward American Way Transit Center, 16
  18% toward Airways and 7% toward American Way.[^q-direction]
- On 1.8 days it was 10 of the 17 routes; 12 and 36 have joined them and
  39 has dropped out. 52 led then (42% against 11%); now 02 does. The
  pattern held.[^one-off]

[^q-direction]: analysis.sql [DIRECTION]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
