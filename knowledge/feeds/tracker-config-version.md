---
type: API Endpoint
title: Tracker network version (/config/version)
description: A small integer that bumps whenever /topo changes; checked cheaply to know when the crosswalk is stale.
resource: https://swiv.mata.cadavl.com/SWIV/MATA/proxy/restWS/config/version
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

An integer that bumps when [`/topo`](tracker-topo.md) changes (196203 when
first captured).[^crosswalk-code] Tiny, so it can be polled cheaply instead
of re-downloading the 28 MB network.

# Used for

The version a crosswalk was built from is stored as `topo_version` in
[network.geojson](../datasets/network-geojson.md). When buses show up on
line IDs [routes.csv](../datasets/routes-csv.md) doesn't know, the
[poller](../system/poller.md) asks this endpoint (at most every 15 minutes);
if it moved past the recorded version, the
[crosswalk builder](../system/crosswalk-builder.md) rebuilds.

[^crosswalk-code]: build_crosswalk.py docstring
