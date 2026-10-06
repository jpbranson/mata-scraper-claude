---
type: Dataset
title: Sample tracker payload (vehicules.json)
description: A saved /topo/vehicules response (41 buses, 20 lines) that the poller's offline --sample check parses; the project's regression check.
resource: ../../vehicules.json
tags: [tracker]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:05:00Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: poller-code
    resource: ../../cadavl_to_gtfs_rt.py
    title: cadavl_to_gtfs_rt.py docstring
  - id: sample-run
    resource: python cadavl_to_gtfs_rt.py --sample vehicules.json, run 2026-10-05 against the working routes.csv (topo 198282)
    title: The --sample check, 2026-10-05
---

# What it is

A real [`/topo/vehicules`](../feeds/tracker-vehicles.md) payload: 41 buses
on 20 lines, `{"vehicule": [...]}`, saved 2026-09-23 under topo 196203.
The [poller's](../system/poller.md) field mapping was verified against
it.[^poller-code] Committed to git.

# Examples

```
python cadavl_to_gtfs_rt.py --sample vehicules.json
```

parses it offline. There are no unit tests: this run is the regression
check; if the parser changes, run it. If the vendor changes the JSON shape,
save a fresh payload and run the same check against it.

Its line IDs (109136–109158) predate every renumbering since, so the check
now ends with `WARNING: 20 lines have no route_id ... rebuild routes.csv`.
That is expected and not a parser failure; the parse itself still reports
41 vehicles on 20 lines.[^sample-run]

[^poller-code]: cadavl_to_gtfs_rt.py docstring
[^sample-run]: The --sample check, 2026-10-05
