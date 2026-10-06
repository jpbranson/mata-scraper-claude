# Settled from the data (2026-09-25, rechecked on 12 days 2026-10-05)

* [Bus capacity: 100% is 50 riders](bus-capacity.md) - The tracker's load % is a rider count out of 50 on every vehicle, trolley included, so riders on board = occupancy_pct / 2; rechecked on 12 days, where all 2.2 million readings are even.
* [Ghost threshold: keep the 30-poll rule](ghost-threshold.md) - Rows of a bus still for 30+ polls stay out of delay figures (they are mostly layovers and holds, 1,196 of 1,332 streaks on 12 days), and spatial queries also drop the dead-tracker rows that ghost_rows finds.
* [Late threshold: 5 minutes](late-threshold.md) - On time means at most 1 minute early and 5 minutes late, the usual window, because MATA's own window isn't published.
* [Speed unit: metres per second](speed-unit.md) - The tracker's speed_raw is whole metres per second, confirmed against MATA's official feed (equal in 97% of 33,269 moving same-report pairs on 11 days) and against the distance buses cover (ratio 1.03).

# Design

* [Host on a home machine](home-hosting.md) - The poller and map run on an always-on Windows machine at home rather than a cloud free tier, because the needs are tiny and a home box costs a few dollars a year in power.
