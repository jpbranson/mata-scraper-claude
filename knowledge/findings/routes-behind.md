---
type: Finding
title: Which routes run behind
description: Routes 36 and 02 are the latest, 26% of their bus-polls 5+ min late over 12 days (weekdays alone, 02 30%, 34 and 36 27%); 36 is late every weekday, and the trolley (7%) and 04 (8%) are the most punctual.
tags: [delay, routes]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:19:00Z }
stale_after: 2026-11-04T06:00:00Z
data_as_of: 2026-10-06T03:33:00Z
queries: ["[Q1]"]
sources:
  - id: q-q1
    resource: ../../analysis.sql
    title: analysis.sql [Q1]
  - id: snapshot
    resource: snapshot-2026-10-05.md
    title: Data snapshot, Mon 2026-10-05 22:37
  - id: one-off
    resource: "One-off DuckDB queries over findings_page/snapshot-2026-10-05, 2026-10-05 (not kept)"
    title: One-off queries, 2026-10-05
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
---

Answers [which routes constantly run behind?](../questions/routes-behind.md)

# Answer

Share of bus-polls 5+ min late, `good` rows, 12 days (8 weekdays, 2
Saturdays, 2 Sundays):[^q-q1][^snapshot]

| Worst | `share_over_5_min` | `weekday_over_5_min` | median | | Best | `share_over_5_min` |
|---|---|---|---|---|---|---|
| 36 | 26% | 27% | 2 min late | | 100 (trolley) | 7% |
| 02 | 26% | 30% | 2 min late | | 04 | 8% |
| 34 | 23% | 27% | 2 min late | | 07, 40, 32 | 10% |
| 19 | 22% | 23% | 2 min late | | 30, 16, 11 | 12% |
| 01 | 22% | 23% | on time | | 42 | 13% |
| 28 | 21% | 25% | 2 min late | | | |

Then 12, 13, 08, 52 and 53 at 18–20%.[^q-q1] The network is 17%
(weekdays 18%, Saturdays 17%, Sundays 8%).[^one-off]

- **Weekdays are the fair ranking.** Routes 12, 19, 34, 37 and 69 don't run
  on Sundays, when buses are late half as often, so their 12-day shares
  aren't diluted the way the others' are. On weekdays alone 02 is the
  latest (30%), then 34 and 36 (27%), 28 (25%), and 19, 52, 01, 13, 12 and
  08 at 21–23% (`weekday_over_5_min`). The most punctual weekday routes
  are 07 (7%), 04, the trolley and 42 (9%).[^q-q1]
- **Route 36 is the one that is late constantly**: 22–36% on each of the 8
  weekdays. 02 is 20%+ on 7 of 8 (11% on Fri 10-02). Route 28's 25% is
  three bad days (48% on Fri 09-25, 63% on Wed 09-30, 48% on Fri 10-02);
  on the other five it was 5–12%.[^one-off]
- On 1.8 days route 02 stood out alone at 39%; over 12 days it shares the
  top with 36. 69 and 16, then the most punctual, are now mid-table (16%
  and 12%).
- Route 02's lateness is spread over its buses, not one bad tracker: 17 of
  the 25 buses with 1,000+ polls on it were 20%+ late
  ([ghost trackers](ghost-trackers.md)).[^one-off]
- Route 02 also misses trips: 18% of its scheduled trips never ran, twice
  the network's 9% ([missed service](missed-service.md)).[^one-off]
- Weekends rank differently, but two of each can't say much. Route 42, 9%
  on weekdays, was late all day on Sat 10-03 (46%, 28–64% every hour from
  7:00 to 20:59) with no rider message about it.[^one-off]
- `[Q1]` also reports `on_time` and `share_early`; the network-wide shares
  are in the [late threshold](../decisions/late-threshold.md) decision.

**Needs a human:** sanity-check this ranking against your own experience of
these routes; see [next steps](../work/next-steps.md).

[^q-q1]: analysis.sql [Q1]
[^snapshot]: Data snapshot, Mon 2026-10-05 22:37
[^one-off]: One-off queries, 2026-10-05
