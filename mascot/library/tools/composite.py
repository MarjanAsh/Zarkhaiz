"""Fit library heads onto library bodies, so a script can swap faces (expressions, talking mouths) on any body.

Usage: python3 composite.py      (after post.py; updates library.json, writes bodies_headless/ and sheets/composite_*.jpg)

For every body whose head is free (no hand on or over the face) it:
 1. fits the neutral head of the same angle onto the body's own head: hair top, head width and centre give a first
    guess, then a small search over scale and offset maximises the overlap (IoU) of the two silhouettes;
 2. writes a head-less copy of the body (bodies_headless/<angle>/<pose>.png): the body's own head is cleared inside
    the fitted head's box above the chin line, so the swapped head never shows a second outline behind it;
 3. stores the fit in library.json on the body asset: "head_fit": {angle, scale, left, top, iou, headless}.
    Draw a head on the body canvas with: x = left, y = top, width = 640*scale, height = 720*scale.
Bodies in SKIP keep their own head (a hand touches the face), and the back view has no face.
"""
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

LIB = Path(__file__).resolve().parents[1]
SKIP = {"thinking_chin"}                       # the hand is on the chin: a swapped head would cover it
HEAD_W, HEAD_H = 640, 720


def alpha(im):
    return np.array(im)[:, :, 3] > 40


def head_box(mask, top, rows):
    """Width and centre of the head over `rows` rows below `top`: the run of occupied columns that contains the
    topmost pixel, so a raised hand next to the head (with a gap) is not counted."""
    sl = mask[top:top + rows]
    occ = sl.any(0)
    xt = int(np.nonzero(mask[top])[0].mean()) if mask[top].any() else int(np.nonzero(occ)[0].mean())
    lo = hi = xt
    while lo > 0 and occ[lo - 1]:
        lo -= 1
    while hi < len(occ) - 1 and occ[hi + 1]:
        hi += 1
    return hi - lo + 1, (hi + lo) / 2


def place_mask(hmask, s, left, top, shape):
    out = np.zeros(shape, bool)
    h = Image.fromarray((hmask * 255).astype(np.uint8)).resize((max(1, round(HEAD_W * s)), max(1, round(HEAD_H * s))))
    hm = np.array(h) > 127
    x0, y0 = int(round(left)), int(round(top))
    ys, xs = slice(max(0, y0), min(shape[0], y0 + hm.shape[0])), slice(max(0, x0), min(shape[1], x0 + hm.shape[1]))
    out[ys, xs] = hm[ys.start - y0:ys.stop - y0, xs.start - x0:xs.stop - x0]
    return out


def fit(body, head):
    bm, hm = alpha(body), alpha(head)
    hy = np.nonzero(hm.any(1))[0]
    h_top, h_bot = hy.min(), hy.max()
    hh = h_bot - h_top
    h_chin = h_top + int(.72 * hh)                          # rows above this are head (hair, face, beard)
    hw, hcx = head_box(hm, h_top, int(.5 * hh))
    # body head: the topmost silhouette near the body axis (head_top is y=215 on the body canvas)
    feet_x = 410
    band = bm[:, feet_x - 140:feet_x + 140]
    by = np.nonzero(band.any(1))[0]
    b_top = int(by.min())
    s = .41
    for _ in range(3):
        bw, bcx = head_box(bm[:, feet_x - 140:feet_x + 140], b_top, int(.5 * hh * s))
        s = bw / hw
    bcx += feet_x - 140
    left, top = bcx - hcx * s, b_top - h_top * s
    # refine: maximise IoU in the head zone (above the fitted chin line)
    best = (-1, s, left, top)
    chin_y = lambda s_, t_: int(t_ + h_chin * s_)
    for ds in np.linspace(-.06, .06, 9):
        s2 = s * (1 + ds)
        for dx in range(-12, 13, 3):
            for dy in range(-12, 13, 3):
                l2, t2 = left + dx + (hcx * (s - s2)), top + dy
                pm = place_mask(hm, s2, l2, t2, bm.shape)
                cy = chin_y(s2, t2)
                x0, x1 = int(l2), int(l2 + HEAD_W * s2)
                a, b = pm[:cy, max(0, x0):x1], bm[:cy, max(0, x0):x1]
                iou = (a & b).sum() / max(1, (a | b).sum())
                if iou > best[0]:
                    best = (iou, s2, l2, t2)
    iou, s, left, top = best
    return {"scale": round(float(s), 4), "left": round(float(left), 1), "top": round(float(top), 1),
            "iou": round(float(iou), 3), "chin_y": chin_y(s, top)}


def headless(body, f):
    """Clear the body's own head inside the fitted head box above the chin line (soft 4 px edge)."""
    a = np.array(body).copy()
    x0, x1 = int(f["left"]) - 6, int(f["left"] + HEAD_W * f["scale"]) + 6
    zone = np.zeros(a.shape[:2], np.float32)
    zone[:f["chin_y"], max(0, x0):x1] = 1
    zone = ndimage.gaussian_filter(zone, 2)
    a[:, :, 3] = (a[:, :, 3] * (1 - zone)).astype(np.uint8)
    return Image.fromarray(a)


def compose(body, head, f):
    c = body.copy()
    h = head.resize((round(HEAD_W * f["scale"]), round(HEAD_H * f["scale"])), Image.LANCZOS)
    c.alpha_composite(h, (int(round(f["left"])), int(round(f["top"]))))
    return c


def main():
    lib = json.loads((LIB / "library.json").read_text())
    heads = {(a["angle"], a["expression"]): a["file"] for a in lib["assets"] if a["kind"] == "head"}
    rows = []
    for a in lib["assets"]:
        if a["kind"] != "body":
            continue
        a.pop("head_fit", None)
        if a["angle"] == "back" or a["pose"] in SKIP or (a["angle"], "neutral") not in heads:
            continue
        body = Image.open(LIB / a["file"]).convert("RGBA")
        head = Image.open(LIB / heads[(a["angle"], "neutral")]).convert("RGBA")
        f = fit(body, head)
        out = LIB / "bodies_headless" / a["angle"] / f"{a['pose']}.png"
        out.parent.mkdir(parents=True, exist_ok=True)
        hl = headless(body, f)
        hl.save(out, optimize=True)
        a["head_fit"] = {"angle": a["angle"], **{k: f[k] for k in ("scale", "left", "top", "iou")},
                         "headless": str(out.relative_to(LIB))}
        rows.append((a, hl, f))
        print(f"{a['file']:40s} scale {f['scale']:.3f}  iou {f['iou']:.3f}")
    lib["canvases"]["head"]["scale_on_body_canvas"] = round(float(np.median([f["scale"] for _, _, f in rows])), 4)
    lib["canvases"]["head"]["fit_note"] = "per body: assets[].head_fit (composite.py); this is the median"
    (LIB / "library.json").write_text(json.dumps(lib, indent=1))
    sheet(rows, heads)


def sheet(rows, heads):
    """Test sheet: each body with its own head, then swapped heads (neutral, talk_a, laugh, wink)."""
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    exprs = ["neutral", "talk_a", "talk_o", "laugh", "wink"]
    tw, th = 220, 333
    S = Image.new("RGB", (tw * (2 + len(exprs)), th * len(rows) + 30), "white")
    d = ImageDraw.Draw(S)
    d.text((6, 6), "own head | headless | swapped heads: " + ", ".join(exprs), fill="black", font=font)
    for r, (a, hl, f) in enumerate(rows):
        body = Image.open(LIB / a["file"]).convert("RGBA")
        tiles = [body, hl] + [compose(hl, Image.open(LIB / heads[(a["angle"], e)]).convert("RGBA"), f) for e in exprs]
        for c, im in enumerate(tiles):
            crop = im.crop((160, 120, 660, 880))           # upper body, where the head swap happens
            crop.thumbnail((tw - 4, th - 24))
            bg = Image.new("RGB", (tw - 4, th - 24), (236, 236, 236))
            bg.paste(crop, ((bg.width - crop.width) // 2, 0), crop)
            S.paste(bg, (c * tw + 2, 30 + r * th))
        d.text((4, 30 + r * th + th - 22), f"{a['angle']}/{a['pose']}  iou {f['iou']:.2f}", fill="black", font=font)
    S.save(LIB / "sheets" / "composite_heads.jpg", quality=85)


if __name__ == "__main__":
    main()
