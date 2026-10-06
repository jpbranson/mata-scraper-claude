---
type: Finding
title: Fleet in service
description: On weekdays 2.3–6.4 fewer buses are out than trips in progress in every hour from 04:30 to 21:30 (about 11% short, worst 13:30–15:30), the same shortfall as the missed trips; weekends run up to 8.5 short.
tags: [missed-service, fleet]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:17:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[FLEET]"]
sources:
  - id: q-fleet
    resource: ../../analysis.sql
    title: analysis.sql [FLEET]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [fleet in service by hour](../questions/fleet-in-service.md).

# Answer

At half past each hour, buses seen vs trips in progress, averaged over the
days of each type:[^q-fleet][^snapshot]

- **Weekdays (8):** short in every hour from 04:30 to 21:30, by 2.3–6.4
  buses. Worst 13:30–15:30: 48–50 trips, 42–43 buses. Least short at
  11:30 and 16:30–17:30 (2.3–2.5). Over the day, about 11% fewer buses
  than trips.[^one-off]
- **Saturdays (2):** about even at 08:30, 11:30 and 20:30; short by up to
  8.5 at 16:30 (42 trips, 33.5 buses).
- **Sundays (2):** short by 2–6.5 from 08:30 to 17:30, worst at 15:30.
- Single weekdays, 06:30–19:30 on average: from 3.1 short (Thu 10-01, Fri
  10-02) to 6.0 short (Wed 09-30).[^one-off]

The same shortfall as the [missed trips](missed-service.md): 11% short in
buses on weekdays, 9.8% of trips never run. The 1.8-day version found it
about even at 16:30–17:30; over 8 weekdays it is still 2.3–2.5 short then.

[^q-fleet]: analysis.sql [FLEET]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
