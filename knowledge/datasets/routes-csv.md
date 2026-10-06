---
type: Dataset
title: Route crosswalk (routes.csv)
description: The tracker's internal line IDs mapped to MATA route numbers, names and colors; rebuilt whenever the vendor renumbers its lines.
resource: ../../routes.csv
tags: [crosswalk, tracker]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: crosswalk-code
    resource: ../../build_crosswalk.py
    title: build_crosswalk.py
  - id: poller-code
    resource: ../../cadavl_to_gtfs_rt.py
    title: cadavl_to_gtfs_rt.py (load_routes, refresh_crosswalk)
  - id: pages
    resource: ../../strips.html
    title: strips.html and schematic.html (fetch("routes.csv"))
  - id: crosswalk-diff
    resource: git diff of routes.csv, stops.csv and network.geojson (working tree of 2026-10-02 04:00 against HEAD 9585066)
    title: Topo 198256 (in git) against 198282 (working tree)
  - id: poller-log
    resource: ../../data/poller.log
    title: poller.log, crosswalk rebuilds at 2026-09-30 04:00 and 2026-10-02 04:00
---

# What it is

One row per line in the tracker's [network](../feeds/tracker-topo.md) (25
lines), built by the [crosswalk builder](../system/crosswalk-builder.md). The
[poller](../system/poller.md) loads it at startup (`load_routes`), and again
after it rebuilds it, to turn each bus's `idLigne` into a route number and
color.[^poller-code] The mapping is not derivable (route 01 was once idLigne
109149 while route 34 was 109134) and every ID changes with a new topo
version, so it is rebuilt when buses show up on unknown lines (see
[network version](../feeds/tracker-config-version.md)).

# Schema

| Column | Notes |
|---|---|
| `line_internal_id` | The tracker's `idLigne`, e.g. 111401 (route 01 in topo 198282; 111295 in 198256); unstable |
| `route_short_name` | MATA route number, e.g. `01`; stable, what everything is keyed on |
| `route_long_name` | e.g. `UNION` |
| `route_color` | Hex without `#`, e.g. `0000ff` |
| `has_alerts` | The tracker's `messageIVExiste` for the line when built: whether it had rider messages then. A snapshot, stale within hours |

# Read by

The poller, [backfill_routes.py and backfill_replay.py](../system/backfill-tools.md)
(through the poller's `ROUTES`), and [strips.html](../system/route-strips.md)
and [schematic.html](../system/schematic-map.md), which take the route list
(number and name) from it.[^pages]

# In git

Committed, with [stops.csv](stops-csv.md) and
[network.geojson](network-geojson.md). The committed copy is topo 198256
(2026-09-24). The working copy is 198282, rebuilt by the poller at
2026-09-30 04:00 and again at 2026-10-02 04:00, after `ops/update.ps1` had
discarded the first rebuild; it is not committed as of
2026-10-05.[^poller-log] Only the line IDs and `has_alerts` differ: the 25
routes, names and colors are the same.[^crosswalk-diff] See the
[crosswalk builder](../system/crosswalk-builder.md) for committing those
rebuilds, and [tracker network](../feeds/tracker-topo.md#versions) for the
versions.

[^poller-code]: cadavl_to_gtfs_rt.py (load_routes, refresh_crosswalk)
[^pages]: strips.html and schematic.html (fetch("routes.csv"))
[^crosswalk-diff]: Topo 198256 (in git) against 198282 (working tree)
[^poller-log]: poller.log, crosswalk rebuilds at 2026-09-30 04:00 and 2026-10-02 04:00
