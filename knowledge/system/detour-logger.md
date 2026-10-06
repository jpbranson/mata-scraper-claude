---
type: Component
title: Detour logger
description: cadavl_detours.py checks the tracker's detours and rider messages hourly and appends a record to data/detours/ whenever either changed, so detour impact can be studied later.
resource: ../../cadavl_detours.py
tags: [detours, poller]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:01:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: flight-log-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FLIGHT_LOG.md
    title: FLIGHT_LOG.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
  - id: detours-code
    resource: ../../cadavl_detours.py
    title: cadavl_detours.py, build_segment_index (objetsSuppl)
  - id: copy-2026-10-05
    resource: ../../findings_page/snapshot-2026-10-05/
    title: Copy of data/ taken 2026-10-05 22:37 (data/detours/, records per UTC day)
---

# Why

The [detour impact](../questions/detour-impact.md) question needs a record
of which routes were detoured when, so the [poller](poller.md) keeps one,
like the [official archive](official-feed-archiver.md).

# Behavior

- Once an hour (and once at every start) `DetourLog.update` fetches
  [`/topo/refresh`](../feeds/tracker-detours.md) (~150 KB) and
  [`/iv/message`](../feeds/tracker-messages.md).
- When either changed since the last save, it appends a line to the
  [detour log](../datasets/detour-log.md),
  `data/detours/dt=<UTC day>/detours.jsonl.gz`. Stop IDs are turned into
  stop codes via [`stops.csv`](../datasets/stops-csv.md).
- The rider messages change most hours, so most hourly checks add a line:
  2 to 17 a day, 4–107 KB a day gzipped (the most on 2026-10-02/03, with
  7–8 lines on detour).[^copy-2026-10-05]
- A failure is logged (`detour log failed: ...`) and never costs a poll; it
  waits for the next hour. A failed check saves nothing, so that hour's
  rider messages are lost too.
- When no line is detoured the tracker sends `objetsSuppl: null`. Until
  `8de1cc1` the parser failed on it, 19 times from 2026-09-25 22:12 to
  2026-09-27 19:00, so the log has no record from 2026-09-26 22:00 to
  2026-09-27 19:38 ([failure modes](../operations/failure-modes.md)).[^detours-code]
- Logging since 2026-09-25 20:12:42 CDT (the first poller restart after it
  was added).

`/iv/message` is the tracker's rider notices, and not only detours: "Route
11 Out of service Outbound from Thomas & Whitney @ 7:45 PM. The next unit is
scheduled to arrive at 8:39 PM" sits beside "Route 39 diverted. Stops: …".
So the log also holds missed-trip notices from the tracker's side.
[`analysis.sql`](analysis-sql.md) reads them as `rider_messages`.

Detours are still not drawn on the map.

[^copy-2026-10-05]: Copy of data/ taken 2026-10-05 22:37 (data/detours/, records per UTC day)
[^detours-code]: cadavl_detours.py, build_segment_index (objetsSuppl)
