---
type: Component
title: Crosswalk builder
description: build_crosswalk.py turns the tracker's full network (/topo) into routes.csv, stops.csv and network.geojson, keyed on stable route numbers and stop codes; the poller reruns it when line IDs change.
resource: ../../build_crosswalk.py
tags: [crosswalk]
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

# Why

The tracker's line and stop IDs are opaque and change whenever the vendor
publishes a new topo version (see [known limits](../feeds/tracker-vehicles.md)).
Route numbers and stop codes are stable, so everything is keyed on those,
and this script maps the vendor's IDs to them.

# Running it

- The [poller](poller.md) runs it (`build_crosswalk.refresh`) when buses
  appear on unknown lines and [`/config/version`](../feeds/tracker-config-version.md)
  has moved.
- By hand: `python build_crosswalk.py --fetch` (downloads
  [`/topo`](../feeds/tracker-topo.md), ~28 MB; the raw `topo.json` is not
  in git).
- Commit the results when convenient. `ops/update.ps1` discards the
  poller's local copies before pulling, and the poller rebuilds again if the
  pulled ones are stale.

# Outputs

- [`routes.csv`](../datasets/routes-csv.md): vendor line ID → route number,
  name, color.
- [`stops.csv`](../datasets/stops-csv.md): stop codes, names, positions.
- [`network.geojson`](../datasets/network-geojson.md): one MultiLineString
  per route and one Point per stop, plus the topo version it was built from;
  the map draws it as the background.
