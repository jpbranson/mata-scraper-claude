---
type: Finding
title: Which routes run behind
description: Route 02 is the latest, 39% of its bus-polls 5+ min late; 36, 52, 08, 28 and 01 follow at 24–28%, and 69 and 16 are the most punctual.
tags: [delay, routes]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[Q1]"]
sources:
  - id: q-q1
    resource: ../../analysis.sql
    title: analysis.sql [Q1]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
---

Answers [which routes constantly run behind?](../questions/routes-behind.md)

# Answer

Share of bus-polls 5+ min late, `good` rows only:[^q-q1][^snapshot]

| Worst | 5+ min late | median | | Best | 5+ min late |
|---|---|---|---|---|---|
| 02 | 39% | 3 min late | | 69 | 2.5% |
| 36 | 28% | 2 min late | | 16 | 4% |
| 52 | 27% | on time | | 12, 04 | 6% |
| 08 | 26% | 2 min late | | 40, 100 (trolley), 07 | 7–8% |
| 28 | 26% | 2 min late | | 42 | 10% |

Route 02 stands out; the next tier (36, 52, 08, 28, 01) is 24–28%, then
19, 50, 39 and 37 at 21%.

- Route 02 is late on all its buses, not because of a bad tracker
  ([ghost trackers](ghost-trackers.md)).
- Route 02 is also among the most missed: 43–47% of its trips never ran
  ([missed service](missed-service.md)).
- `[Q1]` also reports `on_time` and `share_early`; the window behind them
  and the network-wide shares are in the
  [late threshold](../decisions/late-threshold.md) decision.

**Needs a human:** sanity-check this ranking against your own experience of
these routes, and rerun after a full week (~Oct 1); see
[next steps](../work/next-steps.md).

[^q-q1]: analysis.sql [Q1]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
