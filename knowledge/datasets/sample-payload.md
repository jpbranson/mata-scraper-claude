---
type: Dataset
title: Sample tracker payload (vehicules.json)
description: A saved /topo/vehicules response (41 buses, 20 lines) that the poller's offline --sample check parses; the project's regression check.
resource: ../../vehicules.json
tags: [tracker]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: poller-code
    resource: ../../cadavl_to_gtfs_rt.py
    title: cadavl_to_gtfs_rt.py docstring
---

# What it is

A real [`/topo/vehicules`](../feeds/tracker-vehicles.md) payload: 41 buses
on 20 lines, `{"vehicule": [...]}`. The [poller's](../system/poller.md) field
mapping was verified against it.[^poller-code] Committed to git.

# Examples

```
python cadavl_to_gtfs_rt.py --sample vehicules.json
```

parses it offline. There are no unit tests: this run is the regression
check; if the parser changes, run it. If the vendor changes the JSON shape,
save a fresh payload and run the same check against it.

[^poller-code]: cadavl_to_gtfs_rt.py docstring
