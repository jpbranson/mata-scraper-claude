---
type: Architecture
title: Architecture
description: One poller writes everything under data/; static pages, one SQL file and the findings page read it; the crosswalk builder keeps route and stop names current.
tags: [architecture]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
---

# Diagram

```
                 every 10 s
 CADAVL ───────────────────▶  cadavl_to_gtfs_rt.py  (poller, one process)
                                      │
                                      ├─▶ data/positions/dt=YYYY-MM-DD/positions.jsonl.gz   history (append)
                                      ├─▶ data/latest.json                                  current snapshot
                                      ├─▶ data/replay/YYYY-MM-DD.jsonl                       one frame per 30 s, for replay
                                      ├─▶ data/schedule/YYYY-MM-DD/, data/arrivals/YYYY-MM-DD/  timetable + when buses came (schedule.py)
                                      ├─▶ data/official/dt=YYYY-MM-DD/                      official GTFS-RT archive (official_feed.py)
                                      ├─▶ data/detours/dt=YYYY-MM-DD/detours.jsonl.gz        detours + rider messages, when changed (cadavl_detours.py)
                                      └─▶ data/vehicle_positions.pb                         GTFS-RT feed
 GTFS_MATA.zip ── once a day ──▶ poller (schedule.py)
 official GTFS-RT ── every 30 s (trip updates every 5 min) ──▶ poller (official_feed.py)
 /topo/refresh, /iv/message ── hourly ──▶ poller (cadavl_detours.py)
 /topo ── when line IDs change ──▶ poller (build_crosswalk.py) ──▶ routes.csv, stops.csv, network.geojson

 map.html  ── data/latest.json every 10 s + the day's replay file + stop files on click ──▶  live map, replay, stop times  (served by python -m http.server)
 strips.html, schematic.html ── data/latest.json every 10 s + route files ──▶  route strips, subway-style map
 schematic.json ── built by build_schematic.py with LOOM (occasionally, on Linux/WSL) ──▶  the schematic layout
 analysis.sql ── DuckDB reads data/ (history, arrivals, timetables, official archive) ──▶  the three questions and the backlog (knowledge/findings/)
 findings_page/ ── a copy of data/ + analysis.sql's views ──▶  the findings as one page of charts (published as a claude.ai artifact)
 routes.csv / stops.csv / network.geojson ── built by build_crosswalk.py ──▶  names, colors, route lines
```

# What does the work

Five files do the work: the [poller](poller.md), its [timetable
module](timetable-and-arrivals.md), the [map page](live-map.md), the [SQL
file](analysis-sql.md), and the [crosswalk builder](crosswalk-builder.md).
The poller's other two modules, [`official_feed.py`](official-feed-archiver.md)
and [`cadavl_detours.py`](detour-logger.md), only archive. Everything else
in the repo is optional:

- one-off tools: [`backfill_replay.py`, `backfill_routes.py`](backfill-tools.md);
- the two extra views, [`strips.html`](route-strips.md) and
  [`schematic.html`](schematic-map.md), sharing [`transit.js` and
  `pages.css`](transit-js.md), with `build_schematic.py` making the
  schematic's layout;
- the [findings page](findings-page.md) (`findings_page/`).

Inputs: the [SWIV tracker](../feeds/swiv-tracker.md), [MATA's GTFS
timetable](../feeds/gtfs-timetable.md) and [MATA's official
GTFS-Realtime feed](../feeds/official-gtfs-rt.md). Outputs: the datasets
under [datasets/](../datasets/). Running it: [running it](../operations/running-it.md).
