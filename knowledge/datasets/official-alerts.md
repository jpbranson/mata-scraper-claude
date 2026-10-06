---
type: Dataset
title: Official archive - alerts
description: MATA's official GTFS-RT rider alerts, one row each time the set of alerts changed; from 2026-09-25.
resource: ../../data/official/
tags: [official-feed, missed-service]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: official-code
    resource: ../../official_feed.py
    title: official_feed.py (alert_rows, Official.update)
  - id: snapshot-1005
    resource: Measured on findings_page/snapshot-2026-10-05 (copy of data/ taken 2026-10-05 22:37 CDT)
    title: Measurements on the 2026-10-05 snapshot (official archive 2026-09-25 05:45 to 2026-10-05 22:33)
---

# Layout

`data/official/dt=YYYY-MM-DD/alerts.jsonl.gz` (UTC date of `feed_ts`), from
2026-09-25 05:45 CDT, saved by the
[official feed archiver](../system/official-feed-archiver.md) only when the
alerts change, and once more at every poller restart.[^official-code] Not
in git. 13 to 51 rows a day (fewest on Sundays), up to 37 alerts at once,
a few to 50 KB a day; see [official vehicles](official-vehicles.md#size).[^snapshot-1005]

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

[^official-code]: official_feed.py (alert_rows, Official.update)
[^snapshot-1005]: Measurements on the 2026-10-05 snapshot
