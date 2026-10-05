---
type: Finding
title: Layovers
description: Buses sit a median 7 minutes at their first stop before leaving (the trolley 1 min), and short layovers don't predict late starts.
tags: [official-feed, layovers]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
stale_after: 2026-10-01T05:00:00Z
data_as_of: 2026-09-26T01:21:00Z
queries: ["[LAYOVER]"]
sources:
  - id: q-layover
    resource: ../../analysis.sql
    title: analysis.sql [LAYOVER]
  - id: snapshot
    resource: snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

Answers [layover length](../questions/layover-length.md).

# Answer

MATA's [official feed](../feeds/official-gtfs-rt.md) keeps a bus at its
next trip's first stop, where the tracker drops it.[^q-layover][^snapshot]

- 429 Friday trips sat a median 7 min before leaving (trolley 1 min); 25%
  under 5 min.
- Short layovers don't predict late starts here: 19% of trips after a short
  one started 5+ min late, 27% after a longer one.
- One day, small numbers per route.

See also [departures](departures.md).

[^q-layover]: analysis.sql [LAYOVER]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
