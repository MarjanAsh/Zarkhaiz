// OutputDM founder reel: 1080x1920, every frame drawn by render(t) (lemo-opuscar page contract).
const TL = await (await fetch('timeline.json')).json();
const stage = document.getElementById('stage');

// ---------- maths ----------
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const seg = (t, a, b) => clamp((t - a) / (b - a));
const eo = x => 1 - Math.pow(1 - x, 3);
const eio = x => x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
const back = (x, s = 1.7) => 1 + (s + 1) * Math.pow(x - 1, 3) + s * Math.pow(x - 1, 2);

// ---------- timeline lookups ----------
const S = n => TL.scenes.find(s => s.name === n);
const L = id => TL.lines.find(l => l.id === id);
const norm = w => w.toLowerCase().replace(/[^a-z0-9-]/g, '');
function W(id, needle, which = 't0') {
  const w = TL.words.find(x => x.line === id && norm(x.w).startsWith(needle.toLowerCase()));
  if (!w) throw new Error(`word ${needle} not in ${id}`);
  return w[which];
}

// ---------- dom helpers ----------
function el(html, style = {}, parent = stage) {
  const d = document.createElement('div');
  d.innerHTML = html.trim();
  const n = d.firstElementChild;
  Object.assign(n.style, style);
  parent.appendChild(n);
  return n;
}
const px = v => v + 'px';
const TICK = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5" fill="none" stroke="#1a120b" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const CROSS = '<svg viewBox="0 0 24 24"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="#fff" stroke-width="3.2" stroke-linecap="round"/></svg>';
const WA = '<svg viewBox="0 0 32 32" width="50" height="50"><path fill="#fff" d="M16 3.2A12.7 12.7 0 0 0 5.1 22.4L3.4 28.6l6.4-1.7A12.7 12.7 0 1 0 16 3.2zm0 23.1a10.4 10.4 0 0 1-5.3-1.5l-.4-.2-3.8 1 1-3.7-.2-.4A10.4 10.4 0 1 1 16 26.3zm5.7-7.8c-.3-.2-1.8-.9-2.1-1s-.5-.2-.7.2-.8 1-.9 1.2-.3.2-.6.1a8.5 8.5 0 0 1-4.2-3.7c-.3-.5.3-.5.9-1.6a.6.6 0 0 0 0-.5c-.1-.2-.7-1.7-1-2.3s-.5-.5-.7-.5h-.6a1.1 1.1 0 0 0-.8.4 3.4 3.4 0 0 0-1.1 2.6 5.9 5.9 0 0 0 1.3 3.1 13.5 13.5 0 0 0 5.2 4.6c1.9.8 2.7.9 3.6.7a3.1 3.1 0 0 0 2-1.4 2.5 2.5 0 0 0 .2-1.4c-.1-.2-.3-.3-.6-.4z"/></svg>';

// ---------- animated items ----------
const items = [];   // {n, tin, tout, fx, d, x, y}
const EV = [];
function add(n, tin, tout, fx = 'up', opt = {}) {
  const it = { n, tin, tout, fx, d: opt.d ?? .5, sfx: opt.sfx ?? null };
  items.push(it);
  if (it.sfx) EV.push({ t: +(tin + (opt.sfxAt ?? 0)).toFixed(3), type: it.sfx });
  return it;
}
function check(parent, tOn, style = {}) {
  const c = el(`<div class="chk"><div class="fill"></div>${TICK}</div>`, style, parent);
  c._on = tOn; checks.push(c); EV.push({ t: +tOn.toFixed(3), type: 'tick' });
  return c;
}
const checks = [];

// ---------- background ----------
const blobs = [
  el('<div class="blob"></div>', { width: '760px', height: '760px', background: 'rgba(246,181,58,.17)' }),
  el('<div class="blob"></div>', { width: '640px', height: '640px', background: 'rgba(227,52,58,.13)' }),
  el('<div class="blob"></div>', { width: '700px', height: '700px', background: 'rgba(240,138,36,.12)' }),
];

// ---------- 3D floor: a gold grid in perspective that the camera slowly dollies over ----------
const floorWrap = el('<div id="floorwrap"><div id="floor"></div></div>');
const floor = floorWrap.firstElementChild;
el('<div id="horizon"></div>');

// ---------- header + progress ----------
const SCN = ['hook', 'intro', 'since', 'leaks', 'system', 'only', 'cta'];
const SCN_LABEL = { hook: '01 · the problem', intro: '02 · founder', since: '03 · since 2018', leaks: '04 · growth leaks', system: '05 · one system', only: '06 · only what you need', cta: '07 · growth review' };
const hdr = el('<div id="hdr"><div class="l lbl">OutputDM</div><div class="r"></div><div class="rule"></div></div>');
const hdrR = hdr.querySelector('.r');
const dots = el('<div id="dots"></div>');
const dotEls = [], lineEls = [];
SCN.forEach((s, i) => {
  const x = i * (952 - 22) / (SCN.length - 1);
  if (i) { const ln = el('<div class="dline"><div class="f"></div></div>', { left: px(x - (930 / 6) + 22), width: px(930 / 6 - 22) }, dots); lineEls.push(ln); }
  dotEls.push(el('<div class="dot"></div>', { left: px(x) }, dots));
});

// ---------- headings ----------
function heading(h1, sub, tH, tSub, tout, top = 262) {
  const h = el(`<div class="abs h1">${h1}</div>`, { left: '64px', top: px(top) });
  add(h, tH, tout, 'blur', { d: .6 });
  let s = null;
  if (sub) {
    const lines = (h1.match(/<br>/g) || []).length + 1;
    s = el(`<div class="abs sub">${sub}</div>`, { left: '64px', top: px(top + lines * 94 + 12) });
    add(s, tSub, tout, 'blur', { d: .5 });
  }
  return { h, s };
}

// ---------- hero: one animated character (v015) ----------
// Built by mascot/anim (see its README): ONE master body. Head, torso and legs are the same pixels in every frame.
// Each arm is its own half of the body canvas and plays clips made of GPT keyframes (rest -> mid -> end, edits of
// the master through the ChatGPT bridge) with FILM in-between frames, so the arm really travels; nothing dissolves
// between poses. The head (v017) is a 30 fps sequence made by mascot/anim/tools/build_face.py: the master's own face
// re-posed by LivePortrait (mouth follows the voice loudness, expression per line, blinks, small nods). In each frame
// the master's head is removed from the body (erase mask) and the head patch is added in its place.
const ANIM = await (await fetch('assets/anim/anim.json')).json();
const FACE = await (await fetch('assets/anim/face.json')).json();
const FACE_IMGS = {};
for (const f of new Set([FACE.erase, ...FACE.frames])) { const im = new Image(); im.src = `assets/anim/${f}`; FACE_IMGS[f] = im; }
const PW = 820, PH = 1240, PFEET = 1215, BASE = 1392, HERO_H = 1090, PAD = 40;
const smooth = x => x * x * (3 - 2 * x);
const smoother = x => x * x * x * (x * (x * 6 - 15) + 10);
const ANIM_IMGS = [];
const TRACKS = [];   // the scenes only say where he stands: [time, (unused pose), centre-x]
function hero(scene, h, track, tin, tout) { TRACKS.push({ scene, track, tin, tout }); }
function buildHero(ARMS) {
  const h = HERO_H, w = Math.round(h * PW / PH), k = w / PW;
  const a = el(`<div class="abs hero" style="left:0;width:${w}px;height:${h}px"></div>`, { top: px(BASE - h * PFEET / PH) });
  const mv = el('<div class="hmv"></div>', {}, a);
  el('<div class="halo"></div>', {}, mv); el('<div class="shadow"></div>', {}, mv);
  const turn = el('<div class="hturn"></div>', {}, mv);
  const body = el('<div class="hbody"></div>', {}, turn);
  // where he stands: the first key of each scene (he glides there while the old scene fades) and every key that
  // moves him aside
  const marks = [];
  TRACKS.forEach(({ track, tin }, si) => track.map(([t, , x]) => ({ t: Math.max(t, tin), cx: x })).sort((p, q) => p.t - q.t)
    .forEach((key, i) => { const last = marks[marks.length - 1]; if (i === 0) marks.push({ t: si > 0 ? tin - .45 : key.t, cx: key.cx }); else if (Math.abs(key.cx - last.cx) > 120) marks.push(key); }));
  a._marks = marks.map(m => ({ t: m.t, x: m.cx - w / 2 }));
  // arms: per side a list of clips [start, duration, frames]
  a._side = {};
  for (const s of ['L', 'R']) {
    const [x0, x1] = ANIM.half[s];
    const clips = [], files = new Set([ANIM.states[s].rest]);
    let cur = 'rest', free = -9;
    for (const [t, state] of ARMS[s].slice().sort((p, q) => p[0] - q[0])) {
      if (state === cur) continue;
      const fr = ANIM.trans[`${s}:${cur}>${state}`];
      if (!fr) throw new Error(`no arm clip ${s}:${cur}>${state}`);
      const d = Math.min(1.05, .36 + .0125 * fr.length), t0 = Math.max(t, free + .12);   // longer clips take longer; never cut a move short
      clips.push({ t0, d, fr }); fr.forEach(f => files.add(f)); cur = state; free = t0 + d;
    }
    // the two neighbouring frames are mixed on a canvas ('lighter' adds the two weighted layers: a true cross-fade)
    const cv = document.createElement('canvas'); cv.width = x1 - x0; cv.height = PH;
    const imgs = {};
    for (const f of files) { const im = new Image(); im.src = `assets/anim/${f}`; imgs[f] = im; ANIM_IMGS.push(im); }
    a._side[s] = { clips, imgs, ctx: cv.getContext('2d'), ph: s === 'L' ? 0 : 2.1, x0 };
  }
  // v018: the two halves and the head are joined on one pose canvas, lit for the stage, then drawn row by row to
  // the visible canvas with a soft bend (weight shift, breathing): the figure moves like a body, not like a card
  const mk = (cw, ch) => { const c = document.createElement('canvas'); c.width = cw; c.height = ch; return c.getContext('2d'); };
  a._pose = mk(PW, PH); a._tmp = mk(PW, PH); a._rim = mk(PW, PH);
  const out = el(`<canvas width="${PW + 2 * PAD}" height="${PH}" style="position:absolute;left:${(-PAD * k).toFixed(2)}px;top:0;width:${((PW + 2 * PAD) * k).toFixed(2)}px;height:${h}px;-webkit-box-reflect:below ${(-2 * (PH - PFEET) * k + 4).toFixed(1)}px linear-gradient(transparent 82%, rgba(0,0,0,.20))"></canvas>`, {}, body);
  a._out = out.getContext('2d');
  const words = TL.words.slice().sort((p, q) => p.t0 - q.t0);
  a._mv = mv; a._turn = turn; a._body = body; a._w = w; a._speech = words;
  add(a, -.95, TL.dur, 'slide', { d: .9 });
  return a;
}
// giant outlined word behind the scene, drifting sideways
function ghost(text, top, tin, tout, size = 330, dir = 1) {
  const g = el(`<div class="abs ghost" style="font-size:${size}px">${text}</div>`, { left: '0px', top: px(top) });
  g._drift = dir; add(g, tin, tout, 'fade', { d: .8 }); return g;
}
// thick bar that fills (or drains) between two times
const bars = [], wires = [];
function bar(parent, t0, t1, from, to, color, style = {}) {
  const b = el(`<div class="bar"><div style="background:${color}"></div></div>`, style, parent);
  b._bar = [t0, t1, from, to]; bars.push(b); return b;
}

// ================= SCENES =================
const sc = Object.fromEntries(SCN.map(n => [n, S(n)]));

// 1 · hook
{
  const { t0, t1 } = sc.hook;
  heading('Marketing pe<br>paisa lag raha hai,', 'lekin customers nahi aa rahe?', -.6, W('l01', 'lekin') - .1, t1);   // the hook is on screen at frame 0
  ghost('PAISA?', 690, t0 + .2, t1, 300, -1);
  const rows = [
    ['Ads', 'chal rahe hain', W('l01', 'paisa'), true],
    ['Posts', 'lag rahi hain', W('l01', 'raha'), true],
    ['Customers', 'nahi aa rahe', W('l01', 'customers'), false],
  ];
  rows.forEach(([a, b, tt, ok], i) => {
    const c = el(`<div class="abs card big row" style="width:540px"></div>`, { left: '48px', top: px(590 + i * 178) });
    if (ok) check(c, tt + .25);
    else el(`<div class="chk" style="border-color:transparent;background:var(--red)">${CROSS}</div>`, {}, c);
    el(`<div><div class="t1">${a}</div><div class="t2">${b}</div></div>`, {}, c);
    add(c, tt - .15, t1, ok ? 'right' : 'shake', { sfx: ok ? 'pop' : 'thump' });
  });
  // spend goes up, customers stay flat
  const g = el('<div class="abs card big" style="width:540px;padding:26px 32px"></div>', { left: '48px', top: '1130px' });
  el('<div class="row" style="justify-content:space-between"><div class="lbl">Ad spend</div><div class="lbl" style="color:var(--red)">Customers</div></div>', {}, g);
  bar(g, W('l01', 'paisa'), W('l01', 'lekin'), .08, 1, 'linear-gradient(90deg,var(--gold2),var(--gold))', { marginTop: '16px' });
  bar(g, W('l01', 'customers'), t1, .1, .14, 'var(--red)', { marginTop: '14px' });
  add(g, W('l01', 'lag') - .1, t1, 'up', { sfx: 'pop' });
  hero('hook', 1040, [[0, 'confident', 830], [W('l01', 'paisa') - .1, 'presenting', 820], [W('l01', 'raha') - .05, 'explain', 820], [W('l01', 'lekin') - .1, 'thinking', 835], [W('l01', 'customers') - .08, 'surprised', 825], [W('l01', 'aa') - .05, 'oh_no', 835]], t0 + .05, t1, 'walkR');
}

// 2 · intro
{
  const { t0, t1 } = sc.intro;
  heading('Assalam o Alaikum!', 'Main Zarkhaiz', t0 + .05, W('l02', 'main') - .1, t1);
  const sq = el('<svg class="abs squig" width="380" height="40" viewBox="0 0 380 40"><path d="M6 24 C 60 6, 110 38, 170 20 S 280 6, 374 22"/></svg>', { left: '64px', top: px(262 + 94 + 12 + 66) });
  sq._draw = [W('l02', 'zarkhaiz'), t1];
  add(sq, t0 + .05, t1, 'fade');
  ghost('ZARKHAIZ', 560, t0 + .1, t1, 300, 1);
  // he turns round to greet, then steps aside and presents the company card
  hero('intro', 1120, [[0, 'peace', 540], [W('l02', 'main') - .1, 'confident', 540], [W('l02', 'zarkhaiz') - .05, 'presenting', 250, true]], t0 + .02, t1, 'up');
  const c = el(`<div class="abs card big" style="padding:34px 36px;width:580px"></div>`, { left: '452px', top: '760px' });
  el('<img src="assets/logo_icon.png" style="width:170px;display:block;margin-bottom:14px">', {}, c);
  el('<div class="lbl" style="margin-bottom:8px;font-size:28px">Founder</div>', {}, c);
  el('<div style="font-family:Playfair;font-weight:900;font-size:96px;line-height:1">OutputDM</div>', {}, c);
  el('<div class="t2" style="margin-top:12px;font-size:30px">Output Digital Marketing Pvt Ltd</div>', {}, c);
  add(c, W('l02', 'outputdm') - .1, t1, 'pop', { sfx: 'ding' });
}

// 3 · since
{
  const { t0, t1 } = sc.since;
  heading('2018 se', 'Lahore se, Pakistan + UAE', t0 + .05, W('l03', 'lahore') - .1, t1);
  ghost('2018', 520, t0 + .1, t1, 420, -1);
  const places = [['Lahore', W('l03', 'lahore')], ['Pakistan', W('l03', 'pakistan')], ['UAE', W('l03', 'uae')]];
  places.forEach(([p, tt], i) => {
    const c = el(`<div class="abs chip bigchip"><span class="pin"></span>${p}</div>`, { left: px(64 + i * 44), top: px(560 + i * 138) });
    add(c, tt - .15, t1, 'pop', { sfx: 'pop' });
  });
  const vline = el('<div class="abs" style="width:5px;background:linear-gradient(var(--gold),rgba(246,181,58,.1));border-radius:3px"></div>', { left: '40px', top: '600px', height: '0px' });
  vline._grow = [W('l03', 'lahore'), W('l03', 'uae') + .2, 320];
  add(vline, W('l03', 'lahore'), t1, 'fade');
  const brands = ['Dajaj Broast', 'Nabi Cafe', 'Sadaqat Properties', 'Cheesy Chicken', 'Tashkeel Travels', 'Misbah Noor Medical Complex', 'Dabbay Wala', 'Dua Pixels', 'ABS Developers', 'Sami Motors', 'Guftagu Restaurant', 'Elite Health Cart'];
  const tb = W('l03', 'businesses') - .2;
  const lab = el('<div class="abs lbl" style="font-size:30px">Brands we have worked with</div>', { left: '64px', top: '1010px' });
  add(lab, tb, t1, 'up');
  [0, 1, 2].forEach(r => {
    const m = el('<div class="marq"></div>', { top: px(1064 + r * 104) });
    const list = brands.slice(r * 4).concat(brands.slice(0, r * 4));
    m.innerHTML = list.concat(list).map(b => `<span class="chip" style="font-size:40px;padding:16px 32px;margin-right:18px;background:rgba(64,50,38,.95);border-color:rgba(246,181,58,.45);color:#fff8ee">${b}</span>`).join('');
    m._marq = { dir: r % 2 ? 1 : -1, speed: 80 };
    add(m, tb + r * .12, t1, 'up');
  });
  // looks across at the places, then turns to camera in front of the brand wall
  hero('since', 1090, [[0, 'idea', 850], [W('l03', 'lahore') - .1, 'point_screen', 830, true], [W('l03', 'pakistan') - .1, 'presenting', 830], [W('l03', 'uae') - .1, 'side_point', 840], [W('l03', 'businesses') - .1, 'laugh', 830], [W('l03', 'kaam') - .1, 'confident', 820], [W('l03', 'hain') - .05, 'arms_crossed', 820]], t0 + .05, t1, 'walkR');
}

// 4 · leaks
{
  const { t0, t1 } = sc.leaks;
  heading('Teen jagah', 'customers kho jaate hain', t0 + .05, W('l04', 'customers') - .1, t1);
  ghost('LEAKS', 640, t0 + .1, t1, 330, 1);
  const tC = L('l05').t0 - .15;
  const three = el('<div class="abs" style="font-family:Playfair;font-weight:900;font-size:560px;line-height:1;color:var(--gold);text-shadow:0 30px 80px rgba(0,0,0,.6)">3</div>', { left: '120px', top: '520px' });
  add(three, W('l04', 'teen') - .1, tC + .1, 'pop', { sfx: 'thump' });
  const threeL = el('<div class="abs t1" style="font-size:50px;width:480px">jagah customers<br>kho jaate hain</div>', { left: '84px', top: '1120px' });
  add(threeL, W('l04', 'jagah'), tC + .1, 'up');
  const cards = [
    ['01', 'Visibility', 'Log dhoond nahi paate', W('l05', 'dhoond')],
    ['02', 'Conversion', 'Aa kar rukte nahi', W('l05', 'rukte')],
    ['03', 'Follow-up', 'Reply late, lead gone', W('l05', 'follow-up')],
  ];
  cards.forEach(([n, a, b, tt], i) => {
    const c = el(`<div class="abs card big" style="width:560px;padding:28px 30px"></div>`, { left: '40px', top: px(560 + i * 258) });
    const r = el('<div class="row" style="gap:16px"></div>', {}, c);
    el(`<div class="num">${n}</div>`, {}, r);
    el(`<div style="flex:1"><div class="t1">${a}</div><div class="t2">${b}</div></div>`, {}, r);
    bar(c, tt + .1, tt + 1.1, 1, .18, 'var(--red)', { marginTop: '18px' });   // the leak: the bar drains
    add(c, tt - .35, t1, 'right', { sfx: 'pop' });
  });
  hero('leaks', 1090, [[0, 'thinking', 850], [W('l04', 'teen') - .1, 'idea', 845], [W('l04', 'kho') - .1, 'oh_no', 840], [L('l05').t0 - .1, 'explain', 830], [W('l05', 'dhoond') - .1, 'thinking', 845], [W('l05', 'rukte') - .1, 'surprised', 840], [W('l05', 'follow-up') - .1, 'oh_no', 840], [W('l05', 'hota') - .1, 'panic', 835]], t0 + .1, t1, 'walkR');
}

// 5 · system
{
  const { t0, t1 } = sc.system;
  heading('Sab kuch,', 'ek connected system mein', t0 + .05, W('l06', 'system') - .2, t1);
  ghost('SYSTEM', 620, t0 + .1, t1, 300, -1);
  const svc = [['Content', 'posts, reels, design', 'content'], ['Ads', 'Meta & Google', 'ads'], ['Website', '+ Shopify stores', 'website'], ['SEO', 'local visibility', 'seo'], ['Automation', 'lead follow-up', 'automation']];
  const list = el('<div class="abs card big" style="padding:10px 32px;width:560px"></div>', { left: '480px', top: '480px' });
  add(list, t0 + .25, t1, 'pop', { d: .5 });
  const wire = el('<div style="position:absolute;left:63px;top:76px;width:5px;height:0;background:var(--gold);border-radius:3px"></div>', {}, list);
  wire._wire = [W('l06', 'content'), W('l06', 'automation') + .1, 536]; wires.push(wire);
  svc.forEach(([a, b, k], i) => {
    const tt = W('l06', k);
    const r = el(`<div class="row" style="padding:13px 0;position:relative"></div>`, {}, list);
    check(r, tt + .05);
    el(`<div><div class="t1" style="font-size:46px">${a}</div><div class="t2" style="font-size:29px">${b}</div></div>`, {}, r);
  });
  const badge = el(`<div class="abs card big row" style="padding:24px 32px;width:640px;gap:24px;border-color:rgba(246,181,58,.75)"><img src="assets/logo_icon.png" style="width:100px"><div><div class="lbl">OutputDM</div><div class="t1" style="font-size:46px;white-space:nowrap">1 connected system</div></div></div>`, { left: '400px', top: '1196px' });
  add(badge, W('l06', 'system') - .1, t1, 'pop', { sfx: 'ding' });
  hero('system', 1090, [[0, 'presenting', 230, true], [W('l06', 'content') - .1, 'point_screen', 230], [W('l06', 'ads') - .05, 'explain', 240, true], [W('l06', 'website') - .05, 'point_screen', 230], [W('l06', 'seo') - .05, 'presenting', 240, true], [W('l06', 'automation') - .05, 'idea', 235], [W('l06', 'system') - .1, 'victory', 240], [W('l06', 'jodte') - .05, 'triumph', 245]], t0 + .1, t1, 'walkL');
}

// 6 · only what you need
{
  const { t0, t1 } = sc.only;
  heading('Sirf wohi', 'jo aap ke business ko chahiye', t0 + .05, W('l07', 'jo') - .1, t1);
  ghost('SIRF', 640, t0 + .1, t1, 380, 1);
  const opts = [['Social media', 1], ['Paid ads', 1], ['Shopify store', 0], ['Every service', 0], ['Lead follow-up', 1]];
  const c = el('<div class="abs card big" style="padding:30px 34px;width:560px"></div>', { left: '40px', top: '560px' });
  el('<div class="lbl" style="margin-bottom:12px;font-size:28px">Aap ka plan</div>', {}, c);
  add(c, t0 + .2, t1, 'pop', { sfx: 'pop' });
  const tSel = W('l07', 'sirf');
  opts.forEach(([a, need], i) => {
    const r = el(`<div class="row" style="padding:17px 0;position:relative"></div>`, {}, c);
    if (need) check(r, tSel + .15 + i * .12);
    else el(`<div class="chk" style="border-color:rgba(185,171,156,.35)"></div>`, {}, r);
    const tx = el(`<div class="t1" style="font-size:46px;position:relative">${a}</div>`, {}, r);
    if (!need) { const s = el('<div class="strike"></div>', { width: '0px' }, tx); s._strike = [tSel + .2 + i * .1, tx]; tx._dim = tSel + .2; }
  });
  hero('only', 1090, [[0, 'thinking', 850], [W('l07', 'sirf') - .1, 'point_screen', 835, true], [W('l07', 'jo') - .05, 'presenting', 830], [W('l07', 'business') - .05, 'point_camera', 845], [W('l07', 'waqai') - .05, 'confident', 840], [W('l07', 'chahiye') - .05, 'arms_crossed', 840]], t0 + .1, t1, 'walkR');
}

// 7 · CTA
{
  const { t0, t1 } = sc.cta;
  heading('Free Digital<br>Growth Review', 'abhi WhatsApp karein', t0 + .05, W('l08', 'abhi') - .15, t1 + 1);
  ghost('FREE', 700, t0 + .1, t1 + 1, 380, -1);
  const wa = el(`<div class="abs card big row" style="padding:30px 32px;width:600px;gap:24px;border-color:rgba(37,211,102,.6)"><div class="wa">${WA}</div><div><div class="lbl" style="color:#7be3a2">WhatsApp</div><div style="font-family:Jost;font-weight:800;font-size:54px;white-space:nowrap">0344 444 1724</div></div></div>`, { left: '40px', top: '940px' });
  wa._pulse = W('l08', 'whatsapp');
  add(wa, W('l08', 'whatsapp') - .25, t1 + 1, 'pop', { sfx: 'ding' });
  const lg = el('<img class="abs" src="assets/logo.png" style="width:330px">', { left: '70px', top: '560px' });
  add(lg, W('l09', 'outputdm') - .2, t1 + 1, 'pop', { sfx: 'pop' });
  const web = el('<div class="abs chip bigchip">outputdm.com</div>', { left: '56px', top: '1130px' });
  add(web, W('l09', 'dot'), t1 + 1, 'up');
  const tf = L('l09').t1 + .55;
  const fol = el(`<div class="abs chip bigchip" style="padding:16px 20px 16px 34px;gap:24px">@outputdm <span class="btn" style="background:var(--gold);color:#1a120b">Follow</span></div>`, { left: '0px', top: '1404px' });
  fol._follow = [tf, tf + 1.15];
  add(fol, tf, t1 + 1, 'pop', { sfx: 'pop' });
  EV.push({ t: +(tf + 1.15).toFixed(3), type: 'click' });
  hero('cta', 1040, [[0, 'idea', 840], [W('l08', 'growth') - .05, 'side_point', 830], [W('l08', 'whatsapp') - .15, 'point_screen', 820, true], [W('l08', 'karein') - .05, 'point_camera', 830], [W('l09', 'outputdm') - .15, 'presenting', 830], [W('l09', 'com') - .05, 'peace', 835], [L('l09').t1 + .5, 'laugh', 840], [L('l09').t1 + 1.6, 'victory', 840]], t0 + .1, t1 + 1, 'walkR');
}

// the character's storyboard: what each arm does on which word ("L" = the arm on the viewer's left)
const HERO = buildHero({
  L: [[W('l01', 'paisa') - .15, 'present'], [W('l01', 'lekin') - .15, 'explain'],
      [sc.intro.t0 - .3, 'wave'], [W('l02', 'main') - .05, 'rest'],
      [W('l03', 'lahore') - .2, 'present'], [W('l03', 'businesses') - .15, 'explain'],
      [sc.leaks.t0 - .15, 'rest'], [W('l04', 'teen') - .15, 'explain'], [L('l05').t0 - .2, 'present'], [W('l05', 'follow-up') + .2, 'explain'],
      [sc.system.t0 - .45, 'rest'], [W('l06', 'system') - .2, 'explain'],
      [sc.only.t0 - .3, 'rest'], [W('l07', 'sirf') - .15, 'present'], [W('l07', 'business') - .1, 'explain'],
      [W('l08', 'whatsapp') - .2, 'present'], [L('l09').t0 - .1, 'explain'], [L('l09').t1 + .4, 'wave']],
  R: [[W('l01', 'lekin') - .15, 'explain'], [sc.intro.t0 - .3, 'rest'],
      [W('l02', 'zarkhaiz') + .3, 'present'], [sc.since.t0 - .4, 'rest'], [W('l03', 'businesses') - .15, 'explain'],
      [sc.leaks.t0 - .15, 'rest'], [W('l04', 'teen') - .15, 'explain'], [L('l05').t0 - .2, 'rest'], [W('l05', 'follow-up') + .2, 'explain'],
      [sc.system.t0 - .45, 'rest'], [W('l06', 'content') - .25, 'present'], [W('l06', 'system') - .2, 'explain'],
      [sc.only.t0 - .3, 'rest'], [W('l07', 'business') - .1, 'explain'],
      [W('l08', 'whatsapp') - .2, 'rest'], [L('l09').t0 - .1, 'explain'], [L('l09').t1 + .4, 'rest']],
});

// ---------- captions + watermark ----------
const cap = el('<div id="cap"></div>');
const wm = el('<div id="wm">@outputdm</div>');
let capKey = '';

// ================= RENDER =================
const LINGER = .26;
function fxStyle(it, t) {
  // items outlive their scene by a quarter second, so one scene dissolves into the next and the screen never empties
  const pin = seg(t, it.tin, it.tin + it.d), pout = seg(t, it.tout - .08, it.tout + LINGER);
  let o = eo(pin) * (1 - eo(pout)), tf = '', fl = '';
  const k = 1 - pin;
  switch (it.fx) {
    case 'up': tf = `translateY(${60 * Math.pow(k, 2.2)}px)`; break;
    case 'left': tf = `translateX(${140 * Math.pow(k, 2.2)}px)`; break;
    case 'right': tf = `translateX(${-140 * Math.pow(k, 2.2)}px)`; break;
    case 'pop': tf = `scale(${.82 + .18 * back(pin)})`; break;
    case 'blur': tf = `translateY(${24 * Math.pow(k, 2)}px)`; fl = `blur(${14 * Math.pow(k, 1.5)}px)`; break;
    case 'shake': { const s = seg(t, it.tin, it.tin + .55); tf = `scale(${.82 + .18 * back(pin)}) translateX(${Math.sin(s * 28) * 14 * (1 - s)}px)`; break; }
    case 'walkL': case 'walkR': { const dir = it.fx === 'walkL' ? -1 : 1, e = eo(pin); tf = `translateX(${dir * 460 * (1 - e)}px) translateY(${-18 * Math.abs(Math.sin(pin * Math.PI * 4)) * (1 - pin)}px) rotate(${dir * 2.4 * Math.sin(pin * Math.PI * 4) * (1 - pin)}deg)`; o = Math.min(1, pin * 6) * (1 - eo(pout)); break; }
    case 'slide': { const e = smooth(pin); tf = `translateX(${(140 * (1 - e)).toFixed(1)}px)`; o = e; break; }
    case 'fade': break;
  }
  tf += ` translateY(${-28 * eio(pout)}px)`;
  if (pout > 0) fl += ` blur(${8 * pout}px)`;
  return { o, tf, fl, pin };
}

function speechEnv(a, t) {
  let v = 0;
  for (const w of a._speech) {
    if (w.t0 > t + .3) break;
    const on = smooth(seg(t, w.t0 - .1, w.t0 + .15)), off = 1 - smooth(seg(t, w.t1, w.t1 + .4));
    v = Math.max(v, Math.min(on, off));
  }
  return v;
}
function drawArm(S, t, sp) {
  // position inside the current clip, in frames
  let c = null;
  for (const q of S.clips) if (t >= q.t0) c = q;
  let fr, pos;
  if (!c) { fr = S.clips[0].fr; pos = 0; }
  else { fr = c.fr; const p = seg(t, c.t0, c.t0 + c.d); pos = smoother(p) * (fr.length - 1); }
  const n = fr.length - 1;
  // a held pose is one sharp key frame: mixing neighbouring frames there would show a doubled hand
  if (!c) pos = 0;
  const i = Math.max(0, Math.min(n - 1, Math.floor(pos))), f = Math.max(0, Math.min(1, pos - i));
  const A = S.imgs[fr[i]], B = S.imgs[fr[i + 1]], g = S.ctx;
  g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1;
  g.clearRect(0, 0, g.canvas.width, g.canvas.height);
  if (B === A || f <= 0) g.drawImage(A, 0, 0);
  else { g.globalAlpha = 1 - f; g.drawImage(A, 0, 0); g.globalCompositeOperation = 'lighter'; g.globalAlpha = f; g.drawImage(B, 0, 0); }
}
// the body's bend: how far a row follows the hip shift (0 at the feet, 1 at the hips, less at the shoulders, the
// head a little more again), as a smooth curve of n (0 = feet, 1 = top of the head)
const BEND = [[0, 0], [.43, 1], [.66, .3], [1, .55]];
function bend(n) {
  for (let i = 1; i < BEND.length; i++) if (n <= BEND[i][0]) { const [n0, v0] = BEND[i - 1], [n1, v1] = BEND[i]; return v0 + (v1 - v0) * smooth((n - n0) / (n1 - n0)); }
  return BEND[BEND.length - 1][1];
}
function drawPose(a, t) {
  const g = a._pose, L = a._side.L, R = a._side.R, mid = PW / 2;
  g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1; g.filter = 'none';
  g.clearRect(0, 0, PW, PH);
  g.drawImage(L.ctx.canvas, 0, 0, mid, PH, 0, 0, mid, PH);
  g.drawImage(R.ctx.canvas, mid - R.x0, 0, PW - mid, PH, mid, 0, PW - mid, PH);
  // head: take the master's head out of the body, then add this moment's head (two neighbouring head frames mixed
  // by time; additive = an exact blend, so the head moves at the reel's full frame rate)
  const [bx, by] = FACE.box, T = FACE.t;
  let i = 0; while (i < T.length - 2 && T[i + 1] <= t) i++;
  const f = Math.max(0, Math.min(1, (t - T[i]) / (T[i + 1] - T[i])));
  g.globalCompositeOperation = 'destination-out'; g.drawImage(FACE_IMGS[FACE.erase], bx, by);
  g.globalCompositeOperation = 'lighter';
  g.globalAlpha = 1 - f; g.drawImage(FACE_IMGS[FACE.frames[i]], bx, by);
  if (f > 0) { g.globalAlpha = f; g.drawImage(FACE_IMGS[FACE.frames[i + 1]], bx, by); }
  g.globalAlpha = 1;
  // stage light. Rim: the outline band (figure minus the figure pulled in by 4 px) glows warm, like the gold light
  // behind him; legs fall off into the dark floor; a little warm fill from the upper left
  const e = a._tmp, r = a._rim;
  e.globalCompositeOperation = 'copy'; e.drawImage(g.canvas, 0, 0);
  e.globalCompositeOperation = 'destination-in';
  for (const [dx, dy] of [[4, 0], [-4, 0], [0, 4], [0, -4]]) e.drawImage(g.canvas, dx, dy);
  r.globalCompositeOperation = 'copy'; r.drawImage(g.canvas, 0, 0);
  r.globalCompositeOperation = 'destination-out'; r.drawImage(e.canvas, 0, 0);
  r.globalCompositeOperation = 'source-in'; r.fillStyle = 'rgb(255,188,96)'; r.fillRect(0, 0, PW, PH);
  g.globalCompositeOperation = 'source-atop';
  let gr = g.createLinearGradient(0, 560, 0, PH); gr.addColorStop(0, 'rgba(10,5,2,0)'); gr.addColorStop(1, 'rgba(10,5,2,.42)');
  g.fillStyle = gr; g.fillRect(0, 0, PW, PH);
  gr = g.createRadialGradient(240, 260, 0, 240, 260, 820); gr.addColorStop(0, 'rgba(255,186,92,.10)'); gr.addColorStop(1, 'rgba(255,186,92,0)');
  g.fillStyle = gr; g.fillRect(0, 0, PW, PH);
  g.filter = 'blur(2.5px)'; g.globalAlpha = .42; g.drawImage(r.canvas, 0, 0); g.filter = 'none'; g.globalAlpha = 1;
  g.globalCompositeOperation = 'source-over';
}
function drawHero(a, t) {
  // where he stands: a 1.0 s glide between marks
  const M = a._marks; let i = 0;
  for (let j = 0; j < M.length; j++) if (t >= M[j].t) i = j;
  const k = M[i], pv = M[i - 1] || k, u = seg(t, k.t, k.t + 1.0);
  const x = pv.x + (k.x - pv.x) * smooth(u), vel = (k.x - pv.x) * 6 * u * (1 - u);
  const sp = speechEnv(a, t);
  drawArm(a._side.L, t, sp); drawArm(a._side.R, t, sp);
  drawPose(a, t);
  // body motion (v018): no rigid tilt and no card-like turn. The hips shift slowly from one leg to the other with the
  // feet planted, the shoulders go a little the other way, the chest widens with each breath
  const breathe = Math.sin(t * 1.6), shift = 7 * (Math.sin(t * .62) + .35 * Math.sin(t * 1.31 + 1));
  const lean = Math.max(-14, Math.min(14, vel / 55));
  const o = a._out; o.clearRect(0, 0, PW + 2 * PAD, PH);
  for (let y = 0; y < PH; y++) {
    const n = Math.max(0, 1 - y / PFEET);
    const dx = shift * bend(n) + lean * n * n;
    const c = (n - .6) / .16, sx = 1 + .009 * breathe * Math.exp(-c * c);
    o.drawImage(a._pose.canvas, 0, y, PW, 1, PAD + dx - (sx - 1) * PW / 2, y, PW * sx, 1);
  }
  a._mv.style.transform = `translateX(${x.toFixed(2)}px)`;
  a._body.style.transform = `translateY(${(-1.6 * breathe - 2 * sp).toFixed(2)}px)`;
}

window.render = async t => {
  // background drift
  blobs[0].style.transform = `translate(${-120 + 90 * Math.sin(t * .23)}px, ${-160 + 70 * Math.cos(t * .19)}px)`;
  blobs[1].style.transform = `translate(${560 + 80 * Math.cos(t * .17)}px, ${980 + 90 * Math.sin(t * .21)}px)`;
  blobs[2].style.transform = `translate(${380 + 120 * Math.sin(t * .13 + 1)}px, ${380 + 140 * Math.sin(t * .11)}px)`;

  floor.style.backgroundPosition = `${(-14 * t).toFixed(1)}px ${(40 * t).toFixed(1)}px`;
  for (const it of items) {
    const n = it.n;
    if (t < it.tin - .01 || t > it.tout + LINGER + .01) { n.style.opacity = 0; continue; }
    const { o, tf, fl } = fxStyle(it, t);
    let extra = '';
    if (n._marq) extra = ` translateX(${n._marq.dir < 0 ? -n._marq.speed * (t - it.tin) : -1100 + n._marq.speed * (t - it.tin)}px)`;
    if (n._drift) { extra = ` translateX(${n._drift > 0 ? -260 + 60 * (t - it.tin) : 120 - 60 * (t - it.tin)}px)`; }
    if (n._pulse) { const u = t - n._pulse; if (u > 0) extra = ` scale(${1 + .035 * Math.exp(-u * 1.2) * Math.sin(u * 9)})`; }
    n.style.opacity = n._drift ? o * .9 : o; n.style.transform = tf + extra; n.style.filter = fl || 'none';
    if (n._grow) { const [a, b, h] = n._grow; n.style.height = px(h * eio(seg(t, a, b))); }
    if (n._follow) {
      const [a, b] = n._follow, on = t >= b, btn = n.querySelector('.btn');
      btn.textContent = on ? 'Following ✓' : 'Follow';
      btn.style.background = on ? 'transparent' : 'var(--gold)'; btn.style.color = on ? 'var(--gold)' : '#1a120b';
      btn.style.border = on ? '2px solid var(--gold)' : '2px solid transparent';
      n.style.left = px((1080 - n.offsetWidth) / 2);
    }
    if (n._marks) drawHero(n, t);
  }
  for (const b of bars) { const [a, e, f, to] = b._bar; b.firstElementChild.style.width = (100 * (f + (to - f) * eio(seg(t, a, e)))) + '%'; }
  for (const w of wires) { const [a, e, h] = w._wire; w.style.height = px(h * seg(t, a, e)); }
  for (const c of checks) {
    const p = seg(t, c._on, c._on + .28);
    c.querySelector('.fill').style.transform = `scale(${back(p, 2.2) * (p > 0 ? 1 : 0)})`;
    c.querySelector('svg').style.opacity = p > .4 ? 1 : 0;
  }
  document.querySelectorAll('.strike').forEach(s => {
    const [a, tx] = s._strike; s.style.width = px((tx.offsetWidth + 12) * eio(seg(t, a, a + .35)));
    tx.style.opacity = 1 - .62 * seg(t, tx._dim, tx._dim + .4);
  });
  document.querySelectorAll('.squig').forEach(q => {
    const p = q.querySelector('path'), L0 = p.getTotalLength(), [a] = q._draw;
    p.style.strokeDasharray = L0; p.style.strokeDashoffset = L0 * (1 - eio(seg(t, a, a + .6)));
  });

  // header + progress dots
  let cur = 0; SCN.forEach((s, i) => { if (t >= sc[s].t0 - .25) cur = i; });
  hdrR.textContent = SCN_LABEL[SCN[cur]];
  hdr.style.opacity = eo(seg(t, .1, .6));
  dots.style.opacity = eo(seg(t, .2, .7));
  dotEls.forEach((d, i) => {
    const done = i < cur, act = i === cur;
    d.style.background = done ? 'var(--gold)' : act ? 'rgba(246,181,58,.25)' : 'transparent';
    d.style.borderColor = done || act ? 'var(--gold)' : 'rgba(246,181,58,.35)';
    d.style.transform = act ? `scale(${1.15 + .1 * Math.sin(t * 5)})` : 'scale(1)';
  });
  lineEls.forEach((l, i) => {
    const s = sc[SCN[i + 1]]; l.querySelector('.f').style.width = (100 * eio(seg(t, s.t0 - .5, s.t0 - .05))) + '%';
  });

  // captions
  const ch = TL.chunks.find(c => t >= c.t0 && t < c.t1);
  const key = ch ? ch.t0 : capKey;
  if (!ch) { const last = TL.chunks.filter(c => c.t1 <= t).pop(); cap.style.opacity = last ? 1 - seg(t, last.t1, last.t1 + .2) : 0; }   // in a pause the caption fades, it does not cut
  if (ch && key !== capKey) { cap.innerHTML = ch ? ch.words.map(w => `<span>${w.w.replace(/[.,]$/, '')}</span>`).join('') : ''; capKey = key; }
  if (ch) {
    const p = seg(t, ch.t0, ch.t0 + .16);
    // a new caption replaces the old one at full opacity (fading it in made the captions blink); it only settles in scale
    cap.style.opacity = 1; cap.style.transform = `scale(${.97 + .03 * eo(p)})`;
    let on = -1; ch.words.forEach((w, i) => { if (t >= w.t0 - .03) on = i; });
    [...cap.children].forEach((s, i) => { s.className = i === on ? 'on' : ''; });
  }
  wm.style.opacity = eo(seg(t, .3, 1));
  // let the browser paint this frame fully before it is captured (a 4K render under load once dropped the captions)
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
};

window.DUR = TL.dur;
window.EV = EV.sort((a, b) => a.t - b.t);

// ---------- ready once fonts and every image are loaded ----------
await document.fonts.load('800 92px Playfair'); await document.fonts.load('italic 700 52px Playfair');
await document.fonts.load('700 42px Jost'); await document.fonts.load('500 29px Jost'); await document.fonts.load('600 24px Jost');
await document.fonts.load('900 64px Playfair'); await document.fonts.load('800 54px Jost');
await Promise.all([...document.images, ...ANIM_IMGS, ...Object.values(FACE_IMGS)].map(i => i.complete ? 0 : new Promise(r => { i.onload = r; i.onerror = r; })));
await Promise.all(ANIM_IMGS.map(i => i.decode().catch(() => {})));
await Promise.all([...document.images].map(i => i.decode().catch(() => {})));
await document.fonts.ready;
await window.render(0);
window.READY = true;
