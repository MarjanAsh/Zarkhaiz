// OutputDM founder reel: 1080x1920, every frame drawn by render(t) (lemo-opuscar page contract).
const TL = await (await fetch('timeline.json')).json();
const TALK = await (await fetch('talk/manifest.json')).json();
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

// ---------- mascot ----------
const ASP = { m_serious: 949 / 1400, m_smile: 723 / 1400, m_side: 732 / 1400, m_back: 716 / 1400, m_seated: 1138 / 1312 };
const BASE = 1392;
function mascot(src, x, h, bottom, tin, tout, fx = 'up') {
  const m = el(`<div class="m"><div class="halo"></div><div class="shadow"></div><img src="assets/${src}.png"></div>`, { left: px(x), width: px(Math.round(h * ASP[src])), bottom: px(1920 - (bottom ?? BASE)) });
  const it = add(m, tin, tout, fx, { d: .7, sfx: 'whoosh', sfxAt: -.05 });
  it.idle = true;
  return m;
}

// talking-head panel: a 30 fps frame sequence from the LeapTalk clip (talk/<scene>/f_0001.jpg…),
// or, until that clip exists, the portrait still with a slow push-in
const panels = [];
function panel(scene, x, y, size, tin, tout, clipT0, fx = 'pop') {
  const p = el(`<div class="abs panel"><img></div>`, { left: px(x), top: px(y), width: px(size), height: px(size) });
  p._talk = { scene, n: (TALK[scene] || {}).frames || 0, t0: clipT0, tin, tout };
  add(p, tin, tout, fx, { d: .6, sfx: 'whoosh', sfxAt: -.05 });
  panels.push(p);
  return p;
}

// full-body actor: smooth crossfades between poses (turns), breathing, sway, weight shift
const actors = [];
function actor(poses, x, h, tin, tout, fx = 'up') {
  const w = Math.round(h * 0.7);
  const a = el(`<div class="abs" style="width:${w}px;height:${h}px"></div>`, { left: px(x), top: px(BASE - h) });
  el('<div class="shadow"></div>', {}, a); el('<div class="halo"></div>', {}, a);
  a._p = poses.map(([src, t]) => ({ t, img: el(`<img src="assets/${src}.png" style="position:absolute;bottom:0;left:50%;height:100%;transform-origin:50% 100%;opacity:0">`, {}, a) }));
  a._h = h; add(a, tin, tout, fx, { d: .7, sfx: 'whoosh', sfxAt: -.05 }); actors.push(a); return a;
}

// ================= SCENES =================
const sc = Object.fromEntries(SCN.map(n => [n, S(n)]));

// 1 · hook
{
  const { t0, t1 } = sc.hook;
  heading('Marketing pe<br>paisa lag raha hai,', 'lekin customers nahi aa rahe?', t0 + .05, W('l01', 'lekin') - .1, t1);
  actor([['m_serious', 0]], -20, 860, t0 + .1, t1, 'up');
  const rows = [
    ['Ads', 'chal rahe hain', W('l01', 'paisa'), true],
    ['Posts', 'lag rahi hain', W('l01', 'raha'), true],
    ['Customers', 'nahi aa rahe', W('l01', 'customers'), false],
  ];
  rows.forEach(([a, b, tt, ok], i) => {
    const c = el(`<div class="abs card row" style="padding:26px 30px;width:440px"></div>`, { left: '590px', top: px(880 + i * 150) });
    if (ok) check(c, tt + .25);
    else { const x = el(`<div class="chk" style="border-color:transparent;background:var(--red)">${CROSS}</div>`, {}, c); }
    el(`<div><div class="t1">${a}</div><div class="t2">${b}</div></div>`, {}, c);
    add(c, tt - .15, t1, ok ? 'pop' : 'shake', { sfx: ok ? 'pop' : 'thump' });
  });
}

// 2 · intro  (+ mascot carries on into 3 · since)
{
  const { t0, t1 } = sc.intro;
  heading('Assalam o Alaikum!', 'Main Zarkhaiz', t0 + .05, W('l02', 'main') - .1, t1);
  const sq = el('<svg class="abs squig" width="380" height="40" viewBox="0 0 380 40"><path d="M6 24 C 60 6, 110 38, 170 20 S 280 6, 374 22"/></svg>', { left: '64px', top: px(262 + 94 + 12 + 66) });
  sq._draw = [W('l02', 'zarkhaiz'), t1];
  add(sq, t0 + .05, t1, 'fade');
  panel('intro', 140, 490, 800, t0 + .1, t1, L('l02').t0, 'pop');
  const c = el(`<div class="abs card row" style="padding:26px 32px;width:560px;gap:24px"></div>`, { left: '470px', top: '1110px' });
  el('<img src="assets/logo_icon.png" style="width:110px;display:block">', {}, c);
  const ctx = el('<div></div>', {}, c);
  el('<div class="lbl" style="margin-bottom:6px">Founder</div>', {}, ctx);
  el('<div style="font-family:Playfair;font-weight:800;font-size:58px;line-height:1">OutputDM</div>', {}, ctx);
  el('<div class="t2" style="margin-top:8px;font-size:24px">Output Digital Marketing Pvt Ltd</div>', {}, ctx);
  add(c, W('l02', 'outputdm') - .25, t1, 'pop', { sfx: 'pop' });
}

// 3 · since
{
  const { t0, t1 } = sc.since;
  heading('2018 se', 'Lahore se, Pakistan + UAE', t0 + .05, W('l03', 'lahore') - .1, t1);
  actor([['m_back', 0], ['m_side', t0 + .9], ['m_smile', t0 + 1.8]], 40, 700, t0 + .05, t1, 'up');
  const places = [['Lahore', W('l03', 'lahore')], ['Pakistan', W('l03', 'pakistan')], ['UAE', W('l03', 'uae')]];
  places.forEach(([p, tt], i) => {
    const c = el(`<div class="abs chip"><span style="width:16px;height:16px;border-radius:50%;background:var(--gold);display:inline-block"></span>${p}</div>`, { left: px(720 + (i === 0 ? 0 : 40)), top: px(520 + i * 118) });
    add(c, tt - .15, t1, 'pop', { sfx: 'pop' });
  });
  const vline = el('<div class="abs" style="width:3px;background:linear-gradient(var(--gold),rgba(246,181,58,.1));border-radius:2px"></div>', { left: '748px', top: '590px', height: '0px' });
  vline._grow = [W('l03', 'pakistan') - .2, W('l03', 'uae'), 230];
  add(vline, W('l03', 'pakistan') - .2, t1, 'fade');
  const brands = ['Dajaj Broast', 'Nabi Cafe', 'Sadaqat Properties', 'Cheesy Chicken', 'Tashkeel Travels', 'Misbah Noor Medical Complex', 'Dabbay Wala', 'Dua Pixels', 'ABS Developers', 'Sami Motors', 'Guftagu Restaurant', 'Elite Health Cart'];
  const lab = el('<div class="abs lbl" style="font-size:28px">Brands we have worked with</div>', { left: '64px', top: '1128px' });
  const tb = W('l03', 'businesses') - .2;
  add(lab, tb, t1, 'up');
  [0, 1].forEach(r => {
    const m = el('<div class="marq"></div>', { top: px(1172 + r * 100) });
    const list = r ? brands.slice(6).concat(brands.slice(0, 6)) : brands;
    m.innerHTML = list.concat(list).map(b => `<span class="chip" style="font-size:36px;padding:14px 28px;margin-right:16px;background:rgba(64,50,38,.95);border-color:rgba(246,181,58,.45);color:#fff8ee">${b}</span>`).join('');
    m._marq = { dir: r ? 1 : -1, speed: 70 };
    add(m, tb + r * .15, t1, 'up');
  });
}

// 4 · leaks
{
  const { t0, t1 } = sc.leaks;
  heading('Teen jagah', 'customers kho jaate hain', t0 + .05, W('l04', 'customers') - .1, t1);
  actor([['m_side', 0], ['m_serious', W('l05', 'follow-up') - .2]], 600, 880, t0 + .1, t1, 'left');
  const cards = [
    ['01', 'Visibility', 'Log dhoond nahi paate', W('l05', 'dhoond')],
    ['02', 'Conversion', 'Aa kar rukte nahi', W('l05', 'rukte')],
    ['03', 'Follow-up', 'Reply late, lead gone', W('l05', 'follow-up')],
  ];
  cards.forEach(([n, a, b, tt], i) => {
    const c = el(`<div class="abs card row" style="padding:30px 30px;width:560px;gap:16px"></div>`, { left: '64px', top: px(600 + i * 190) });
    el(`<div class="num">${n}</div>`, {}, c);
    el(`<div style="flex:1"><div class="t1">${a}</div><div class="t2">${b}</div></div>`, {}, c);
    el(`<div style="width:18px;height:18px;border-radius:50%;background:var(--red);box-shadow:0 0 0 8px rgba(227,52,58,.18)"></div>`, {}, c);
    add(c, tt - .35, t1, 'right', { sfx: 'pop' });
  });
}

// 5 · system
{
  const { t0, t1 } = sc.system;
  heading('Sab kuch,', 'ek connected system mein', t0 + .05, W('l06', 'system') - .2, t1);
  panel('system', 40, 470, 600, t0 + .1, t1, L('l06').t0, 'up');
  const svc = [['Content', 'posts, reels, design', 'content'], ['Ads', 'Meta & Google', 'ads'], ['Website', '+ Shopify stores', 'website'], ['SEO', 'local visibility', 'seo'], ['Automation', 'lead follow-up', 'automation']];
  const list = el('<div class="abs card" style="padding:18px 28px;width:450px"></div>', { left: '590px', top: '510px' });
  add(list, t0 + .25, t1, 'pop', { d: .5 });
  svc.forEach(([a, b, k], i) => {
    const tt = W('l06', k);
    const r = el(`<div class="row" style="padding:16px 0;${i ? 'border-top:1.5px solid rgba(246,181,58,.12)' : ''}"></div>`, {}, list);
    check(r, tt + .05);
    el(`<div><div class="t1" style="font-size:38px">${a}</div><div class="t2" style="font-size:26px">${b}</div></div>`, {}, r);
  });
  const badge = el(`<div class="abs card row" style="padding:22px 30px;width:540px;gap:20px;border-color:rgba(246,181,58,.55)"><img src="assets/logo_icon.png" style="width:74px"><div><div class="lbl">OutputDM</div><div class="t1" style="font-size:38px">1 connected system</div></div></div>`, { left: '470px', top: '1215px' });
  add(badge, W('l06', 'system') - .1, t1, 'pop', { sfx: 'ding' });
}

// 6 · only what you need
{
  const { t0, t1 } = sc.only;
  heading('Sirf wohi', 'jo aap ke business ko chahiye', t0 + .05, W('l07', 'jo') - .1, t1);
  panel('only', 420, 470, 620, t0 + .1, t1, L('l07').t0, 'left');
  const opts = [['Social media', 1], ['Paid ads', 1], ['Shopify store', 0], ['Every service', 0], ['Lead follow-up', 1]];
  const c = el('<div class="abs card" style="padding:26px 30px;width:470px"></div>', { left: '56px', top: '600px' });
  el('<div class="lbl" style="margin-bottom:10px">Aap ka plan</div>', {}, c);
  add(c, t0 + .2, t1, 'pop', { sfx: 'pop' });
  const tSel = W('l07', 'sirf');
  opts.forEach(([a, need], i) => {
    const r = el(`<div class="row" style="padding:13px 0;position:relative"></div>`, {}, c);
    if (need) check(r, tSel + .15 + i * .12);
    else el(`<div class="chk" style="border-color:rgba(185,171,156,.35)"></div>`, {}, r);
    const tx = el(`<div class="t1" style="font-size:39px;position:relative">${a}</div>`, {}, r);
    if (!need) { const s = el('<div class="strike"></div>', { width: '0px' }, tx); s._strike = [tSel + .2 + i * .1, tx]; tx._dim = tSel + .2; }
  });
}

// 7 · CTA
{
  const { t0, t1 } = sc.cta;
  heading('Free Digital<br>Growth Review', 'abhi WhatsApp karein', t0 + .05, W('l08', 'abhi') - .15, t1 + 1);
  actor([['m_seated', 0], ['m_smile', W('l08', 'whatsapp') - .3]], 520, 820, t0 + .1, t1 + 1, 'left');
  const wa = el(`<div class="abs card row" style="padding:26px 30px;width:540px;gap:22px"><div class="wa">${WA}</div><div><div class="lbl" style="color:#7be3a2">WhatsApp</div><div style="font-family:Jost;font-weight:700;font-size:42px;white-space:nowrap">0344 444 1724</div></div></div>`, { left: '64px', top: '1030px' });
  add(wa, W('l08', 'whatsapp') - .25, t1 + 1, 'pop', { sfx: 'ding' });
  const lg = el('<img class="abs" src="assets/logo.png" style="width:300px">', { left: '80px', top: '590px' });
  add(lg, W('l09', 'outputdm') - .2, t1 + 1, 'pop', { sfx: 'pop' });
  const web = el('<div class="abs chip" style="font-size:36px">outputdm.com</div>', { left: '96px', top: '895px' });
  add(web, W('l09', 'dot'), t1 + 1, 'up');
  const tf = L('l09').t1 + .55;
  const fol = el(`<div class="abs chip" style="padding:14px 18px 14px 30px;gap:22px">@outputdm <span class="btn" style="background:var(--gold);color:#1a120b">Follow</span></div>`, { left: '0px', top: '1410px' });
  fol._follow = [tf, tf + 1.15];
  add(fol, tf, t1 + 1, 'pop', { sfx: 'pop' });
  EV.push({ t: +(tf + 1.15).toFixed(3), type: 'click' });
}

// ---------- captions + watermark ----------
const cap = el('<div id="cap"></div>');
const wm = el('<div id="wm">@outputdm</div>');
let capKey = '';

// ================= RENDER =================
function fxStyle(it, t) {
  const pin = seg(t, it.tin, it.tin + it.d), pout = seg(t, it.tout - .32, it.tout);
  let o = eo(pin) * (1 - eo(pout)), tf = '', fl = '';
  const k = 1 - pin;
  switch (it.fx) {
    case 'up': tf = `translateY(${60 * Math.pow(k, 2.2)}px)`; break;
    case 'left': tf = `translateX(${140 * Math.pow(k, 2.2)}px)`; break;
    case 'right': tf = `translateX(${-140 * Math.pow(k, 2.2)}px)`; break;
    case 'pop': tf = `scale(${.82 + .18 * back(pin)})`; break;
    case 'blur': tf = `translateY(${24 * Math.pow(k, 2)}px)`; fl = `blur(${14 * Math.pow(k, 1.5)}px)`; break;
    case 'shake': { const s = seg(t, it.tin, it.tin + .55); tf = `scale(${.82 + .18 * back(pin)}) translateX(${Math.sin(s * 28) * 14 * (1 - s)}px)`; break; }
    case 'fade': break;
  }
  tf += ` translateY(${-28 * eio(pout)}px)`;
  if (pout > 0) fl += ` blur(${8 * pout}px)`;
  return { o, tf, fl, pin };
}

window.render = async t => {
  const pend = [];
  // background drift
  blobs[0].style.transform = `translate(${-120 + 90 * Math.sin(t * .23)}px, ${-160 + 70 * Math.cos(t * .19)}px)`;
  blobs[1].style.transform = `translate(${560 + 80 * Math.cos(t * .17)}px, ${980 + 90 * Math.sin(t * .21)}px)`;
  blobs[2].style.transform = `translate(${380 + 120 * Math.sin(t * .13 + 1)}px, ${380 + 140 * Math.sin(t * .11)}px)`;

  for (const it of items) {
    const n = it.n;
    if (t < it.tin - .01 || t > it.tout + .01) { n.style.opacity = 0; continue; }
    const { o, tf, fl } = fxStyle(it, t);
    let extra = '';
    if (it.idle) extra = ` translateY(${Math.sin(t * 1.6) * 5}px) scale(${1 + .006 * Math.sin(t * 1.1)})`;
    if (n._marq) extra = ` translateX(${n._marq.dir < 0 ? -n._marq.speed * (t - it.tin) : -900 + n._marq.speed * (t - it.tin)}px)`;
    n.style.opacity = o; n.style.transform = tf + extra; n.style.filter = fl || 'none';
    if (n._grow) { const [a, b, h] = n._grow; n.style.height = px(h * eio(seg(t, a, b))); }
    if (n._follow) {
      const [a, b] = n._follow, on = t >= b, btn = n.querySelector('.btn');
      btn.textContent = on ? 'Following ✓' : 'Follow';
      btn.style.background = on ? 'transparent' : 'var(--gold)'; btn.style.color = on ? 'var(--gold)' : '#1a120b';
      btn.style.border = on ? '2px solid var(--gold)' : '2px solid transparent';
      n.style.left = px((1080 - n.offsetWidth) / 2);
    }
  }
  for (const a of actors) {
    const ps = a._p; let cur = 0; ps.forEach((p, i) => { if (t >= p.t) cur = i; });
    ps.forEach((p, i) => {
      const nx = ps[i + 1], fin = i === 0 ? 1 : seg(t, p.t, p.t + .4), fout = nx ? seg(t, nx.t, nx.t + .4) : 0;
      const o = eio(fin) * (1 - eio(fout));
      const turn = (1 - eio(fin)) * 6 - eio(fout) * 6;
      p.img.style.opacity = o;
      p.img.style.filter = o < 1 ? `blur(${(1 - o) * 4}px)` : 'none';
      const br = 1 + .012 * Math.sin(t * 2.2), sw = 1.4 * Math.sin(t * .9), sx = 6 * Math.sin(t * .6);
      p.img.style.transform = `translateX(calc(-50% + ${sx + turn * 4}px)) rotate(${sw}deg) scaleY(${br}) scaleX(${2 - br})`;
    });
  }
  for (const p of panels) {
    const k = p._talk, img = p.firstElementChild;
    if (t < k.tin - .01 || t > k.tout + .01) continue;
    let src;
    if (k.n) { const i = Math.min(k.n, Math.max(1, Math.floor((t - k.t0) * 30) + 1)); src = `talk/${k.scene}/f_${String(i).padStart(4, '0')}.jpg`; }
    else src = `talk/${k.scene}/still.jpg`;
    if (img._src !== src) { img._src = src; img.src = src; pend.push(img.decode().catch(() => {})); }
    img.style.transform = `scale(${1.02 + .05 * seg(t, k.tin, k.tout)})`;
  }
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
  const key = ch ? ch.t0 : '';
  if (key !== capKey) { cap.innerHTML = ch ? ch.words.map(w => `<span>${w.w.replace(/[.,]$/, '')}</span>`).join('') : ''; capKey = key; }
  if (ch) {
    const p = seg(t, ch.t0, ch.t0 + .16);
    cap.style.opacity = eo(p); cap.style.transform = `translateY(${14 * (1 - eo(p))}px) scale(${.96 + .04 * eo(p)})`;
    let on = -1; ch.words.forEach((w, i) => { if (t >= w.t0 - .03) on = i; });
    [...cap.children].forEach((s, i) => { s.className = i === on ? 'on' : ''; });
  }
  wm.style.opacity = eo(seg(t, .3, 1));
  await Promise.all(pend);
};

window.DUR = TL.dur;
window.EV = EV.sort((a, b) => a.t - b.t);

// ---------- ready once fonts and every image are loaded ----------
await document.fonts.load('800 92px Playfair'); await document.fonts.load('italic 700 52px Playfair');
await document.fonts.load('700 42px Jost'); await document.fonts.load('500 29px Jost'); await document.fonts.load('600 24px Jost');
await document.fonts.load('900 64px Playfair');
await Promise.all([...document.images].map(i => i.complete ? 0 : new Promise(r => { i.onload = r; i.onerror = r; })));
await document.fonts.ready;
await window.render(0);
window.READY = true;
