---
type: Dataset
title: Stop crosswalk (stops.csv)
description: Every stop in the tracker's network with its stable stop code, name, position and the internal lines that pass it.
resource: ../../stops.csv
tags: [crosswalk, tracker, gtfs]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: crosswalk-code
    resource: ../../build_crosswalk.py
    title: build_crosswalk.py
---

# What it is

One row per stop in the tracker's [network](../feeds/tracker-topo.md) (about
3,700), built by the [crosswalk builder](../system/crosswalk-builder.md).

# Schema

| Column | Notes |
|---|---|
| `stop_internal_id` | The tracker's internal stop ID; unstable, changes with each topo version |
| `stop_code` | The tracker's `mnemoPointArret`, e.g. `THIEASNN`; stable. MATA's GTFS `stop_id` is `0:` + this ([GTFS timetable](../feeds/gtfs-timetable.md)) |
| `stop_name` | Display name, e.g. `3RD ST @EASTMAN RD`; names repeat across the street |
| `lat`, `lon` | |
| `line_internal_ids` | Internal line IDs passing the stop, `|`-separated |

# Read by

The `stops` view in [analysis.sql](../system/analysis-sql.md), the
[detour logger](../system/detour-logger.md) (turning stop IDs into codes),
[schedule.py](../system/timetable-and-arrivals.md) and
[build_schematic.py](../system/schematic-map.md). The
[findings page](../system/findings-page.md) snapshot copies it.

# In git

Committed, with [routes.csv](routes-csv.md) and
[network.geojson](network-geojson.md).
