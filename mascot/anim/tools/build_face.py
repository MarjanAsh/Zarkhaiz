"""Build the animated head for the reel (v017): one LivePortrait frame per 1/30 s of the reel.

Every frame is the master's own face re-posed by lp_face.Face from a parameter track:
  - mouth: opens with the loudness of the real voiceover (vo/*.wav at each line's t0), rounder on o/u words;
  - expression: smile and brows per line (concerned on the problem lines, warm on the greeting and the CTA);
  - life: blinks, small nods on line starts, a slow idle head turn.
Output: out/head/NNNN.webp (RGBA patches in the 820x1240 body canvas), out/head/erase.png (where the page removes
the master's head before adding the patch) and out/face.json {fps, box, erase, frames}.

Usage: python3 build_face.py [--part K N] [--every M] [--sheet out.jpg]
  --part K N   render only frames with index % N == K (run N processes side by side; set LP_THREADS for each)
  --every M    render only every M-th frame (quick preview; the frames are kept, a later full run skips them)
  --sheet F    contact sheet of the rendered frames
Then: python3 build_face.py --finish     (writes face.json once all frames exist)
"""
import hashlib, json, math, sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy.io import wavfile

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "raw", ROOT / "out"
REEL = ROOT.parents[1] / "video" / "outputdm-reel"
W, H = 820, 1240
FPS = 30
BOX = (300, 170, 510, 448)         # x0, y0, x1, y1 of the head patch in the body canvas


def canvas(rgb):
    return np.array(Image.fromarray(rgb).crop((4, 0, 1020, 1536)).resize((W, H), Image.LANCZOS))


def sm(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def bump(t, t0, d):
    """0 -> 1 -> 0 over d seconds starting at t0."""
    u = (t - t0) / d
    return math.sin(math.pi * u) ** 2 if 0 < u < 1 else 0.0


# ---------- parameter track ----------
def track():
    TL = json.loads((REEL / "timeline.json").read_text())
    L = {l["id"]: l for l in TL["lines"]}
    dur = TL["dur"]
    n = int(round(dur * FPS)) + 1
    # voice loudness per frame
    env = np.zeros(n + 8)
    for l in TL["lines"]:
        sr, x = wavfile.read(REEL / "vo" / f"{l['id']}.wav")
        x = x.astype(np.float32)
        if x.ndim > 1:
            x = x.mean(1)
        x /= (np.abs(x).max() or 1)
        hop = sr / FPS
        for i in range(int(len(x) / hop)):
            seg = x[int(i * hop):int((i + 1) * hop)]
            k = int(round(l["t0"] * FPS)) + i
            if k < len(env):
                env[k] = max(env[k], float(np.sqrt((seg ** 2).mean())))
    env = np.clip(env / np.percentile(env[env > .01], 88), 0, 1) ** .75
    # the mouth leads the sound by a frame, opens fast, closes a little slower
    mouth = np.zeros_like(env)
    for i in range(len(env) - 1):
        target = max(env[i], env[i + 1] * .8)
        prev = mouth[i - 1] if i else 0
        mouth[i] = target if target > prev else prev + (target - prev) * .55
    words = TL["words"]

    def word(line, w):
        return next(x for x in words if x["line"] == line and x["w"].lower().strip(".,!?") == w)

    # expression keys: (time, smile, brow); values glide to the next key over .45 s
    keys = [(-9, .35, 0), (L["l01"]["t0"] - .2, .2, 6), (word("l01", "lekin")["t0"] - .15, -.25, -18),
            (L["l01"]["t1"] + .15, .9, 8), (L["l03"]["t0"] - .2, .55, 3),
            (L["l04"]["t0"] - .2, -.05, -12), (L["l05"]["t0"] - .1, -.2, -18),
            (L["l05"]["t1"] + .1, .7, 8), (L["l07"]["t0"] - .2, .5, 2), (L["l08"]["t0"] - .2, .85, 10),
            (L["l09"]["t1"] + .35, 1.25, 6)]
    blinks = []
    t = 1.9
    while t < dur:
        blinks.append(t)
        t += 2.9 + 1.7 * ((math.sin(t * 12.9898) * 43758.5453) % 1)
    out = []
    for i in range(n):
        t = i / FPS
        k = max(j for j in range(len(keys)) if keys[j][0] <= t)
        a, b = keys[max(0, k - 1)], keys[k]
        u = sm((t - b[0]) / .45)
        smile, brow = a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u
        m = float(mouth[i])
        p = dict(smile=smile, brow=brow)
        nod = 0.0
        for l in TL["lines"]:
            nod += bump(t, l["t0"] - .05, .5)
            brow += 7 * bump(t, l["t0"], .6)
        p["brow"] = brow
        p["pitch"] = 1.0 * math.sin(.7 * t + 2) + 3.2 * nod + 1.2 * m
        p["yaw"] = 2.2 * math.sin(.5 * t) + .8 * math.sin(1.3 * t + 1)
        p["roll"] = .8 * math.sin(.43 * t) + (1.5 if smile < 0 else 0) * min(1, -smile * 5)
        if m > .06:
            p["lip"] = .02 + .25 * m
            wd = next((x for x in words if x["t0"] <= t < x["t1"]), None)
            if wd and (wd["w"].lower().find("o") >= 0 or wd["w"].lower().find("u") >= 0):
                p["woo"] = 6 * m
        e = None
        for bt in blinks:
            v = bump(t, bt, .23)
            if v > 0:
                e = .30 * (1 - v)
        if e is not None and e < .27:
            p["eye"] = e
        out.append({k2: round(v, 2 if k2 in ("smile", "lip", "eye") else 1) for k2, v in p.items()})
    return out


# ---------- masks ----------
def masks(master_c):
    """Mh: soft region of the head patch (1 on the head, fading out over the collar)."""
    near = (master_c.min(2) > 236).astype(np.uint8)
    ff = near.copy()
    cv2.floodFill(ff, None, (2, 2), 2)
    sil = (ff != 2)
    r = np.zeros((H, W), np.uint8)
    r[208:404, 318:492] = sil[208:404, 318:492]
    r[:208, 300:510] = sil[:208, 300:510]
    r[380:440, 360:450] = 1
    r = cv2.dilate(r, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (27, 27)))
    m = cv2.GaussianBlur(r.astype(np.float32), (0, 0), 3)
    fade = np.clip((438 - np.arange(H)) / 22, 0, 1)[:, None]
    return m * fade


def patch(frame_c, mh):
    x0, y0, x1, y1 = BOX
    sub = frame_c[y0:y1, x0:x1].astype(np.float32)
    near = (sub.min(2) > 225).astype(np.uint8)
    ff = near.copy()
    for pt in ((1, 1), (x1 - x0 - 2, 1), (1, 120), (x1 - x0 - 2, 120)):
        if ff[pt[1], pt[0]] == 1:
            cv2.floodFill(ff, None, pt, 2)
    bg = (ff == 2)
    dist = 255 - sub.min(2)
    ak = np.clip((dist - 10) / 40, 0, 1)
    ak = ak * ak * (3 - 2 * ak)
    bgs = cv2.GaussianBlur(cv2.dilate(bg.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 1.2)
    a = np.where(bgs > .02, np.minimum(ak, 1 - bgs), 1.0)      # white key only next to the background
    a = np.where(bg, 0, a)
    un = (sub - (1 - a[:, :, None]) * 255) / np.maximum(a[:, :, None], .05)
    rgb = np.where((a[:, :, None] > .02) & (a[:, :, None] < 1), np.clip(un, 0, 255), sub)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    e = cv2.GaussianBlur(cv2.erode(a, k, borderType=cv2.BORDER_REPLICATE), (0, 0), 1.1, borderType=cv2.BORDER_REPLICATE)
    a = np.minimum(a, e) * mh[y0:y1, x0:x1]
    return np.dstack([rgb, a * 255]).astype(np.uint8)


def name(p):
    return hashlib.md5(json.dumps(p, sort_keys=True).encode()).hexdigest()[:12] + ".webp"


def main():
    args = sys.argv[1:]
    hd = OUT / "head"
    hd.mkdir(parents=True, exist_ok=True)
    tr = track()
    files = [name(p) for p in tr]
    if "--finish" in args:
        miss = sorted({f for f in files if not (hd / f).exists()})
        if miss:
            sys.exit(f"{len(miss)} frames missing")
        x0, y0, x1, y1 = BOX
        (OUT / "face.json").write_text(json.dumps({"fps": FPS, "box": [x0, y0, x1 - x0, y1 - y0],
                                                   "erase": "head/erase.png", "frames": [f"head/{f}" for f in files]}))
        keep = set(files) | {"erase.png"}
        for f in hd.iterdir():
            if f.name not in keep:
                f.unlink()
        print(len(set(files)), "distinct frames,", sum((hd / f).stat().st_size for f in set(files)) // 1024, "KB")
        return
    idx = list(range(len(tr)))
    if "--every" in args:
        m = int(args[args.index("--every") + 1]); idx = idx[::m]
    if "--part" in args:
        k, n = int(args[args.index("--part") + 1]), int(args[args.index("--part") + 2]); idx = [i for i in idx if i % n == k]
    todo = [i for i in idx if not (hd / files[i]).exists()]
    if todo:
        sys.path.insert(0, str(Path(__file__).parent))
        from lp_face import Face
        face = Face(str(RAW / "master.png"))
        mh = masks(canvas(face.img))
        x0, y0, x1, y1 = BOX
        er = np.zeros((y1 - y0, x1 - x0, 4), np.uint8); er[:, :, 3] = (mh[y0:y1, x0:x1] * 255).astype(np.uint8)
        Image.fromarray(er).save(hd / "erase.png")
        for n_, i in enumerate(todo):
            if (hd / files[i]).exists():
                continue
            im = patch(canvas(face.render(**tr[i])), mh)
            Image.fromarray(im).save(hd / files[i], "WEBP", quality=88, method=4)
            if n_ % 20 == 0:
                print(n_, "/", len(todo), flush=True)
    if "--sheet" in args:
        cols = 13
        ims = [Image.open(hd / files[i]) for i in idx]
        w, h = ims[0].size
        sh = Image.new("RGB", (cols * w, -(-len(ims) // cols) * h), (40, 30, 20))
        for j, im in enumerate(ims):
            sh.paste(im, ((j % cols) * w, (j // cols) * h), im)
        sh.save(args[args.index("--sheet") + 1], quality=85)


if __name__ == "__main__":
    main()
