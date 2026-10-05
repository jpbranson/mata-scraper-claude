---
type: API Endpoint
title: Tracker detours (/topo/refresh)
description: The network's current detours (bypassed segments, replacement geometry, affected stops), changing over days; saved hourly to the detour log.
resource: https://swiv.mata.cadavl.com/SWIV/MATA/proxy/restWS/topo/refresh
tags: [tracker, detours]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: detours-code
    resource: ../../cadavl_detours.py
    title: cadavl_detours.py docstring
---

# What it is

Despite the name, `refresh` is not a polling-interval endpoint. It is the
current network-deviation state: which line segments are being bypassed,
the replacement geometry, and which stops are affected. ~150–385 KB; the
first sample was 385 KB covering 11 lines, 105 stops and 14 detour
paths.[^detours-code] It changes on the scale of days, not seconds: poll it
hourly at most.

# Used for

The [detour logger](../system/detour-logger.md) fetches it once an hour,
with the [rider messages](tracker-messages.md), and saves it to the
[detour log](../datasets/detour-log.md) when it changed. Not drawn on the
map.

[^detours-code]: cadavl_detours.py docstring
