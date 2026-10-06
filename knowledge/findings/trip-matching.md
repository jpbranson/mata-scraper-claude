---
type: Finding
title: Trip matching against MATA's trip IDs
description: Over 11 days, where schedule.py names a trip it is MATA's own trip 99.7% of the time (99.8% leaving out ad-hoc trips MATA's dispatch creates); most other disagreements are the other direction around a turnaround.
tags: [timetable, official-feed, data-quality]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[TRIPMATCH]"]
sources:
  - id: q-tripmatch
    resource: ../../analysis.sql
    title: analysis.sql [TRIPMATCH]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [does our trip matching hold up?](../questions/trip-matching.md) The
matching itself is described in
[timetable and arrivals](../system/timetable-and-arrivals.md).

# Method

651,889 official vehicle reports (Fri 09-25 to Mon 10-05) against our row
for the same bus (fleet number) within a minute.[^q-tripmatch][^snapshot]

# Answer

- Where we named a trip, it's the official one **99.7%** of the time, every
  day between 99.35% (Sat 10-03) and 99.88%. Lowest by route: 50 (99.2%),
  52 (99.5%), the trolley and 07 (99.6%).
- **MATA's dispatch makes up trips.** 36 official trip IDs over the 11 days
  aren't in the timetable (about three a day, named for when they were
  made, e.g. `0_Weekday2026-10-01-19-35-14-…`), 742 of route 50's reports
  among them. On their 2,534 reports we named no trip (2,081) or a
  scheduled one (453). Leaving them out, we agree **99.8%**, and route 50
  99.7%.[^one-off]
- The other 1,167 disagreements are mostly (1,046) the **same route, other
  direction**, a median 75 min apart: around a turnaround, the tracker's
  headsign flips before or after MATA assigns the next trip. 107 are the
  same direction (a median 40 min apart) and 14 another route.
- We name no trip for **2.6%** of rows: 11,498 with no next stop (between
  trips), 4,489 with a "1h+" delay (by design: no trustworthy delay, no
  match), 994 for other reasons such as no trip due near. Highest on the
  trolley (8.0%), 07 (6.0%) and 69 (4.9%), which sit longer between
  trips.[^one-off]
- At trip level the feeds agree too: of 5,484 trips the official feed saw
  running, the tracker saw 5,402 (98.5%), and it saw 2 the official feed
  didn't ([missed service](missed-service.md)).[^one-off]

[^q-tripmatch]: analysis.sql [TRIPMATCH]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
