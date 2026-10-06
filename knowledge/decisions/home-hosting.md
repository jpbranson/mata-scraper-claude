---
type: Decision
title: Host on a home machine
description: The poller and map run on an always-on Windows machine at home rather than a cloud free tier, because the needs are tiny and a home box costs a few dollars a year in power.
tags: [ops]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:19:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: measured
    resource: "du over data/ on the home machine, 2026-10-05"
    title: Disk use measured, 2026-10-05
---

# Decision

An always-on Windows machine at home, kept running by Task Scheduler
([running it](../operations/running-it.md)), reached from away over
Tailscale ([remote access](../operations/remote-access.md)).

# Alternatives considered

| Option | Cost | Catch |
|---|---|---|
| Google Cloud e2-micro | Free, but its external IP is ~$3.65/month | |
| Oracle Cloud free tier | $0 | Signup and idle-reclamation caveats |
| Home machine (chosen) | A few dollars a year in power | Must not sleep; Windows-specific scheduling |

# Why it's enough

Needs are tiny: one 12 KB request every 10 s (plus the official feed's two
of ~2 KB, ~120 KB every 5 minutes, and the detour check's ~150 KB an hour)
and about 43 MB of disk a weekday, 34 MB a Saturday and 21 MB a Sunday
(on a weekday: positions ~17.5 MB, the official archive ~14.5 MB, replay
frames ~7.5 MB, arrivals ~4 MB, timetables ~1 MB), so about 14 GB a
year.[^measured] Everything runs natively (Python, `http.server`,
DuckDB); only "keep it running" is Windows-specific.

[^measured]: Disk use measured, 2026-10-05
