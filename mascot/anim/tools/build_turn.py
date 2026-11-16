"""Body turns (v019): front -> 3/4 toward the viewer's left ("tl") or right ("tr"), as whole-body frames.

Keys: the front master body and mascot/library/bodies/34left|34right/neutral.png, brought to the same height and
feet line. FILM makes N in-between frames. Every frame is saved as
  out/turn/<dir>_<i>.webp        the whole figure (RGBA, 820x1240), head included
  out/turn/<dir>_<i>_head.webp   the head alone (RGBA patch), so the page can draw it smaller (HEAD_S) at its pivot
  out/turn/<dir>_<i>_erase.png   where the page removes the frame's own head first
and out/turn.json: {"tl": [{"f", "head", "erase", "box": [x, y, w, h], "pivot": [x, y]}, ...], "tr": [...]}.
Frame 0 is the front pose (arms at rest), the last frame the 3/4 pose.

Usage: python3 build_turn.py        (FILM results are cached in out/turn/_film; about 3 min per direction on CPU)
"""
import json, sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
OUT, LIB = ROOT / "out", ROOT.parent / "library"
W, H = 820, 1240
N = 7
SRC = {"tl": "34left", "tr": "34right"}
SLIM = .91
sys.path.insert(0, str(Path(__file__).parent))


def bbox(rgba):
    ys, xs = np.nonzero(rgba[:, :, 3] > 128)
    return xs.min(), ys.min(), xs.max(), ys.max()


def on_white(im):
    bg = Image.new("RGBA", im.size, "white"); bg.alpha_composite(im)
    return np.array(bg.convert("RGB"))


def aligned(name):
    """The library body `name` at the front body's height, feet line and centre, on white."""
    front = Image.open(LIB / "bodies/front/neutral.png").convert("RGBA")
    bm = bbox(np.array(front))
    im = Image.open(LIB / f"bodies/{name}/neutral.png").convert("RGBA")
    b = bbox(np.array(im))
    k = (bm[3] - bm[1]) / (b[3] - b[1])
    # the library 3/4 bodies are drawn broader than the front master: SLIM narrows them so the build stays the same
    im2 = im.resize((round(W * k * SLIM), round(H * k)), Image.LANCZOS)
    cv = Image.new("RGBA", (W, H), (255, 255, 255, 0))
    cv.paste(im2, (round((bm[0] + bm[2]) / 2 - (b[0] + b[2]) / 2 * k * SLIM), round(bm[3] - b[3] * k)), im2)
    return on_white(front), on_white(cv)


_crop = None


def landmarks(rgb):
    """Face landmarks (x, y) in the image's own pixels, from LivePortrait's cropper."""
    global _crop
    if _crop is None:
        import lp_face  # noqa: F401  (puts LivePortrait on the path)
        from src.config.crop_config import CropConfig
        from src.utils.cropper import Cropper
        _crop = (Cropper(crop_cfg=CropConfig(flag_force_cpu=True, scale=2.3)), CropConfig(flag_force_cpu=True, scale=2.3))
    ci = _crop[0].crop_source_image(rgb, _crop[1])
    pts = np.c_[ci["pt_crop"], np.ones(len(ci["pt_crop"]))] @ np.asarray(ci["M_c2o"])[:2].T
    return pts


def head_geo(rgb, pts=None):
    """Soft head region Mh (1 on the head, fading out over the collar), its box and the pivot at the collar."""
    pts = landmarks(rgb) if pts is None else pts
    cx, chin = float(pts[:, 0].mean()), float(pts[:, 1].max())
    fw = float(pts[:, 0].max() - pts[:, 0].min())
    half, neck = .89 * fw, .46 * fw
    near = (rgb.min(2) > 236).astype(np.uint8)
    ff = near.copy(); cv2.floodFill(ff, None, (2, 2), 2)
    sil = ff != 2
    r = np.zeros((H, W), np.uint8)
    x0, x1, c = int(cx - half), int(cx + half), int(chin)
    r[:c + 3, x0:x1] = sil[:c + 3, x0:x1]
    r[c - 21:c + 39, int(cx - neck):int(cx + neck)] = 1
    r = cv2.dilate(r, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (27, 27)))
    m = cv2.GaussianBlur(r.astype(np.float32), (0, 0), 3)
    m *= np.clip((chin + 37 - np.arange(H)) / 22, 0, 1)[:, None]
    ys, xs = np.nonzero(m > .004)
    box = [int(xs.min()) - 2, max(0, int(ys.min()) - 2), int(xs.max()) + 3, int(ys.max()) + 3]
    return m, box, [round(cx, 1), round(chin + 33, 1)], fw


def key(rgb, below=0):
    """RGBA from a figure on white: white key at the outline (the inside stays solid), edge pulled in and feathered.
    Below row `below` (under the head) every white area counts as background, also the closed gaps between an arm
    and the body and the white ghosts FILM leaves next to a moving hand."""
    near = (rgb.min(2) > 225).astype(np.uint8)
    ff = near.copy()
    for pt in ((1, 1), (W - 2, 1), (1, H - 2), (W - 2, H - 2)):
        if ff[pt[1], pt[0]] == 1:
            cv2.floodFill(ff, None, pt, 2)
    bg = ff == 2
    gap = (rgb.min(2) > 205).astype(np.uint8); gap[:int(below)] = 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(gap)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] > 25:
            bg |= lab == i
    sub = rgb.astype(np.float32)
    ak = np.clip((255 - sub.min(2) - 10) / 40, 0, 1)
    ak = ak * ak * (3 - 2 * ak)
    bgs = cv2.GaussianBlur(cv2.dilate(bg.astype(np.uint8), np.ones((5, 5), np.uint8)).astype(np.float32), (0, 0), 1.2)
    a = np.where(bgs > .02, np.minimum(ak, 1 - bgs), 1.0)
    a = np.where(bg, 0, a)
    un = (sub - (1 - a[:, :, None]) * 255) / np.maximum(a[:, :, None], .05)
    out = np.where((a[:, :, None] > .02) & (a[:, :, None] < 1), np.clip(un, 0, 255), sub)
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    e = cv2.GaussianBlur(cv2.erode(a, k), (0, 0), 1.1)
    return np.dstack([out, np.minimum(a, e) * 255]).astype(np.uint8)


def main():
    td = OUT / "turn"; cache = td / "_film"
    cache.mkdir(parents=True, exist_ok=True)
    meta = {}
    for d, name in SRC.items():
        a, b = aligned(name)
        files = [cache / f"{name}_{i}.png" for i in range(N + 2)]
        if not all(f.exists() for f in files):
            import film
            seq = [a] + film.interpolate(a, b, N) + [b]
            for f, im in zip(files, seq):
                Image.fromarray(im).save(f)
        meta[d] = []
        for i, f in enumerate(files):
            rgb = np.array(Image.open(f).convert("RGB"))
            m, (x0, y0, x1, y1), piv, fw = head_geo(rgb)
            rgba = key(rgb, piv[1] + 12)
            Image.fromarray(rgba).save(td / f"{d}_{i}.webp", "WEBP", quality=90, method=6)
            head = rgba[y0:y1, x0:x1].copy()
            head[:, :, 3] = (head[:, :, 3] * m[y0:y1, x0:x1]).astype(np.uint8)
            Image.fromarray(head).save(td / f"{d}_{i}_head.webp", "WEBP", quality=90, method=6)
            er = np.zeros((y1 - y0, x1 - x0, 4), np.uint8); er[:, :, 3] = (m[y0:y1, x0:x1] * 255).astype(np.uint8)
            Image.fromarray(er).save(td / f"{d}_{i}_erase.png")
            meta[d].append({"f": f"turn/{d}_{i}.webp", "head": f"turn/{d}_{i}_head.webp", "erase": f"turn/{d}_{i}_erase.png",
                            "box": [x0, y0, x1 - x0, y1 - y0], "pivot": piv})
            print(d, i, "box", [x0, y0, x1, y1], "pivot", piv, "face width", round(fw), flush=True)
    (OUT / "turn.json").write_text(json.dumps(meta))


if __name__ == "__main__":
    main()
