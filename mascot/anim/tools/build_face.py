"""Build the animated head for the reel: LivePortrait frames of the master's own face (v017, changed in v018).

Every frame is the master's face re-posed by lp_face.Face from a parameter track (track() below):
  - expression: a small change of smile and brows per line (a little concerned on the problem lines, warm on the
    greeting and the CTA). The mouth stays closed: the user wants small expressions, not a talking mouth (v018);
  - life: blinks, a small nod at each line start, a slow idle head turn.
Frames are sampled 15 times a second (30 through blinks); the page blends neighbouring frames by time.
Output: out/head/<hash>.webp (RGBA patches in the 820x1240 body canvas), out/head/erase.png (where the page removes
the master's head before adding the patch) and out/face.json {box, erase, t, frames}.

Usage: python3 build_face.py [--part K N] [--every M] [--sheet out.jpg]
  --part K N   render only frames with index % N == K (run N processes side by side; set LP_THREADS for each)
  --every M    render only every M-th frame (quick preview; the frames are kept, a later full run skips them)
  --sheet F    contact sheet of the rendered frames
Then: python3 build_face.py --finish     (writes face.json once all frames exist, removes frames no longer used)
"""
import hashlib, json, math, sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

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
    words = TL["words"]

    def word(line, w):
        return next(x for x in words if x["line"] == line and x["w"].lower().strip(".,!?") == w)

    # expression keys: (time, smile, brow); values glide to the next key over .9 s. Small expressions only (v018:
    # the user wants no talking mouth): the mouth stays closed, the smile and brows change a little per line.
    keys = [(-9, .45, 0), (L["l01"]["t0"] - .2, .35, 4), (word("l01", "lekin")["t0"] - .15, .0, -9),
            (L["l01"]["t1"] + .15, .85, 5), (L["l03"]["t0"] - .2, .55, 2),
            (L["l04"]["t0"] - .2, .15, -7), (L["l05"]["t0"] - .1, .05, -10),
            (L["l05"]["t1"] + .1, .65, 5), (L["l07"]["t0"] - .2, .5, 1), (L["l08"]["t0"] - .2, .75, 6),
            (L["l09"]["t1"] + .35, 1.0, 4)]
    blinks = []
    t = 1.9
    while t < dur:
        blinks.append(t)
        t += 2.9 + 1.7 * ((math.sin(t * 12.9898) * 43758.5453) % 1)

    def at(t):
        k = max(j for j in range(len(keys)) if keys[j][0] <= t)
        a, b = keys[max(0, k - 1)], keys[k]
        u = sm((t - b[0]) / .9)
        smile, brow = a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u
        nod = 0.0
        for l in TL["lines"]:
            nod += bump(t, l["t0"] - .1, .8)
            brow += 4 * bump(t, l["t0"], .9)
        p = dict(smile=smile, brow=brow)
        p["pitch"] = 1.0 * math.sin(.7 * t + 2) + 1.8 * nod
        p["yaw"] = 2.4 * math.sin(.5 * t) + .8 * math.sin(1.3 * t + 1)
        p["roll"] = .9 * math.sin(.43 * t) + .5 * math.sin(.9 * t + 2)
        e = None
        for bt in blinks:
            v = bump(t, bt, .23)
            if v > 0:
                e = .30 * (1 - v)
        if e is not None and e < .27:
            p["eye"] = e
        return {k2: round(v, 2 if k2 in ("smile", "eye") else 1) for k2, v in p.items()}

    # sample times: 15 per second (the page blends neighbours, the motion is slow), 30 per second through blinks
    ts = set(range(0, 2 * n, 4))
    for bt in blinks:
        ts |= set(range(int(bt * 60) // 2 * 2 - 2, int((bt + .23) * 60) + 4, 2))
    ts = sorted(x for x in ts if 0 <= x < 2 * n)
    return [x / 60 for x in ts], [at(x / 60) for x in ts]


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
    times, tr = track()
    files = [name(p) for p in tr]
    if "--finish" in args:
        miss = sorted({f for f in files if not (hd / f).exists()})
        if miss:
            sys.exit(f"{len(miss)} frames missing")
        x0, y0, x1, y1 = BOX
        (OUT / "face.json").write_text(json.dumps({"fps": FPS, "box": [x0, y0, x1 - x0, y1 - y0],
                                                   "erase": "head/erase.png", "t": [round(x, 4) for x in times],
                                                   "frames": [f"head/{f}" for f in files]}))
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
