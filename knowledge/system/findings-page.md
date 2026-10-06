---
type: Component
title: Findings page
description: findings_page/ builds "Memphis Buses, Measured", the findings as one page of charts (inline SVG, no libraries) published as a claude.ai artifact, from one copy of data/ made by snapshot.py (12 days since version 4).
resource: ../../findings_page/
tags: [findings-page, analysis]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T05:09:00Z }
sources:
  - id: findings-page-readme
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/findings_page/README.md
    title: findings_page/README.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: snapshot-py
    resource: ../../findings_page/snapshot.py
    title: findings_page/snapshot.py (the folders it copies, DEST_DIR)
  - id: page-data-py
    resource: ../../findings_page/page_data.py
    title: findings_page/page_data.py (SNAPSHOT_DIR, FEED_DAY)
  - id: relief-data-py
    resource: ../../findings_page/relief_data.py
    title: findings_page/relief_data.py
  - id: build-page-py
    resource: ../../findings_page/build_page.py
    title: findings_page/build_page.py
  - id: template-html
    resource: ../../findings_page/template.html
    title: findings_page/template.html (section "Changing drivers", DAYS, footer)
  - id: gitignore
    resource: ../../.gitignore
    title: .gitignore
  - id: rider-messages-commit
    resource: https://github.com/jpbranson/mata-scraper-claude/commit/2a1b9ab
    title: "2a1b9ab analysis.sql: rider_messages view (reads data/detours/)"
  - id: update-log
    resource: ../log.md
    title: Update log, 2026-10-05
---

# What it is

"Memphis Buses, Measured": the [findings](../findings/) as one page of
charts (inline SVG, no libraries), published as a claude.ai artifact. Every
chart comes from one copy of `data/`, so the page describes a single span
of days. The artifact is private until its owner shares it; its link is
deliberately kept out of this public repo.

# Building it

From the repo folder:

    .venv\Scripts\python findings_page\snapshot.py [DEST_DIR]        # copy data/ (default: findings_page\snapshot\)
    .venv\Scripts\python findings_page\page_data.py [SNAPSHOT_DIR]   # the page's queries -> out\page_data.json, out\numbers.txt
    .venv\Scripts\python findings_page\relief_data.py SNAPSHOT_DIR   # "Changing drivers" -> out\relief.json
    .venv\Scripts\python findings_page\build_page.py                 # fill template.html -> out\findings.html

- `snapshot.py` copies what [`analysis.sql`](analysis-sql.md) reads: the
  `positions`, `official`, `arrivals`, `schedule` and `detours` folders,
  `latest.json`, and the repo's current `stops.csv`. It skips `.tmp`
  files. A later run into the same folder copies only the files whose size
  changed or whose live copy is newer, so it brings an old copy up to date:
  give a new `DEST_DIR` to keep an older copy as it was.[^snapshot-py] It
  copies neither `data/replay/` nor `data/gtfs.zip`; `analysis.sql` reads
  neither. Never point the queries at the live `data/`, which the poller is
  writing.
- The copy needs all five folders. `analysis.sql`'s views are bound when
  they are created, so a missing folder stops the script with "No files
  found that match the pattern". `data/detours/` has been read since
  `2a1b9ab` (the `rider_messages` view, 2026-09-27)[^rider-messages-commit]
  and copied since 2026-10-05.
- `page_data.py` creates `analysis.sql`'s views over the copy
  (`findings_page/snapshot/` unless given another folder), then runs the
  page's own queries (the predictions join and headway lags computed once).
  It is laid out for weeks of data: service days are days with 6+ hours
  recorded, and the hour, route-by-hour, riders, fleet and missed-by-hour
  figures are split into weekdays, Saturdays and Sundays. Its queries follow
  `analysis.sql`'s 2026-10-05 definitions (lateness gained, boardings per
  weekday, ad-hoc trips left out of trip matching, layovers from when the
  bus stopped). If the copy holds `data/gtfs.zip`, slow stretches are
  measured along the route, from the timetable's `shape_dist_traveled`.
  `out/numbers.txt` lists the figures the page's text quotes. On the
  12-day copy it takes about 13 minutes.[^page-data-py]
- `relief_data.py` runs `[RELIEF]` over a copy that covers weeks, and times
  every southbound route 42 pass within 450 m of the garage the same way,
  for the "Changing drivers" chart. It stops on an assertion if `[RELIEF]`
  finds a driver change on any trip but route 42 to Airways Transit.
  `window` in `out/relief.json` is the copy's first and last
  poll.[^relief-data-py]
- `template.html` is the page: text, styles and the code that draws each
  chart (with a hover readout and a table view). `build_page.py` needs both
  `out/page_data.json` and `out/relief.json`; it adds the second to the
  first as `relief` and puts the result into the template's
  `<script id="page-data">`.[^build-page-py]
- `snapshot*/` and `out/` are not in git.[^gitignore]
- Output is deterministic: ties are broken in every sort and pick, so two
  runs on one copy give byte-identical output.

# Current build

Version 4, republished to the same artifact on 2026-10-06, reads one copy:
`findings_page/snapshot-2026-10-05/`, 12 service days (the
[snapshot](../findings/snapshot-2026-10-05.md)), the same copy the findings
are computed from.[^template-html] Against the earlier two-day page it
replaces the trip barcode with a route-by-day grid of trips that never ran,
adds "Which days are bad" (each day's late share and missed share), draws
lateness by hour, riders on board and the fleet for weekdays apart from
Saturdays and Sundays, and adds a weekday late column to the route table.
Versions 1 to 3 (2026-09-25 to 10-05) showed the 2026-09-25 20:21 copy;
version 2 added "Changing drivers" and version 3 rebuilt it from the
12-day copy.[^update-log]

Two copies of `data/` are kept on the home machine, both
gitignored:[^update-log]

- **`findings_page/snapshot-2026-10-05/`**: the full copy taken 2026-10-05
  at 22:37, after Monday's service ended (positions to 22:33), plus that
  day's `data/gtfs.zip`, copied by hand. The page and the findings read it.
- **`findings_page/snapshot/`**: the 2026-09-25 20:21 copy versions 1 to 3
  were built from. It was overwritten by accident on 2026-10-05 and rebuilt
  from a later copy by keeping every record up to the original's last poll
  (`observed_at` 1790385690, 20:21:30 CDT; arrivals with `t` before it),
  with `stops.csv` from git `HEAD` and `latest.json` rebuilt from that
  poll's 27 rows, without trails; `page_data.py` as it was then reproduced
  that version's `out/page_data.json` and `out/numbers.txt` byte for byte.
  `snapshot.py` without a `DEST_DIR` writes into this folder, which is how
  it was overwritten.

# Before publishing a rebuild

- **Copy.** Run `snapshot.py` with a new `DEST_DIR` (such as
  `findings_page\snapshot-<date>`), so the copy the published page was
  built from stays as it was.
- **One copy.** Run `page_data.py` and `relief_data.py` on the same copy.
- **Days.** The charts take whatever days the copy holds; the day grid and
  the day-by-day bars grow a column per day, and stay legible to about
  four weeks at desktop width.
- **Words.** The text and captions in `template.html` quote the numbers by
  hand, from `out/numbers.txt`, the findings and the
  [driver changes](../findings/driver-changes.md) finding; the header's
  dateline and the footer name the copy. Update them as for the
  findings.
- **Look.** Check the page at desktop and phone widths, in light and dark
  mode. Headless Chrome's `--screenshot` works; for phone width, load the
  page in a 375 px iframe, since Chrome won't make a window that narrow.
- **Publish** by republishing `out/findings.html` to the existing artifact,
  so its link stays the same.

[^snapshot-py]: findings_page/snapshot.py (the folders it copies, DEST_DIR)
[^rider-messages-commit]: 2a1b9ab analysis.sql: rider_messages view (reads data/detours/)
[^page-data-py]: findings_page/page_data.py (SNAPSHOT_DIR, service_days, DAY_TYPE, stop_dist)
[^relief-data-py]: findings_page/relief_data.py
[^build-page-py]: findings_page/build_page.py
[^gitignore]: .gitignore
[^template-html]: findings_page/template.html (DAYTYPES, fig-missed, fig-days, footer)
[^update-log]: Update log, 2026-10-05
