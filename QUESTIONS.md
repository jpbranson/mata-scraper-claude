# Analysis questions

Backlog of questions the data could answer, beyond the three in `DESIGN.md`
(which routes run behind, which days are bad, how many people are riding).
Groups 1–3 need nothing beyond the row schema in `DESIGN.md`. Group 4 needs
extra collection or data.

Suggested order: ghost detection first (it validates everything else), then
bunching / headways and where delay accumulates.

## 1. Delay, deeper than "which routes"

- **Where along the route does delay accumulate?** Delay by `next_stop_name`
  per route — pinpoints the intersection or segment causing it.
- **Which direction is worse?** Group by `destination` (headsign) within a
  route. Inbound mornings and outbound evenings often differ a lot.
- **When does it go bad?** Delay by hour of day × weekday. Separates rush-hour
  congestion from "always".
- **Does delay recover or compound?** Follow one bus through a run: does a bus
  5 min late at the start end 5 min late or 15? Wrong schedules vs buses
  getting stuck.
- **Early running.** Negative `delay_seconds`. Leaving early is worse for
  riders than a few minutes late and is invisible in on-time percentages.

## 2. Ridership and crowding

- **Peak load by route and hour.** Max / percentile of `occupancy_pct`, not
  the sum — which routes get uncomfortably full, and when.
- **Are the busiest routes the latest routes?** Crowding vs delay by route. If
  they coincide, dwell time (boarding) may be the delay cause.
- **Ridership by day of week / weather / events.** Daily rider-minutes as one
  trend line; games and storms show as spikes or dips.
- **Where do buses fill and empty?** Change in `occupancy_pct` between
  consecutive polls, grouped by `next_stop_name` — a rough boarding/alighting
  map without passenger-count data.

## 3. Service delivered vs promised

- **Bus bunching.** Two buses on the same route and direction within a minute
  of each other means a long gap behind them. Detectable from positions
  alone; the thing riders feel most.
- **Effective headway.** Time between successive buses passing the same
  `next_stop_name` in the same direction — actual frequency vs the
  timetable's promised frequency.
- **Fleet in service by hour.** Buses per route over the day vs what the
  schedule implies. Dropped runs never show up as "late".
- **Ghost buses / GPS reliability.** Share of polls with high
  `unchanged_polls`, by `equipment_no`. Chronically bad trackers corrupt the
  delay stats, so settle this before trusting anything else.
- **Speed profiles.** Average `speed_raw` by route segment and hour (relative
  comparisons work without knowing the unit). Slow segments on a map = where
  bus lanes or signal priority would help.

## 4. Needs more than the current design

- **Detour impact.** Delay and ridership on detoured vs normal days — needs
  `cadavl_detours.py` running hourly so there's a detour log. Cheap to add.
- **Self-computed schedule adherence** (instead of the vendor's number) —
  needs static GTFS and trip matching. A non-goal in `DESIGN.md`; only worth
  it if the vendor's delay values prove untrustworthy.
- **Stop-level wait times riders actually experience** — needs the headway
  analysis above plus stop coordinates from `stops.csv`, matched by name (the
  payload gives display names, not stop IDs).
