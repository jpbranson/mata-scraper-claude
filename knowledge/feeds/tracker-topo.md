---
type: API Endpoint
title: Tracker network (/topo)
description: The tracker's full network definition (lines, stops, segments, deviations), ~28 MB, read only to rebuild the route and stop crosswalk.
resource: https://swiv.mata.cadavl.com/SWIV/MATA/proxy/restWS/topo
tags: [tracker, crosswalk]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: crosswalk-code
    resource: ../../build_crosswalk.py
    title: build_crosswalk.py docstring
  - id: poller-code
    resource: ../../cadavl_to_gtfs_rt.py
    title: cadavl_to_gtfs_rt.py (refresh_crosswalk, TOPO_CHECK_SECONDS)
  - id: update-ps1
    resource: ../../ops/update.ps1
    title: ops/update.ps1 (git checkout -- routes.csv stops.csv network.geojson)
  - id: poller-log
    resource: ../../data/poller.log
    title: poller.log, crosswalk rebuilds at 2026-09-30 04:00 and 2026-10-02 04:00
  - id: crosswalk-diff
    resource: git diff of routes.csv, stops.csv and network.geojson (working tree of 2026-10-02 04:00 against HEAD 9585066)
    title: Topo 198256 (in git) against 198282 (working tree)
  - id: snapshot-1005
    resource: Measured on findings_page/snapshot-2026-10-05 (copy of data/ taken 2026-10-05 22:37 CDT)
    title: Measurements on the 2026-10-05 snapshot (line IDs in the position history)
---

# What it is

`/topo` (no suffix) is the [tracker's](swiv-tracker.md) full network: 25
lines and 3,762 stops in version 198282 (3,766 stops and 2,283 deviations
when first captured).[^crosswalk-code] It is ~28 MB and took 14 seconds to
serve when captured; the poller's two downloads of 198282 took 5 and 8
seconds.[^poller-log] It changes rarely, so it is fetched only when needed
and cached as `topo.json` (31.6 MB as re-saved, not in git);
[`/config/version`](tracker-config-version.md) says when it has changed.

# Used for

The [crosswalk builder](../system/crosswalk-builder.md) turns it into
[routes.csv](../datasets/routes-csv.md), [stops.csv](../datasets/stops-csv.md)
and [network.geojson](../datasets/network-geojson.md) (route lines from its
2-point segments). Stop codes come from its `mnemoPointArret`.

# Versions

Each new version so far renumbered every internal line and stop ID; the
last two took effect overnight, before the first bus. The stop count went
from 3,766 to 3,762 with 198238 and has stayed there.[^snapshot-1005][^crosswalk-diff]

| Version | In service | Route 01's `idLigne` |
|---|---|---|
| 196203 | First captured, 2026-09-23 | 109149 |
| 198238 | 2026-09-23 evening | 111245 |
| 198256 | 2026-09-24 to 09-29; the version committed to git | 111295 |
| 198282 | From 2026-09-30 | 111401 |

198282 against 198256: the same 25 routes with the same names and colors,
the same 3,762 stop codes and names, and the same route geometry. Besides
the IDs, one stop moved about 17 m (`JONHOLNF`, Jonetta St @ Holmes Rd),
the trolley (route 100) is listed at 10 more downtown stops on Third and
Second St, and `has_alerts` is set on route 42 only (it was on 9
routes).[^crosswalk-diff]

# Rebuilds

The [poller](../system/poller.md) rebuilds the crosswalk itself: when a
poll has buses on line IDs routes.csv doesn't know, it checks
`/config/version` (at most every 15 minutes) and, if that differs from the
version in network.geojson, downloads `/topo` and rewrites all three files
before saving the poll, so no row is stored unmapped.[^poller-code] It
rebuilt 198282 at 2026-09-30 04:00:01, on the first poll of the
day.[^poller-log]

Those rebuilds are not committed. `ops/update.ps1` discards the working
copies (`git checkout --`) before pulling,[^update-ps1] so after the update
at 2026-10-01 23:09 the files were 198256 again and the poller downloaded
198282 a second time at 2026-10-02 04:00:00. As of 2026-10-05 the working
tree holds 198282, uncommitted; git still has 198256.[^poller-log]

# Limits

- Every internal line and stop ID changes with each new topo version (see
  [known limits](tracker-vehicles.md#known-limits)).
- It lists the lines that pass a stop, including ones that pass without
  stopping, so which routes *serve* a stop comes from the timetable instead
  ([schedule files](../datasets/schedule-files.md)).

[^crosswalk-code]: build_crosswalk.py docstring
[^poller-code]: cadavl_to_gtfs_rt.py (refresh_crosswalk, TOPO_CHECK_SECONDS)
[^update-ps1]: ops/update.ps1
[^poller-log]: poller.log, crosswalk rebuilds at 2026-09-30 04:00 and 2026-10-02 04:00
[^crosswalk-diff]: Topo 198256 (in git) against 198282 (working tree)
[^snapshot-1005]: Measurements on the 2026-10-05 snapshot
