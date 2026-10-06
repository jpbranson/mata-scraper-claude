---
type: Runbook
title: Running it
description: Install, update and backfill the always-on Windows home machine that runs the poller and the map server as two scheduled tasks.
resource: ../../ops/setup.ps1
tags: [ops]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:39:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: setup-ps1
    resource: ../../ops/setup.ps1
    title: ops/setup.ps1
  - id: update-ps1
    resource: ../../ops/update.ps1
    title: ops/update.ps1
  - id: backfill-ps1
    resource: ../../ops/backfill.ps1
    title: ops/backfill.ps1
  - id: data-sizes
    resource: ../../data/
    title: data/ folder sizes, 2026-09-28 to 2026-10-04 (read-only du)
  - id: gitignore
    resource: ../../.gitignore
    title: .gitignore
---

# The machine

An always-on Windows machine at home ([why](../decisions/home-hosting.md)).
Everything runs natively (Python, `http.server`, DuckDB); only "keep it
running" is Windows-specific, and Task Scheduler does that.

Needs are tiny: one 12 KB request every 10 s (plus the official feed's two
of ~2 KB, ~120 KB every 5 minutes, and the detour check's ~150 KB an hour).
Disk, measured 2026-09-28 to 2026-10-04: ~43 MB a weekday (history 15–17.5
MB, official archive 12–14.5, replay frames ~7.5, arrivals ~3.8, saved
timetable ~1.1), ~34 MB on the Saturday and ~21 MB on the Sunday; the
detour log adds 4–107 KB a day.[^data-sizes]

- The machine's clock is already Central time, so the service-hours check
  needs no time-zone setting.
- Set Power settings to never sleep (and, on a laptop, "do nothing" on lid
  close, plugged in).

# Install (once)

From an administrator PowerShell in the repo folder, with Python 3.10+ on
PATH:

    Set-ExecutionPolicy -Scope Process Bypass
    .\ops\setup.ps1

It makes the venv (`.venv`) from `requirements.txt` (`requests`,
`gtfs-realtime-bindings`, `duckdb`), registers two scheduled tasks that
start at boot with nobody logged in and restart a minute after any crash,
and opens port 8000 to the home LAN and Tailscale only:

- `mata-poller`: `python -u cadavl_to_gtfs_rt.py` ([poller](../system/poller.md)),
  output appended to [`data\poller.log`](../datasets/poller-log.md).
- `mata-web`: `python -m http.server 8000`; the map is at
  `http://localhost:8000/map.html` ([live map](../system/live-map.md)).

Setup also grants the installing account read + execute on both tasks,
which is enough to start and stop them without admin.

# After pulling new code

`.\ops\update.ps1` pulls, re-runs `pip install -r requirements.txt`, and
restarts both tasks. It needs no admin. It discards the poller's local
copies of the [crosswalk files](../system/crosswalk-builder.md) before
pulling; the poller rebuilds them again if the pulled ones are stale.

Run it from your own PowerShell, not from an agent's shell ([working with
live data](working-with-live-data.md)).

# Backfill

After the poller has logged `cadavl:<id>` routes, for days recorded before
replay or arrivals existed, or to bring a day's replay frames up to the
current format, run `.\ops\backfill.ps1` (every day) or
`.\ops\backfill.ps1 2026-09-24` (one day) from your own PowerShell window.
It pauses the poller, runs `backfill_routes.py` (every history file) and
`backfill_replay.py`, and starts the poller again ([backfill
tools](../system/backfill-tools.md)).

Any day works: past days are matched to the timetable saved that day
([backfill tools](../system/backfill-tools.md)).

# Analysis on Windows

Run [`analysis.sql`](../system/analysis-sql.md) from inside a copy of the
data made by `findings_page\snapshot.py`, with the DuckDB CLI
(`duckdb.exe`, a single file) or the venv's Python `duckdb`.

# What git tracks

Code, the crosswalk outputs ([`routes.csv`](../datasets/routes-csv.md),
[`stops.csv`](../datasets/stops-csv.md),
[`network.geojson`](../datasets/network-geojson.md)),
[`schematic.json`](../datasets/schematic-json.md),
[`vehicules.json`](../datasets/sample-payload.md) (the sample payload for
`--sample`), and this knowledge bundle. `data/`, the raw `topo.json`, the
copies of `data/` under `findings_page/snapshot*/` and `findings_page/out/`
are ignored, as are `.venv/` and `__pycache__/`.[^gitignore]

The poller rewrites the crosswalk files in the working copy when MATA
renumbers its lines, and they stay modified until someone commits them
(the 2026-09-30 rebuild, topo version 198282, is uncommitted as of
2026-10-05). Until then `update.ps1` puts the committed ones back and the
poller rebuilds again ([failure modes](failure-modes.md)).

[^data-sizes]: data/ folder sizes, 2026-09-28 to 2026-10-04 (read-only du)
[^gitignore]: .gitignore

Away from home: [remote access](remote-access.md). When something breaks:
[failure modes](failure-modes.md).
