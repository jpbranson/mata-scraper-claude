# Findings

What the recorded data says so far, question by question. The queries are
in `analysis.sql` (tags in brackets, e.g. `[Q1]`); rerun them as days
accumulate, since every figure here is from a short window.

**Data behind this version:** tracker history Thu 2026-09-24 04:00–22:35
(a full service day) and Fri 2026-09-25 04:00–19:10, plus 55 minutes on Wed
evening; official GTFS-RT archive from Fri 05:45. That is **under two
weekdays and no weekend**, so anything by day of week, weather or event is
still unanswerable, and route rankings can move.

## The three questions (DESIGN.md)

Ran `analysis.sql` unchanged on 2026-09-25 at 19:10. The `good` filter
keeps ~97.5% of rows (1–1.5% are "1h+" caps, ~1% stuck GPS).

**1. Which routes constantly run behind?** Share of bus-polls 5+ min late:

| Worst | 5+ min late | median | | Best | 5+ min late |
|---|---|---|---|---|---|
| 02 | 40% | 4 min late | | 69 | 2% |
| 52 | 28% | on time | | 16 | 4% |
| 36 | 28% | 2 min late | | 40, 04, 12 | 6% |
| 08 | 26% | 2 min late | | 100 (trolley) | 7% |
| 28 | 26% | 2 min late | | 07 | 8% |

Route 02 stands out; the next tier (52, 36, 08, 28, 01, 50) is 22–28%.

**2. Which days are especially bad?** Fri 19% of polls 5+ min late, Thu 17%.
Two days can't say which days are bad. The query now also shows `hours`
covered, so partial days (Wed: 0.9 h) are obvious.

**3. How many people are riding right now?** Works: at 19:10 Friday, 31
buses and 144 riders on board (load % ÷ 2, see Bus capacity below; the
first run, with the old placeholder of 40 riders per full bus, said ~115).

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
| 1–1.5 min (6–9 polls) | 1,205 | 69 | 1,126 | 37% |
| 2–3.5 min (10–19) | 454 | 53 | 395 | 38% |
| 3.5–5.5 min (20–29) | 163 | 24 | 135 | 54% |
| 5.5+ min (30+) | 183 | 8 | 172 | 70% |

- The 30-poll rule mostly catches **layovers** (127 of 183 streaks at a
  route's end) and **holds** (45 mid-route, typically a bus sitting 5–10
  min while its delay climbs from ~0 to +5…+10, e.g. route 50 on Poplar,
  route 57 on Park). Only 8 were dead trackers.
- Dead trackers are mostly **short** (1–5 min) and slip past it. Over those
  stretches the official feed also freezes: same position, report age
  climbing to ~2 min (median), versus ~10 s for parked buses.
- **It doesn't matter for delay.** The vendor freezes delay with position
  (median delay 0 at a ghost's start, end and after the jump), and every
  route's 5+ min late share is within 1.2 points either way. Route 02 is
  late on all its buses (450: 31%, 458: 52%, 22607: 50%), not because of
  a bad tracker.
- **One bad tracker:** bus 458 (routes 19, 02) has 1,002 ghost rows, 15%
  of its polls and nearly half of all ghost rows. Next worst: 21501 (5%),
  21809 (1.5%).

Decision: `good` keeps `unchanged_polls < 30`; spatial queries drop
`ghost_rows` (new view). The map's dashed "no GPS movement" marker is
usually a layover, as DESIGN.md now says.

### Speed unit — settled: metres per second

- **Same report, both feeds:** matching each official vehicle position to
  the tracker row for the same bus (fleet number) at the identical
  coordinates gave 5,382 pairs; for the 2,557 moving ones, the official
  speed (m/s by the GTFS-RT spec) *equals* `speed_raw` 97% of the time.
- **Distance covered:** over 10,592 five-minute windows of moving buses
  (ghost rows left out), metres covered ÷ (`speed_raw` × seconds) = 1.03
  (middle half 0.98–1.08). mph would give 0.45, km/h 0.28. Slightly over 1
  fits whole-number speeds rounded down.
- `speed_raw` is typically 0–21 (40% of polls 0); 284 rows (1 in 1,200)
  are impossible (41–347).

Done: `cadavl_to_gtfs_rt.py` drops the `SPEED_UNIT` switch and writes
speed into `vehicle_positions.pb`, skipping readings over 40 m/s (takes
effect when the poller is restarted).

### Bus capacity — settled: 100% = 50 riders, every vehicle

- **The percentages are all even.** All 340,389 readings, from every
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
  (5,382 pairs): EMPTY ≈ 0 riders, MANY_SEATS ≈ 1–5, FEW_SEATS ≈ 6–10,
  STANDING_ROOM_ONLY ≈ 11–20, *no category* ≈ 21–40, FULL ≈ 41+. Fixed
  bands of the same count; a bus with 11 riders has plenty of seats.
  Don't use them for crowding.

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
- **The vendor's "on time" spans ±1 minute.** In 340k rows it never says
  "1 min"; the smallest non-zero values are ±2 min. So the usual window
  (≤ 1 min early, ≤ 5 min late) means, in vendor minutes: early = 2+ min
  early, late = 6+ min late.
- **On that window:** 73% of bus-polls on time (18% late, 9% early); 75%
  of departures from mid-route timepoints (17% late, 8% early); and
  **59% of departures from a trip's first stop** `[DEPART]` (from MATA's
  feed, 443 Friday trips: median 4.3 min late, 40% left 5+ min late, 1%
  early). That last is the number nearest MATA's own figures (54–65% in
  2021–22), which suggests MATA measures departures.
- **Early running is real:** 2+ min early in 20% of trolley (100) polls,
  18% on route 40, 14–15% on 07, 04, 30, 57.
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
- **Bunching essentially never happens.** Of 64,677 pairs of consecutive
  buses at a stop (line ends aside), 6 came within a quarter of their
  planned gap (5 of them one pair: route 50 buses 32055 and 23023, 20 min
  apart on paper, together Fri 11:18–11:23), and 37 were overtakes.
- **The buses that run keep their spacing.** Gaps over 1.5× plan between
  two buses that ran: ≤ 0.6% (routes 50, 36), otherwise ~0. A rider
  turning up at random waits ≤ 1 min longer than the timetable implies on
  most routes; route 02 +3.9 min, 52 +2.3, 37 +1.8, 53 +1.4.
- The gaps riders actually get are **trips that never run**, next.
- Method: `[HEADWAY]` pairs each bus with the one before it at the stop and
  compares against *their two trips'* planned difference. Counting from
  "the previous bus seen" instead overstates gaps, because the arrivals log
  catches only ~83–85% of the stops on a trip that ran (99% on the trolley).

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
| 42 → Airways / → Frayser | Bellevue @ Central, Cleveland @ Jefferson, Cleveland @ Larkin | +1.6–1.7 | 24–25 each |
| 50 → William Hudson / → Exeter | Poplar @ Innsbruck, @ Kirby Pkwy, @ High | +0.9–1.1 | 20–24 each |
| 100 trolley → Central Station | Main St @ Union Ave | +1.8 | 23 |

Route 36's Getwell / American Way stretch costs time in both directions,
and 50's Poplar corridor and 42's Cleveland corridor add up stop after
stop.

**Per trip** (delay at the last logged stop minus the first, line ends
aside, trips logged 20+ min): most routes **start late and recover**.
Median start 2–4 min late (37: 6), median end on time or early. 30, 37,
40 end 5.6–7.7 min earlier than they started, and 04, 42, 50, 57 about
4.3: their schedules have slack, which fits their early running. Some
**compound** instead: 02 +3.7 min per trip (31% of trips gain 5+), 28
+2.1, 01 +1.9, 13 +1.6, 36 +1.6, 08 +1.3. The late starts come from the
terminal: departures run a median 4.3 min late (`[DEPART]`, under Late
threshold), 5.7 on route 50 and 6.8 on 37.

### Missed service `[MISSED]`, `[MISSED_HOUR]` — 13–17% of trips never ran

A trip never ran if no bus was ever on it: none in the tracker (no arrival
or position matched to it) and, from Friday, none in MATA's official feed.
The two agree: of 441 Friday trips (06:00–18:30) the official feed saw
running, the tracker saw 434, and it saw none the official feed didn't.

- **Thu: 84 of 651 scheduled trips (13%) never ran. Fri: 99 of 593 (17%)**
  (trips due by 18:40).
- **Worst:** Fri route 01, 30 of 38: no bus at all until 12:46, then one
  (Thu it ran two all day). Thu route 69, 13 of 17 (no bus before 14:00);
  53, 19 of 31; 37, 5 of 10 (13:00–17:00 only); 02, 14 of 30; 32, 9 of 23.
  Fri: 16 and 30 lost half, 02 45%, 34 40%, 52 30%.
- Routes 04, 07, 13, 40 and the trolley lost nothing either day; 50 and
  11 one trip in two days; 36 four on Thursday, none Friday.
- **Every hour:** 11–23% of trips missed from 5 a.m. to 6 p.m., worst at
  6 a.m. (23%).
- **MATA's own records undercount it.** Of Friday's 99 unrun trips, its
  feed marked 27 CANCELED (and 5 trips it marked canceled did run). Its
  alerts are dispatchers' free text, 32 on Friday for ~15 routes ("Route 1
  is not running from William Hudson at 5:15a. The next bus is expected at
  6:00a"), with "back in service" notes, route tags that are sometimes
  wrong ("Route 1 back in service" tagged route 2, route 34 tagged 304),
  and active periods that never end. Counting missed service takes the
  timetable against buses seen, as `[MISSED]` does.
- Missed trips belong beside "which routes run behind": route 02 is both
  the latest (40% of polls 5+ min late) and among the most missed (45–47%
  of its trips).

### Does our trip matching hold up? `[TRIPMATCH]` — yes, 99.8%

58,429 official vehicle reports (Fri) against our row for the same bus
(fleet number) within a minute:

- Where we named a trip, it's the official one **99.8%** of the time; no
  route below 99.1% (28), 39 and trolley 99.2–99.5%.
- The 125 disagreements are nearly all the **same route, other
  direction**, a median 75 min apart: around a turnaround, the tracker's
  headsign flips before or after MATA assigns the next trip.
- We name no trip for **2.7%** of rows: 1,057 with no next stop (between
  trips), 505 with a "1h+" delay (by design: no trustworthy delay, no
  match), 4 with no trip due near. Highest on the trolley (14%) and 39
  (12%), which sit longer between trips.
- At trip level too: of 441 Friday trips the official feed saw running,
  the tracker saw 434 ([MISSED] section).

### What riders get at the stop `[STOP_WAIT]` (group 5)

Turn up at a mid-route timepoint 2 minutes before the timetable says; how
long until a bus of that route leaves? (Lateness, early departures and
missed trips all count; a trip the tracker didn't log at that stop is
placed at its scheduled time plus its own median delay.)

- **All routes: median 5.0 min, but 23% of the time over 15 min** (p90 74
  min), and 122 of 5,775 calls had no bus at all for the rest of the day.
- **Worst:** 69 (median 48 min, 50% over 15), 02 (25 min, 57%), 01 (14.9,
  49%), 53 (9.1, 44%), 52 (7.6, 34%): the missed-trip routes.
- **Best:** 11 3.0, 07 3.1, 04 and the trolley 3.2, 39 3.3.

### Group 1: delay, deeper

- **Which direction `[DIRECTION]`: leaving downtown.** On almost every
  route the trip *away* from William Hudson is late far more often: 52 to
  Methodist Hospital 43% vs 12% inbound, 57 33% vs 5%, 34 32% vs 4%, 02
  51–54% vs 27%, 39 41% vs 14%, 13 28% vs 7%, 11 21% vs 5%, 01 30% vs 13%.
- **When `[HOUR]`: the afternoon.** Share 5+ min late climbs from 5–7%
  before 7 a.m. to 17–20% through midday and **26–32% at 15:00–17:59**;
  median delay is 2 min only in those three hours. Early running peaks at
  night (27% at 21:00, 40% at 22:00) and 4 a.m. (16%): evening schedules
  are slack. Weekday vs weekend needs more weeks.
- **Recover or compound:** see `[WHERE_ROUTE]` above: most routes start late
  and recover; 100, 02, 36 compound.
- **Early running `[EARLY]`, `[Q1]`.** 9% of all bus-polls are 2+ min
  early, and 8% of departures from mid-route timepoints. It clusters at a
  few: route 30 at American Way Transit Center 65% (avg 3.9 min early, at
  a transfer point), 40 at James Rd @ Hollywood 40%, the trolley at Main @
  Madison 36%, 01 at Union @ Waldran 33%, 04 at Pendleton @ Ketchum 28%,
  then 20–22% on 28, 40, 50 (Poplar @ Cleveland) and 57 (Lamar @ East
  Pkwy, Park @ Perkins). From the start of a line buses almost never leave
  early (1%, `[DEPART]`); they leave late.

### Group 2: ridership and crowding

- **Peak loads `[LOAD]`: buses are rarely full.** Average 1–11 riders on
  board; the 95th percentile 25–29 on 50, 42, 36 and under 25 elsewhere.
  Every seat taken (40+) only on 50 (1.1% of polls), 42 (0.2%), 36 (0.1%).
  Busiest hours differ: 50 at 9, 36 at 15, 42 at 17.
- **Busiest vs latest `[LOAD_DELAY]`.** Across routes, barely related
  (correlation 0.19): 42, the busiest, is 10% late. But *within* a route
  fuller buses are much later: 50 46% late with 20+ riders vs 16% under 10;
  57 42 vs 15; 12 40 vs 6; 08 58 vs 26; 02 62 vs 35; 36 39 vs 22.
  Boarding time, or late buses collecting more waiting riders: the data
  can't separate the two.
- **Riding per day `[RIDERS_DAY]`.** Thu 4,064 rider-hours, peak 451 on
  board at 15:40, at least 8,077 boardings; Fri 3,900, 423 at 15:40, 7,824.
  MATA reported ~230,600 bus riders in September 2023 (~7,700 a day), the
  same scale, which also supports reading the load as riders out of 50.
  Weather and events need weeks plus outside data.
- **Where buses fill `[BOARDINGS]`: downtown hubs.** Second @ Jackson (820
  on per day, the first stop out of William Hudson for 01, 04, 07, 12, 13,
  50, 57) and Second @ Market (382); then Third @ Mill (145), Airways Blvd @
  Winchester (132), Directors Row @ Brooks (129), AW Willis @ Third (120),
  Getwell @ Mallory (99). Net changes between polls, so floors.

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
  Jefferson 3.7 mph, Cleveland @ Union → Bellevue @ Carr 6.3); Poplar @
  Reese → Highland (50, 01: 6.5–7.0); 36 on Pauline / Jefferson and
  Winchester @ Malco → Kirby Terrace (6.5); 01 Summer @ Franklin → Tillman
  (6.8). The 42 and 50 corridors are also where `[WHERE]` finds delay
  building.
- Bunching, headways, ghost buses: above.

### Group 4: MATA's official feed

- **Countdowns `[PREDICT]`: good close up, optimistic far out.** 242,014
  predictions for trips with a bus, against when it left the stop:

  | Made ahead | Within ±2 min | Bus 1+ min *earlier* | Bus 5+ min later |
  |---|---|---|---|
  | 0–5 min | 87% | 9% | 4% |
  | 5–10 | 70% | 29% | 5% |
  | 10–20 | 54% | 36% | 8% |
  | 20–40 | 40% | 42% | 12% |
  | 40+ | 32% | 45% | 16% |

  The median error is about 0, but far-out countdowns lean late: **a rider
  timing their walk to a 20-minute countdown finds the bus already gone 4
  times in 10.**
- **Departures `[DEPART]`** (the numbers are under Late threshold): by
  route, worst 37 (78% of trips left 5+ min late), 50 (66%), 16 (60%), 28
  (57%); best 30 (86% on time), 07 (85%), trolley (76%), 13 (75%), 53
  (74%). Small numbers per route (4–35 trips, one day).
- **Layovers `[LAYOVER]`.** MATA's feed keeps a bus at its next trip's first
  stop (the tracker drops it): 418 Friday trips sat a median 7 min before
  leaving (trolley 1 min); 24% under 5 min. Short layovers don't predict
  late starts here: 20% of trips after a short one started 5+ min late, 27%
  after a longer one. One day, small numbers per route.
- Missed service and trip matching: above.

### Not answerable yet

- **Weekday vs weekend, weather, events** (groups 1–2): need weeks of data;
  the queries (`[Q2]`, `[HOUR]` + `dayname`, `[RIDERS_DAY]`) are ready.
- **Detour impact** (group 5): needs weeks of the poller's new detour log
  (`data/detours/`), which starts when the poller is next restarted.
- **Self-computed schedule adherence** (group 5): still a non-goal. The
  vendor's delay agrees with actual − scheduled, and `sched` now makes it a
  one-line join if ever needed.
