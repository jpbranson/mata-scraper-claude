// Shared by strips.html and schematic.html: delay tiers (same as map.html),
// live data, and placing a live bus along its route's stop pattern. Patterns
// come from the day's data/schedule/<day>/<route>.json (schedule.py): per
// headsign, stops in order as [code, name, lat, lon, seconds from first stop,
// timepoint].
const TZ = "America/Chicago", POLL_MS = 10000, GHOST_POLLS = 30;
const $ = (id) => document.getElementById(id);
const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const esc = (x) => String(x ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
const hm = (t) => new Date(t * 1000).toLocaleTimeString([], { hour: "numeric", minute: "2-digit", timeZone: TZ });
const TROLLEY = new Set(["100"]);

function tier(v) {
  const d = v.delay_seconds;
  if (d == null) return "ontime";
  if (v.delay_capped) return d > 0 ? "late20" : d < 0 ? "early" : "ontime";
  if (d >= 1200) return "late20";
  if (d >= 600) return "late10";
  if (d >= 300) return "late5";
  if (d <= -60) return "early";
  return "ontime";
}
function delayText(v) {
  const d = v.delay_seconds;
  if (v.delay_raw) return v.delay_raw;
  if (d == null) return "no delay data";
  if (v.delay_capped) return d < 0 ? "1h+ early" : "1h+ late";
  const m = Math.round(Math.abs(d) / 60);
  return m === 0 ? "on time" : `${m} min ${d < 0 ? "early" : "late"}`;
}

async function getJSON(url, cache = "no-store") {
  try { const r = await fetch(url, { cache }); return r.ok ? await r.json() : null; }
  catch { return null; }
}
// Route files change once a day; keep them for the page's life.
const routeFiles = {};
const routeFile = (day, route) => routeFiles[day + "/" + route] ??= getJSON(`data/schedule/${day}/${route}.json`);

function distM(lat1, lon1, lat2, lon2) {
  const x = (lon2 - lon1) * Math.PI / 180 * Math.cos((lat1 + lat2) / 2 * Math.PI / 180);
  return 6371000 * Math.hypot(x, (lat2 - lat1) * Math.PI / 180);
}

// Where a live bus is along one of its route's patterns: { pat, pos } with
// pos in stop-index units (2.4 = 40% of the way from stop 2 to stop 3), or
// null if it can't be placed. The pattern is the one for its headsign; the
// stop is its next stop by name (the nearest, if the name repeats), and the
// fraction is how far it is from the stop before, by distance.
// If its headsign's pattern lacks that stop (a branch trip), the route's
// other patterns are tried.
function locate(v, patterns) {
  const head = (v.destination ?? "").trim(), all = patterns.map((_, i) => i);
  const same = all.filter(i => patterns[i].head === head);
  const nearest = (byName) => {
    let best = null;
    for (const i of (same.length ? same : all)) scan(i);
    if (!best && same.length) for (const i of all) if (!same.includes(i)) scan(i);
    return best;
    function scan(i) { patterns[i].stops.forEach((s, k) => {
      if (byName && s[1] !== v.next_stop_name) return;
      if (s[2] == null) return;
      const d = distM(v.lat, v.lon, s[2], s[3]);
      if (!best || d < best.d) best = { pat: i, k, d };
    }); }
  };
  const byName = v.next_stop_name ? nearest(true) : null;
  if (!byName) {
    // No usable next stop: park it at the nearest stop, if it's close.
    const b = nearest(false);
    return b && b.d < 400 ? { pat: b.pat, pos: b.k } : null;
  }
  const st = patterns[byName.pat].stops, k = byName.k;
  if (k === 0) return { pat: byName.pat, pos: 0 };
  const d1 = distM(v.lat, v.lon, st[k - 1][2], st[k - 1][3]);
  return { pat: byName.pat, pos: k - 1 + d1 / ((d1 + byName.d) || 1) };
}
// Scheduled seconds from the pattern's first stop at a fractional position.
function offsetAt(pattern, pos) {
  const st = pattern.stops, i = Math.min(Math.floor(pos), st.length - 1), f = pos - i;
  return i + 1 < st.length ? st[i][4] + f * (st[i + 1][4] - st[i][4]) : st[i][4];
}

// Poll data/latest.json every POLL_MS; `onData(latest)` on each success.
// Returns nothing; marks #clock stale (red dot) when the snapshot is > 90 s old.
function followLive(onData) {
  const tick = async () => {
    const j = await getJSON("data/latest.json");
    if (!j) return;
    j.day ??= new Date(j.fetched_at * 1000).toLocaleDateString("en-CA", { timeZone: TZ });
    const c = $("clock");
    if (c) {
      c.querySelector("span").textContent = hm(j.fetched_at);
      c.classList.toggle("stale", Date.now() / 1000 - j.fetched_at > 90);
    }
    await onData(j);
  };
  tick();
  setInterval(tick, POLL_MS);
}
