---
type: Component
title: Shared page code
description: transit.js and pages.css, shared by the strips and schematic pages (and helpers the map uses) - page links, route chips, the replay bottom bar, and placing a bus along its route's stop pattern.
resource: ../../transit.js
tags: [map, replay]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: transit-code
    resource: ../../transit.js
    title: transit.js
---

# What the two extra views share

[`strips.html`](route-strips.md) and [`schematic.html`](schematic-map.md)
are two more views of the same data as the [map](live-map.md), each with:

- page links;
- a row of route chips (bus count on each; one sideways-scrolling row on
  phones);
- the map's bottom bar: play/pause, scrubber, clock, speed, LIVE, day
  picker, replaying the same [`data/replay/<day>.jsonl`](../datasets/replay-frames.md)
  frames (`transit.js`, `timeline`).

Styles are in `pages.css`. `map.html` uses `transit.js`'s helpers instead of
its own copies. Delay colors are the map's tiers.

# Replay needs a saved timetable

A day can only be replayed here if the poller saved that day's timetable
([`data/schedule/<day>/`](../datasets/schedule-files.md)). MATA's [GTFS
feed](../feeds/gtfs-timetable.md) only covers today onward, so 2026-09-23
can't be.

# Placing a bus on its route (`locate`)

Both views place a bus along its route's stop pattern the same way:

1. the pattern for its headsign;
2. its next stop by name (nearest if the name repeats; other patterns if
   its branch's isn't the main one);
3. the fraction between that stop and the one before, by distance.

Replay frames from 2026-09-25 on carry `destination`, `next_stop_name` and
`equipment_no`, which this needs; older frames still load.
