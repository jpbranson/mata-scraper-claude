---
type: Dataset
title: Route crosswalk (routes.csv)
description: The tracker's internal line IDs mapped to MATA route numbers, names and colors; rebuilt whenever the vendor renumbers its lines.
resource: ../../routes.csv
tags: [crosswalk, tracker]
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

One row per line in the tracker's [network](../feeds/tracker-topo.md) (25
lines), built by the [crosswalk builder](../system/crosswalk-builder.md). The
[poller](../system/poller.md) loads it at startup (`load_routes`) to turn each
bus's `idLigne` into a route number and color. The mapping is not derivable
(route 01 was once idLigne 109149 while route 34 was 109134) and every ID
changes with a new topo version, so it is rebuilt when buses show up on
unknown lines (see [network version](../feeds/tracker-config-version.md)).

# Schema

| Column | Notes |
|---|---|
| `line_internal_id` | The tracker's `idLigne`, e.g. 111401; unstable |
| `route_short_name` | MATA route number, e.g. `01`; stable, what everything is keyed on |
| `route_long_name` | e.g. `UNION` |
| `route_color` | Hex without `#`, e.g. `0000ff` |
| `has_alerts` | The tracker's `messageIVExiste` for the line when built: whether it had rider messages |

# In git

Committed, with [stops.csv](stops-csv.md) and
[network.geojson](network-geojson.md). The poller rewrites the working copy
when it rebuilds; see the [crosswalk builder](../system/crosswalk-builder.md)
for committing those rebuilds.
