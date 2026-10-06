---
type: Dataset
title: Stop crosswalk (stops.csv)
description: Every stop in the tracker's network with its stable stop code, name, position and the internal lines that pass it.
resource: ../../stops.csv
tags: [crosswalk, tracker, gtfs]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: crosswalk-code
    resource: ../../build_crosswalk.py
    title: build_crosswalk.py
  - id: crosswalk-diff
    resource: git diff of routes.csv, stops.csv and network.geojson (working tree of 2026-10-02 04:00 against HEAD 9585066)
    title: Topo 198256 (in git) against 198282 (working tree)
  - id: gtfs-1005
    resource: Measured on findings_page/snapshot-2026-10-05/data/gtfs.zip (downloaded by the poller 2026-10-05 04:00 CDT)
    title: The timetable of 2026-10-05 (stop_times.txt) against stops.csv
---

# What it is

One row per stop in the tracker's [network](../feeds/tracker-topo.md):
3,762 since topo 198238, each code once. Built by the
[crosswalk builder](../system/crosswalk-builder.md). Every stop the
timetable's trips call at (3,600) is in it; 162 are on no trip.[^gtfs-1005]

# Schema

| Column | Notes |
|---|---|
| `stop_internal_id` | The tracker's internal stop ID; unstable, every one changes with each topo version |
| `stop_code` | The tracker's `mnemoPointArret`, e.g. `THIEASNN`; stable. MATA's GTFS `stop_id` is `0:` + this ([GTFS timetable](../feeds/gtfs-timetable.md)) |
| `stop_name` | Display name, e.g. `3RD ST @EASTMAN RD`; names repeat across the street (2,780 distinct), and 25 end in a space (`WILLIAM HUDSON `) |
| `lat`, `lon` | |
| `line_internal_ids` | Internal line IDs passing the stop, `|`-separated, including lines that pass without stopping |

# Read by

The `stops` view in [analysis.sql](../system/analysis-sql.md), the
[detour logger](../system/detour-logger.md) (turning stop IDs into codes),
[schedule.py](../system/timetable-and-arrivals.md) and
[build_schematic.py](../system/schematic-map.md). The
[findings page](../system/findings-page.md) snapshot copies it.

# In git

Committed, with [routes.csv](routes-csv.md) and
[network.geojson](network-geojson.md). The committed copy is topo 198256;
the working copy, rebuilt by the poller, is 198282 and not committed as of
2026-10-05. Between the two every `stop_internal_id` and line ID changed,
while codes and names did not; one stop moved about 17 m (`JONHOLNF`), and
the trolley's line now passes 10 more downtown stops on Third and Second
St.[^crosswalk-diff]

[^crosswalk-diff]: Topo 198256 (in git) against 198282 (working tree)
[^gtfs-1005]: The timetable of 2026-10-05 (stop_times.txt) against stops.csv
