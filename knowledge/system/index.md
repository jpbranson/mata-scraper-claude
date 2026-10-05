# Overview

* [Architecture](architecture.md) - One poller writes everything under data/; static pages, one SQL file and the findings page read it; the crosswalk builder keeps route and stop names current.

# Collection

* [Poller](poller.md) - cadavl_to_gtfs_rt.py, the one long-running process; every 10 s during service hours it fetches the tracker's vehicles and writes the history, the snapshot, the replay frames and a GTFS-RT feed, and drives the timetable, official-feed and detour modules.
* [Timetable and arrivals](timetable-and-arrivals.md) - schedule.py loads MATA's GTFS timetable once per service day, writes per-route schedule files for the pages, and every poll names the trip each bus is running and logs when it served each stop.
* [Official feed archiver](official-feed-archiver.md) - official_feed.py fetches MATA's own GTFS-Realtime vehicle positions and alerts every poll, and trip updates every 5 minutes, and appends each new snapshot to data/official/ as flat rows.
* [Detour logger](detour-logger.md) - cadavl_detours.py checks the tracker's detours and rider messages hourly and appends a record to data/detours/ whenever either changed, so detour impact can be studied later.
* [Crosswalk builder](crosswalk-builder.md) - build_crosswalk.py turns the tracker's full network (/topo) into routes.csv, stops.csv and network.geojson, keyed on stable route numbers and stop codes; the poller reruns it when line IDs change.
* [Backfill tools](backfill-tools.md) - backfill_routes.py remaps history rows stored as cadavl:<id> to route numbers, and backfill_replay.py rebuilds a day's replay frames and arrivals from the full history; ops/backfill.ps1 runs both with the poller paused.

# Views

* [Live map](live-map.md) - map.html, one static Leaflet page that shows every bus live (delay as color, load as size, heading, trails), stop and bus panels from the timetable and arrivals log, and a replay of any recorded day.
* [Route strips](route-strips.md) - strips.html, one vertical line diagram per stop pattern of a route, with live or replayed buses, their delay, the gap to the bus ahead, and load as a band along the line.
* [Schematic map](schematic-map.md) - schematic.html draws the whole network as a subway map from schematic.json (laid out by LOOM via build_schematic.py), with live or replayed buses sliding along their own lanes and load shown as a band.
* [Shared page code](transit-js.md) - transit.js and pages.css, shared by the strips and schematic pages (and helpers the map uses) - page links, route chips, the replay bottom bar, and placing a bus along its route's stop pattern.

# Analysis

* [Analysis SQL](analysis-sql.md) - analysis.sql, one DuckDB file of views over everything in data/ and a tagged query per question; the findings cite its queries by tag.
* [Findings page](findings-page.md) - findings_page/ builds "Memphis Buses, Measured", the findings as one page of charts (inline SVG, no libraries) published as a claude.ai artifact, from one copy of data/.
