# Settled from the data (2026-09-25)

* [Bus capacity: 100% is 50 riders](bus-capacity.md) - The tracker's load % is a rider count out of 50 on every vehicle, trolley included, so riders on board = occupancy_pct / 2.
* [Ghost threshold: keep the 30-poll rule](ghost-threshold.md) - Rows of a bus still for 30+ polls stay out of delay figures (they are mostly layovers), and spatial queries also drop the dead-tracker rows that ghost_rows finds.
* [Late threshold: 5 minutes](late-threshold.md) - On time means at most 1 minute early and 5 minutes late, the usual window, because MATA's own window isn't published.
* [Speed unit: metres per second](speed-unit.md) - The tracker's speed_raw is whole metres per second, confirmed against MATA's official feed and against the distance buses cover.

# Design

* [Host on a home machine](home-hosting.md) - The poller and map run on an always-on Windows machine at home rather than a cloud free tier, because the needs are tiny and a home box costs a few dollars a year in power.
