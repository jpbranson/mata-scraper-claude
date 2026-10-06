---
type: Finding
title: When delay goes bad
description: The weekday afternoon; 27–28% of weekday bus-polls are 5+ min late at 15:00–17:59, the worst stretch on each weekday, against 9–12% before 7 a.m.; Saturdays have no rush (13–23% all day), Sundays stay at 5–14%, and early running peaks late in the evening.
tags: [delay, hours]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:19:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[HOUR]"]
sources:
  - id: q-hour
    resource: ../../analysis.sql
    title: analysis.sql [HOUR]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers the hour-of-day half of [when does it go bad?](../questions/when-it-goes-bad.md)

# Answer

Share of bus-polls 5+ min late (`share_over_5_min`) by `day_type` and
hour, from `[HOUR]`:[^q-hour][^snapshot]

| Hours | Weekdays (8) | Saturdays (2) | Sundays (2) |
|---|---|---|---|
| 4:00–6:59 | 9–12% | | |
| 7:00–7:59 | 13% | 16% | |
| 8:00–14:59 | 17–21% | 13–23% | 5–14% |
| 15:00–17:59 | **27–28%** | 16–22% | 7–10% |
| 18:00–18:59 | 16% | 16% | 37% (last few buses) |
| 19:00–22:59 | 9–12% | 7–18% | |

- **Weekdays go bad in the afternoon.** The share climbs from 9–12% before
  7 a.m. to 17–21% from 8:00 to 14:59 and 27–28% at 15:00–17:59, then
  falls to 16% at 18:00. Median delay is 2 min only in those three
  hours.[^q-hour] 15:00–17:59 is the worst stretch on each of the 8
  weekdays (21–31%).[^one-off]
- **Saturdays have no rush**: 13–23% from 7:00 to 20:59, highest at
  14:00–15:59. **Sundays** stay at 5–14% from 8:00 to
  17:59.[^q-hour]
- **Early running peaks late in the evening** (`share_early`): on weekdays
  19% of bus-polls are 2+ min early at 20:00, 21% at 21:00 and 32% at
  22:00, and 15% at 4:00; Saturday's last hour, 21:00, is 51%. Evening
  schedules are slack. See [early running](early-running.md).[^q-hour]
- All days together the afternoon peak is 24%, because weekends dilute
  it.[^one-off]
- `[HOUR]`'s weekday 23:00 row (100% late, median 51 min) is one route 01
  bus running 51 min late until 23:34 on Fri 10-02.[^one-off]
- On 1.8 days the afternoon peak read 26–32% and the early morning 5–7%;
  with 8 weekdays it is 27–28% and 9–12%. Comparing one weekday with
  another needs more weeks.

[^q-hour]: analysis.sql [HOUR]
[^one-off]: One-off queries, 2026-10-05
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
