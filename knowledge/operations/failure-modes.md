---
type: Playbook
title: Failure modes
description: What happens, and what to do, when the vendor, the machine, MATA's routes, the GTFS feed, the official feed or the detour endpoints misbehave, and how often each has since 2026-09-25.
tags: [ops]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:01:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: poller-code
    resource: ../../cadavl_to_gtfs_rt.py
    title: cadavl_to_gtfs_rt.py, run_poller (the "poll failed" handler and the 10 s clock)
  - id: official-code
    resource: ../../official_feed.py
    title: official_feed.py, Official.update
  - id: detours-code
    resource: ../../cadavl_detours.py
    title: cadavl_detours.py, DetourLog.update and build_segment_index
  - id: schedule-code
    resource: ../../schedule.py
    title: schedule.py, Schedule.timetable (RETRY_S)
  - id: update-ps1
    resource: ../../ops/update.ps1
    title: ops/update.ps1 (git checkout of the crosswalk files)
  - id: poller-log
    resource: ../../data/poller.log
    title: data/poller.log, 2026-09-25 20:12 to 2026-10-05 22:47 (read-only grep)
  - id: objetssuppl-fix
    resource: https://github.com/jpbranson/mata-scraper-claude/commit/8de1cc1
    title: "8de1cc1 cadavl_detours: treat a null objetsSuppl as no itineraries"
  - id: copy-2026-10-05
    resource: ../../findings_page/snapshot-2026-10-05/
    title: Copy of data/ taken 2026-10-05 22:37 (poll gaps, detour records, cadavl rows)
---

# Failure modes and the response to each

| Failure | What happens | Response |
|---|---|---|
| Vendor down or slow | The [poller](../system/poller.md) logs `poll failed: ...` and writes nothing for that poll, and skips the official-feed and detour steps for it. A read timeout (10 s) overruns the tick, so the next tick is skipped too | None; gaps in the history are just missing rows |
| Windows refuses to replace `data/latest.json` | `poll failed: [WinError 5] Access is denied`. The history rows and replay frame are already written; `latest.json` stays one poll old, and `vehicle_positions.pb`, the log line and the official-feed and detour steps are skipped for that poll. The code puts it down to `http.server` having the file open[^poller-code] | None; the next poll rewrites it |
| Machine reboots | Task Scheduler restarts both tasks; the day file is appended, not overwritten | None |
| MATA changes routes or renumbers lines | The poller notices unmapped lines and [rebuilds the crosswalk](../system/crosswalk-builder.md) itself, then re-reads the same poll, so no `cadavl:<id>` rows are stored when the rebuild succeeds. Rows logged while it can't rebuild (a failed check waits 15 minutes) keep `cadavl:<id>` | `.\ops\backfill.ps1` remaps them in the history (`backfill_routes.py`); see [backfill tools](../system/backfill-tools.md) for what its replay step does to past days |
| [GTFS feed](../feeds/gtfs-timetable.md) down | The cached `data/gtfs.zip` is used; with none, stop panels say there's no timetable, and the load is retried every 15 minutes[^schedule-code] | Everything else carries on |
| [Official GTFS-RT](../feeds/official-gtfs-rt.md) down | `official <feed> failed: ...`, per feed; that feed is fetched again the next poll; its archive has a gap[^official-code] | Nothing else notices |
| Detour endpoints down, or a payload the parser can't read | `detour log failed: ...`; no record that hour, for detours or rider messages | [Tried again](../system/detour-logger.md) the next hour |
| Vendor changes the JSON shape | `normalize_vehicle` returns nothing useful | Save a fresh payload and debug with the `--sample` check ([sample payload](../datasets/sample-payload.md)) |
| MATA reroutes lines | [`schematic.json`](../datasets/schematic-json.md) goes out of date | Rerun `build_schematic.py` ([schematic map](../system/schematic-map.md)); line-ID renumberings alone don't need it |

# Observed, 2026-09-25 20:12 to 2026-10-05 22:47

From the time-stamped [`poller.log`](../datasets/poller-log.md) (read-only
grep) and the 2026-10-05 copy of `data/`.[^poller-log] [^copy-2026-10-05]
No Python traceback appears in the log; every failure was caught and
logged.

**Vendor errors on `/topo/vehicules`**: 319 failed polls against about
72,300 good ones (0.44%).

| Day | Failed | Read timeout (10 s) | 503 | 502 | 500 | Connection reset |
|---|---|---|---|---|---|---|
| 09-26 | 20 | 6 | 12 | 0 | 2 | 0 |
| 09-27 | 17 | 9 | 4 | 2 | 2 | 0 |
| 09-28 | 33 | 25 | 5 | 1 | 2 | 0 |
| 09-29 | 18 | 13 | 4 | 1 | 0 | 0 |
| 09-30 | 55 | 48 | 4 | 1 | 2 | 0 |
| 10-01 | 46 | 38 | 6 | 1 | 1 | 0 |
| 10-02 | 63 | 45 | 12 | 4 | 2 | 0 |
| 10-03 | 9 | 3 | 5 | 0 | 0 | 1 |
| 10-04 | 23 | 8 | 12 | 0 | 2 | 1 |
| 10-05 | 35 | 27 | 6 | 0 | 2 | 0 |

- Most come in bursts of one to four minutes, mostly between 04:00 and
  07:00. The two longest: 2026-09-30 05:37–05:46 (30 failed polls) and
  2026-10-02 23:10–23:23 (46).
- Consecutive read timeouts are logged 20 s apart: each one costs its tick
  and the next.
- In the stored history from 2026-09-26 on, every gap between polls is a
  multiple of 10 s, and the longest within a service day are those two
  outages (540 s and 840 s).

**`[WinError 5] Access is denied` replacing `latest.json`**: 13 times
(09-26 ×1, 09-28 ×7, 10-01 ×1, 10-03 ×2, 10-04 ×2), plus 3 before the log
was stamped. No history is lost; see the table above.

**Official feed**: 5 failures, all fetched again the next poll:
VehiclePosition read timeouts (5 s) on 10-03 23:31 and 10-04 22:44,
connection resets on 10-03 21:05 and 10-04 17:28, and a 502 on Alert on
10-03 21:49.

**Detour log**: `detour log failed: TypeError("'NoneType' object is not
subscriptable")` 19 times, 2026-09-25 22:12 to 2026-09-27 19:00: the
tracker sends `objetsSuppl: null` when no line is detoured, and the parser
didn't allow for it.[^detours-code] Those 19 hourly checks saved nothing,
rider messages included; the longest hole in the log runs from 2026-09-26
22:00 to 2026-09-27 19:38. Fixed in `8de1cc1`, live from the 19:38 restart
that evening.[^objetssuppl-fix]

**Crosswalk rebuilds**: the poller rebuilt the crosswalk on the day's first
poll on 2026-09-30 04:00 (topo version 198256 → 198282; every line ID
changed) and again on 2026-10-02 04:00 at the same version 198282, after a
restart at 2026-10-01 23:09 when no buses were out. `ops/update.ps1` checks
the committed crosswalk files out before pulling,[^update-ps1] and the
198282 files are still uncommitted, so a restart through it costs another
~28 MB rebuild on the next poll with buses. No `cadavl:<id>` row was
stored in either case.

**Restarts** (a "timetable for" line outside the day's first poll):
2026-09-25 20:12 and 21:12, 2026-09-27 19:38, 19:54 and 20:23, 2026-10-01
23:09. The log alone doesn't say which were reboots.

[^poller-code]: cadavl_to_gtfs_rt.py, run_poller (the "poll failed" handler and the 10 s clock)
[^official-code]: official_feed.py, Official.update
[^detours-code]: cadavl_detours.py, DetourLog.update and build_segment_index
[^schedule-code]: schedule.py, Schedule.timetable (RETRY_S)
[^update-ps1]: ops/update.ps1 (git checkout of the crosswalk files)
[^poller-log]: data/poller.log, 2026-09-25 20:12 to 2026-10-05 22:47 (read-only grep)
[^objetssuppl-fix]: 8de1cc1 cadavl_detours: treat a null objetsSuppl as no itineraries
[^copy-2026-10-05]: Copy of data/ taken 2026-10-05 22:37 (poll gaps, detour records, cadavl rows)
