---
type: Dataset
title: Live snapshot (latest.json)
description: The current poll's rows plus each bus's recent trail, rewritten atomically every 10 s; what the pages and the "right now" query read.
resource: ../../data/latest.json
tags: [tracker, map]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: poller-code
    resource: ../../cadavl_to_gtfs_rt.py
    title: cadavl_to_gtfs_rt.py (write_latest, run_poller)
  - id: live-files
    resource: ../../data/latest.json
    title: data/latest.json and data/poller.log as of 2026-10-05 22:44 CDT
---

# What it holds

The same rows as the [position history](positions.md) for the current poll,
written by the [poller](../system/poller.md) atomically (tmp file + rename)
every poll. Not in git.

After the evening's last bus the tracker lists none, so `vehicles` is empty
(the file is ~60 bytes) until midnight. From 00:00 to 04:00 the poller
doesn't poll, so the file keeps the last poll before
midnight.[^poller-code][^live-files]

# Schema

```json
{"fetched_at": 1790381360, "day": "2026-09-25",
 "vehicles": [{"vehicle_id": "...", "...": "...", "trail": [...]}]}
```

- `fetched_at`: Unix seconds of the poll.
- `day`: the poller's local service day, which names the
  [replay file](replay-frames.md).[^poller-code]
- `vehicles`: one [positions](positions.md) row per bus, plus `trail`: its
  last ten replay positions (one per 30 s). The poller holds trails in
  memory and seeds them from the replay file when it starts, so the map
  draws full trails the moment it opens without waiting for the multi-MB
  replay file.

# Read by

[map.html](../system/live-map.md), [strips.html](../system/route-strips.md)
and [schematic.html](../system/schematic-map.md) every 10 s, and the `[Q3]`
"riders right now" query in [analysis.sql](../system/analysis-sql.md)
(`unnest(vehicles)`).

[^poller-code]: cadavl_to_gtfs_rt.py (write_latest, run_poller)
[^live-files]: data/latest.json and data/poller.log as of 2026-10-05 22:44 CDT
