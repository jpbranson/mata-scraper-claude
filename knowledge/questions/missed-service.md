---
type: Question
title: How much scheduled service never runs?
description: The share of scheduled trips that never ran, by route, hour and weekday, which belongs beside which routes run behind (by route, hour and weekdays against weekends answered on 12 days; one weekday against another waits for weeks of data).
tags: [missed-service, official-feed]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:55Z }
answer_status: partial
sources:
  - id: questions-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/QUESTIONS.md
    title: QUESTIONS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
  - id: flight-log-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FLIGHT_LOG.md
    title: FLIGHT_LOG.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Question

Missed service. Trips marked `CANCELED` in `trip_updates.jsonl.gz` and the
"Route N is not running from … at 5:30a" alerts, by route, hour and weekday.
The share of scheduled trips that never ran belongs beside
"[which routes run behind](routes-behind.md)".

Group 4 of the backlog (from MATA's official GTFS-RT archive).

# Data

The [official trip updates](../datasets/official-trip-updates.md) and
[alerts](../datasets/official-alerts.md), the
[saved timetables](../datasets/schedule-files.md), and the tracker's own
record of which trips ran ([positions](../datasets/positions.md) and the
[arrivals log](../datasets/arrivals-log.md)). The tracker's rider notices in
the [detour log](../datasets/detour-log.md) also hold missed-trip notices.

# Status

Partial. Answered on 12 days (8 weekdays, 2 Saturdays, 2 Sundays) by
route, day, hour and weekdays against weekends: `[MISSED]` and
`[MISSED_HOUR]`, in [missed service](../findings/missed-service.md).
Comparing one weekday with another needs weeks of data: there are one or
two of each so far. Worked out alongside [bunching](bunching.md), because
missed trips explained the first headway results.
