---
type: Component
title: Timetable and arrivals
description: schedule.py loads MATA's GTFS timetable once per service day, writes per-route schedule files for the pages, and every poll names the trip each bus is running and logs when it served each stop.
resource: ../../schedule.py
tags: [timetable, gtfs, poller]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:01:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: schedule-code
    resource: ../../schedule.py
    title: schedule.py
  - id: poller-log
    resource: ../../data/poller.log
    title: data/poller.log, "timetable for" lines (read-only grep)
---

# Daily load

Once per service day (and at startup) the [poller](poller.md) downloads
[`GTFS_MATA.zip`](../feeds/gtfs-timetable.md) if the server's copy is newer
than `data/gtfs.zip` (an `If-Modified-Since` request), loads today's trips,
and writes the [schedule files](../datasets/schedule-files.md) for the
pages: `data/schedule/<day>/stops.json` (stop code → routes scheduled
there) and `data/schedule/<day>/<route>.json` (that route's trips, stop
times and stop patterns). It logs `timetable for <day>: N stop times`
(55,953 on a weekday, 39,065 on a Saturday, 23,777 on a
Sunday).[^poller-log] If the GTFS feed is down, the cached `data/gtfs.zip`
is used; with none, stop panels say there's no timetable, everything else
carries on, and the load is retried every 15 minutes (`RETRY_S`).

After a [crosswalk rebuild](crosswalk-builder.md) the poller has it load
the timetable again on the next poll, since stop names may have
moved.[^schedule-code]

# Matching, every poll

- **Trip.** The trip a bus is running is the one of its route and headsign
  due at its next stop closest to *now + ETA − reported delay*, within 20
  minutes. Stored as `trip_id` on the [positions](../datasets/positions.md)
  row. Needs an uncapped delay.
- **Arrival.** When a bus's next stop changes away from A, it has served A,
  at the time of the last poll that still showed A (±10 s). The stop is the
  one named A on that route and direction nearest the bus (names repeat
  across the street), and the trip is matched as above, at the arrival
  time minus the delay. Skipped if the bus was over 300 m away, the
  polls were over two minutes apart, the bus changed route between them,
  or the same bus served the same stop under 10 minutes before (GPS
  jitter). Appended to the [arrivals log](../datasets/arrivals-log.md),
  `data/arrivals/<local day>/<route>.jsonl`, split by route so the map
  fetches only the routes at a clicked stop.[^schedule-code]

A failure here is logged and never costs a poll.

# Checks

- Checked live: every arrival's actual − scheduled time agreed with the
  vendor's reported delay to within a minute.
- The trip matching agrees with MATA's own trip IDs 99.8% of the time
  ([trip matching](../findings/trip-matching.md)).

# Limits

Measured 2026-09-25:

- The log catches ~83–85% of the stops on a trip that ran (buses pass some
  stops between polls, or out of the feed).
- At the end of a line the tracker still shows the finished trip's headsign
  while the bus waits, so what it logs there is the departure, credited to
  the trip that just ended. [`analysis.sql`](analysis-sql.md) leaves line
  ends out of timing questions (`line_ends`) and times departures from the
  official feed instead ([departures](../findings/departures.md)).
- The GTFS zip has service only from the day it was fetched (the
  2026-10-05 zip's calendar starts 20261005), so a past day's timetable
  can't be loaded from today's zip; that is why
  [`backfill_replay.py`](backfill-tools.md) is unsafe for past days.

[^schedule-code]: schedule.py
[^poller-log]: data/poller.log, "timetable for" lines (read-only grep)
