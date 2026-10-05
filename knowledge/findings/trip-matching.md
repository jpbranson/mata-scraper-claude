---
type: Finding
title: Trip matching against MATA's trip IDs
description: Where schedule.py names a trip, it is MATA's own trip 99.8% of the time; nearly all disagreements are the other direction around a turnaround.
tags: [timetable, official-feed, data-quality]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[TRIPMATCH]"]
sources:
  - id: q-tripmatch
    resource: ../../analysis.sql
    title: analysis.sql [TRIPMATCH]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [does our trip matching hold up?](../questions/trip-matching.md) The
matching itself is described in
[timetable and arrivals](../system/timetable-and-arrivals.md).

# Method

60,662 official vehicle reports (Fri) against our row for the same bus
(fleet number) within a minute.[^q-tripmatch][^snapshot]

# Answer

- Where we named a trip, it's the official one **99.8%** of the time; no
  route below 99.1% (39, 28), and 50 and the trolley 99.5%.
- The 128 disagreements are nearly all (122) the **same route, other
  direction**, a median 75 min apart: around a turnaround, the tracker's
  headsign flips before or after MATA assigns the next trip.
- We name no trip for **2.6%** of rows: 1,094 with no next stop (between
  trips), 505 with a "1h+" delay (by design: no trustworthy delay, no
  match), a handful with no trip due near. Highest on the trolley (13.5%)
  and 39 (12%), which sit longer between trips.
- At trip level the feeds agree too: of 471 Friday trips the official feed
  saw running, the tracker saw 464 ([missed service](missed-service.md)).

[^q-tripmatch]: analysis.sql [TRIPMATCH]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
