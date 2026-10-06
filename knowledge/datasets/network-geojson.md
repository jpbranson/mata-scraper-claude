---
type: Dataset
title: Network map (network.geojson)
description: Every route's line and every stop as GeoJSON, with the topo version it was built from; the live map's background.
resource: ../../network.geojson
tags: [crosswalk, map]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: crosswalk-code
    resource: ../../build_crosswalk.py
    title: build_crosswalk.py (extract_network, built_version, main)
  - id: map-code
    resource: ../../map.html
    title: map.html (fetch("network.geojson"), STOP_ZOOM)
  - id: crosswalk-diff
    resource: git diff of routes.csv, stops.csv and network.geojson (working tree of 2026-10-02 04:00 against HEAD 9585066)
    title: Topo 198256 (in git) against 198282 (working tree)
---

# What it is

Built by the [crosswalk builder](../system/crosswalk-builder.md) from the
tracker's [network](../feeds/tracker-topo.md), beside
[routes.csv](routes-csv.md) and [stops.csv](stops-csv.md). 975 KB, one
line: 25 route features and 3,762 stop features. Committed to git.

# Schema

A `FeatureCollection` with a top-level `topo_version`: the
[network version](../feeds/tracker-config-version.md) it was built from, so
the version travels with the crosswalk through git and the
[poller](../system/poller.md) can tell when it is stale. It is null when
the file was built by hand from a saved `--topo` file.[^crosswalk-code]

| Feature | Geometry | Properties |
|---|---|---|
| One per route | `MultiLineString`, built from the 2-point segments in `/topo`, de-duplicated across a route's direction and branch variants, rounded to 5 decimals | `route_id` (e.g. `01`), `name` (e.g. `UNION`) |
| One per stop | `Point` | `stop` (name), `code` (stop code) |

# Versions

The committed copy says `"topo_version": 198256`. The working copy says
198282, rebuilt by the poller on 2026-09-30 and again on 2026-10-02 (file
time 04:00), and is not committed as of 2026-10-05. Its route lines cover
exactly the same points; the parts come in a different order, and one stop
moved about 17 m.[^crosswalk-diff] See
[tracker network](../feeds/tracker-topo.md#versions).

# Read by

[map.html](../system/live-map.md) draws it once as the background: routes as
hairlines, stops as small hollow dots from zoom 13, each opening its stop
panel by code.[^map-code] The [findings page](../system/findings-page.md)
builder reads its route lines, and the poller reads its `topo_version`.

[^crosswalk-code]: build_crosswalk.py (extract_network, built_version, main)
[^map-code]: map.html (fetch("network.geojson"), STOP_ZOOM)
[^crosswalk-diff]: Topo 198256 (in git) against 198282 (working tree)
