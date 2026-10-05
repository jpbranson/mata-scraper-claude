---
okf_version: "0.2"
---

# Start here

* [MATA bus feed](project.md) - Continuously record where every MATA (Memphis) bus is, show it on a live map, and keep enough history to answer which routes run behind, which days are bad, and how many people are riding.
* [Next steps](work/) - The work plan in progress and what still needs a human.
* [Update log](log.md) - What changed in the project and its knowledge, newest first.

# What we know

* [Questions](questions/) - The three core questions and the backlog beyond them, each with its answer status.
* [Findings](findings/) - What the recorded data says, one concept per question, all from the 2026-09-25 20:21 snapshot (stale since 2026-10-01).
* [Decisions](decisions/) - Open questions settled from the data (capacity, ghost and late thresholds, speed unit) and how the system is hosted.

# Where the data comes from

* [Feeds](feeds/) - The vendor's tracker endpoints and MATA's GTFS and GTFS-Realtime feeds: what each has, lacks and gets wrong.
* [Datasets](datasets/) - What the poller records under data/ and the crosswalk files committed to git, with schemas, sizes and limits.

# How it works

* [System](system/) - The poller and its modules, the crosswalk builder, the three pages, analysis.sql and the findings page.
* [Operations](operations/) - Installing, updating, backfilling and reaching the home machine, what to do when something fails, and rules for working beside the live poller.
