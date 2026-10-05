---
type: API Endpoint
title: Tracker network (/topo)
description: The tracker's full network definition (lines, stops, segments, deviations), ~28 MB, read only to rebuild the route and stop crosswalk.
resource: https://swiv.mata.cadavl.com/SWIV/MATA/proxy/restWS/topo
tags: [tracker, crosswalk]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: crosswalk-code
    resource: ../../build_crosswalk.py
    title: build_crosswalk.py docstring
---

# What it is

`/topo` (no suffix) is the [tracker's](swiv-tracker.md) full network: 25
lines, about 3,700 stops (3,766 and 2,283 deviations when
captured).[^crosswalk-code] It is ~28 MB, took 14 seconds to serve, and
changes rarely, so it is fetched once and cached (the raw copy is
`topo.json`, not in git); [`/config/version`](tracker-config-version.md)
says when it has changed.

# Used for

The [crosswalk builder](../system/crosswalk-builder.md) turns it into
[routes.csv](../datasets/routes-csv.md), [stops.csv](../datasets/stops-csv.md)
and [network.geojson](../datasets/network-geojson.md) (route lines from its
2-point segments). Stop codes come from its `mnemoPointArret`.

# Limits

- Every internal line and stop ID changes with each new topo version (see
  [known limits](tracker-vehicles.md#known-limits)).
- It lists the lines that pass a stop, including ones that pass without
  stopping, so which routes *serve* a stop comes from the timetable instead
  ([schedule files](../datasets/schedule-files.md)).

[^crosswalk-code]: build_crosswalk.py docstring
