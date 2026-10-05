---
type: Finding
title: What riders get at the stop
description: Turning up 2 minutes early at a mid-route timepoint, the median wait is 4.9 min, but 23% of waits pass 15 min; the missed-trip routes are worst.
tags: [headway, missed-service, riders]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[STOP_WAIT]"]
sources:
  - id: q-stop_wait
    resource: ../../analysis.sql
    title: analysis.sql [STOP_WAIT]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [stop-level wait times](../questions/stop-waits.md).

# Method

Turn up at a mid-route timepoint 2 minutes before the timetable says; how
long until a bus of that route leaves? Lateness, early departures and
missed trips all count. A trip the tracker didn't log at that stop is
placed at its scheduled time plus its own median delay.

# Answer

- **All routes: median 4.9 min, but 23% of the time over 15 min** (p90 73
  min), and 120 of 5,842 calls had no bus at all for the rest of the
  day.[^q-stop_wait][^snapshot]
- **Worst:** 69 (median 48 min, 50% over 15), 02 (25 min, 57%), 01 (14.9,
  49%), 53 (9.1, 44%), 52 (7.6, 34%): the
  [missed-trip](missed-service.md) routes.
- **Best:** 11 3.0, 07 3.1, 39 3.3, 04 3.4, the trolley 3.5 (though 40% of
  its 52 waits pass 15 min).

[^q-stop_wait]: analysis.sql [STOP_WAIT]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
