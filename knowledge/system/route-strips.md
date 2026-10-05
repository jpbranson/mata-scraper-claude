---
type: Component
title: Route strips
description: strips.html, one vertical line diagram per stop pattern of a route, with live or replayed buses, their delay, the gap to the bus ahead, and load as a band along the line.
resource: ../../strips.html
tags: [map, headway, load]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: strips-code
    resource: ../../strips.html
    title: strips.html
---

# Layout

`strips.html#36`: one vertical strip per [stop
pattern](../datasets/schedule-files.md) of the chosen route, stops top to
bottom in travel order, evenly spaced and all named (timepoints bold with a
big dot), like the line diagram over a subway door. Branches with the same
headsign say "via" their first stop the others lack.

Reads [`data/latest.json`](../datasets/latest-snapshot.md) every 10 s and the
route's schedule file; the chips, bottom bar and bus placement are the
[shared page code](transit-js.md).

# Buses

- Buses sit on the line with a chevron for direction.
- Beside each: its delay, fleet number and the gap to the bus ahead in
  scheduled minutes, so bunching and holes read at a glance.
- Labels shift down rather than overlap.
- Delay colors are the [map's](live-map.md) tiers.

# Load

Load is the schematic's band: the line between the timepoints before and
after a bus, widened by up to 24 px at 100% full (so it stays short of the
stop names), drawn under the line and stops. Hover a bus for the exact %.
