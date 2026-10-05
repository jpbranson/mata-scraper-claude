---
type: Runbook
title: Running it
description: Install, update and backfill the always-on Windows home machine that runs the poller and the map server as two scheduled tasks.
resource: ../../ops/setup.ps1
tags: [ops]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
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
---

# The machine

An always-on Windows machine at home ([why](../decisions/home-hosting.md)).
Everything runs natively (Python, `http.server`, DuckDB); only "keep it
running" is Windows-specific, and Task Scheduler does that.

Needs are tiny: one 12 KB request every 10 s (plus the official feed's two
of ~2 KB, ~120 KB every 5 minutes, and the detour check's ~150 KB an hour),
~40–55 MB/day of disk (history, replay frames, official archive; the detour
log adds a few KB).

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

# Analysis on Windows

Download the DuckDB CLI (`duckdb.exe`, a single file) and run
`Get-Content analysis.sql | .\duckdb.exe` from the repo folder (see
[analysis SQL](../system/analysis-sql.md)), on a copy of the data.

# What git tracks

Code, the crosswalk outputs ([`routes.csv`](../datasets/routes-csv.md),
[`stops.csv`](../datasets/stops-csv.md),
[`network.geojson`](../datasets/network-geojson.md)),
[`schematic.json`](../datasets/schematic-json.md),
[`vehicules.json`](../datasets/sample-payload.md) (the sample payload for
`--sample`), and this knowledge bundle. `data/`, the raw `topo.json`,
`findings_page/snapshot/` and `findings_page/out/` are ignored.

Away from home: [remote access](remote-access.md). When something breaks:
[failure modes](failure-modes.md).
