---
type: Playbook
title: Working with live data
description: Rules for agents and people working on the repo while the poller runs - analyse a copy of data/, use the repo's .venv Python, test poller changes in a scratch copy, and leave restarting the poller to the human.
tags: [ops, analysis]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-06T04:01:00Z }
sources:
  - id: flight-log-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FLIGHT_LOG.md
    title: FLIGHT_LOG.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
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
    title: findings_page/snapshot.py (DEST_DIR)
  - id: update-log
    resource: ../log.md
    title: Update log, 2026-10-05
  - id: schedule-code
    resource: ../../schedule.py
    title: schedule.py, Schedule.timetable (the "timetable for" log line)
---

# Analyse a copy, never the live files

The [poller](../system/poller.md) is always writing `data/`. Query a copy:
`findings_page/snapshot.py [DEST_DIR]` makes one, and
`findings_page/page_data.py [SNAPSHOT_DIR]` creates
[`analysis.sql`](../system/analysis-sql.md)'s views over it ([findings
page](../system/findings-page.md)).[^snapshot-py]

- A run into a folder that already holds a copy updates it (only the files
  that changed are copied), so give a new `DEST_DIR` for a fresh copy.
  Without one it writes into `findings_page/snapshot/`, the copy the
  published findings page was built from; that is how it was overwritten
  on 2026-10-05 and had to be rebuilt.[^update-log]
- Two copies are kept: `findings_page/snapshot/` (2026-09-25 20:21) and
  `findings_page/snapshot-2026-10-05/` (2026-10-05 22:37, the fullest).
  Both are gitignored (`findings_page/snapshot*/`).
- Listing or grepping the live `data/` read-only is fine; never write to it.

# Use the repo's Python

Run scripts with `.venv\Scripts\python`. The venv has `duckdb` (from
`requirements.txt`); the system Python does not.

# Test poller changes in a scratch copy

Before a poller change is deployed, test it against a scratch copy of the
loop with every output path redirected away from `data/`, plus the offline
`--sample` check ([sample payload](../datasets/sample-payload.md)). Poller
changes from 2026-09-25 (the fixed 10 s clock, stamped log lines, speed in
the feed, the detour log) were all tested this way, then deployed together.

# Restarting the poller is the human's job

- An agent's or sandboxed shell can't see or stop the scheduled tasks'
  python processes: `OpenProcess` on them returns access denied, and their
  command line reads empty. `ops\update.ps1` and `ops\backfill.ps1` need to
  stop that process, so they can't work from there.
- The poller is a live data-collection workload: stopping it costs data,
  and stopping the task alone leaves an orphaned python running old code.
- So never restart or kill `mata-poller` or `mata-web` from an agent.
  Deploy code changes by asking the human to run `.\ops\update.ps1` (and
  backfills `.\ops\backfill.ps1`) from their own PowerShell ([running
  it](running-it.md)).
- Verify a deploy read-only, from copies of the live files: the first
  time-stamped line in [`poller.log`](../datasets/poller-log.md) after a
  change shows when the new code first ran. Every start also logs
  "timetable for <day>: N stop times" on its first successful poll. The
  same line follows the day's first poll (04:00) and every crosswalk
  rebuild; anywhere else it marks a restart.[^schedule-code]

# Timestamps

Log only clock times read from a tool or from file timestamps, never
guessed ones (a guessed set in the 2026-09-25 run log was several hours off
and had to be corrected from file timestamps).

[^snapshot-py]: findings_page/snapshot.py (DEST_DIR)
[^update-log]: Update log, 2026-10-05
[^schedule-code]: schedule.py, Schedule.timetable (the "timetable for" log line)
