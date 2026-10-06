---
type: Finding
title: Which days are bad
description: Sundays are the good days (8% of bus-polls 5+ min late); weekdays (17–21%) and Saturdays (16–19%) are much alike, and the worst day, Wed 09-30 at 21%, was a few routes' bad day; one weekday against another needs more weeks.
tags: [delay, days]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[Q2]"]
sources:
  - id: q-q2
    resource: ../../analysis.sql
    title: analysis.sql [Q2]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
---

Answers [which days are especially bad?](../questions/bad-days.md)

# Answer

| Day | 5+ min late | Hours covered |
|---|---|---|
| Wed 2026-09-30 | 21% | 18.6 |
| Fri 2026-09-25 | 19% | 18.8 |
| Sat 2026-10-03 | 19% | 14.9 |
| Thu 2026-10-01 | 19% | 18.6 |
| Fri 2026-10-02 | 18% | 19.6 |
| Mon 2026-10-05 | 17% | 18.6 |
| Thu 2026-09-24 | 17% | 18.6 |
| Tue 2026-09-29 | 17% | 18.6 |
| Mon 2026-09-28 | 17% | 18.2 (to 22:11) |
| Sat 2026-09-26 | 16% | 14.8 |
| Sun 2026-10-04 | 8% | 10.8 |
| Sun 2026-09-27 | 8% | 10.4 |

The median bus is on time every day.[^q-q2][^snapshot]

- **Sundays are the good days**: 8% late against 18% on weekdays, and 81%
  of bus-polls on time against 74%. In most Sunday hours 5–14% are late,
  with no afternoon rush ([time of day](time-of-day.md)).[^one-off]
- **Saturdays are like weekdays overall** (17% late over the two), but the
  lateness is spread over the day instead of peaking in the
  afternoon.[^one-off]
- **No weekday stands out.** The 8 weekdays span 17–21%, and with one or
  two of each weekday that can't rank Monday against Friday.
- **A bad day is a few routes' bad day.** On Wed 09-30, the worst, route 28
  was 63% late, 34 45%, 02 40%, 01 39% and 12 36%; without those five the
  day was 17%. It also had the fewest trips leaving their first stop on
  time (54%, [departures](departures.md)). Sat 10-03's 19% is route 42,
  late all day (46%): without it both Saturdays were 15%.[^one-off]
- On 1.8 days this couldn't be answered: there were only Thursday (17%) and
  part of Friday (19%).

The query also shows `hours`, first to last bus recorded, so partial days
are obvious (Wed 09-23: 0.9 h).

[^q-q2]: analysis.sql [Q2]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
