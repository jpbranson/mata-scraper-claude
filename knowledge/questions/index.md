# Core questions

* [Which routes constantly run behind?](routes-behind.md) - Core question 1, ranking routes by how often their buses run 5+ minutes late (answered on 1.8 days; week-long rerun and human sanity check pending).
* [Which days are especially bad?](bad-days.md) - Core question 2, comparing whole service days by how late buses ran (waiting for weeks of data; two weekdays can't say which days are bad).
* [How many people are riding right now?](riders-now.md) - Core question 3, counting buses in service and riders on board from the latest poll (answered).

# 1. Delay, deeper than "which routes" (the tracker history's row schema alone)

* [Where along the route does delay accumulate?](where-delay-accumulates.md) - Which stops on each route add delay, pinpointing the intersection or segment causing it (answered on 1.8 days).
* [Which direction is worse?](which-direction.md) - Whether a route's buses run later one way than the other (answered on 1.8 days).
* [When does it go bad?](when-it-goes-bad.md) - Delay by hour of day and weekday, separating rush-hour congestion from always (by hour answered; by weekday waits for weeks of data).
* [Does delay recover or compound?](recover-or-compound.md) - Whether a bus late at the start of a trip catches up or falls further behind, telling wrong schedules from stuck buses (answered on 1.8 days).
* [Where and how often do buses run early?](early-running.md) - Early running, which strands riders and is invisible in on-time percentages (answered on 1.8 days).

# 2. Ridership and crowding (the tracker history's row schema alone)

* [How full do buses get, by route and hour?](peak-load.md) - Peak load by route and hour, showing which routes get uncomfortably full and when (answered on 1.8 days).
* [Are the busiest routes the latest routes?](busiest-vs-latest.md) - Crowding against delay by route, a hint whether boarding time causes delay (answered on 1.8 days).
* [How does ridership vary by day of week, weather and events?](ridership-trend.md) - Daily rider-minutes as one trend line, where games and storms would show as spikes or dips (per-day totals answered; day of week, weather and events wait for weeks of data).
* [Where do buses fill and empty?](where-buses-fill.md) - A rough boarding and alighting map from changes in load between polls, without passenger-count data (answered on 1.8 days).

# 3. Service delivered vs promised (the tracker history's row schema alone)

* [Which buses' trackers stop reporting?](ghost-buses.md) - Ghost buses and GPS reliability, to settle before trusting anything else since bad trackers corrupt the delay stats (answered on 1.8 days; recheck after a week).
* [Do buses bunch?](bunching.md) - Whether buses of a route and direction run close together and leave long gaps behind them, the thing riders feel most (answered on 1.8 days).
* [What headway do riders actually get?](effective-headway.md) - Time between successive buses at a stop against the timetable's promised frequency (answered on 1.8 days).
* [How many buses are out, against what the schedule needs?](fleet-in-service.md) - Buses in service by hour against the trips the timetable has running, since dropped runs never show up as late (answered on 1.8 days).
* [Where and when are buses slow?](speed-profiles.md) - Speed by route segment and hour, showing where bus lanes or signal priority would help (answered on 1.8 days).

# 4. From the official GTFS-RT archive (data/official/, from 2026-09-25)

* [How much scheduled service never runs?](missed-service.md) - The share of scheduled trips that never ran, by route, hour and weekday, which belongs beside which routes run behind (by route and hour answered; by weekday waits for weeks of data).
* [Are the countdowns riders see honest?](countdowns.md) - How MATA's official arrival predictions compare with when the bus actually came, by how far ahead they were made (answered on one day of official data).
* [Does our trip matching hold up?](trip-matching.md) - How often the trip schedule.py infers for a bus is the trip MATA's official feed names (answered on one day of official data).
* [How long do buses sit at the terminal, and do short layovers make late starts?](layover-length.md) - Layover length at each terminal from MATA's official positions, and whether short layovers predict late departures (answered on one day of official data).

# 5. Needs more than the current design (extra collection or data)

* [What do detours do to delay and ridership?](detour-impact.md) - Delay and ridership on detoured vs normal days (waiting for weeks of the detour log, kept since 2026-09-25 20:12).
* [Should we compute schedule adherence ourselves?](self-computed-adherence.md) - Self-computed schedule adherence instead of the vendor's reported delay, a non-goal unless the vendor's values prove untrustworthy (not planned).
* [How long do riders actually wait at the stop?](stop-waits.md) - Stop-level wait times riders experience, missed trips included, against the timetable's promised gaps (answered on 1.8 days).
