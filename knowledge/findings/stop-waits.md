---
type: Finding
title: What riders get at the stop
description: Turning up 2 minutes early at a mid-route timepoint, the median wait over 12 days is 4.3 min, but 16% of waits pass 15 min and 3% of calls get no bus for the rest of the day; the hourly, often-early trolley is worst, then the missed-trip routes.
tags: [headway, missed-service, riders]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:55Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[STOP_WAIT]"]
sources:
  - id: q-stop_wait
    resource: ../../analysis.sql
    title: analysis.sql [STOP_WAIT]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [stop-level wait times](../questions/stop-waits.md).

# Method

Turn up at a mid-route timepoint 2 minutes before the timetable says; how
long until a bus of that route leaves? Lateness, early departures and
missed trips all count. A trip the tracker didn't log at that stop is
placed at its scheduled time plus its own median delay.

# Answer

- **All routes, 12 days: median 4.3 min, but 16% of the time over 15
  min** (p90 52 min), and 944 of 30,466 calls (3.1%) had no bus at all for
  the rest of the day.[^q-stop_wait][^snapshot] Counting those as over 15
  min, 18%.[^one-off]
- **By day type:** weekdays median 4.5 min, 17% over 15; Saturdays 4.3
  and 13%; Sundays 3.5 and 15% (two of each).[^one-off]
- **Worst: the trolley** (median 55 min, 52% over 15). It runs once an
  hour each way and leaves the Main @ Madison timepoints a median 2.3 min
  early (56% of the time 2+ min early, 88% outbound at weekends), so a
  rider who turns up 2 minutes early usually waits for the next
  one.[^one-off]
- **Then the [missed-trip](missed-service.md) routes:** 01 (5.7 min, 25%
  over 15, 204 calls with no bus for the rest of the day), 02 (5.8, 25%),
  30 (4.0, 24%, 87 such calls), 52 (4.7, 23%), 53 and 69 (19%). Route 34
  left 86 of its 480 calls with no bus for the rest of the day.
- **Best:** 07 2.8 min (6% over 15), 11 3.3, 04 3.5, 40 3.7, 32 3.8; 13,
  16, 08 and 19 rarely pass 15 min (6–8%).
- On 1.8 days waits looked longer (median 4.9 min, 23% over 15), because
  those were the two worst days for missed trips, and the trolley looked
  among the best (3.5 min, from 52 waits).

[^q-stop_wait]: analysis.sql [STOP_WAIT]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
