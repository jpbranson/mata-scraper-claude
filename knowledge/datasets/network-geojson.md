---
type: Dataset
title: Network map (network.geojson)
description: Every route's line and every stop as GeoJSON, with the topo version it was built from; the live map's background.
resource: ../../network.geojson
tags: [crosswalk, map]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
---

# What it is

Built by the [crosswalk builder](../system/crosswalk-builder.md) from the
tracker's [network](../feeds/tracker-topo.md), beside
[routes.csv](routes-csv.md) and [stops.csv](stops-csv.md). Just under 1 MB.
Committed to git.

# Schema

A `FeatureCollection` with a top-level `topo_version`: the
[network version](../feeds/tracker-config-version.md) it was built from, so
the version travels with the crosswalk through git and the
[poller](../system/poller.md) can tell when it is stale.

| Feature | Geometry | Properties |
|---|---|---|
| One per route | `MultiLineString`, built from the 2-point segments in `/topo`, de-duplicated across a route's direction and branch variants, rounded to 5 decimals | `route_id` (e.g. `01`), `name` (e.g. `UNION`) |
| One per stop | `Point` | `stop` (name), `code` (stop code) |

# Read by

[map.html](../system/live-map.md) draws it once as the background: routes as
hairlines, stops as small hollow dots.
