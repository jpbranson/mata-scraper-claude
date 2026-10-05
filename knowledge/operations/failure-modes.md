---
type: Playbook
title: Failure modes
description: What happens, and what to do, when the vendor, the machine, MATA's routes, the GTFS feed, the official feed or the detour endpoints misbehave.
tags: [ops]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
---

# Failure modes and the response to each

| Failure | What happens | Response |
|---|---|---|
| Vendor down or slow | The [poller](../system/poller.md) logs and retries next cycle | None; gaps in the history are just missing rows |
| Machine reboots | Task Scheduler restarts both tasks; the day file is appended, not overwritten | None |
| MATA changes routes or renumbers lines | The poller notices unmapped lines and [rebuilds the crosswalk](../system/crosswalk-builder.md) itself; rows from before the rebuild keep `cadavl:<id>` | `.\ops\backfill.ps1` remaps them in the history (`backfill_routes.py`) and rebuilds the replay and arrivals files ([backfill tools](../system/backfill-tools.md)) |
| [GTFS feed](../feeds/gtfs-timetable.md) down | The cached `data/gtfs.zip` is used; with none, stop panels say there's no timetable | Everything else carries on |
| [Official GTFS-RT](../feeds/official-gtfs-rt.md) down | Logged per feed; its archive has a gap | Nothing else notices |
| Detour endpoints down | Logged | [Tried again](../system/detour-logger.md) the next hour |
| Vendor changes the JSON shape | `normalize_vehicle` returns nothing useful | Save a fresh payload and debug with the `--sample` check ([sample payload](../datasets/sample-payload.md)) |
| MATA reroutes lines | [`schematic.json`](../datasets/schematic-json.md) goes out of date | Rerun `build_schematic.py` ([schematic map](../system/schematic-map.md)); line-ID renumberings alone don't need it |
