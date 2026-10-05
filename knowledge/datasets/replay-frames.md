---
type: Dataset
title: Replay frames
description: One compact frame of every bus each 30 s, one file per local day; drives the pages' replay scrubber and trails.
resource: ../../data/replay/
tags: [tracker, map]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: poller-code
    resource: ../../cadavl_to_gtfs_rt.py
    title: cadavl_to_gtfs_rt.py (replay_frame)
---

# Layout

`data/replay/<local day>.jsonl`. Every third poll (30 s) the
[poller](../system/poller.md) appends one line. Not in git.

# Schema

```json
{"t": 1790381360, "v": [[id, route, lat, lon, bearing, delay_seconds, delay_capped,
                         occupancy_pct, unchanged_polls, destination, next_stop_name, equipment_no], ...]}
```

`t` is the poll time; one array per bus, fields as in the
[position history](positions.md) (lat/lon rounded to 5
decimals).[^poller-code] The last three (headsign, next stop, fleet number),
from 2026-09-25, let the strips and schematic place a replayed bus on its
stop pattern; older frames stop at `unchanged_polls` and still load.

# Size

~110 B per bus per frame, ~7 MB for a full day (~2.5 GB/year).

# Read by

Each page ([map](../system/live-map.md), [strips](../system/route-strips.md),
[schematic](../system/schematic-map.md)) loads the viewed day's file once; it
drives the replay scrubber and, on the map, the trails while replaying. The
poller seeds the [live snapshot's](latest-snapshot.md) trails from it at
startup.

# Rebuilding

`python backfill_replay.py [day]` rebuilds these (and the day's
[arrivals](arrivals-log.md)) from the full history: for days recorded before
replay existed, after any gap, or to bring old frames up to the current
format. See [backfill tools](../system/backfill-tools.md).

[^poller-code]: cadavl_to_gtfs_rt.py (replay_frame)
