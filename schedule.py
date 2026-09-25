"""
Timetable and arrivals: MATA's GTFS timetable joined to the live positions.

MATA publishes its timetable as GTFS (a zip of CSVs) from the same vendor
that runs the tracker, refreshed nightly. The two line up exactly: GTFS
stop_id is "0:" + the tracker's stop code (stops.csv `stop_code`), route_id
is the route number, and trip_headsign is the bus's `destination`. The
vendor's delay is measured against this timetable: a bus "8 min late" at
LAMAR @LAPALOMA at 18:01 is the 17:52:59 trip.

The poller calls `Schedule.update` every poll. Per local service day it
writes, for map.html's stop panel:

    data/schedule/<day>/stops.json      stop code -> routes scheduled there
    data/schedule/<day>/<route>.json    that route's scheduled times per stop,
                                        and its stop patterns (below)
    data/arrivals/<day>/<route>.jsonl   each time a bus served a stop

A bus has served stop A when its next stop changes away from A. Which
stop: the one named A on the bus's route and direction nearest the bus.
Which trip: the one due at A closest to (arrival time - reported delay).
Each bus row also gets `trip_id`, the same match for its next stop, so the
map can say when a scheduled trip is expected.
"""

from __future__ import annotations

import csv
import io
import json
import math
import zipfile
from bisect import bisect_left
from collections import Counter, defaultdict
from datetime import date, datetime
from email.utils import formatdate
from pathlib import Path
from statistics import median

import requests

GTFS_URL = "https://gtfs.mata.cadavl.com/MATA/GTFS/GTFS_MATA.zip"
HERE = Path(__file__).parent
OUT_DIR = HERE / "data"
GTFS_PATH = OUT_DIR / "gtfs.zip"
STOPS_CSV = HERE / "stops.csv"

MATCH_WINDOW = 20 * 60   # a trip is due within 20 min of the estimate, or it's no match
NEAR_M = 300             # the bus was this close to the stop it just served
REPEAT_S = 10 * 60       # a second arrival at the same stop this soon is GPS jitter
MAX_GAP_S = 120          # polls further apart than this can't time an arrival
RETRY_S = 15 * 60        # after a failed timetable load


def fetch_gtfs(session: requests.Session) -> None:
    """Download the zip (~1.5 MB) unless ours is as new as the server's."""
    headers = {}
    if GTFS_PATH.exists():
        headers["If-Modified-Since"] = formatdate(GTFS_PATH.stat().st_mtime, usegmt=True)
    resp = session.get(GTFS_URL, headers=headers, timeout=60)
    if resp.status_code == 304:
        return
    resp.raise_for_status()
    GTFS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = GTFS_PATH.with_suffix(".tmp")
    tmp.write_bytes(resp.content)
    tmp.replace(GTFS_PATH)


def local_midnight(day: date) -> int:
    """GTFS times count from "noon minus 12 h", which is midnight except on
    DST change days."""
    return int(datetime(day.year, day.month, day.day, 12).timestamp()) - 43200


def dist_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Equirectangular distance; exact enough at city scale."""
    x = math.radians(lon2 - lon1) * math.cos(math.radians((lat1 + lat2) / 2))
    return 6371000 * math.hypot(x, math.radians(lat2 - lat1))


class Timetable:
    """One service day of the GTFS feed, indexed for matching."""

    def __init__(self, zip_path: Path, day: date) -> None:
        self.day = day
        self.t0 = local_midnight(day)
        with zipfile.ZipFile(zip_path) as z:
            def rows(name: str):
                if name not in z.namelist():
                    return []
                return csv.DictReader(io.TextIOWrapper(z.open(name), "utf-8-sig"))

            services = self._services(rows("calendar.txt"), rows("calendar_dates.txt"))
            all_trips = {r["trip_id"]: (r["route_id"], r["trip_headsign"].strip(), r["service_id"],
                                        r.get("direction_id", ""))
                         for r in rows("trips.txt")}
            # trip -> [(stop_sequence, code, seconds, timepoint)], for patterns.
            calls: dict[str, list] = defaultdict(list)
            # (route, headsign, stop code) -> [(unix time due, trip_id)], today only.
            self.due: dict[tuple, list] = defaultdict(list)
            # Every stop each route + direction calls at, any day: name lookup
            # still works on a day the feed has no service for.
            pattern: set[tuple] = set()
            for r in rows("stop_times.txt"):
                route, head, service, _ = all_trips.get(r["trip_id"], (None,) * 4)
                if route is None:
                    continue
                code = r["stop_id"].split(":", 1)[-1]
                pattern.add((route, head, code))
                h, m, s = map(int, r["arrival_time"].split(":"))
                secs = h * 3600 + m * 60 + s
                calls[r["trip_id"]].append((int(r["stop_sequence"]), code, secs, r.get("timepoint") == "1"))
                if service in services:
                    self.due[(route, head, code)].append((self.t0 + secs, r["trip_id"]))
        for times in self.due.values():
            times.sort()
        self.headsign = {t: head for t, (_, head, _, _) in all_trips.items()}

        with STOPS_CSV.open(encoding="utf-8") as fh:
            stops = {r["stop_code"]: r for r in csv.DictReader(fh)}
        self.patterns = self._patterns(all_trips, calls, services, stops)
        # (route, headsign, stop name as the tracker spells it) -> [(code, lat, lon)]
        self.by_name: dict[tuple, list] = defaultdict(list)
        for route, head, code in pattern:
            s = stops.get(code)
            if s and s["lat"]:
                self.by_name[(route, head, s["stop_name"])].append(
                    (code, float(s["lat"]), float(s["lon"])))

    @staticmethod
    def _patterns(all_trips: dict, calls: dict, services: set, stops: dict) -> dict[str, list]:
        """Per route, the stop patterns its trips run: for each headsign, every
        stop sequence carrying at least a fifth (and 3) of its trips that is
        a real branch, sharing under 80% of its stops with the ones already
        kept (counting today's trips, or any day's if none run today). So
        route 39's two ways into William Hudson are two patterns, while
        route 36's variants a few stops apart stay one. Each
        stop has its name, position, median seconds from the first stop, and
        whether it is a timepoint (the timetable's major stops). For the strip
        and schematic pages, which place buses along these."""
        seqs: dict[tuple, Counter] = defaultdict(Counter)
        offsets: dict[tuple, list] = defaultdict(list)
        for trip, cs in calls.items():
            route, head, service, direction = all_trips[trip]
            cs.sort()
            key = tuple((c[1], c[3]) for c in cs)
            seqs[(route, head, direction)][(service in services, key)] += 1
            offsets[(route, head, key)].append([c[2] - cs[0][2] for c in cs])
        out: dict[str, list] = defaultdict(list)
        for (route, head, direction), counts in sorted(seqs.items()):
            today = any(on for on, _ in counts)
            ranked = sorted(((n, key) for (on, key), n in counts.items() if on == today), reverse=True)
            total = sum(n for n, _ in ranked)
            kept: list[set] = []
            for n, key in ranked:
                codes = {c for c, _ in key}
                if kept and (n < max(3, total / 5) or any(
                        len(codes & k) / len(codes | k) >= .8 for k in kept)):
                    continue
                kept.append(codes)
                mins = [median(o) for o in zip(*offsets[(route, head, key)])]
                out[route].append({"head": head, "dir": direction, "trips": n, "stops": [
                    [code, stops.get(code, {}).get("stop_name", code),
                     round(float(stops[code]["lat"]), 5) if code in stops else None,
                     round(float(stops[code]["lon"]), 5) if code in stops else None,
                     round(off), int(tp)]
                    for (code, tp), off in zip(key, mins)]})
        return out

    def _services(self, calendar, calendar_dates) -> set[str]:
        ymd = self.day.strftime("%Y%m%d")
        weekday = self.day.strftime("%A").lower()
        on = {r["service_id"] for r in calendar
              if r["start_date"] <= ymd <= r["end_date"] and r[weekday] == "1"}
        for r in calendar_dates:
            if r["date"] == ymd:
                (on.add if r["exception_type"] == "1" else on.discard)(r["service_id"])
        return on

    def stop_for(self, route: str, headsign: str | None, name: str | None,
                 lat: float, lon: float) -> tuple[str | None, float]:
        """The stop called `name` on this route and direction nearest the
        bus, and how far away it is."""
        cands = self.by_name.get((route, (headsign or "").strip(), name))
        if not cands:
            return None, math.inf
        d, code = min((dist_m(lat, lon, la, lo), code) for code, la, lo in cands)
        return code, d

    def trip_for(self, route: str, headsign: str | None, stop: str, t: float) -> str | None:
        """The trip due at `stop` closest to time t, if one is near enough."""
        due = self.due.get((route, (headsign or "").strip(), stop))
        if not due:
            return None
        i = bisect_left(due, (t,))
        best = min(due[max(i - 1, 0):i + 1], key=lambda d: abs(d[0] - t))
        return best[1] if abs(best[0] - t) <= MATCH_WINDOW else None

    def write(self) -> None:
        """data/schedule/<day>/: stops.json and one <route>.json per route.
        Times are seconds after the file's `t0` (local midnight)."""
        out = OUT_DIR / "schedule" / self.day.isoformat()
        out.mkdir(parents=True, exist_ok=True)
        routes: dict[str, dict] = defaultdict(lambda: {"trips": [], "stops": defaultdict(list)})
        index: dict[str, dict] = defaultdict(dict)
        at_stop: dict[str, set] = defaultdict(set)
        for (route, head, code), due in sorted(self.due.items()):
            r = routes[route]
            at_stop[code].add(route)
            for t, trip in due:
                i = index[route].setdefault(trip, len(r["trips"]))
                if i == len(r["trips"]):
                    r["trips"].append([trip, head])
                r["stops"][code].append([t - self.t0, i])
        for route, r in routes.items():
            for times in r["stops"].values():
                times.sort()
            (out / f"{route}.json").write_text(json.dumps(
                {"t0": self.t0, **r, "patterns": self.patterns.get(route, [])},
                separators=(",", ":")))
        (out / "stops.json").write_text(json.dumps(
            {"t0": self.t0, "stops": {c: sorted(rs) for c, rs in at_stop.items()}},
            separators=(",", ":")))


class Arrivals:
    """Watches each bus's next stop. When it moves on from A, the bus has
    served A, at the time of the last poll that still showed A."""

    def __init__(self) -> None:
        self.prev: dict[str, dict] = {}
        self.seen: dict[tuple, int] = {}

    def update(self, tt: Timetable, rows: list[dict]) -> list[dict]:
        out = []
        for r in rows:
            vid = r["vehicle_id"]
            p, self.prev[vid] = self.prev.get(vid), r
            if (not p or not p["next_stop_name"] or p["next_stop_name"] == r["next_stop_name"]
                    or p["route_id"] != r["route_id"]
                    or r["observed_at"] - p["observed_at"] > MAX_GAP_S):
                continue
            stop, d = tt.stop_for(p["route_id"], p["destination"], p["next_stop_name"],
                                  p["lat"], p["lon"])
            t = p["observed_at"]
            if stop is None or d > NEAR_M or t - self.seen.get((vid, stop), -REPEAT_S) < REPEAT_S:
                continue
            self.seen[(vid, stop)] = t
            delay = None if p["delay_capped"] else p["delay_seconds"]
            out.append({"t": t, "route": p["route_id"], "stop": stop, "vehicle": vid,
                        "trip": tt.trip_for(p["route_id"], p["destination"], stop,
                                            t - (delay or 0)) if delay is not None else None,
                        "delay": delay})
        return out


def live_trip(tt: Timetable, r: dict) -> str | None:
    """The trip a bus is running: the one due at its next stop when the bus
    would get there on time."""
    if not r["next_stop_name"] or r["delay_seconds"] is None or r["delay_capped"]:
        return None
    stop, _ = tt.stop_for(r["route_id"], r["destination"], r["next_stop_name"], r["lat"], r["lon"])
    if stop is None:
        return None
    eta = (r["next_stop_eta_min"] or 0) * 60
    return tt.trip_for(r["route_id"], r["destination"], stop,
                       r["observed_at"] + eta - r["delay_seconds"])


def arrivals_path(day: str, route: str) -> Path:
    return OUT_DIR / "arrivals" / day / f"{route}.jsonl"


def append_arrivals(arrivals: list[dict], mode: str = "a") -> None:
    by_file: dict[Path, list] = defaultdict(list)
    for a in arrivals:
        day = datetime.fromtimestamp(a["t"]).strftime("%Y-%m-%d")
        by_file[arrivals_path(day, a["route"])].append(a)
    for path, rows in by_file.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open(mode, encoding="utf-8") as fh:
            for a in rows:
                fh.write(json.dumps({k: v for k, v in a.items() if k != "route"},
                                    separators=(",", ":")) + "\n")


class Schedule:
    """The poller's handle: keeps today's timetable loaded (fetching the
    feed at most once per day, retrying after failures), tags each row with
    its trip, and logs arrivals."""

    def __init__(self) -> None:
        self.tt: Timetable | None = None
        self.arrivals = Arrivals()
        self.retry_at = 0

    def timetable(self, session: requests.Session, now: int) -> Timetable | None:
        day = date.fromtimestamp(now)
        if (self.tt and self.tt.day == day) or now < self.retry_at:
            return self.tt if self.tt and self.tt.day == day else None
        try:
            fetch_gtfs(session)
        except requests.RequestException as exc:
            print(f"timetable download failed, using the cached copy: {exc}")
        try:
            self.tt = Timetable(GTFS_PATH, day)
            self.tt.write()
            print(f"timetable for {day}: {sum(map(len, self.tt.due.values()))} stop times")
        except (OSError, KeyError, ValueError, zipfile.BadZipFile) as exc:
            print(f"timetable unavailable: {exc}")
            self.tt, self.retry_at = None, now + RETRY_S
        return self.tt

    def reload_stops(self) -> None:
        """After a crosswalk rebuild: stop names may have moved."""
        self.tt = None
        self.retry_at = 0

    def update(self, session: requests.Session, rows: list[dict], now: int) -> None:
        tt = self.timetable(session, now)
        for r in rows:
            r["trip_id"] = live_trip(tt, r) if tt else None
        if tt:
            append_arrivals(self.arrivals.update(tt, rows))
