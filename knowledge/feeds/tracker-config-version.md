---
type: API Endpoint
title: Tracker network version (/config/version)
description: A small integer that bumps whenever /topo changes; checked cheaply to know when the crosswalk is stale.
resource: https://swiv.mata.cadavl.com/SWIV/MATA/proxy/restWS/config/version
tags: [tracker, crosswalk]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: crosswalk-code
    resource: ../../build_crosswalk.py
    title: build_crosswalk.py (docstring, fetch_version, refresh)
  - id: poller-code
    resource: ../../cadavl_to_gtfs_rt.py
    title: cadavl_to_gtfs_rt.py (run_poller, TOPO_CHECK_SECONDS)
  - id: poller-log
    resource: ../../data/poller.log
    title: poller.log, crosswalk rebuilds at 2026-09-30 04:00 and 2026-10-02 04:00
---

# What it is

An integer that bumps when [`/topo`](tracker-topo.md) changes, sent as
`{"version": [{"valeur": 198282}]}`.[^crosswalk-code] Tiny, so it can be
polled cheaply instead of re-downloading the 28 MB network. It was 196203
when first captured (2026-09-23) and 198282 from 2026-09-30; the
[version history](tracker-topo.md#versions) is with the network.[^poller-log]

# Used for

The version a crosswalk was built from is stored as `topo_version` in
[network.geojson](../datasets/network-geojson.md). When buses show up on
line IDs [routes.csv](../datasets/routes-csv.md) doesn't know, the
[poller](../system/poller.md) asks this endpoint (at most every 15
minutes);[^poller-code] if it differs from the recorded version, the
[crosswalk builder](../system/crosswalk-builder.md) rebuilds. So a new
version is picked up only when it renumbers lines; every one so far has.

[^crosswalk-code]: build_crosswalk.py (docstring, fetch_version, refresh)
[^poller-code]: cadavl_to_gtfs_rt.py (run_poller, TOPO_CHECK_SECONDS)
[^poller-log]: poller.log, crosswalk rebuilds at 2026-09-30 04:00 and 2026-10-02 04:00
