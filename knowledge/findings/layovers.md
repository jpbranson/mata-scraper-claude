---
type: Finding
title: Layovers
description: Buses lay over a median 13 min before a trip and reach its first stop 9 min before it's due (the trolley 1 min); 16% get there after the trip is due and 39% of those start 5+ min late, against 20–22% after short or long layovers.
tags: [official-feed, layovers]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:17:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[LAYOVER]"]
sources:
  - id: q-layover
    resource: ../../analysis.sql
    title: analysis.sql [LAYOVER]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [layover length](../questions/layover-length.md).

# Method

MATA's [official feed](../feeds/official-gtfs-rt.md) keeps a bus at its
next trip's first stop, where the tracker drops it. `[LAYOVER]` counts the
layover from when the bus last moved 50 m or more to when it left that
stop, and the slack as how long before the trip was due it got there. The
feed marks a bus as stopped at the first stop only from about 5 minutes
before the trip is due, so that status alone doesn't give the layover.

# Answer

- **Over 11 days, 4,777 trips: median layover 13.2 min, and buses reach
  the first stop a median 9.4 min before the trip is due.** 29% have
  under 5 min, and 16% (742 trips) get there after the trip is
  due.[^q-layover][^snapshot] Weekdays 13.4 min, Saturdays 12.6, Sundays
  12.8.[^one-off]
- **Arriving late makes late starts; short layovers don't.** 39% of trips
  whose bus got there after the trip was due started 5+ min late, against
  22% after 0–5 min of slack and 20% after more.
- **By route,** median layovers run from 8 min (01, 13) to 23 min (42);
  the trolley turns round in about a minute. Per route, 51–377 trips.
- The 1.8-day version counted only the time the feed marked the bus as
  stopped there (a median 7 min over 11 days), which starts about 5
  minutes before the trip is due.[^one-off] Measured from when the bus
  stopped moving, layovers are about twice as long.

See also [departures](departures.md).

[^q-layover]: analysis.sql [LAYOVER]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
