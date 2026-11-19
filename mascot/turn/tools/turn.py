"""360-degree turn of the mascot from the six library body angles (no AI generation, runs on CPU).

Method: a visual hull (3D shape carved from the six silhouettes) gives every pixel a depth, then each frame at any
angle is rendered by looking up every visible surface point in the two nearest real library images
(view-dependent texturing). At the six key angles the result is the library image itself; in between, the body
really rotates (the nose, shoulders and shoes travel on circles) instead of two images dissolving.

Usage:
  python3 turn.py fit                 estimate the 3/4 angle from the silhouettes
  python3 turn.py render A0 A1 N OUT  render N frames from angle A0 to A1 (degrees) into OUT/turn_XXXX.png
  python3 turn.py at ANGLE OUT.png    render one angle

Angles: 0 front, +a 34left (face toward the viewer's left), 90 profileleft, 180 back, 270 profileright, 360-a 34right.
Canvas 820x1240, rotation axis x=410 (leg centre in every library body), orthographic camera.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

LIB = Path(__file__).resolve().parents[2] / "library" / "bodies"
OUT = Path(__file__).resolve().parents[1] / "out"
CX = 410
W, H = 820, 1240
VIEWS = ["front", "34left", "profileleft", "back", "profileright", "34right"]
TOL_SIL = 5      # silhouettes are dilated by this many px before carving (the six images are separate drawings)
TOL_VIS = 6      # depth tolerance for "this surface point is visible in that key image"


def load_views():
    ims = {}
    for v in VIEWS:
        a = np.array(Image.open(LIB / v / "neutral.png").convert("RGBA"))
        al = a[:, :, 3]
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))       # same edge clean as mascot/anim/tools/edges.py
        e = cv2.GaussianBlur(cv2.erode(al, k), (0, 0), 1.1)
        a[:, :, 3] = np.minimum(al, e)
        ims[v] = a
    return ims


def angles(a34):
    return {"front": 0.0, "34left": a34, "profileleft": 90.0, "back": 180.0, "profileright": 270.0,
            "34right": 360.0 - a34}


class Hull:
    """Visual hull on a full-resolution grid: x in [X0, X1), z in [-R, R), rows Y0..Y1."""
    X0, X1, R = 170, 650, 240

    def __init__(self, sils, angs, y0, y1):
        self.y0, self.y1 = y0, y1
        xs = np.arange(self.X0, self.X1) - CX
        zs = np.arange(-self.R, self.R)
        self.gx, self.gz = np.meshgrid(xs, zs, indexing="xy")        # shape (2R, X1-X0)
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * TOL_SIL + 1, 2 * TOL_SIL + 1))
        dil = {v: cv2.dilate((s > 0).astype(np.uint8), k) for v, s in sils.items()}
        uidx = {}
        for v, th in angs.items():
            t = np.radians(th)
            u = np.rint(self.gx * np.cos(t) - self.gz * np.sin(t) + CX).astype(np.int32)
            uidx[v] = np.clip(u, 0, W - 1), (u >= 0) & (u < W)
        self.vox = np.zeros((y1 - y0,) + self.gx.shape, bool)
        for y in range(y0, y1):
            m = np.ones(self.gx.shape, bool)
            for v in angs:
                ui, ok = uidx[v]
                m &= ok & (dil[v][y][ui] > 0)
            self.vox[y - y0] = m
        # surface shell (3 px) of every slice, as point lists
        shell = []
        ke = np.ones((3, 3), np.uint8)
        for i in range(self.vox.shape[0]):
            s = self.vox[i].astype(np.uint8)
            if not s.any():
                continue
            inner = cv2.erode(s, ke, iterations=3)
            zz, xx = np.nonzero(s & (1 - inner))
            shell.append(np.stack([self.gx[zz, xx], self.gz[zz, xx], np.full(len(zz), i + y0)], 1))
        self.pts = np.concatenate(shell).astype(np.float32)

    def depth(self, th):
        """Front-most depth (toward the viewer) for every pixel at angle th; -inf where the hull is absent."""
        t = np.radians(th)
        x, z, y = self.pts[:, 0], self.pts[:, 1], self.pts[:, 2].astype(np.int32)
        u = np.rint(x * np.cos(t) - z * np.sin(t) + CX).astype(np.int32)
        zv = x * np.sin(t) + z * np.cos(t)
        d = np.full((H, W), -np.inf, np.float32)
        ok = (u >= 0) & (u < W)
        np.maximum.at(d, (y[ok], u[ok]), zv[ok])
        # close 1 px cracks along u
        d2 = d.copy()
        for s in (-1, 1):
            sh = np.roll(d, s, 1)
            hole = ~np.isfinite(d2) & np.isfinite(sh) & np.isfinite(np.roll(d, -s, 1))
            d2[hole] = sh[hole]
        return d2


def sample(img, u, y):
    """Bilinear sample of an RGBA image at float column u, integer row y."""
    u0 = np.clip(np.floor(u).astype(np.int32), 0, W - 2)
    f = np.clip(u - u0, 0, 1)[:, None]
    a = img[y, u0].astype(np.float32)
    b = img[y, u0 + 1].astype(np.float32)
    return a * (1 - f) + b * f


class Turn:
    def __init__(self, a34=40.0):
        self.ims = load_views()
        self.angs = angles(a34)
        sils = {v: (im[:, :, 3] > 127).astype(np.uint8) for v, im in self.ims.items()}
        ys = np.nonzero(sum(s.any(1) for s in sils.values()))[0]
        self.hull = Hull(sils, self.angs, max(0, ys.min() - 4), min(H, ys.max() + 4))
        self.kdepth = {v: self.hull.depth(th) for v, th in self.angs.items()}
        # premultiplied colour for clean blending
        self.pm = {}
        for v, im in self.ims.items():
            f = im.astype(np.float32)
            f[:, :, :3] *= f[:, :, 3:4] / 255
            self.pm[v] = f

    def keys_around(self, th):
        th %= 360
        seq = sorted(self.angs.items(), key=lambda kv: kv[1]) + [("front", 360.0)]
        for (va, ta), (vb, tb) in zip(seq, seq[1:]):
            if ta <= th <= tb:
                return va, ta, vb, tb
        return "front", 0.0, "front", 0.0

    def render(self, th, primary=None):
        """Render angle th. primary=None: blend the two neighbour keys; primary=view: take every point from that key
        where it is visible, the other neighbour (then the rest) only where it is not."""
        th = float(th) % 360
        for v, t in self.angs.items():          # exactly a key angle: the library image itself
            if abs(t - th) < 1e-6 or (v == "front" and abs(th - 360) < 1e-6):
                return self.ims[v].copy()
        va, ta, vb, tb = self.keys_around(th)
        s = (th - ta) / (tb - ta)
        wb = s * s * (3 - 2 * s)
        if primary == va:
            wb = 0.0
        elif primary == vb:
            wb = 1.0
        d = self.hull.depth(th)
        yy, uu = np.nonzero(np.isfinite(d))
        zv = d[yy, uu]
        t = np.radians(th)
        x = (uu - CX) * np.cos(t) + zv * np.sin(t)          # back to the body frame
        z = -(uu - CX) * np.sin(t) + zv * np.cos(t)
        order = [(va, 1 - wb), (vb, wb)] + [(v, 0.0) for v, _ in
                                            sorted(self.angs.items(), key=lambda kv: min(abs(kv[1] - th), 360 - abs(kv[1] - th)))
                                            if v not in (va, vb)]
        order = [o for o in order if o[1] > 0] + [o for o in order if o[1] <= 0]
        acc = np.zeros((len(yy), 4), np.float32)
        wsum = np.zeros(len(yy), np.float32)
        filled = np.zeros(len(yy), bool)
        for v, w in order:
            tk = np.radians(self.angs[v])
            uk = x * np.cos(tk) - z * np.sin(tk) + CX
            zk = x * np.sin(tk) + z * np.cos(tk)
            ui = np.clip(np.rint(uk).astype(np.int32), 0, W - 1)
            vis = zk >= self.kdepth[v][yy, ui] - TOL_VIS
            if w > 0:
                m = vis
                ww = w
            else:                                     # fallback key only where nothing else saw the point
                m = vis & ~filled & (wsum <= 0)
                ww = 1.0
            if not m.any():
                continue
            c = sample(self.pm[v], uk[m], yy[m])
            acc[m] += c * ww
            wsum[m] += ww
            filled |= m
        ok = wsum > 0
        acc[ok] /= wsum[ok][:, None]
        out = np.zeros((H, W, 4), np.float32)
        out[yy[ok], uu[ok]] = acc[ok]
        a = out[:, :, 3:4]
        rgb = np.where(a > 0, out[:, :, :3] / np.maximum(a, 1e-3) * 255, 0)
        res = np.concatenate([np.clip(rgb, 0, 255), a], 2).astype(np.uint8)
        # soften the hull's stair-step edge a little
        res[:, :, 3] = cv2.GaussianBlur(res[:, :, 3], (0, 0), 0.6)
        return res


def fit():
    """Pick the 3/4 angle whose hull reproduces the 3/4 silhouettes best."""
    ims = load_views()
    sils = {v: (im[:, :, 3] > 127).astype(np.uint8) for v, im in ims.items()}
    best = None
    for a in (30, 35, 40, 45, 50, 55):
        ang = angles(a)
        sub = {v: sils[v] for v in ("front", "profileleft", "back", "profileright")}
        h = Hull(sub, {v: ang[v] for v in sub}, 200, 1230)
        sc = []
        for v in ("34left", "34right"):
            dd = np.isfinite(h.depth(ang[v]))
            sc.append((dd & (sils[v] > 0)).sum() / ((dd | (sils[v] > 0)).sum()))
        print(a, [round(x, 4) for x in sc])
        if best is None or sum(sc) > best[1]:
            best = (a, sum(sc))
    print("best", best)
    return best[0]


if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "fit":
        fit()
    elif cmd == "at":
        tr = Turn(float(sys.argv[4]) if len(sys.argv) > 4 else 40)
        Image.fromarray(tr.render(float(sys.argv[2]))).save(sys.argv[3])
    elif cmd == "render":
        a0, a1, n, out = float(sys.argv[2]), float(sys.argv[3]), int(sys.argv[4]), Path(sys.argv[5])
        a34 = float(sys.argv[6]) if len(sys.argv) > 6 else 40
        out.mkdir(parents=True, exist_ok=True)
        tr = Turn(a34)
        for i in range(n):
            th = a0 + (a1 - a0) * i / max(1, n - 1)
            Image.fromarray(tr.render(th)).save(out / f"turn_{i:04d}.png")
        json.dump({"a0": a0, "a1": a1, "n": n, "a34": a34}, open(out / "turn.json", "w"))
