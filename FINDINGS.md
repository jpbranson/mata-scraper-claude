# Findings

What the recorded data says so far, question by question. The queries are
in `analysis.sql` (tags in brackets, e.g. `[Q1]`); rerun them as days
accumulate, since every figure here is from a short window.

**Data behind this version:** tracker history Thu 2026-09-24 04:00–22:35
(a full service day) and Fri 2026-09-25 04:00–20:21 (service runs to about
22:35, so Friday is two hours short), plus 55 minutes on Wed evening:
351,576 bus-polls from 61 vehicles. Official GTFS-RT archive Fri
05:45–20:21 (1,640 snapshots). That is **under two weekdays and no
weekend**, so anything by day of week, weather or event is still
unanswerable, and route rankings can move.

## The three questions (DESIGN.md)

Ran `analysis.sql` on a copy of the data taken 2026-09-25 at 20:21. The
`good` filter keeps 97.9% of rows (1.2% are "1h+" caps, 0.9% still for 30+
polls).

**1. Which routes constantly run behind?** Share of bus-polls 5+ min late:

| Worst | 5+ min late | median | | Best | 5+ min late |
|---|---|---|---|---|---|
| 02 | 39% | 3 min late | | 69 | 2.5% |
| 36 | 28% | 2 min late | | 16 | 4% |
| 52 | 27% | on time | | 12, 04 | 6% |
| 08 | 26% | 2 min late | | 40, 100 (trolley), 07 | 7–8% |
| 28 | 26% | 2 min late | | 42 | 10% |

Route 02 stands out; the next tier (36, 52, 08, 28, 01) is 24–28%, then
19, 50, 39 and 37 at 21%.

**2. Which days are especially bad?** Fri 19% of polls 5+ min late (16.4 h
covered, to 20:21), Thu 17%. Two days can't say which days are bad. The
query now also shows `hours` covered, so partial days (Wed: 0.9 h) are
obvious.

**3. How many people are riding right now?** Works: at 20:21 Friday, 25
buses and 95 riders on board (load % ÷ 2, see Bus capacity below).

**Needs you:** sanity-check the route ranking against your own experience
of these routes (DESIGN step 5), and rerun after a full week (~Oct 1).

## Open questions (DESIGN.md)

### Ghost threshold `[GPS]` — settled

A still streak is a run of polls where a bus's coordinates don't change. How
it *ends* says what it was: if the bus then drives off from the same spot
(first move ≤ 200 m) it was really there; if it reappears 200 m+ away within
two minutes, its tracker had stopped and the bus was moving all along.

| Still for | Streaks | Dead tracker | Drove off | At a route end |
|---|---|---|---|---|
| 1–1.5 min (6–9 polls) | 1,241 | 69 | 1,160 | 37% |
| 2–3.5 min (10–19) | 466 | 53 | 406 | 38% |
| 3.5–5.5 min (20–29) | 170 | 24 | 142 | 55% |
| 5.5+ min (30+) | 191 | 8 | 177 | 69% |

(The rest left the feed, or were still under way when the copy was taken.)

- The 30-poll rule mostly catches **layovers** (130 of 191 streaks at a
  route's end) and **holds** (47 mid-route, typically a bus sitting 5–10
  min while its delay climbs from ~0 to +5…+10, e.g. route 50 on Poplar,
  route 57 on Park). Only 8 were dead trackers.
- Dead trackers are mostly **short** (1–5 min) and slip past it. Over those
  stretches the official feed also freezes: same position, report age
  climbing to ~2 min (median), versus ~10 s for parked buses.
- **It doesn't matter for delay.** The vendor freezes delay with position
  (median delay 0 at a ghost's start, end and after the jump), and every
  route's 5+ min late share is within 1.4 points either way. Route 02 is
  late on all its buses (21715: 22%, 450: 31%, 21808: 37%, 458: 44%,
  22607: 50%), not because of a bad tracker.
- **One bad tracker:** bus 458 (routes 19, 02) has 1,002 ghost rows, 15%
  of its polls and nearly half of all 2,148 ghost rows. Next worst: 21501
  (5%), 21809 (1.5%).

Decision: `good` keeps `unchanged_polls < 30`; spatial queries drop
`ghost_rows` (new view). The map's dashed "no GPS movement" marker is
usually a layover, as DESIGN.md now says.

### Speed unit — settled: metres per second

- **Same report, both feeds:** matching each official vehicle position to
  the tracker row for the same bus (fleet number) at the identical
  coordinates gave 5,915 pairs; for the 2,751 moving ones, the official
  speed (m/s by the GTFS-RT spec) *equals* `speed_raw` 97% of the time.
- **Distance covered:** over 10,924 five-minute windows of moving buses
  (ghost rows left out), metres covered ÷ (`speed_raw` × seconds) = 1.03
  (middle half 0.98–1.08). mph would give 0.45, km/h 0.28. Slightly over 1
  fits whole-number speeds rounded down.
- `speed_raw` is typically 0–21 (40% of polls 0); 295 rows (1 in 1,200)
  are impossible (41–347).

Done: `cadavl_to_gtfs_rt.py` drops the `SPEED_UNIT` switch and writes
speed into `vehicle_positions.pb`, skipping readings over 40 m/s (live
since the poller restart on 2026-09-25 at 20:12).

### Bus capacity — settled: 100% = 50 riders, every vehicle

- **The percentages are all even.** All 351,576 readings, from every
  fleet series (4xx, 20xxx–22xxx, 4xxx, 5004) and the trolley (603), are
  even, and together they cover every even value 0–100. The vendor
  divides a rider count by one fixed 50; a per-bus capacity like 38 or 40
  would produce odd values. So **riders = `occupancy_pct` ÷ 2**, as exact
  as the passenger counters.
- **For scale** (MATA's 2012 Short Range Transit Plan, service guidelines):
  a 40-ft bus is planned at 40 seats with a 48-rider maximum (120% of
  seats at peak on key corridors, 100% otherwise). So on the vendor's
  scale, **80% ≈ every seat taken** and **96–100% ≈ MATA's maximum load**.
  The fullest: every reading of 96%+ was route 50 (Poplar) heading out to
  Exeter Rd, 08:40–13:10 (e.g. bus 21212 for 16 minutes Fri from 09:25).
  Route 50 runs 80%+ (every seat taken) in 1.1% of its polls; only 42 and
  36 otherwise reach 80% at all.
- **The official feed's categories don't mean what they say.** Pairing
  each official report with the tracker's for the same bus and position
  (5,915 pairs), the middle 90% of each: EMPTY ≈ 0 riders, MANY_SEATS ≈
  1–5, FEW_SEATS ≈ 6–10, STANDING_ROOM_ONLY ≈ 11–20, *no category* ≈
  21–36 (never above 40), FULL ≈ 41+. Fixed bands of the same count; a
  bus with 11 riders has plenty of seats. Don't use them for crowding.

Done: `CAPACITY = 50` in `map.html` (the "riders" figure is ~25% higher
than before), `[Q3]` in `analysis.sql` now `sum(occupancy_pct) // 2`,
DESIGN.md updated.

### Late threshold — kept at 5 minutes; MATA's own window not found

- **MATA has a standard but doesn't publish the window.** Its Board
  adopted service standards including on-time performance in 2014 (Title
  VI program update, Dec 2020 board packet: 40 of 46 routes met the OTP
  standard; a 72% OTP goal is mentioned in the Oct 2020 minutes). The
  city's open-data hub has MATA's monthly fixed-route on-time share
  (roughly 45–50% in 2015, 55–70% in 2016, 54–65% in 2021–22). Neither,
  nor MATA's 2012 Short Range Transit Plan, states the minutes; the data
  hub's "Data Dictionary" PDF might, but its host was refused in the
  browser.
- **The vendor's "on time" spans ±1 minute.** In 351k rows it never says
  "1 min"; the smallest non-zero values are ±2 min. So the usual window
  (≤ 1 min early, ≤ 5 min late) means, in vendor minutes: early = 2+ min
  early, late = 6+ min late.
- **On that window:** 73% of bus-polls on time (18% late, 9% early); 75%
  of departures from mid-route timepoints (17% late, 8% early); and
  **60% of departures from a trip's first stop** `[DEPART]` (from MATA's
  feed, 455 Friday trips: median 4.2 min late, 40% left 5+ min late, 1%
  early). That last is the number nearest MATA's own figures (54–65% in
  2021–22), which suggests MATA measures departures.
- **Early running is real:** 2+ min early in 20% of trolley (100) polls,
  17% on route 40, 14–15% on 07, 30, 04, 57.
- Why departures come from MATA's feed: at a line's end the tracker still
  shows the finished trip's headsign when the bus leaves, so its log there
  is a departure credited to the trip just ended (it made line ends look
  22% early). `arrivals_due` now leaves line ends out.

Done: `[Q1]` now also reports `share_early` and `on_time` (≤ 1 early, ≤ 5
late). **Needs you:** if you can get MATA's definition (the data
dictionary on data.memphistn.gov, or ask MATA), adjust the two numbers.

## QUESTIONS.md backlog

### Bunching and headways `[HEADWAY]` — buses don't bunch; trips go missing

- **Headways are long.** Median planned gap between consecutive trips at a
  stop: 45 min on the busiest routes (01, 08, 36, 50), 60–120 on most,
  4–6 hours on 28, 34, 37.
- **Bunching essentially never happens.** Of 65,766 pairs of consecutive
  buses at a stop (line ends aside), 6 came within a quarter of their
  planned gap (5 of them one pair: route 50 buses 32055 and 23023, 20 min
  apart on paper, together Fri 11:18–11:23), and 34 were overtakes. Two
  buses logged in the same second are now ordered by their timetable, so
  the count no longer shifts from run to run.
- **The buses that run keep their spacing.** Gaps over 1.5× plan between
  two buses that ran: ≤ 0.6% (routes 50, 36), otherwise ~0. A rider
  turning up at random waits ≤ 1 min longer than the timetable implies on
  most routes; route 28 +5.6 min (6-hour gaps, 54 pairs), 02 +3.7, 52
  +2.3, 37 +1.8, 53 +1.5.
- The gaps riders actually get are **trips that never run**, next.
- Method: `[HEADWAY]` pairs each bus with the one before it at the stop and
  compares against *their two trips'* planned difference. Counting from
  "the previous bus seen" instead overstates gaps, because the arrivals log
  catches only ~84% of the stops on a trip that ran (99% on the trolley).

### Where delay builds up `[WHERE]`, `[WHERE_ROUTE]`

**Per stop** (delay gained since the previous logged stop on the same
trip, summed into bus-minutes lost per day, stops passed 20+ times; line
ends left out):

| Route → direction | Stop | Avg gained | Bus-min/day |
|---|---|---|---|
| 36 → Centennial / Hacks Cross | American Way @ Getwell | +3.1 min | 60 |
| 36 → William Hudson | Getwell Rd @ Allenbrooke Cv | +3.0 | 32 |
| 50 → William Hudson | Poplar @ Claybrook | +1.4 | 29 |
| 01 → Walnut @ Racine | Tillman at Johnson | +1.1 | 26 |
| 42 → Frayser / → Airways | Cleveland @ Larkin, Cleveland @ Jefferson, Bellevue @ Central | +1.6–1.7 | 24–25 each |
| 50 → William Hudson / → Exeter | Poplar @ Innsbruck, @ Kirby Pkwy, @ High | +0.9–1.0 | 20–24 each |
| 100 trolley → Central Station | Main St @ Union Ave | +1.8 | 24 |

Route 36's Getwell / American Way stretch costs time in both directions,
and 50's Poplar corridor and 42's Cleveland corridor add up stop after
stop.

**Per trip** (delay at the last logged stop minus the first, line ends
aside, trips logged 20+ min): most routes **start late and recover**.
Median start 2–4 min late on most routes (37: 6), and on most the median
end is on time or early. 30, 37, 40 end 5.6–7.7 min earlier than they
started, and 04, 42, 50, 57 about 4.3: their schedules have slack, which
fits their early running. Some **compound** instead: 02 +3.8 min per trip
(31% of trips gain 5+), 28 +2.1, 01 +2.0, 13 +1.5, 36 +1.4, 08 +1.2. The
late starts come from the terminal: departures run a median 4.2 min late
(`[DEPART]`, under Late threshold), 5.7 on route 50 and 6.8 on 37.

### Missed service `[MISSED]`, `[MISSED_HOUR]` — 13–16% of trips never ran

A trip never ran if no bus was ever on it: none in the tracker (no arrival
or position matched to it) and, from Friday, none in MATA's official feed.
The two agree: of 471 Friday trips (06:00–19:50) the official feed saw
running, the tracker saw 464, and it saw none the official feed didn't.

- **Thu: 84 of 651 scheduled trips (13%) never ran. Fri: 101 of 618 (16%)**
  (trips due by 19:50).
- **Worst:** Fri route 01, 31 of 40: no bus at all until 12:46, then one
  (Thu it ran two all day). Thu route 69, 13 of 17 (no bus before 14:00);
  53, 19 of 31; 37, 5 of 10 (13:00–17:00 only); 02, 14 of 30; 32, 9 of 23.
  Fri: 16 and 30 lost about half, 02 43%, 34 40%, 52 28%.
- Routes 04, 07, 13, 40 and the trolley lost nothing either day; 50 and
  11 one trip in two days; 36 four on Thursday, none Friday.
- **Every hour:** 11–23% of trips missed from 5 a.m. to 6 p.m., worst at
  6 a.m. (23%).
- **MATA's own records undercount it.** Of Friday's 101 unrun trips, its
  feed marked 27 CANCELED (and 5 trips it marked canceled did run). Its
  alerts are dispatchers' free text, 34 on Friday ("Route 1 is not running
  from William Hudson at 5:15a. The next bus is expected at 6:00a"), with
  "back in service" notes, route tags that are sometimes wrong ("Route 1
  back in service" tagged route 2, route 34 tagged 304), and active
  periods that never end. Counting missed service takes the timetable
  against buses seen, as `[MISSED]` does.
- Missed trips belong beside "which routes run behind": route 02 is both
  the latest (39% of polls 5+ min late) and among the most missed (43–47%
  of its trips).

### Does our trip matching hold up? `[TRIPMATCH]` — yes, 99.8%

60,662 official vehicle reports (Fri) against our row for the same bus
(fleet number) within a minute:

- Where we named a trip, it's the official one **99.8%** of the time; no
  route below 99.1% (39, 28), and 50 and the trolley 99.5%.
- The 128 disagreements are nearly all (122) the **same route, other
  direction**, a median 75 min apart: around a turnaround, the tracker's
  headsign flips before or after MATA assigns the next trip.
- We name no trip for **2.6%** of rows: 1,094 with no next stop (between
  trips), 505 with a "1h+" delay (by design: no trustworthy delay, no
  match), a handful with no trip due near. Highest on the trolley (13.5%)
  and 39 (12%), which sit longer between trips.
- At trip level too: of 471 Friday trips the official feed saw running,
  the tracker saw 464 ([MISSED] section).

### What riders get at the stop `[STOP_WAIT]` (group 5)

Turn up at a mid-route timepoint 2 minutes before the timetable says; how
long until a bus of that route leaves? (Lateness, early departures and
missed trips all count; a trip the tracker didn't log at that stop is
placed at its scheduled time plus its own median delay.)

- **All routes: median 4.9 min, but 23% of the time over 15 min** (p90 73
  min), and 120 of 5,842 calls had no bus at all for the rest of the day.
- **Worst:** 69 (median 48 min, 50% over 15), 02 (25 min, 57%), 01 (14.9,
  49%), 53 (9.1, 44%), 52 (7.6, 34%): the missed-trip routes.
- **Best:** 11 3.0, 07 3.1, 39 3.3, 04 3.4, the trolley 3.5 (though 40%
  of its 52 waits pass 15 min).

### Group 1: delay, deeper

- **Which direction `[DIRECTION]`: leaving downtown.** On 10 of the 17
  bus routes that reach William Hudson, the trip *away* from it is 5+ min
  late at least 10 points more often: 52 to Methodist Hospital 42% vs 11%
  inbound, 57 32% vs 5%, 34 32% vs 4%, 02 51–54% vs 26%, 39 18–41% vs
  14%, 13 28% vs 6%, 11 21% vs 5%, 01 30% vs 13%. Only 28 and 40 lean the
  other way.
- **When `[HOUR]`: the afternoon.** Share 5+ min late climbs from 5–7%
  before 7 a.m. to 17–20% through midday and **26–32% at 15:00–17:59**;
  median delay is 2 min only in those three hours. Early running peaks at
  night (27% at 21:00, 40% at 22:00) and 4 a.m. (16%): evening schedules
  are slack. Weekday vs weekend needs more weeks.
- **Recover or compound:** see `[WHERE_ROUTE]` above: most routes start late
  and recover; 02, 28, 01, 13, 36 and 08 compound.
- **Early running `[EARLY]`, `[Q1]`.** 9% of all bus-polls are 2+ min
  early, and 8% of departures from mid-route timepoints. It clusters at a
  few: route 30 at American Way Transit Center 65% (avg 3.9 min early, at
  a transfer point), 40 at James Rd @ Hollywood 40%, the trolley at Main @
  Madison 37%, 01 at Union @ Waldran 32%, 04 at Pendleton @ Ketchum 28%,
  then 19–22% on 28, 57 (Park @ Perkins, Lamar @ East Pkwy), 40 (Stage @
  Summer), 50 (Poplar @ Cleveland) and 69 (Sax Rd @ Mitchell). From the
  start of a line buses almost never leave early (1%, `[DEPART]`); they
  leave late.

### Group 2: ridership and crowding

- **Peak loads `[LOAD]`: buses are rarely full.** Average 1–11 riders on
  board; the 95th percentile 25–29 on 50, 42, 36 and under 25 elsewhere.
  Every seat taken (40+) only on 50 (1.1% of polls), 42 (0.2%), 36 (0.1%).
  Busiest hours differ: 50 at 9, 36 at 15, 42 at 17.
- **Busiest vs latest `[LOAD_DELAY]`.** Across routes, barely related
  (correlation 0.19): 42, the busiest, is 10% late. But *within* a route
  fuller buses are much later: 50 46% late with 20+ riders vs 16% under 10;
  57 42 vs 15; 12 40 vs 6; 08 58 vs 26; 02 62 vs 34; 36 39 vs 22.
  Boarding time, or late buses collecting more waiting riders: the data
  can't separate the two.
- **Riding per day `[RIDERS_DAY]`.** Thu 4,064 rider-hours, peak 451 on
  board at 15:40, at least 8,077 boardings; Fri (to 20:21) 3,962, 423 at
  15:40, 7,913. MATA reported ~230,600 bus riders in September 2023
  (~7,700 a day), the same scale, which also supports reading the load as
  riders out of 50. Weather and events need weeks plus outside data.
- **Where buses fill `[BOARDINGS]`: downtown hubs.** Second @ Jackson (823
  on per day, the first stop out of William Hudson for 01, 04, 07, 12, 13,
  50, 57) and Second @ Market (382); then Third @ Mill (148), Airways Blvd
  @ Winchester (133), Directors Row @ Brooks (129), AW Willis @ Third
  (124), Getwell @ Mallory (99). Net changes between polls, so floors.

### Group 3: service delivered

- **Fleet in service `[FLEET]`.** At half past each hour, buses seen vs
  trips in progress: short by 3–8.5 buses most of the day (e.g. 08:30: 49
  trips, 40.5 buses; 13:30–15:30: 48–49 trips, 40–41 buses), about even
  16:30–17:30. The same shortfall as the missed trips.
- **Speed `[SPEED]`, `[SPEED_SLOW]`.** Average speed including stops:
  11.5–18.5 mph on most routes (01 slowest), 24 mph on 28, trolley 4.4;
  stopped 25–47% of the time (trolley 62%). Peak and midday differ by
  about 1 mph on most routes (28: 3 mph). The
  slowest stretches (300 m+): trolley on Main, Madison → Union (2.9 mph, 5
  min for 400 m); **route 42 on Cleveland and Bellevue** (Poplar →
  Jefferson 3.7 mph, Bellevue @ Lamar → Carr 6.2, Cleveland @ Union →
  Bellevue @ Carr 6.3); Poplar @ Reese → Highland (50, 01: 6.2–7.0); 36
  on Pauline / Jefferson (6.5–7.0) and Winchester @ Malco → Kirby Terrace
  (6.6); 52 Jackson @ McDavitt → Auction (6.7); 01 Summer @ Franklin →
  Tillman (6.8). The 42 and 50 corridors are also where `[WHERE]` finds
  delay building.
- Bunching, headways, ghost buses: above.

### Group 4: MATA's official feed

- **Countdowns `[PREDICT]`: good close up, optimistic far out.** 250,024
  predictions for trips with a bus, against when it left the stop:

  | Made ahead | Within ±2 min | Bus 1+ min *earlier* | Bus 5+ min later |
  |---|---|---|---|
  | 0–5 min | 87% | 9% | 4% |
  | 5–10 | 70% | 29% | 5% |
  | 10–20 | 54% | 37% | 8% |
  | 20–40 | 41% | 42% | 12% |
  | 40+ | 33% | 45% | 15% |

  The median error is about 0, but far-out countdowns lean late: **a rider
  timing their walk to a 20-minute countdown finds the bus already gone 4
  times in 10.**
- **Departures `[DEPART]`** (the numbers are under Late threshold): by
  route, worst 37 (78% of trips left 5+ min late), 50 (66%), 16 (60%), 28
  (57%); best 30 (86% on time), 07 (85%), trolley (77%), 53 (76%), 13
  (75%). Small numbers per route (4–35 trips, one day).
- **Layovers `[LAYOVER]`.** MATA's feed keeps a bus at its next trip's first
  stop (the tracker drops it): 429 Friday trips sat a median 7 min before
  leaving (trolley 1 min); 25% under 5 min. Short layovers don't predict
  late starts here: 19% of trips after a short one started 5+ min late, 27%
  after a longer one. One day, small numbers per route.
- Missed service and trip matching: above.

### Not answerable yet

- **Weekday vs weekend, weather, events** (groups 1–2): need weeks of data;
  the queries (`[Q2]`, `[HOUR]` + `dayname`, `[RIDERS_DAY]`) are ready.
- **Detour impact** (group 5): needs weeks of the poller's new detour log
  (`data/detours/`), which has been running since 2026-09-25 at 20:12.
- **Self-computed schedule adherence** (group 5): still a non-goal. The
  vendor's delay agrees with actual − scheduled, and `sched` now makes it a
  one-line join if ever needed.
