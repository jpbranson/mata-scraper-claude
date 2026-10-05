---
type: Dataset
title: Official archive - alerts
description: MATA's official GTFS-RT rider alerts, one row each time the set of alerts changed; from 2026-09-25.
resource: ../../data/official/
tags: [official-feed, missed-service]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
---

# Layout

`data/official/dt=YYYY-MM-DD/alerts.jsonl.gz` (UTC date of `feed_ts`), from
2026-09-25, saved by the
[official feed archiver](../system/official-feed-archiver.md) only when the
alerts change. Not in git. Size: see
[official vehicles](official-vehicles.md#size).

# Schema

One row per snapshot whose alerts changed, holding the whole list:

| Field | Notes |
|---|---|
| `feed_ts` | Feed header time, Unix seconds |
| `alerts` | List of `{id, routes, stops, active: [[start, end]], cause, effect, header, description}`; an empty list means none, so it marks when the last alert cleared |

Enum values (`cause`, `effect`) are the GTFS-RT names. What the alerts say
in practice (dispatchers' free text, wrong route tags, periods that never
end) is under [missed service](../findings/missed-service.md).
`off_alerts` in [analysis.sql](../system/analysis-sql.md) is the view over
this file.
