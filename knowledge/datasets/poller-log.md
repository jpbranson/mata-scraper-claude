---
type: Dataset
title: Poller log (poller.log)
description: The mata-poller task's output, one time-stamped line per poll plus any errors; a few hundred KB a day, safe to delete.
resource: ../../data/poller.log
tags: [ops]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: flight-log-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FLIGHT_LOG.md
    title: FLIGHT_LOG.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
  - id: poller-code
    resource: ../../cadavl_to_gtfs_rt.py
    title: cadavl_to_gtfs_rt.py (Stamped, run_poller)
  - id: log-measured
    resource: ../../data/poller.log
    title: data/poller.log as of 2026-10-05 22:44 CDT (lines and bytes per stamped day)
---

# What it is

`data\poller.log`: the `mata-poller` scheduled task's output
(`python -u cadavl_to_gtfs_rt.py`), appended (see
[running it](../operations/running-it.md)). Each line is stamped with the
local date and time (since 2026-09-25 20:12:38). The format, from the
scratch-copy test of the change at 19:09, before it went live:

```
2026-09-25 19:09:20 31 vehicles, 26 moved
```

One such line per poll from 04:00 to midnight, including `0 vehicles, 0
moved` after the evening's last bus. Besides those: `timetable for <day>:
<n> stop times` at 04:00 and at every start, and `topo version <n> ...
downloading` and `wrote ...` lines when the poller rebuilds the
[crosswalk](routes-csv.md).[^poller-code] Failures of the poll, the
[official feed](../system/official-feed-archiver.md),
[detour](../system/detour-logger.md), timetable and crosswalk steps are
logged here; only a failed poll costs a poll. By 2026-10-05: 502 failed
polls (370 connection errors or timeouts, 115 vendor 500/502/503s, 16
times Windows refused to replace latest.json), 19 failed detour checks and
5 failed official fetches.[^log-measured]

# Size

About 7,200 lines and 0.31 MB a day, every day of the week; 3.4 MB from
2026-09-23 to 10-05, ~110 MB a year.[^log-measured] Delete it whenever. Not
in git.

[^poller-code]: cadavl_to_gtfs_rt.py (Stamped, run_poller)
[^log-measured]: data/poller.log as of 2026-10-05 22:44 CDT
