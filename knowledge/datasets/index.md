# Recorded by the poller (data/, not in git)

* [Position history](positions.md) - One row per bus per poll (every 10 s of service), in daily gzipped JSONL partitions; the history every delay and load question is answered from.
* [Live snapshot (latest.json)](latest-snapshot.md) - The current poll's rows plus each bus's recent trail, rewritten atomically every 10 s; what the pages and the "right now" query read.
* [Replay frames](replay-frames.md) - One compact frame of every bus each 30 s, one file per local day; drives the pages' replay scrubber and trails.
* [Saved timetables (data/schedule)](schedule-files.md) - Each service day's timetable as the pages need it, per stop and per route with its stop patterns; the only record of past days' timetables.
* [Arrivals log](arrivals-log.md) - Each time a bus served a stop, with the trip it was matched to and its delay, split by day and route; ~42k a weekday.
* [Official archive - vehicle positions](official-vehicles.md) - MATA's official GTFS-RT vehicle positions, one row per bus per 30 s snapshot, with trip IDs and report times the tracker lacks; from 2026-09-25.
* [Official archive - trip updates](official-trip-updates.md) - MATA's official GTFS-RT trip updates every 5 minutes, with per-stop predictions and cancelled trips; from 2026-09-25.
* [Official archive - alerts](official-alerts.md) - MATA's official GTFS-RT rider alerts, one row each time the set of alerts changed; from 2026-09-25.
* [Detour log](detour-log.md) - The tracker's detours and rider messages, one line each time either changed (checked hourly); from 2026-09-25 20:12, for the detour-impact question.
* [Our GTFS-RT feed (vehicle_positions.pb)](vehicle-positions-pb.md) - A GTFS-Realtime VehiclePosition feed the poller rewrites every poll; fresher than MATA's but without trip IDs, and nothing reads it.
* [Poller log (poller.log)](poller-log.md) - The mata-poller task's output, one time-stamped line per poll plus any errors; a few hundred KB a day, safe to delete.

# Committed to git

* [Route crosswalk (routes.csv)](routes-csv.md) - The tracker's internal line IDs mapped to MATA route numbers, names and colors; rebuilt whenever the vendor renumbers its lines.
* [Stop crosswalk (stops.csv)](stops-csv.md) - Every stop in the tracker's network with its stable stop code, name, position and the internal lines that pass it.
* [Network map (network.geojson)](network-geojson.md) - Every route's line and every stop as GeoJSON, with the topo version it was built from; the live map's background.
* [Schematic layout (schematic.json)](schematic-json.md) - The subway-style network layout from LOOM, timepoints as stations and per-route edge chains between them; what schematic.html draws.
* [Sample tracker payload (vehicules.json)](sample-payload.md) - A saved /topo/vehicules response (41 buses, 20 lines) that the poller's offline --sample check parses; the project's regression check.
