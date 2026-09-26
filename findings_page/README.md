# Findings page

"Memphis Buses, Measured": FINDINGS.md as one page of charts (inline SVG,
no libraries), published as a claude.ai artifact. Every chart on it comes
from one copy of `data/`, so the page describes a single moment.

Build it from the repo folder:

    .venv\Scripts\python findings_page\snapshot.py     # copy data/ into findings_page\snapshot\
    .venv\Scripts\python findings_page\page_data.py    # run the queries -> out\page_data.json, out\numbers.txt
    .venv\Scripts\python findings_page\build_page.py   # fill template.html -> out\findings.html

- `snapshot.py` copies what `analysis.sql` reads (positions, the official
  feed archive, arrivals, schedules, `latest.json`, `stops.csv`); later runs
  copy only the files that changed. Never point the queries at the live
  `data/`, which the poller is writing.
- `page_data.py` creates `analysis.sql`'s views over the snapshot, then runs
  the page's own queries. `out/numbers.txt` lists the figures the page's
  text and FINDINGS.md quote. Give it a folder to use a different snapshot.
- `template.html` is the page: text, styles and the code that draws each
  chart (with a hover readout and a table view). `build_page.py` puts the
  data into its `<script id="page-data">`.
- `snapshot/` and `out/` are not in git.

The published page was built from a copy taken 2026-09-25 at 20:21. Before
publishing a rebuild:

- **Days.** The page is laid out for two days, Thursday 2026-09-24 and
  Friday 2026-09-25 (`FEED_DAY` in `page_data.py`, `DAYS` in
  `template.html`): the trip barcode, riders and fleet charts draw one panel
  or line per day. A week of data needs those charts redesigned.
- **Words.** The text and captions in `template.html` quote the 20:21
  numbers by hand. Update them from `out/numbers.txt`, as for FINDINGS.md.
- **Look.** Check the page at desktop and phone widths, in light and dark
  mode. Headless Chrome's `--screenshot` works; for phone width, load the
  page in a 375 px iframe, since Chrome won't make a window that narrow.
- **Publish** by republishing `out/findings.html` to the existing artifact,
  so its link stays the same.
