---
type: Component
title: Schematic map
description: schematic.html draws the whole network as a subway map from schematic.json (laid out by LOOM via build_schematic.py), with live or replayed buses sliding along their own lanes and load shown as a band.
resource: ../../schematic.html
tags: [map, load]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: schematic-code
    resource: ../../schematic.html
    title: schematic.html
  - id: build-schematic-code
    resource: ../../build_schematic.py
    title: build_schematic.py
  - id: loom
    resource: https://github.com/ad-freiburg/loom
    title: LOOM (University of Freiburg)
---

# The page

`schematic.html#36`: the whole network as a subway map, drawn with Leaflet
on a flat (`CRS.Simple`) plane from [`schematic.json`](../datasets/schematic-json.md).
The chips, bottom bar and bus placement are the [shared page
code](transit-js.md).

- Stations are the timetable's timepoints, merged where LOOM merged them
  (246 → 143); segments are at 45°/90°.
- Routes that share a street run as parallel lanes in LOOM's
  crossing-minimising order.
- Lines are one neutral ink so color stays with the buses; route numbers
  mark each route's ends.
- Click a line, a bus or a chip to pick a route out (others fade).
- Lanes keep a fixed pixel spacing (5 px, halved at a phone's whole-network
  zoom), so the offsets are recomputed on zoom.
- Labels: the transit centers at overview, every station from zoom 0,
  placed right or left of their station and skipped where they would
  collide.

# Buses

- A bus slides along its own lane between the timepoints before and after
  it, by scheduled time, using the edge chain stored for that pair of
  timepoints.
- How full it is shows as a translucent band along that stretch of its
  lane: the lane's width plus up to 32 px at 100% (12 px at a phone's
  overview), drawn under the lines so the other lanes in a bundle stay
  visible through it.
- No band for a bus with stuck GPS, or for other routes while one is picked
  out; the tooltip gives the exact %.
- Delay colors are the [map's](live-map.md) tiers.

# Building the layout

`build_schematic.py` makes `schematic.json` (56 KB, committed) from the
[GTFS feed](../feeds/gtfs-timetable.md) with LOOM[^loom] (University of
Freiburg: `gtfs2graph | topo | loom | octi`), cut to timepoints first.

- LOOM is C++ and builds on Linux or WSL; the script's docstring has the
  build line. Build only the four tools: `topo`'s test suite takes most of
  an hour to compile.
- Rerun only when MATA changes its routes. Line-ID renumberings don't
  matter, since routes are keyed by number and stops by code.

[^loom]: LOOM (University of Freiburg)
