---
type: Decision
title: "Late threshold: 5 minutes"
description: On time means at most 1 minute early and 5 minutes late, the usual window, because MATA's own window isn't published.
tags: [delay, on-time]
generated: { by: claude-code/claude-opus-5-5, at: 2026-10-05T02:18:04Z }
sources:
  - id: q-q1
    resource: ../../analysis.sql
    title: analysis.sql [Q1]
  - id: snapshot
    resource: ../findings/snapshot-2026-09-25.md
    title: Data snapshot, Fri 2026-09-25 20:21
  - id: departures
    resource: ../findings/departures.md
    title: Departures from the first stop
  - id: mata-otp-hub
    resource: https://data.memphistn.gov/datasets/mata-on-time-performance-1/about
    title: "Memphis Open Data Hub: MATA On Time Performance"
  - id: mata-otp-dictionary
    resource: "The data hub page's \"Data Dictionary\" PDF, hosted on memegis.maps.arcgis.com (not opened)"
    title: MATA On Time Performance data dictionary
  - id: mata-title-vi-2020
    resource: "MATA board packet, Dec 2020: Title VI program update"
    title: MATA Title VI program update, Dec 2020
  - id: mata-minutes-2020-10
    resource: "MATA board minutes, Oct 2020"
    title: MATA board minutes, Oct 2020
  - id: srtp-2012
    resource: "matatransit.com: MATA_SRTP_Plan_APPENDICES.pdf"
    title: MATA 2012 Short Range Transit Plan
  - id: design-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/2a1b9ab/DESIGN.md
    title: DESIGN.md at 2a1b9ab
    last_modified: 2026-09-28T01:29:38Z
  - id: findings-md
    resource: https://github.com/jpbranson/mata-scraper-claude/blob/513d93a/FINDINGS.md
    title: FINDINGS.md at 513d93a
    last_modified: 2026-09-26T02:35:29Z
---

# Decision

Kept at 5 minutes (2026-09-25). `[Q1]` uses the usual window, at most 1
minute early and 5 late, and reports `on_time` and `share_early` beside
`share_over_5_min`.[^q-q1] In the vendor's whole minutes (it never says
"1 min"), early is 2+ min early and late is 6+ min late. If MATA's
definition turns up, change the two numbers in `[Q1]` of
[analysis.sql](../system/analysis-sql.md).

# Evidence

- **MATA has a standard but doesn't publish the window.** Its Board adopted
  service standards including on-time performance in 2014, as its Title VI
  monitoring reports say (Dec 2020 board packet: 40 of 46 routes met the
  OTP standard;[^mata-title-vi-2020] a 72% OTP goal is mentioned in the Oct
  2020 minutes[^mata-minutes-2020-10]). The city's open-data hub has MATA's
  monthly fixed-route on-time share since 2015:[^mata-otp-hub] roughly
  45–50% in 2015, 55–70% in 2016, 54–65% in 2021–22. Neither, nor MATA's
  2012 Short Range Transit Plan,[^srtp-2012] states the minutes; the data
  hub's "Data Dictionary" PDF might,[^mata-otp-dictionary] but its host was
  refused in the browser.
- **The vendor's "on time" spans ±1 minute.** In 351k rows it never says
  "1 min"; the smallest non-zero values are ±2 min (see the
  [tracker's known limits](../feeds/tracker-vehicles.md)).
- **On that window:**[^snapshot]
  - 73% of bus-polls on time (18% late, 9% early);
  - 75% of departures from mid-route timepoints (17% late, 8% early);
  - 60% of departures from a trip's first stop, from MATA's feed (59% on
    the earlier copy first used).[^departures] That last is the number
    nearest MATA's own figures (54–65% in 2021–22), which suggests MATA
    measures departures.
- Early running is real, at some routes and timepoints much more than
  others: [early running](../findings/early-running.md).

**Needs a human:** MATA's on-time window. The data hub page links a "Data
Dictionary" PDF on memegis.maps.arcgis.com that the browser refused. If you
can open it (or ask MATA), and the window isn't "≤ 1 min early, ≤ 5 min
late", change the two numbers in `[Q1]`.

[^q-q1]: analysis.sql [Q1]
[^snapshot]: Data snapshot, Fri 2026-09-25 20:21
[^departures]: Departures from the first stop
[^mata-otp-hub]: Memphis Open Data Hub: MATA On Time Performance
[^mata-otp-dictionary]: MATA On Time Performance data dictionary
[^mata-title-vi-2020]: MATA Title VI program update, Dec 2020
[^mata-minutes-2020-10]: MATA board minutes, Oct 2020
[^srtp-2012]: MATA 2012 Short Range Transit Plan
