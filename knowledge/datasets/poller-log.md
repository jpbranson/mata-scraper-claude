---
type: Dataset
title: Poller log (poller.log)
description: The mata-poller task's output, one time-stamped line per poll plus any errors; a few hundred KB a day, safe to delete.
resource: ../../data/poller.log
tags: [ops]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: flight-log-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FLIGHT_LOG.md
    title: FLIGHT_LOG.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
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

Failures of the [official feed](../system/official-feed-archiver.md),
[detour](../system/detour-logger.md), timetable and crosswalk steps are
logged here without costing a poll.

# Size

A few hundred KB per day (~0.3 MB measured). Delete it whenever. Not in git.
