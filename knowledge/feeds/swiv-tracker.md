---
type: API
title: MATA bus tracker (SWIV / CADAVL)
description: MATA's public bus tracker site, run by the vendor CADAVL, whose unauthenticated JSON endpoints feed the poller, the crosswalk and the detour log.
resource: https://swiv.mata.cadavl.com/SWIV/MATA
tags: [tracker]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: poller-code
    resource: ../../cadavl_to_gtfs_rt.py
    title: cadavl_to_gtfs_rt.py (BASE, HEADERS)
---

# Overview

MATA's public bus tracker (the "SWIV" site) is fed by a vendor system called
CADAVL. Its JSON endpoints are unauthenticated and stateless: no cookies,
tokens, or keys. Everything here was confirmed against live traffic; details
live in the docstrings of the scripts.

The same vendor publishes MATA's [GTFS timetable](gtfs-timetable.md) and its
[official GTFS-Realtime feed](official-gtfs-rt.md).

# Access

- JSON endpoints live under
  `https://swiv.mata.cadavl.com/SWIV/MATA/proxy/restWS` (`BASE`).[^poller-code]
- Request headers are copied from a working browser request.
  `Referer: https://swiv.mata.cadavl.com/SWIV/MATA` and
  `X-Requested-With: XMLHttpRequest` are the two most likely to be checked
  by the proxy; keep them.

# Endpoints

| Endpoint | What it is | Size / cadence | Used for |
|---|---|---|---|
| [`/topo/vehicules`](tracker-vehicles.md) | Every bus: position, heading, speed, next stop, schedule adherence, passenger load | ~12 KB, refreshes every 10 s | The [poller](../system/poller.md), the only thing hit continuously |
| [`/topo`](tracker-topo.md) | Full network: 25 lines, ~3,700 stops | ~28 MB, changes rarely | [routes.csv](../datasets/routes-csv.md) / [stops.csv](../datasets/stops-csv.md) crosswalk |
| [`/config/version`](tracker-config-version.md) | Integer that bumps when `/topo` changes | tiny | Knowing when to rebuild the crosswalk |
| [`/topo/refresh`](tracker-detours.md) | Current detours (bypassed and replacement segments) | ~150–385 KB, changes over days | [Detour log](../datasets/detour-log.md), hourly |
| [`/iv/message`](tracker-messages.md) | Rider-facing notices: detours, and trips out of service | small | [Detour log](../datasets/detour-log.md), hourly |
| [`/horaires/pta/<stop id>`](tracker-stop-times.md) | The tracker's own stop popup: next one or two times per route | small | Nothing (kept as a cross-check) |

[^poller-code]: cadavl_to_gtfs_rt.py (BASE, HEADERS)
