# Data

* [Data snapshot, Mon 2026-10-05 22:37](snapshot-2026-10-05.md) - The copy of data/ the findings are computed from since 2026-10-05, with 12 service days of tracker history (8 weekdays, 2 Saturdays, 2 Sundays) and 11 days of MATA's official feed.
* [Data snapshot, Fri 2026-09-25 20:21](snapshot-2026-09-25.md) - The copy of data/ the findings and the findings page were computed from until 2026-10-05, with under two weekdays of tracker history and one day of MATA's official feed.

# The three questions

* [Which routes run behind](routes-behind.md) - Routes 36 and 02 are the latest, 26% of their bus-polls 5+ min late over 12 days (weekdays alone, 02 30%, 34 and 36 27%); 36 is late every weekday, and the trolley (7%) and 04 (8%) are the most punctual.
* [Which days are bad](bad-days.md) - Sundays are the good days (8% of bus-polls 5+ min late); weekdays (17–21%) and Saturdays (16–19%) are much alike, and the worst day, Wed 09-30 at 21%, was a few routes' bad day; one weekday against another needs more weeks.
* [How many people are riding right now](riders-now.md) - The query works, now after service too (0 buses, 0 riders at 22:37 Monday); at 20:21 on Fri 2026-09-25, 25 buses carried 95 riders, and at 20:21 on the 8 weekdays 21–29 buses carried 82–152.

# Delay

* [Where delay builds up](where-delay-builds.md) - Lateness builds most where route 36 leaves American Way Transit Center (46 bus-min a day at American Way @ Getwell, 21 at Getwell @ Allenbrooke), then on 42's Cleveland corridor (25 at Cleveland @ Larkin), 01's Tillman at Johnson and 50's Poplar; most routes start trips 2–4 min late and recover, while on weekdays 13, 01, 08, 28, 02 and 36 lose 0.7–1.5 min a trip.
* [Which direction is worse](direction.md) - Leaving downtown; on 11 of the 17 bus routes that reach William Hudson, the trip away from it is 5+ min late at least 10 points more often (02 40% against 12%), on weekdays from 6:00 to 18:00, and only 28 and 40 lean the other way.
* [When delay goes bad](time-of-day.md) - The weekday afternoon; 27–28% of weekday bus-polls are 5+ min late at 15:00–17:59, the worst stretch on each weekday, against 9–12% before 7 a.m.; Saturdays have no rush (13–23% all day), Sundays stay at 5–14%, and early running peaks late in the evening.
* [Early running](early-running.md) - 9% of bus-polls are 2+ min early, clustered at a few timepoints led by the trolley at Main @ Madison (52%) and route 30 at American Way Transit Center (51%); Sundays run early more (11%), and from the start of a line buses almost never leave early (1%).
* [Departures from the first stop](departures.md) - 60% of 5,011 trips over 11 days left their first stop on time (58% on weekdays, 75% on Sundays); the median left 3.9 min late, 39% left 5+ min late, and 1% left early; routes 19 and 34 are worst (64–65% 5+ min late).
* [Driver changes](driver-changes.md) - No feed names the driver; long weekday blocks keep one bus all day, so drivers change on the street, and it only shows on route 42 at the garage, where 5 trips a weekday sit ~9 min instead of ~2 and leave 5 min late.

# Service delivered

* [Missed service](missed-service.md) - 9% of scheduled trips never ran over 12 days (603 of 6,702; weekdays 9.8%, Saturdays 5.6%, Sundays 7.3%; worst day 16%), mostly a bus missing for hours, and MATA's feed marked only 126 of 519 canceled.
* [Bunching and headways](headways.md) - Buses don't bunch (231 of 306,716 pairs at a stop in 12 days, nearly all in seven episodes) and the ones that run keep their spacing; the gaps riders get are trips that never run.
* [What riders get at the stop](stop-waits.md) - Turning up 2 minutes early at a mid-route timepoint, the median wait over 12 days is 4.3 min, but 16% of waits pass 15 min and 3% of calls get no bus for the rest of the day; the hourly, often-early trolley is worst, then the missed-trip routes.
* [Fleet in service](fleet-in-service.md) - On weekdays 2.3–6.4 fewer buses are out than trips in progress in every hour from 04:30 to 21:30 (about 11% short, worst 13:30–15:30), the same shortfall as the missed trips; weekends run up to 8.5 short.
* [Layovers](layovers.md) - Buses lay over a median 13 min before a trip and reach its first stop 9 min before it's due (the trolley 1 min); 16% get there after the trip is due and 39% of those start 5+ min late, against 20–22% after short or long layovers.
* [Speeds and slow stretches](speed.md) - Buses average 11–19 mph including stops on most routes over 12 days (01 slowest, 28 25 mph, trolley 4.6), with peak and midday within about 1 mph; the slowest stretches are the trolley on Main, route 42 on Cleveland and Bellevue, and buses leaving American Way Transit Center.

# Ridership and crowding

* [Peak loads](peak-loads.md) - Buses are rarely full; routes average 1.7–9.9 riders on board, and every seat is taken (40+ riders) on 0.9% of route 50's polls, 0.2% of 42's and under 0.1% anywhere else, never on a Sunday.
* [Busiest vs latest](load-vs-delay.md) - Across routes, load and lateness are barely related (correlation 0.15), but within a route fuller buses are much later, 31% against 18% 5+ min late at the same route and hour on weekdays; route 42 is the exception.
* [Riding per day](riders-per-day.md) - A weekday carries 3,800–4,500 rider-hours and at least 7,900–9,400 boardings, with 370–456 riders on board at the peak; a Saturday about 60% of that and a Sunday about a third, ~7,300 boardings a day over a week, the same scale as MATA's reported ridership.
* [Where buses fill](boardings.md) - Buses fill at William Hudson Transit Center, ~1,770 riders on a weekday (a fifth of all boardings), which [BOARDINGS] credits to the first stop out (Second @ Jackson 828 a weekday); away from downtown the busiest stops take 110–140 a weekday.

# Data quality and MATA's feed

* [Ghost trackers and still buses](ghost-trackers.md) - A bus still for 30+ polls is nearly always at a layover or a hold (1,196 of 1,332 streaks); dead trackers are short, don't move delay figures, and bus 458 has a quarter of the ghost rows, while a third come at the start of service and some from fleet-wide freezes.
* [Trip matching against MATA's trip IDs](trip-matching.md) - Over 11 days, where schedule.py names a trip it is MATA's own trip 99.7% of the time (99.8% leaving out ad-hoc trips MATA's dispatch creates); most other disagreements are the other direction around a turnaround.
* [Countdown accuracy](countdowns.md) - Over 11 days and 2.7 million predictions, MATA's countdowns are good close up (87% within 2 min) and lean late far out; a rider timing their walk to a 20-minute countdown finds the bus already gone 4 times in 10, every day.
