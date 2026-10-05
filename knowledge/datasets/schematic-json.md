---
type: Dataset
title: Schematic layout (schematic.json)
description: The subway-style network layout from LOOM, timepoints as stations and per-route edge chains between them; what schematic.html draws.
resource: ../../schematic.json
tags: [map, gtfs]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: schematic-code
    resource: ../../build_schematic.py
    title: build_schematic.py
---

# What it is

56 KB, committed to git. Built occasionally by
[build_schematic.py](../system/schematic-map.md) from the
[GTFS timetable](../feeds/gtfs-timetable.md) with LOOM; rerun only when MATA
changes its routes (line-ID renumberings don't matter, since routes are keyed
by number and stops by code).

# Schema

From the builder's output:[^schematic-code]

| Key | Holds |
|---|---|
| `built` | Local time it was built, e.g. `2026-09-25T02:27:02` |
| `nodes` | `[x, y, stop code, name]` per node, on a flat plane |
| `edges` | `[from node, to node, polyline, routes]` per segment, at 45°/90° |
| `stations` | Timepoint stop code → the node it merged into |
| `legs` | Per route, `"A>B"` for each pair of consecutive timepoints → the chain of edges between them, as `[edge index, +1 along / -1 against]` |

Only timepoints (the timetable's timed stops, plus each trip's first and
last stop) become stations; LOOM merges ones that sit close together.

# Read by

[schematic.html](../system/schematic-map.md), which slides each bus along its
route's leg between the timepoints before and after it.

[^schematic-code]: build_schematic.py
