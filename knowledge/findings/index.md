# Data

* [Data snapshot, Fri 2026-09-25 20:21](snapshot-2026-09-25.md) - The copy of data/ every finding is computed from, with under two weekdays of tracker history and one day of MATA's official feed.

# The three questions

* [Which routes run behind](routes-behind.md) - Route 02 is the latest, 39% of its bus-polls 5+ min late; 36, 52, 08, 28 and 01 follow at 24–28%, and 69 and 16 are the most punctual.
* [Which days are bad](bad-days.md) - Not answerable yet; of the two days recorded, Friday had 19% of bus-polls 5+ min late and Thursday 17%.
* [How many people are riding right now](riders-now.md) - The query works; at 20:21 Friday, 25 buses were in service with 95 riders on board.

# Delay

* [Where delay builds up](where-delay-builds.md) - Delay builds on route 36's Getwell / American Way stretch, 50's Poplar corridor and 42's Cleveland corridor; most routes start late and recover, while 02, 28, 01, 13, 36 and 08 compound.
* [Which direction is worse](direction.md) - Leaving downtown; on 10 of the 17 bus routes that reach William Hudson, the trip away from it is 5+ min late at least 10 points more often.
* [When delay goes bad](time-of-day.md) - The afternoon; 26–32% of bus-polls are 5+ min late at 15:00–17:59 against 5–7% before 7 a.m., and early running peaks at night.
* [Early running](early-running.md) - 9% of bus-polls are 2+ min early, clustered at a few timepoints led by route 30 at American Way Transit Center (65%); from the start of a line buses almost never leave early.
* [Departures from the first stop](departures.md) - 60% of Friday's trips left their first stop on time; the median left 4.2 min late, 40% left 5+ min late, and 1% left early.

# Service delivered

* [Missed service](missed-service.md) - 13–16% of scheduled trips never ran (Thu 84 of 651, Fri 101 of 618), in every hour of the day, and MATA's own feed marked only 27 of Friday's 101 canceled.
* [Bunching and headways](headways.md) - Buses don't bunch and the ones that run keep their spacing; the gaps riders get are trips that never run.
* [What riders get at the stop](stop-waits.md) - Turning up 2 minutes early at a mid-route timepoint, the median wait is 4.9 min, but 23% of waits pass 15 min; the missed-trip routes are worst.
* [Fleet in service](fleet-in-service.md) - For most of the day 3–8.5 fewer buses are out than trips in progress, the same shortfall as the missed trips.
* [Layovers](layovers.md) - Buses sit a median 7 minutes at their first stop before leaving (the trolley 1 min), and short layovers don't predict late starts.
* [Speeds and slow stretches](speed.md) - Buses average 11.5–18.5 mph including stops on most routes; the slowest stretches are the trolley on Main and route 42 on Cleveland and Bellevue.

# Ridership and crowding

* [Peak loads](peak-loads.md) - Buses are rarely full; average loads are 1–11 riders, and every seat is taken (40+ riders) only on routes 50, 42 and 36, route 50 most.
* [Busiest vs latest](load-vs-delay.md) - Across routes, load and lateness are barely related (correlation 0.19), but within a route fuller buses are much later.
* [Riding per day](riders-per-day.md) - About 4,000 rider-hours and at least 7,900–8,100 boardings a day, peaking near 450 riders on board at 15:40, the same scale as MATA's reported ridership.
* [Where buses fill](boardings.md) - Buses fill at the downtown hubs, above all Second @ Jackson (823 riders on per day), the first stop out of William Hudson for seven routes.

# Data quality and MATA's feed

* [Ghost trackers and still buses](ghost-trackers.md) - A bus still for 30+ polls is almost always at a layover or a hold; dead trackers are short, don't move delay figures, and one bus (458) has nearly half of them.
* [Trip matching against MATA's trip IDs](trip-matching.md) - Where schedule.py names a trip, it is MATA's own trip 99.8% of the time; nearly all disagreements are the other direction around a turnaround.
* [Countdown accuracy](countdowns.md) - MATA's countdowns are good close up and optimistic far out; a rider timing their walk to a 20-minute countdown finds the bus already gone 4 times in 10.
