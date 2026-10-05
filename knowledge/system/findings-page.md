---
type: Component
title: Findings page
description: findings_page/ builds "Memphis Buses, Measured", the findings as one page of charts (inline SVG, no libraries) published as a claude.ai artifact, from one copy of data/.
resource: ../../findings_page/
tags: [findings-page, analysis]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: findings-page-readme
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/findings_page/README.md
    title: findings_page/README.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
---

# What it is

"Memphis Buses, Measured": the [findings](../findings/) as one page of
charts (inline SVG, no libraries), published as a claude.ai artifact.
Every chart on it comes from one copy of `data/`, so the page describes a
single moment. The artifact is private until its owner shares it; its link
is deliberately kept out of this public repo.

# Building it

From the repo folder:

    .venv\Scripts\python findings_page\snapshot.py     # copy data/ into findings_page\snapshot\
    .venv\Scripts\python findings_page\page_data.py    # run the queries -> out\page_data.json, out\numbers.txt
    .venv\Scripts\python findings_page\build_page.py   # fill template.html -> out\findings.html

- `snapshot.py` copies what [`analysis.sql`](analysis-sql.md) reads
  (positions, the official feed archive, arrivals, schedules,
  `latest.json`, `stops.csv`); later runs copy only the files that changed.
  Never point the queries at the live `data/`, which the poller is writing.
- `page_data.py` creates `analysis.sql`'s views over the snapshot, then runs
  the page's own queries (the predictions join and headway lags computed
  once). `out/numbers.txt` lists the figures the page's text and the
  findings quote. Give it a folder to use a different snapshot.
- `template.html` is the page: text, styles and the code that draws each
  chart (with a hover readout and a table view). `build_page.py` puts the
  data into its `<script id="page-data">`.
- `snapshot/` and `out/` are not in git.
- Output is deterministic: ties are broken in every sort and pick, so two
  runs on one copy give byte-identical output.

# Current build

The published page was built from a copy taken 2026-09-25 at 20:21 (the
[findings snapshot](../findings/snapshot-2026-09-25.md)), two hours before
Friday's service ended. A rebuild from that copy differs from the published
page only in the 30th delay-map circle (a tie at 13.5 bus-min/day) and six
stops drawn 20–155 m from where they were (several stops share a name).

# Before publishing a rebuild

- **Days.** The page is laid out for two days, Thursday 2026-09-24 and
  Friday 2026-09-25 (`FEED_DAY` in `page_data.py`, `DAYS` in
  `template.html`): the trip barcode, riders and fleet charts draw one panel
  or line per day. A week of data needs those charts redesigned.
- **Words.** The text and captions in `template.html` quote the 20:21
  numbers by hand. Update them from `out/numbers.txt`, as for the findings.
- **Look.** Check the page at desktop and phone widths, in light and dark
  mode. Headless Chrome's `--screenshot` works; for phone width, load the
  page in a 375 px iframe, since Chrome won't make a window that narrow.
- **Publish** by republishing `out/findings.html` to the existing artifact,
  so its link stays the same.
