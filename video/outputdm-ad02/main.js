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
function W(id, needle, which = 't0', nth = 1) {
  const ws = TL.words.filter(x => x.line === id && norm(x.w).startsWith(needle.toLowerCase()));
  const w = ws[nth - 1];
  if (!w) throw new Error(`word ${needle} (${nth}) not in ${id}`);
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
const SCN = ['hook', 'gap', 'solution', 'founder', 'fear', 'objection', 'lifestyle', 'authority', 'cta'];
const SCN_LABEL = { hook: '01 · confession', gap: '02 · the missing link', solution: '03 · the fix', founder: '04 · who I am', fear: '05 · no stress', objection: '06 · your doubt', lifestyle: '07 · imagine this', authority: '08 · trusted', cta: '09 · free review' };
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
// body turns (v019, mascot/anim/tools/build_turn.py): whole-body frames front -> 3/4 toward the viewer's left (tl)
// or right (tr); each frame brings its own head patch, so the head can be drawn at HEAD_S like the front head
const TURN = await (await fetch('assets/anim/turn.json')).json();
for (const fr of Object.values(TURN)) for (const q of fr) for (const f of [q.f, q.head, q.erase]) { const im = new Image(); im.src = `assets/anim/${f}`; FACE_IMGS[f] = im; }
const ANGLES = await (await fetch('angles.json')).json();   // d and yaw of a body turn (also read by build_face.py)
// v020: what the arms, the body and the turns do comes from acting.json, written by mascot/anim/tools/director.py from
// the script and the real word times (the head frames are built from the same file)
const ACT = await (await fetch('acting.json')).json();
const TURN_D = ANGLES.d, TURN_PRE = .05;
const PW = 820, PH = 1240, PFEET = 1215, BASE = 1392, HERO_H = 1090, PAD = 40;
const HEAD_S = .93, HEAD_PX = 405, HEAD_PY = 434;
const smooth = x => x * x * (3 - 2 * x);
const smoother = x => x * x * x * (x * (x * 6 - 15) + 10);
// v021 arm timing: a damped spring over the clip (damping ratio .8, about 1.5 % overshoot), normalised to end at 1
const SPR_Z = .8, SPR_W = 5.5, SPR_D = SPR_W * Math.sqrt(1 - SPR_Z * SPR_Z);
const sprRaw = p => 1 - Math.exp(-SPR_Z * SPR_W * p) * (Math.cos(SPR_D * p) + SPR_Z * SPR_W / SPR_D * Math.sin(SPR_D * p));
const armSpring = p => p <= 0 ? 0 : p >= 1 ? 1 : sprRaw(p) / sprRaw(1);
const ANIM_IMGS = [];
const TRACKS = [];   // the scenes only say where he stands: [time, (unused pose), centre-x]
function hero(scene, h, track, tin, tout) { TRACKS.push({ scene, track, tin, tout }); }
function buildHero(ARMS, TURNS = []) {
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
  // body angle: [time, 'tl' | 'tr' | 'front']. A turn is a whole-body clip, so both arms must be at rest when it
  // starts, and arm moves asked for while he is turned wait until he faces the front again
  const turns = []; let ang = 'front';
  for (const [t, to] of TURNS.slice().sort((p, q) => p[0] - q[0])) {
    if (to === ang) continue;
    if (to !== 'front' && ang !== 'front') throw new Error('turn back to the front before turning the other way');
    if (to !== 'front') turns.push({ dir: to, t0: t, t1: Infinity }); else turns[turns.length - 1].t1 = t;
    ang = to;
  }
  a._turns = turns;
  const busy = t => { for (const q of turns) if (t > q.t0 - TURN_PRE - .1 && t < q.t1 + TURN_D + TURN_PRE) return q; return null; };
  // arms: per side a list of clips [start, duration, frames]
  a._side = {};
  for (const s of ['L', 'R']) {
    const [x0, x1] = ANIM.half[s];
    const clips = [], files = new Set([ANIM.states[s].rest]);
    let cur = 'rest', free = -9;
    for (const [t, state, dd] of ARMS[s].slice().sort((p, q) => p[0] - q[0])) {
      if (state === cur) continue;
      const fr = ANIM.trans[`${s}:${cur}>${state}`];
      if (!fr) throw new Error(`no arm clip ${s}:${cur}>${state}`);
      const d = dd || Math.min(1.3, .45 + .016 * fr.length); let t0 = Math.max(t, free + (dd ? .02 : .12));   // the director gives the length; otherwise longer clips take longer
      const tq = busy(t0) || busy(t0 + d);
      if (tq) { if (cur !== 'rest') throw new Error(`arm ${s} is not at rest for the turn at ${tq.t0.toFixed(2)} s`); t0 = tq.t1 + TURN_D + TURN_PRE + .02; }
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
  a._pose = mk(PW, PH); a._tmp = mk(PW, PH); a._rim = mk(PW, PH); a._c1 = mk(PW, PH); a._c2 = mk(PW, PH);
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
// Ad 01 (Nov 26): the nine beats the user asked for, in order: confession + contradiction hook, curiosity gap,
// simple solution reveal, credibility anchor, fear removal, last objection killed, lifestyle normalisation,
// authority validation, CTA. Same stage, palette, fonts, logo and character as the founder reel.
const sc = Object.fromEntries(SCN.map(n => [n, S(n)]));
const STAND = { right: 830, left: 240, centre: 540 };
const STAGE = await (await fetch('staging.json')).json();
const stand = (scene, t0, t1) => hero(scene, 1090, [[0, '', STAND[STAGE[scene] || 'right']]], t0 + .05, t1);
// a word that de-blurs (the reveal of the curiosity gap)
const blurs = [], counters = [];
function unblur(n, a, b, from = 18) { n._unblur = [a, b, from]; blurs.push(n); return n; }

// 1 · hook: a marketer saying followers do not run a business
{
  const { t0, t1 } = sc.hook;
  heading('Main marketing<br>karta hoon...', 'lekin sach bataun?', -.6, W('l01', 'lekin') - .1, t1);   // on screen at frame 0
  ghost('SACH', 620, t0 + .2, t1, 380, -1);
  const conf = el('<div class="abs chip" style="background:var(--red);border-color:var(--red);color:#fff;font-size:32px;font-weight:800;letter-spacing:.08em">MARKETER KA SACH</div>', { left: '64px', top: '545px' });
  add(conf, -.6, t1, 'pop');
  // followers count up, sales stay at zero
  const c = el('<div class="abs card big" style="width:560px;padding:30px 34px"></div>', { left: '40px', top: '650px' });
  el('<div class="lbl" style="font-size:28px">Followers</div>', {}, c);
  const fol = el('<div style="font-family:Playfair;font-weight:900;font-size:120px;line-height:1.05;color:var(--gold)">0</div>', {}, c);
  fol._count = [W('l01', 'followers') - .3, W('l01', 'business') + .2, 0, 48000];
  counters.push(fol);
  el('<div class="row" style="justify-content:space-between;margin-top:10px"><div class="lbl" style="font-size:28px;color:var(--red)">Sales</div><div style="font-family:Jost;font-weight:800;font-size:64px;color:var(--red)">0</div></div>', {}, c);
  add(c, W('l01', 'followers') - .35, t1, 'pop', { sfx: 'pop' });
  const stamp = el('<div class="abs"><div class="stamp">BUSINESS NAHI CHALTA</div></div>', { left: '30px', top: '1060px' });
  stamp.firstElementChild.style.fontSize = '46px';
  add(stamp, W('l01', 'nahi') - .05, t1, 'pop', { sfx: 'thump' });
  stand('hook', t0, t1);
}

// 2 · curiosity gap: the missing link
{
  const { t0, t1 } = sc.gap;
  heading('Jo sales laata hai...', 'woh pages pe hota hi nahi', t0 + .05, W('l02', 'woh') - .1, t1);
  ghost('???', 600, t0 + .1, t1, 420, 1);
  const row = el('<div class="abs row" style="gap:16px"></div>', { left: '40px', top: '660px' });
  const box = (txt, gold) => el(`<div class="card big" style="padding:28px 26px;width:180px;text-align:center"><div class="t1" style="font-size:40px;${gold ? 'color:var(--gold)' : ''}">${txt}</div></div>`, {}, row);
  box('Post'); const mid = box('?', true); box('Sale');
  mid.style.borderStyle = 'dashed'; mid.style.borderColor = 'rgba(246,181,58,.8)';
  mid.firstElementChild.style.fontSize = '80px';
  add(row, W('l02', 'jo') - .15, t1, 'pop', { sfx: 'pop' });
  const miss = el('<div class="abs chip bigchip" style="border-color:rgba(227,52,58,.6)">missing link</div>', { left: '150px', top: '900px' });
  add(miss, W('l02', 'woh') - .1, t1, 'shake', { sfx: 'thump' });
  stand('gap', t0, t1);
}

// 3 · simple solution reveal: one straight path under every post
{
  const { t0, t1 } = sc.solution;
  heading('Har post ke saath', 'ek seedha raasta', t0 + .05, W('l03', 'ek') - .1, t1);
  ghost('PATH', 620, t0 + .1, t1, 340, -1);
  const steps = [['1', 'Post dekhi', W('l03', 'post', 't0', 2)], ['2', 'WhatsApp kiya', W('l03', 'whatsapp')], ['3', 'Order ho gaya', W('l03', 'order')]];
  const list = el('<div class="abs card big" style="padding:14px 32px;width:600px"></div>', { left: '440px', top: '520px' });
  add(list, W('l03', 'seedha') - .1, t1, 'pop', { d: .5, sfx: 'pop' });
  const wire = el('<div style="position:absolute;left:65px;top:80px;width:5px;height:0;background:var(--gold);border-radius:3px"></div>', {}, list);
  wire._wire = [steps[0][2], steps[2][2] + .1, 330]; wires.push(wire);
  steps.forEach(([n, a, tt]) => {
    const r = el('<div class="row" style="padding:18px 0;position:relative"></div>', {}, list);
    check(r, tt + .05);
    const tx = el(`<div><div class="t1" style="font-size:52px">${a}</div></div>`, {}, r);
    unblur(tx, tt - .25, tt + .15, 16);
  });
  const key = el('<div class="abs chip bigchip" style="background:var(--gold);color:#1a120b;border-color:var(--gold);font-size:38px">Post → WhatsApp → Order</div>', { left: '440px', top: '1080px' });
  add(key, W('l03', 'order') + .25, t1, 'pop', { sfx: 'ding' });
  stand('solution', t0, t1);
}

// 4 · credibility anchor
{
  const { t0, t1 } = sc.founder;
  heading('Main Zarkhaiz', 'Founder, OutputDM', t0 + .05, W('l04', 'outputdm') - .1, t1);
  ghost('2018', 560, t0 + .1, t1, 420, 1);
  const c = el('<div class="abs card big" style="padding:34px 36px;width:580px"></div>', { left: '40px', top: '640px' });
  el('<img src="assets/logo_icon.png" style="width:150px;display:block;margin-bottom:14px">', {}, c);
  el('<div class="lbl" style="margin-bottom:8px;font-size:28px">Founder</div>', {}, c);
  el('<div style="font-family:Playfair;font-weight:900;font-size:92px;line-height:1">OutputDM</div>', {}, c);
  el('<div class="t2" style="margin-top:12px;font-size:30px">Output Digital Marketing Pvt Ltd</div>', {}, c);
  add(c, W('l04', 'outputdm') - .15, t1, 'pop', { sfx: 'ding' });
  const since = el('<div class="abs chip bigchip"><span class="pin"></span>Since 2018 · Lahore</div>', { left: '60px', top: '1130px' });
  add(since, W('l04', '2018') - .15, t1, 'up', { sfx: 'pop' });
  stand('founder', t0, t1);
}

// 5 · fear removal: no daily posting stress, no need to be on camera
{
  const { t0, t1 } = sc.fear;
  heading('Tension', 'aap ki nahi, hamari', t0 + .05, W('l05', 'camera') - .1, t1);
  ghost('EASY', 640, t0 + .1, t1, 380, -1);
  const fears = [['Roz post ki tension', W('l05', 'roz')], ['Camera ke saamne', W('l05', 'camera')]];
  fears.forEach(([a, tt], i) => {
    const c = el('<div class="abs card big row" style="width:600px"></div>', { left: '30px', top: px(600 + i * 178) });
    el(`<div class="chk" style="border-color:transparent;background:var(--red)">${CROSS}</div>`, {}, c);
    const tx = el(`<div class="t1" style="position:relative;white-space:nowrap">${a}</div>`, {}, c);
    const st = el('<div class="strike"></div>', { width: '0px' }, tx); st._strike = [tt + .35, tx]; tx._dim = tt + .4;
    add(c, tt - .2, t1, 'right', { sfx: 'thump' });
  });
  const ok = el('<div class="abs card big row" style="width:610px;border-color:rgba(246,181,58,.8)"></div>', { left: '30px', top: '980px' });
  check(ok, W('l05', 'banate') + .05);
  el('<div><div class="t1" style="white-space:nowrap;font-size:40px">Content hum banate hain</div><div class="t2">posts, reels, design</div></div>', {}, ok);
  add(ok, W('l05', 'content') - .15, t1, 'pop', { sfx: 'ding' });
  stand('fear', t0, t1);
}

// 6 · last objection killed: "my business is too small for this"
{
  const { t0, t1 } = sc.objection;
  heading('"Chhota business hai,', 'itna sab kis liye?"', t0 + .05, W('l06', 'itna') - .1, t1);
  ghost('START', 620, t0 + .1, t1, 340, 1);
  const bub = el('<div class="abs"><div class="bubble">Chhota business hai...<br>itna sab kis liye?</div></div>', { left: '470px', top: '540px' });
  add(bub, W('l06', 'sochte') - .1, W('l06', 'free') + .1, 'pop', { sfx: 'pop' });
  const x = el(`<div class="abs chk" style="width:110px;height:110px;border-color:transparent;background:var(--red)">${CROSS}</div>`, { left: '930px', top: '520px' });
  add(x, W('l06', 'free') - .1, W('l06', 'free') + .3, 'pop', { sfx: 'thump' });
  const c = el('<div class="abs card big" style="width:600px;padding:32px 34px;border-color:rgba(246,181,58,.8)"></div>', { left: '440px', top: '560px' });
  el('<div class="row" style="gap:16px;margin-bottom:16px"><div class="lock" style="background:var(--gold);color:#1a120b">&#128269;</div><div class="lbl" style="font-size:30px">Free review</div></div>', {}, c);
  el('<div class="t1" style="font-size:46px">Kahan se shuru karein</div><div class="t2" style="font-size:31px;margin-top:8px">aap ke business ke hisaab se</div>', {}, c);
  ['Pehla qadam', 'Doosra qadam', 'Phir barhayein'].forEach((m, i) => {
    el(`<div class="row" style="margin-top:14px;gap:14px"><span class="num" style="font-size:40px;width:44px">${i + 1}</span><div class="t2" style="font-size:32px;color:var(--cream)">${m}</div></div>`, {}, c);
  });
  add(c, W('l06', 'free') + .25, t1, 'pop', { sfx: 'ding' });
  stand('objection', t0, t1);
}

// 7 · lifestyle normalisation: a post in the morning, orders by the evening
{
  const { t0, t1 } = sc.lifestyle;
  heading('Socho...', 'subah post, shaam tak orders', t0 + .05, W('l07', 'shaam') - .1, t1);
  ghost('6:45', 600, t0 + .1, t1, 400, -1);
  const ph = el('<div class="abs phone" style="background:linear-gradient(#3a2216,#1a110c)"><div class="pclock">6:45</div><div class="pdate">shaam</div></div>', { left: '70px', top: '560px' });
  add(ph, W('l07', 'subah') - .1, t1, 'up', { sfx: 'whoosh' });
  const msgs = ['Order: 2 pack chahiye', 'Delivery kab tak?', 'Mera order bhi likh lein', 'Price list bhej dein'];
  const tm = W('l07', 'orders');
  msgs.forEach((m, i) => {
    const n = el(`<div class="note"><div class="wa" style="width:58px;height:58px">${WA.replace(/50/g, '34')}</div><div><div class="nt">Naya order</div><div class="nb">${m}</div></div></div>`, {}, ph);
    n.style.top = px(300 + i * 124);
    add(n, tm - .45 + i * .22, t1, 'up', { sfx: i < 2 ? 'pop' : null });
  });
  const nm = el('<div class="abs" style="font-family:Playfair;font-weight:900;font-size:80px;line-height:1;width:560px;text-align:center"><span style="color:var(--muted);font-size:50px">yahi hona chahiye</span><br><span style="color:var(--gold)">NORMAL</span></div>', { left: '40px', top: '1190px' });
  add(nm, W('l07', 'normal') - .15, t1, 'pop', { sfx: 'ding' });
  stand('lifestyle', t0, t1);
}

// 8 · authority validation: industries, two countries, the brand wall
{
  const { t0, t1 } = sc.authority;
  heading('Har industry', 'Pakistan + UAE', t0 + .05, W('l08', 'pakistan') - .1, t1);
  ghost('TRUST', 600, t0 + .1, t1, 360, 1);
  const tags = [['Restaurants', 'restaurants'], ['Real estate', 'real'], ['Health', 'health'], ['Travel', 'travel']];
  tags.forEach(([p, k], i) => {
    const c = el(`<div class="abs chip bigchip"><span class="pin"></span>${p}</div>`, { left: px(50 + (i % 2) * 370), top: px(560 + Math.floor(i / 2) * 120) });
    add(c, W('l08', k) - .15, t1, 'pop', { sfx: 'pop' });
  });
  const brands = ['Dajaj Broast', 'Nabi Cafe', 'Sadaqat Properties', 'Cheesy Chicken', 'Tashkeel Travels', 'Misbah Noor Medical Complex', 'Dabbay Wala', 'Dua Pixels', 'ABS Developers', 'Sami Motors', 'Guftagu Restaurant', 'Elite Health Cart'];
  const tb = W('l08', 'businesses') - .2;
  [0, 1, 2].forEach(r => {
    const m = el('<div class="marq"></div>', { top: px(860 + r * 104) });
    const list = brands.slice(r * 4).concat(brands.slice(0, r * 4));
    m.innerHTML = list.concat(list).map(b => `<span class="chip" style="font-size:40px;padding:16px 32px;margin-right:18px;background:rgba(64,50,38,.95);border-color:rgba(246,181,58,.45);color:#fff8ee">${b}</span>`).join('');
    m._marq = { dir: r % 2 ? 1 : -1, speed: 80 };
    add(m, tb + r * .12, t1, 'up');
  });
  const ch = el('<div class="abs chip bigchip" style="background:var(--gold);color:#1a120b;border-color:var(--gold)">OutputDM chunte hain</div>', { left: '60px', top: '1200px' });
  add(ch, W('l08', 'chunte') - .15, t1, 'pop', { sfx: 'ding' });
  stand('authority', t0, t1);
}

// 9 · CTA
{
  const { t0, t1 } = sc.cta;
  heading('Free Digital<br>Growth Review', 'abhi WhatsApp karein', t0 + .05, W('l09', 'abhi') - .15, t1 + 1);
  ghost('FREE', 700, t0 + .1, t1 + 1, 380, -1);
  const wa = el(`<div class="abs card big row" style="padding:30px 32px;width:600px;gap:24px;border-color:rgba(37,211,102,.6)"><div class="wa">${WA}</div><div><div class="lbl" style="color:#7be3a2">WhatsApp</div><div style="font-family:Jost;font-weight:800;font-size:54px;white-space:nowrap">0344 444 1724</div></div></div>`, { left: '40px', top: '940px' });
  wa._pulse = W('l09', 'whatsapp');
  add(wa, W('l09', 'whatsapp') - .25, t1 + 1, 'pop', { sfx: 'ding' });
  const lg = el('<img class="abs" src="assets/logo.png" style="width:330px">', { left: '70px', top: '560px' });
  add(lg, W('l10', 'outputdm') - .2, t1 + 1, 'pop', { sfx: 'pop' });
  const web = el('<div class="abs chip bigchip">outputdm.com</div>', { left: '56px', top: '1130px' });
  add(web, W('l10', 'dot'), t1 + 1, 'up');
  const tf = L('l10').t1 + .55;
  const fol = el(`<div class="abs chip bigchip" style="padding:16px 20px 16px 34px;gap:24px">@outputdm <span class="btn" style="background:var(--gold);color:#1a120b">Follow</span></div>`, { left: '0px', top: '1404px' });
  fol._follow = [tf, tf + 1.15];
  add(fol, tf, t1 + 1, 'pop', { sfx: 'pop' });
  EV.push({ t: +(tf + 1.15).toFixed(3), type: 'click' });
  stand('cta', t0, t1 + 1);
}

// the character's storyboard comes from acting.json (director.py): arm clips [start, state, length] per side and the
// slight body turns. To change the acting, change the script or the director's rules and rebuild, not this file.
const HERO = buildHero(ACT.arms, ACT.turns);
HERO._bodyEv = ACT.body;

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
  else {
    // v021: spring timing (as in motion-primitives' spring transitions): the arm starts at once, slows down into
    // the pose and settles with a very small overshoot (reflected back), instead of the symmetric slow-in/slow-out
    fr = c.fr; const p = seg(t, c.t0, c.t0 + c.d), N_ = fr.length - 1;
    pos = armSpring(p) * N_; if (pos > N_) pos = 2 * N_ - pos;
  }
  const n = fr.length - 1;
  // a held pose is one sharp key frame: mixing neighbouring frames there would show a doubled hand
  if (!c) pos = 0;
  const i = Math.max(0, Math.min(n - 1, Math.floor(pos)));
  // v021: blend two neighbouring frames only for a short moment in the middle of a step: a long 50/50 mix of two
  // hand positions read as a doubled, ghosted hand in the fast part of a move
  let f = Math.max(0, Math.min(1, pos - i)); f = Math.max(0, Math.min(1, (f - .3) / .4)); f = f * f * (3 - 2 * f);
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
// the front pose: both arm halves joined, the master's head replaced by this moment's LivePortrait head
function composeFront(a, t, g) {
  const L = a._side.L, R = a._side.R, mid = PW / 2;
  g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1; g.filter = 'none';
  g.clearRect(0, 0, PW, PH);
  g.drawImage(L.ctx.canvas, 0, 0, mid, PH, 0, 0, mid, PH);
  g.drawImage(R.ctx.canvas, mid - R.x0, 0, PW - mid, PH, mid, 0, PW - mid, PH);
  g.globalCompositeOperation = 'destination-out'; g.drawImage(FACE_IMGS[FACE.erase], FACE.box[0], FACE.box[1]);
  liveHead(g, t, 0, 0);
}
// this moment's LivePortrait head, added to g (two neighbouring head frames mixed by time; additive = an exact blend,
// so the head moves at the reel's full frame rate). It is drawn a little smaller than in the master (HEAD_S, scaled
// at the collar: the user found the head too big) and moved by (ox, oy) when the body is turned.
function liveHead(g, t, ox, oy) {
  const [bx, by] = FACE.box, T = FACE.t;
  let i = 0; while (i < T.length - 2 && T[i + 1] <= t) i++;
  const f = Math.max(0, Math.min(1, (t - T[i]) / (T[i + 1] - T[i])));
  const hw = FACE.box[2] * HEAD_S, hh = FACE.box[3] * HEAD_S, hx = ox + HEAD_PX + (bx - HEAD_PX) * HEAD_S, hy = oy + HEAD_PY + (by - HEAD_PY) * HEAD_S;
  g.globalCompositeOperation = 'lighter';
  g.globalAlpha = 1 - f; g.drawImage(FACE_IMGS[FACE.frames[i]], hx, hy, hw, hh);
  if (f > 0) { g.globalAlpha = f; g.drawImage(FACE_IMGS[FACE.frames[i + 1]], hx, hy, hw, hh); }
  g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
}
// one frame of a body turn: the frame's own head is removed and the live head put on its collar point, so the face
// keeps blinking and smiling while the body turns
function composeTurnFrame(q, g, t) {
  const [bx, by] = q.box, [px, py] = q.pivot;
  g.globalCompositeOperation = 'source-over'; g.globalAlpha = 1; g.filter = 'none';
  g.clearRect(0, 0, PW, PH); g.drawImage(FACE_IMGS[q.f], 0, 0);
  g.globalCompositeOperation = 'destination-out'; g.drawImage(FACE_IMGS[q.erase], bx, by);
  liveHead(g, t, px - HEAD_PX, py - HEAD_PY);
}
// which turn he is in at t: {dir, pos (0 = front ... last = turned)}
function turnAt(a, t) {
  for (const q of a._turns) {
    if (t <= q.t0 || t >= q.t1 + TURN_D) continue;
    const p = t < q.t1 ? smoother(seg(t, q.t0, q.t0 + TURN_D)) : 1 - smoother(seg(t, q.t1, q.t1 + TURN_D));
    return { dir: q.dir, pos: p * (TURN[q.dir].length - 1) };
  }
  return null;
}
function drawPose(a, t) {
  const g = a._pose, tn = turnAt(a, t);
  if (!tn) composeFront(a, t, g);
  else {
    const fr = TURN[tn.dir], i = Math.max(0, Math.min(fr.length - 2, Math.floor(tn.pos))), f = Math.max(0, Math.min(1, tn.pos - i));
    composeTurnFrame(fr[i], a._c1, t);
    if (f > 0) composeTurnFrame(fr[i + 1], a._c2, t);
    g.globalCompositeOperation = 'source-over'; g.filter = 'none'; g.clearRect(0, 0, PW, PH);
    g.globalCompositeOperation = 'lighter';
    g.globalAlpha = 1 - f; g.drawImage(a._c1.canvas, 0, 0);
    if (f > 0) { g.globalAlpha = f; g.drawImage(a._c2.canvas, 0, 0); }
    g.globalAlpha = 1; g.globalCompositeOperation = 'source-over';
  }
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
  // v020 note: lean, shrug and single-shoulder warps of the pose canvas were tried and REMOVED: drawing the rows in
  // strips left notches along the shoulders and fractional source rows left a dotted edge (the user: "shoulders
  // break, cuts"). The body events stay in acting.json but the page does not draw them. Do not bring them back as
  // 2D warps; a shrug needs its own arm keys.
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
    if (n._sweep) { const [a, b, w] = n._sweep; n.style.width = px(w * eio(seg(t, a, b))); }
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
  for (const n of counters) { const [a, b, f, to] = n._count, p = eio(seg(t, a, b)); n.textContent = Math.round(f + (to - f) * p).toLocaleString('en-US'); }
  for (const n of blurs) { const [a, b, f] = n._unblur, p = eio(seg(t, a, b)); n.style.filter = p < 1 ? `blur(${(f * (1 - p)).toFixed(2)}px)` : 'none'; n.style.opacity = .35 + .65 * p; }
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

window.DUR = +new URLSearchParams(location.search).get('dur') || TL.dur;
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
