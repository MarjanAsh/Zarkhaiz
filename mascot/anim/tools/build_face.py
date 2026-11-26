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
  --upto S     only the frames of the first S seconds (a cheap test; also with --finish, which then keeps other frames)
Then: python3 build_face.py --finish     (writes face.json once all frames exist, removes frames no longer used)
"""
import hashlib, json, math, sys
from pathlib import Path

import os
import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "raw", ROOT / "out"
REEL = Path(os.environ.get("REEL_DIR") or ROOT.parents[1] / "video" / "outputdm-reel")   # REEL_DIR: another video project
TAG = os.environ.get("ANIM_TAG", "")      # ANIM_TAG: this project's head frames go to out/head_<tag>, face_<tag>.json
W, H = 820, 1240
FPS = 30
BOX = (292, 164, 518, 448)         # x0, y0, x1, y1 of the head patch in the body canvas (wider from v020: bigger head moves)


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
    """v020: the head follows acting.json (tools/director.py) and the audio-driven mouth (tools/speech_face.py).

    Every frame = expression (base per line, glides .45 s) + accents on stressed words + head events (nod, shake,
    tilt...) + gaze + blinks + the body-turn yaw + the speech mouth and its small head motion. 30 frames a second
    while he speaks or blinks or the head acts, 15 otherwise (the page blends neighbours).
    Returns (times, params, speech): params are plain numbers; the mouth offsets are looked up again at render time.
    """
    sys.path.insert(0, str(Path(__file__).parent))
    import expressions as E
    from speech_face import Speech
    TL = json.loads((REEL / "timeline.json").read_text())
    A = json.loads((REEL / "acting.json").read_text())
    AN = json.loads((REEL / "angles.json").read_text())
    dur = TL["dur"]
    n = int(round(dur * 60)) + 1
    sp = Speech(np.load(OUT / "speech" / "master_exp.npy"), head=.3)     # a third of the generated head motion
    keys = A["face"]
    sm5 = lambda u: (lambda u: u * u * u * (u * (u * 6 - 15) + 10))(min(1.0, max(0.0, u)))

    def turn_yaw(t):
        y, ev = 0.0, A["turns"]
        for i, (tt, to) in enumerate(ev):
            if to == "front":
                continue
            t1 = ev[i + 1][0] if i + 1 < len(ev) else 1e9
            u = (t - tt) / AN["d"] if t < t1 else 1 - (t - t1) / AN["d"]
            y += (-1 if to == "tl" else 1) * AN["yaw"] * sm5(u)
        return y

    def controls(t):
        k = max(j for j in range(len(keys)) if keys[j]["t"] <= t)
        cur = E.mix(keys[k]["expr"], keys[k]["k"])
        if k > 0:
            cur = E.blend(E.mix(keys[k - 1]["expr"], keys[k - 1]["k"]), cur, sm5((t - keys[k]["t"]) / .45))
        for ac in A["accents"]:                       # a stressed word pulls the face toward its expression for a moment
            w = bump(t, ac["t"], ac["d"])
            if w > 0:
                cur = E.blend(cur, E.mix(ac["expr"], ac["k"]), .75 * w)
        c = dict(cur)
        # v020 after the user's feedback (the face "breaks", not symmetrical): calm, symmetric head. No idle roll,
        # no tilt events, smaller and slower nods and shakes, tight limits; the expression's own roll is dropped.
        c["roll"] = 0.0
        c["pitch"] += .4 * math.sin(.7 * t + 2); c["yaw"] += .8 * math.sin(.5 * t) + .3 * math.sin(1.3 * t + 1)
        act = 0.0
        for h in A["head"]:
            u = (t - h["t"]) / h["d"]
            if not 0 < u < 1:
                continue
            w, a_ = math.sin(math.pi * u) ** 2, h["amp"]
            act = max(act, w)
            if h["kind"] == "nod":
                c["pitch"] += 2.6 * a_ * w
            elif h["kind"] == "forward":
                c["pitch"] += 1.6 * a_ * w
            elif h["kind"] == "look_up":
                c["pitch"] -= 2.2 * a_ * w
            elif h["kind"] == "look_down":
                c["pitch"] += 2.2 * a_ * w
            elif h["kind"] == "tilt":
                pass                                   # tilt events are ignored (kept in old acting files)
            elif h["kind"] == "shake":
                c["yaw"] += 2.4 * a_ * math.sin(2 * math.pi * 1.5 * u) * math.sin(math.pi * u)
        for g_ in A["gaze"]:
            w = bump(t, g_["t"], g_["d"])
            c["gx"] += g_["gx"] * w; c["gy"] += g_["gy"] * w
        blink = 0.0
        for bt in A["blinks"]:
            blink = max(blink, bump(t, bt, .23))
        if blink > .05:
            c["eye"] = E.EYE_OPEN * (1 - blink)
        c["yaw"] = max(-3.5, min(3.5, c["yaw"])) + turn_yaw(t)
        c["pitch"] = max(-3.5, min(3.5, c["pitch"])); c["roll"] = 0.0
        return c, act, blink

    ts, out = [], []
    for x in range(0, n, 2):                           # 30 per second candidates
        t = x / 60
        c, act, blink = controls(t)
        s = sp.at(t)
        s["roll"] = 0.0                              # symmetric head: no roll from the generated motion either
        fast = s["speaking"] > .02 or act > .02 or blink > .02 or any(abs(t - tt - AN["d"] / 2) < AN["d"] for tt, _ in A["turns"])
        if not fast and x % 4:
            continue
        p = E.apply(c, s)
        p.pop("exp_delta", None)
        p = {k2: round(float(v), 3 if k2 in ("smile", "eye", "lip") else 1) for k2, v in p.items()}
        p["st"] = round(t, 4) if s["speaking"] > .001 else -1       # the mouth is looked up from this time
        ts.append(t); out.append(p)
    return ts, out


_SP = None


def render_params(p):
    """Parameters for Face.render: the stored numbers plus the mouth offsets for the frame's time."""
    global _SP
    q = dict(p)
    st = q.pop("st")
    if st >= 0:
        if _SP is None:
            from speech_face import Speech
            _SP = Speech(np.load(OUT / "speech" / "master_exp.npy"))
        q["exp_delta"] = _SP.at(st)["exp_delta"]
    return q


# ---------- masks ----------
def masks(master_c):
    """Mh: soft region of the head patch (1 on the head, fading out over the collar)."""
    near = (master_c.min(2) > 236).astype(np.uint8)
    ff = near.copy()
    cv2.floodFill(ff, None, (2, 2), 2)
    sil = (ff != 2)
    r = np.zeros((H, W), np.uint8)
    r[208:404, 318:492] = sil[208:404, 318:492]
    r[:208, 292:518] = sil[:208, 292:518]
    r[380:440, 360:450] = 1
    r = cv2.dilate(r, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (35, 35)))
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
    hd = OUT / ("head_" + TAG if TAG else "head")
    hd.mkdir(parents=True, exist_ok=True)
    mexp = OUT / "speech" / "master_exp.npy"       # the master's own expression keypoints (the mouth offsets start from them)
    if not mexp.exists():
        sys.path.insert(0, str(Path(__file__).parent))
        from lp_face import Face
        np.save(mexp, Face(str(RAW / "master.png")).info['exp'][0].numpy())
    times, tr = track()
    if "--upto" in args:                               # a test: only the first seconds of the reel
        lim = float(args[args.index("--upto") + 1])
        times, tr = [t for t in times if t <= lim], [p for t, p in zip(times, tr) if t <= lim]
    files = [name(p) for p in tr]
    if "--finish" in args:
        miss = sorted({f for f in files if not (hd / f).exists()})
        if miss:
            sys.exit(f"{len(miss)} frames missing")
        x0, y0, x1, y1 = BOX
        (OUT / (f"face_{TAG}.json" if TAG else "face.json")).write_text(json.dumps({"fps": FPS, "box": [x0, y0, x1 - x0, y1 - y0],
                                                   "erase": "head/erase.png", "t": [round(x, 4) for x in times],
                                                   "frames": [f"head/{f}" for f in files]}))
        keep = set(files) | {"erase.png"}
        for f in hd.iterdir():
            if f.name not in keep and "--upto" not in args and "--keep" not in args:
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
            im = patch(canvas(face.render(**render_params(tr[i]))), mh)
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
