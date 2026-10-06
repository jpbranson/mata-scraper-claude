---
type: Component
title: Crosswalk builder
description: build_crosswalk.py turns the tracker's full network (/topo) into routes.csv, stops.csv and network.geojson, keyed on stable route numbers and stop codes; the poller reruns it when line IDs change.
resource: ../../build_crosswalk.py
tags: [crosswalk]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:01:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: crosswalk-code
    resource: ../../build_crosswalk.py
    title: build_crosswalk.py, main and refresh
  - id: poller-log
    resource: ../../data/poller.log
    title: data/poller.log, "topo version" and "wrote" lines; git diff of routes.csv and network.geojson
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
  [`/topo`](../feeds/tracker-topo.md), ~28 MB, and saves it as `topo.json`,
  which is not in git), or `--topo topo.json` to rebuild from a saved copy.
  `--topo` records no topo version (`topo_version` null), so the poller's
  next check rebuilds whatever `/config/version` says.[^crosswalk-code]
- Commit the results when convenient. `ops/update.ps1` discards the
  poller's local copies before pulling, and the poller rebuilds again if the
  pulled ones are stale.
- Seen live: topo version 198256 → 198282 on 2026-09-30, every line ID
  changed. The poller rebuilt on the day's first poll (04:00), and again on
  2026-10-02 04:00 at the same version, so by then the working copy held
  older files again; the poller had restarted at 2026-10-01 23:09, and
  `update.ps1` checks out the committed (198256) ones. The 198282 files are
  uncommitted as of 2026-10-05 ([failure
  modes](../operations/failure-modes.md)).[^poller-log]

# Outputs

- [`routes.csv`](../datasets/routes-csv.md): vendor line ID → route number,
  name, color.
- [`stops.csv`](../datasets/stops-csv.md): stop codes, names, positions.
- [`network.geojson`](../datasets/network-geojson.md): one MultiLineString
  per route and one Point per stop, plus the topo version it was built from;
  the map draws it as the background.

[^crosswalk-code]: build_crosswalk.py, main and refresh
[^poller-log]: data/poller.log, "topo version" and "wrote" lines; git diff of routes.csv and network.geojson
