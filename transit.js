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

// --- Live and replay ----------------------------------------------------------
// The map's timeline, in #bar: play/pause, a scrubber across the viewed
// day's frames, the clock, replay speed, LIVE, and a day picker. Live is
// data/latest.json every POLL_MS; replaying, data/replay/<day>.jsonl (one
// frame per FRAME_S, written by the poller; the files map.html replays).
// `onShow(snap)` gets { t, day, vehicles } for whatever moment is showing,
// vehicles shaped like latest.json's.
const FRAME_S = 30, SPEEDS = [10, 60, 300];
// Frames from before 2026-09-25 stop at unchanged_polls: no headsign or next
// stop, so `locate` can only park those buses at a nearby stop.
const fromFrame = (f, day) => ({ t: f.t, day, vehicles: f.v.map(a => ({
  vehicle_id: a[0], route_id: a[1], lat: a[2], lon: a[3], bearing: a[4], delay_seconds: a[5],
  delay_capped: a[6], occupancy_pct: a[7], unchanged_polls: a[8], destination: a[9],
  next_stop_name: a[10], equipment_no: a[11] })) });

function timeline(onShow) {
  $("bar").innerHTML = `<button id="play" title="play / pause">&#9654;</button>
    <input id="scrub" type="range" min="0" max="0" value="0" aria-label="time of day">
    <div id="clock"><i></i><span>–</span></div>
    <button id="speed" title="replay speed">60&times;</button>
    <button id="live" title="back to live">LIVE</button>
    <input id="day" type="date" aria-label="day">`;
  // frames: the viewed day's snapshots, oldest first. cursor: index into
  // frames while replaying, or null when live. serverDay: the poller's
  // service day (from latest.json), which names today's replay file.
  let frames = [], cursor = null, live = null, serverDay = null, playing = false, speed = 60, ticker = null;

  function show() {
    const s = cursor == null ? live : frames[cursor];
    $("clock").querySelector("span").textContent = s ? hm(s.t) : "–";
    $("clock").classList.toggle("live", cursor == null);
    $("clock").classList.toggle("stale", cursor == null && !!s && Date.now() / 1000 - s.t > 90);
    $("play").innerHTML = playing ? "&#10074;&#10074;" : "&#9654;";
    $("play").classList.toggle("on", playing);
    $("live").classList.toggle("on", cursor == null);
    $("scrub").max = Math.max(frames.length - 1, 0);
    $("scrub").value = cursor == null ? frames.length - 1 : cursor;
    if (s) onShow(s);
  }
  // The file can be several MB by evening; live doesn't wait for it.
  async function loadDay(day) {
    const r = await fetch(`data/replay/${day}.jsonl`, { cache: "no-store" }).catch(() => null);
    const loaded = r?.ok ? (await r.text()).split("\n").filter(Boolean).map(l => fromFrame(JSON.parse(l), day)) : [];
    if ($("day").value !== day) return;          // another day was picked meanwhile
    frames = loaded;
  }
  function setCursor(i) {
    cursor = frames.length ? Math.max(0, Math.min(i, frames.length - 1)) : null;
    show();
  }
  function goLive() {
    playing = false; clearInterval(ticker); cursor = null;
    if ($("day").value !== serverDay) { $("day").value = serverDay; loadDay(serverDay).then(show); }
    show();
  }
  function play(on) {
    playing = on; clearInterval(ticker);
    if (!on) return show();
    if (cursor == null) cursor = Math.max(frames.length - 1, 0);
    ticker = setInterval(() => {
      if (cursor >= frames.length - 1) return $("day").value === serverDay ? goLive() : play(false);
      setCursor(cursor + 1);
    }, FRAME_S * 1000 / speed);
    show();
  }
  $("play").onclick = () => play(!playing);
  $("scrub").oninput = (e) => setCursor(+e.target.value);
  $("speed").onclick = () => { speed = SPEEDS[(SPEEDS.indexOf(speed) + 1) % SPEEDS.length];
    $("speed").innerHTML = speed + "&times;"; if (playing) play(true); };
  $("live").onclick = goLive;
  $("day").onchange = async (e) => { playing = false; clearInterval(ticker);
    await loadDay(e.target.value); cursor = frames.length ? 0 : null; show(); };

  const tick = async () => {
    const j = await getJSON("data/latest.json");
    if (!j) return;
    const day = j.day ?? new Date(j.fetched_at * 1000).toLocaleDateString("en-CA", { timeZone: TZ });
    live = { t: j.fetched_at, day, vehicles: j.vehicles };
    // First load, or the service day rolled over while watching live.
    if (day !== serverDay && (serverDay == null || cursor == null)) {
      serverDay = day; $("day").value = day; frames = [];
      loadDay(day).then(() => { if (cursor == null) show(); });
    }
    // Extend today's timeline at the file's cadence so the scrubber reaches now.
    if ($("day").value === serverDay && (!frames.length || live.t - frames.at(-1).t >= FRAME_S - 5)) frames.push(live);
    if (cursor == null) show(); else $("scrub").max = Math.max(frames.length - 1, 0);
  };
  tick();
  setInterval(tick, POLL_MS);
}
