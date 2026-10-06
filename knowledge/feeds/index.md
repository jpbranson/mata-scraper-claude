# The tracker (SWIV / CADAVL)

* [MATA bus tracker (SWIV / CADAVL)](swiv-tracker.md) - MATA's public bus tracker site, run by the vendor CADAVL, whose unauthenticated JSON endpoints feed the poller, the crosswalk and the detour log.
* [Tracker vehicles (/topo/vehicules)](tracker-vehicles.md) - Every bus's position, heading, speed, next stop, schedule adherence and passenger load, refreshed every 10 s; the only endpoint polled continuously.
* [Tracker network (/topo)](tracker-topo.md) - The tracker's full network definition (lines, stops, segments, deviations), ~28 MB, read only to rebuild the route and stop crosswalk.
* [Tracker network version (/config/version)](tracker-config-version.md) - A small integer that bumps whenever /topo changes; checked cheaply to know when the crosswalk is stale.
* [Tracker detours (/topo/refresh)](tracker-detours.md) - The network's current detours (bypassed segments, replacement geometry, affected stops), changing over days; saved hourly to the detour log.
* [Tracker rider messages (/iv/message)](tracker-messages.md) - The tracker's rider-facing notices, detours and trips out of service alike; saved hourly to the detour log.
* [Tracker stop popup (/horaires/pta)](tracker-stop-times.md) - The tracker's own stop popup, the next one or two times per route at a stop; unused, kept as a cross-check.

# MATA's GTFS feeds

* [MATA GTFS timetable (GTFS_MATA.zip)](gtfs-timetable.md) - MATA's published timetable from the tracker's vendor, rebuilt nightly; it lines up exactly with the tracker and is the base for trip matching, stop schedules and the schematic.
* [MATA official GTFS-Realtime feed](official-gtfs-rt.md) - MATA's own GTFS-RT vehicle positions, trip updates and alerts from the tracker's vendor; it has trip IDs, report times and cancellations the tracker lacks, but no delay, and positions only every 30 s.
