"""Dense 360-degree turnaround of the mascot: the six library bodies + FILM in-between frames.

The six angles (front, 34left, profileleft, back, profileright, 34right) are real library images. FILM fills the gaps
twice, on a black and on a white ground; the alpha of every in-between frame is the difference of the two (exact for
the linear blends FILM makes; a green-screen key was tried first and left green hands). Steps are finer where the turn is slow (around the front) and coarser across
the back, which the turn crosses fast and under motion blur.

Usage: python3 build_turn.py            (cached: only missing segments are computed; about 15 s per FILM frame on CPU)
Writes out/dense_k/*.png and out/dense_w/*.png (RGB crops on black / white) and out/dense.json [{"file", "angle"}].
Then frame_at(angle) gives an RGBA 820x1240 frame for any angle (blend of the two nearest dense frames).
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "anim" / "tools"))
LIB = HERE.parents[1] / "library" / "bodies"
OUT = HERE.parent / "out" / "dense"
G = np.array([0, 255, 0], np.float32)
BGS = {"k": np.array([0, 0, 0], np.float32), "w": np.array([255, 255, 255], np.float32)}
W, H = 820, 1240
CROP = (185, 199, 617, 1231)          # x0, y0, x1, y1: union of all six bodies + margin
KEYS = [("front", 0), ("34left", 45), ("profileleft", 90), ("back", 180), ("profileright", 270), ("34right", 315),
        ("front", 360)]
STEPS = {0: 7, 45: 3, 90: 3, 180: 3, 270: 3, 315: 7}   # in-betweens after each key angle


def body(v):
    import cv2
    a = np.array(Image.open(LIB / v / "neutral.png").convert("RGBA"))
    al = a[:, :, 3]
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))       # the edge clean of mascot/anim/tools/edges.py
    a[:, :, 3] = np.minimum(al, cv2.GaussianBlur(cv2.erode(al, k), (0, 0), 1.1))
    return a


def on_green(a, bg=G):
    al = a[:, :, 3:4].astype(np.float32) / 255
    rgb = a[:, :, :3] * al + bg * (1 - al)
    x0, y0, x1, y1 = CROP
    return np.clip(rgb + .5, 0, 255).astype(np.uint8)[y0:y1, x0:x1]


def key_green(rgb):
    """RGB on green -> RGBA 820x1240 (alpha from the green excess, colour un-premultiplied, spill removed)."""
    f = rgb.astype(np.float32)
    r, g, b = f[..., 0], f[..., 1], f[..., 2]
    spill = g - np.maximum(r, b)
    a = np.clip(1 - spill / 255, 0, 1)
    a = np.clip((a - .04) / .92, 0, 1)                    # snap almost-clear and almost-solid pixels
    c = (f - (1 - a[..., None]) * G) / np.maximum(a[..., None], 1e-3)
    c[..., 1] = np.minimum(c[..., 1], np.maximum(c[..., 0], c[..., 2]) + 18)   # despill
    out = np.zeros((H, W, 4), np.uint8)
    x0, y0, x1, y1 = CROP
    out[y0:y1, x0:x1, :3] = np.clip(c, 0, 255).astype(np.uint8)
    out[y0:y1, x0:x1, 3] = (a * 255 + .5).astype(np.uint8)
    return out


def build():
    """Write out/dense.json: the angle of every dense frame (file names are shared by dense_k/ and dense_w/)."""
    seq = []
    for (va, ta), (vb, tb) in zip(KEYS, KEYS[1:]):
        n = STEPS[ta]
        for i in range(n + 1):
            seq.append({"file": f"{ta:03d}_{i:02d}.png", "angle": ta + (tb - ta) * i / (n + 1)})
    seq.append({"file": seq[0]["file"], "angle": 360.0})
    json.dump(seq, open(OUT.parent / "dense.json", "w"), indent=1)
    return seq


def build_bw():
    """FILM on black and on white grounds: alpha by difference matting (exact for linear blends), no green spill."""
    import film
    for tag, bg in BGS.items():
        d = OUT.parent / f"dense_{tag}"
        d.mkdir(parents=True, exist_ok=True)
        for (va, ta), (vb, tb) in zip(KEYS, KEYS[1:]):
            n = STEPS[ta]
            names = [f"{ta:03d}_{i:02d}.png" for i in range(n + 1)]
            if all((d / f).exists() for f in names):
                continue
            A, B = on_green(body(va), bg), on_green(body(vb), bg)
            for f, im in zip(names, [A] + film.interpolate(A, B, n)):
                Image.fromarray(im).save(d / f)
            print("segment", tag, va, "->", vb, flush=True)


def key_bw(k, w):
    """Black-ground and white-ground crops (float) -> RGBA 820x1240."""
    a = np.clip(1 - (w - k).mean(2) / 255, 0, 1)
    a = np.clip((a - .03) / .94, 0, 1)
    c = np.clip(k / np.maximum(a[..., None], 1e-3), 0, 255)
    out = np.zeros((H, W, 4), np.uint8)
    x0, y0, x1, y1 = CROP
    out[y0:y1, x0:x1, :3] = (c + .5).astype(np.uint8)
    out[y0:y1, x0:x1, 3] = (a * 255 + .5).astype(np.uint8)
    return out


class Dense:
    def __init__(self):
        self.seq = json.load(open(OUT.parent / "dense.json"))
        self.ang = np.array([s["angle"] for s in self.seq])
        self.cache = {}

    def rgb(self, i, tag="k"):
        f = self.seq[i]["file"]
        key = (tag, f)
        if key not in self.cache:
            self.cache[key] = np.array(Image.open(OUT.parent / f"dense_{tag}" / f).convert("RGB")).astype(np.float32)
        return self.cache[key]

    def at(self, th, tag):
        """Crop on one ground for any angle (linear blend of the two nearest dense frames)."""
        th = th % 360
        j = int(np.searchsorted(self.ang, th, side="right")) - 1
        j = min(max(j, 0), len(self.ang) - 2)
        s = (th - self.ang[j]) / (self.ang[j + 1] - self.ang[j])
        return self.rgb(j, tag) * (1 - s) + self.rgb(j + 1, tag) * s

    def frame_at(self, th):
        return key_bw(self.at(th, "k"), self.at(th, "w"))


if __name__ == "__main__":
    import torch
    import film
    film._model()
    torch.set_num_threads(2)
    build()
    build_bw()
    print("done", flush=True)
