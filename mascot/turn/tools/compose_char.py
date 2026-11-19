"""Character layer for the 360 + talking clip: RGBA frames at 60 fps, ready to lay over the HyperFrames stage.

0.00-0.20  front, still (the thumbnail)
0.20-0.42  wind-up: turns 12 degrees the other way
0.42-1.62  the full 360 (FILM turnaround of the six library angles, 180-degree shutter motion blur)
1.62-1.85  overshoot 8 degrees and settle on the front
1.85-      talking: the mascot/anim body (GPT-key arm clips + FILM in-betweens), mouth patches from lipsync.py
           on every frame; wave on "Assalam o Alaikum", both hands present on "Main Zarkhaiz, OutputDM ka founder".

Usage: python3 compose_char.py OUTDIR [--scale 1.12]
Writes OUTDIR/c_0000.png ... and OUTDIR/char.json (fps, frames, size, angle per frame for the stage's turntable).
"""
import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_turn  # noqa: E402

ANIM = HERE.parents[1] / "anim" / "out"
TURN = HERE.parent / "out"
FPS = 60
DUR = 5.3
VO_AT = 1.80           # voice l02 starts here (keep in step with video/turn360/index.html)
TALK_AT = 1.85
W, H = 820, 1240


def smoother(x):
    x = min(max(x, 0), 1)
    return x * x * x * (x * (x * 6 - 15) + 10)


def ease_io3(x):
    x = min(max(x, 0), 1)
    return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def angle(t):
    """Body angle in degrees (0 = front, positive = face turns toward the viewer's left). Same curve in the HTML."""
    if t < .20:
        return 0.0
    if t < .42:
        return -12 * (1 - math.cos(math.pi * (t - .20) / .22)) / 2
    if t < 1.62:
        return -12 + 380 * ease_io3((t - .42) / 1.20)
    if t < 1.85:
        p = (t - 1.62) / .23
        return 360 + 8 * math.sin(math.pi * min(p * 1.15, 1)) * (1 - p) ** .5
    return 360.0


# ---------------- talking body ----------------
class Body:
    def __init__(self):
        self.a = json.load(open(ANIM / "anim.json"))
        self.cache = {}
        self.faces = {k: np.array(Image.open(ANIM / v["src"]).convert("RGBA")).astype(np.float32)
                      for k, v in self.a["faces"].items() if v["kind"] == "mouth"}

    def img(self, f):
        if f not in self.cache:
            self.cache[f] = np.array(Image.open(ANIM / f).convert("RGBA")).astype(np.float32)
        return self.cache[f]

    def clips(self, side, plan):
        """plan: [(t, state)] -> list of (t0, d, frames)."""
        cur, free, out = "rest", -9, []
        for t, st in plan:
            fr = self.a["trans"][f"{side}:{cur}>{st}"]
            d = min(1.05, .36 + .0125 * len(fr))
            t0 = max(t, free + .12)
            out.append((t0, d, fr)); cur = st; free = t0 + d
        return out, cur

    def half(self, side, clips, rest_state, t):
        state_file = self.a["states"][side]["rest"]
        for t0, d, fr in clips:
            if t >= t0 + d:
                state_file = fr[-1]
            elif t >= t0:
                p = smoother((t - t0) / d) * (len(fr) - 1)
                i = int(p); s = p - i
                a = self.img(fr[i]); b = self.img(fr[min(i + 1, len(fr) - 1)])
                return a * (1 - s) + b * s
        return self.img(state_file)

    def frame(self, t, arms, mouth_w):
        """arms: {'L': clips, 'R': clips}; mouth_w: {shape: weight} (weights sum <= 1, rest = closed)."""
        out = np.zeros((H, W, 4), np.float32)
        for side in ("L", "R"):
            x0, x1 = self.a["half"][side]
            hf = self.half(side, arms[side], None, t)
            al = hf[:, :, 3:4] / 255
            out[:, x0:x1, :3] = hf[:, :, :3] * al + out[:, x0:x1, :3] * (1 - al)
            out[:, x0:x1, 3:4] = 255 * (al + out[:, x0:x1, 3:4] / 255 * (1 - al))
        fx, fy, fw, fh = self.a["face_box"]
        base = out[fy:fy + fh, fx:fx + fw].copy()
        acc = base * (1 - sum(mouth_w.values()))
        for shp, w in mouth_w.items():
            p = self.faces[shp]
            al = p[:, :, 3:4] / 255
            c = base.copy()
            c[:, :, :3] = p[:, :, :3] * al + base[:, :, :3] * (1 - al)
            acc += c * w
        out[fy:fy + fh, fx:fx + fw] = acc
        return out


def mouth_weights(shapes, t):
    """Shape per voice frame -> weights at time t, with a 2-frame cross-fade on every change."""
    k = (t - VO_AT) * FPS
    if k < 0 or k >= len(shapes):
        return {}
    i = int(k)
    cur = shapes[i]
    prev = shapes[i - 1] if i > 0 else "closed"
    # how long has cur been held?
    j = i
    while j > 0 and shapes[j - 1] == cur:
        j -= 1
    f = min(1.0, (k - j + 1) / 2)          # 0.5 on the first frame of a new shape, 1 from the second
    w = {}
    if cur != "closed":
        w[cur] = w.get(cur, 0) + f
    if prev != cur and f < 1 and prev != "closed":
        w[prev] = w.get(prev, 0) + (1 - f)
    return w


def over_premul(frames):
    """Average RGBA float frames in premultiplied space (motion blur)."""
    acc = np.zeros_like(frames[0])
    for f in frames:
        a = f[:, :, 3:4] / 255
        acc[:, :, :3] += f[:, :, :3] * a
        acc[:, :, 3:4] += f[:, :, 3:4]
    acc /= len(frames)
    a = acc[:, :, 3:4] / 255
    acc[:, :, :3] = np.where(a > 1e-3, acc[:, :, :3] / np.maximum(a, 1e-3), 0)
    return acc


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--scale", type=float, default=1.12)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    dense = build_turn.Dense()
    body = Body()
    shapes = json.load(open(TURN / "l02_mouth.json"))["shapes"]
    tr = body.a["trans"]
    # FILM in-betweens where the hand dissolves (between two GPT keys far apart) are skipped: the arm snaps
    # through them in a frame or two, which reads as a fast move instead of a melting hand.
    up = [f for i, f in enumerate(tr["L:rest>wave"]) if not 13 <= i <= 19]
    wave = tr["L:rest>wave"]
    pump = [wave[k] for k in (40, 37, 35, 37, 40, 37, 35, 37, 40)]           # the raised hand waves twice
    down = [f for i, f in enumerate(tr["L:wave>present"]) if not 23 <= i <= 28]
    armsL = [(TALK_AT, .62, up), (2.48, .44, pump), (2.94, .92, down)]
    armsR = [(3.06, .62, tr["R:rest>present"])]
    arms = {"L": armsL, "R": armsR}
    sw, sh = int(round(W * a.scale / 2)) * 2, int(round(H * a.scale / 2)) * 2
    n = int(round(DUR * FPS))
    only = {int(x) for x in a.only.split(",") if x}
    meta = []
    for i in range(n):
        t = i / FPS
        th = angle(t)
        meta.append(round(th, 3))
        if only and i not in only:
            continue
        if t < TALK_AT:
            if th == 0.0 or th == 360.0:
                fr = dense.frame_at(0).astype(np.float32)
            else:
                # 180-degree shutter: 9 samples across half a frame interval
                subs = [angle(t + (k / 8 - .5) * .5 / FPS) for k in range(9)]
                if max(subs) - min(subs) < .4:
                    fr = dense.frame_at(th).astype(np.float32)
                else:
                    fr = over_premul([dense.frame_at(s).astype(np.float32) for s in subs])
            # hand over to the talking body over 4 frames before TALK_AT
            k = (TALK_AT - t) * FPS
            if k < 4:
                tb = body.frame(t, arms, {})
                w = 1 - k / 4
                fr = over_mix(fr, tb, w)
        else:
            fr = body.frame(t, arms, mouth_weights(shapes, t))
        im = Image.fromarray(np.clip(fr + .5, 0, 255).astype(np.uint8), "RGBA").resize((sw, sh), Image.LANCZOS)
        im.save(out / f"c_{i:04d}.png", compress_level=1)
        if i % 30 == 0:
            print("frame", i, flush=True)
    json.dump({"fps": FPS, "frames": n, "size": [sw, sh], "scale": a.scale, "vo_at": VO_AT, "angle": meta},
              open(out / "char.json", "w"))


def over_mix(a, b, w):
    """Cross-fade two RGBA float frames in premultiplied space."""
    pa = a.copy(); pb = b.copy()
    pa[:, :, :3] *= pa[:, :, 3:4] / 255; pb[:, :, :3] *= pb[:, :, 3:4] / 255
    m = pa * (1 - w) + pb * w
    al = m[:, :, 3:4] / 255
    m[:, :, :3] = np.where(al > 1e-3, m[:, :, :3] / np.maximum(al, 1e-3), 0)
    return m


if __name__ == "__main__":
    main()
