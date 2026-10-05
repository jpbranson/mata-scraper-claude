---
type: Component
title: Live map
description: map.html, one static Leaflet page that shows every bus live (delay as color, load as size, heading, trails), stop and bus panels from the timetable and arrivals log, and a replay of any recorded day.
resource: ../../map.html
tags: [map, delay, load]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: map-code
    resource: ../../map.html
    title: map.html
---

# Overview

One static page, Leaflet from a CDN, no build step. It fetches:

- [`data/latest.json`](../datasets/latest-snapshot.md) every 10 s;
- the day's [`data/replay/`](../datasets/replay-frames.md) file once, in
  the background (the live view doesn't wait for it);
- [`network.geojson`](../datasets/network-geojson.md) once;
- a clicked stop's [schedule](../datasets/schedule-files.md) and
  [arrival](../datasets/arrivals-log.md) files.

Visual-first: the picture carries the information and text is confined to
a tooltip and a three-number strip. All text is Inter (Google Fonts) at
16 px (12 pt) or larger, including the route numbers inside the markers.

# Bus encodings

- **Fill = schedule adherence**, in tiers: early (blue), on time (grey, so
  problems stand out), 5+ / 10+ / 20+ min late (yellow → orange → red, the
  status palette). `"1h+"` capped values count as 20+ late or early,
  matching their direction.
- **Size = passenger load** (`occupancy_pct`), radius 13–19 px (16–22 px
  for three-character route numbers, so the digits fit).
- **Number = route**, a wedge on the rim = heading.
- **Shape = mode**: the trolley (route 100) is a diamond, buses are
  circles. The vendor types every vehicle "Bus", so the route is the only
  tell.
- **Trail** = the last ten positions, 30 s apart (live, from `latest.json`;
  replaying, from the frames), in the tier color, one segment per pair:
  bright, thick and solid where the bus just was, darker, thinner and
  fainter as it ages.
- **Still 5+ minutes** (`unchanged_polls` ≥ 30) = dashed hollow circle, no
  wedge, "no GPS movement for N min" in the tooltip. The code calls it a
  ghost, but it is usually a bus at layover; a dead tracker can't be told
  apart until the bus reappears somewhere else ([ghost
  threshold](../decisions/ghost-threshold.md)).
- Late buses are stacked on top of on-time ones.
- Hover for route, headsign, delay text, load, fleet number.

# Network and places

- The whole network as hairlines and every stop as a small hollow dot with
  a high-contrast ring (light on the dark basemap, larger at higher zoom,
  hover for its name): visible but subordinate to the buses.
- Squares mark the four transit centers (hollow; click for the combined
  times of all their bays) and the bus garage at 1370 Levee Rd and trolley
  barn at 547 N Main St (filled). Hard-coded in `PLACES`; the transit
  centers were located from where the timetable ends trips headed to them.
- The OSM basemap is muted with a CSS filter so the data reads on top;
  dark mode inverts it and follows the OS setting.

# Clicking a bus

Its route highlights, drawn over the other lines, while every other route
and bus dims (click the bus again or the map to clear), a ring marks it, and
a panel shows:

- its fleet number, delay and load;
- the last three stops it served in the past 90 minutes (scheduled vs
  actual, from the arrivals log);
- its next three on its trip (scheduled vs expected = scheduled + current
  delay, from the timetable; located by its next stop, or replaying, by its
  last arrival);
- a line chart of its delay over the last four hours from the replay frames
  (tier colors, 0/5/10/20 guides, "1h+" readings left as gaps, crosshair
  tooltip). A bus that ran more than one route in that window (MATA's
  timetable interlines 13 and 40 in one block, see [GTFS
  timetable](../feeds/gtfs-timetable.md)) gets a line at each switch, each
  stretch's route along the top (the current one always), and a break in
  the delay line there.
- a link to its route's [strip](route-strips.md).

# Clicking a stop

The routes that stop there highlight, and a panel lists for each route the
last three and next three scheduled trips: when each bus actually came (with
minutes late/early in the tier colors), "not seen" when no arrival was
recorded, and, live, "~time" when a bus on that trip is on its way
(scheduled + its current delay). Replaying, the panel shows the same as of
the viewed moment.

# Chrome

- Clock times are Memphis time wherever the viewer is.
- Top-right: buses in service, buses 5+ min late, riders on board (load % ×
  `CAPACITY = 50`, see [bus capacity](../decisions/bus-capacity.md)). A dot
  goes red when the snapshot is older than 90 s.
- Bottom-left legend; it links to the two other views, [route
  strips](route-strips.md) and the [schematic](schematic-map.md).
- Bottom bar: play/pause, a scrubber across the day's frames, the clock,
  replay speed (10× / 60× / 300× real time), LIVE, and a date picker for
  earlier days. Any moment of any recorded day can be revisited and played
  forward, with the same encodings and trails.

# Phones

- The panel takes the top of the screen and the map slides the clicked bus
  or stop into the clear area below it.
- At ≤ 720 px wide the scrubber gets its own row and the legend moves up
  out of its way.

# Serving

Served by `python -m http.server` from the repo root (the `mata-web` task,
see [running it](../operations/running-it.md)). Browsers block `fetch()` on
`file://` URLs, so a server is required, but that one command is all of it.
Away from home: [remote access](../operations/remote-access.md).
