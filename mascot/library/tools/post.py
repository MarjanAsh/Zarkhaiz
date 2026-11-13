"""Cut the raw generated images into normalized library assets and write library.json + contact sheets.

Usage: python3 post.py            (needs rembg, scipy, pillow; reads raw/*.png, writes the asset folders)

Normalization (all PNG, transparent):
  bodies  820x1240, head top to sole = 1000 px, soles on y=1215, leg centre on x=410 (as CHARACTER.md)
  heads   640x720, neck point (bottom centre of the collar cut) at (320, 700), head+neck height 620 px
  hands   480x560, wrist (centre of the cuff end) at (240, 540), cuff width 130 px; left = mirrored right
  arms    trimmed, sleeve end width 130 px (matches the hand cuff); anchors: top (proximal) and bottom (distal)
  torsos  bodies with the head cut off at the neck line (820x1240 canvas, same anchors as bodies)
"""
import json, sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from scipy import ndimage

sys.path.insert(0, str(Path(__file__).parent))
from jobs import jobs  # noqa: E402

LIB = Path(__file__).resolve().parents[1]
RAW, CUT = LIB / "raw", LIB / "raw" / "cutout"
BODY_W, BODY_H, BODY_FEET, BODY_HEIGHT = 820, 1240, 1215, 1000
HEAD_W, HEAD_H, HEAD_NECK, HEAD_HEIGHT = 640, 720, (320, 700), 620
HAND_W, HAND_H, HAND_WRIST, CUFF_W = 480, 560, (240, 540), 130
NECK_FRAC = 0.198  # neck line below the head top, as a fraction of body height (from mascot/rig: neck 282 of 1370)

_sess = None


def cutout(job_id):
    """Background-removed RGBA of raw/<job>.png, cached in raw/cutout/."""
    global _sess
    CUT.mkdir(exist_ok=True)
    out = CUT / f"{job_id}.png"
    src = RAW / f"{job_id}.png"
    if out.exists() and out.stat().st_mtime > src.stat().st_mtime:
        return Image.open(out).convert("RGBA")
    from rembg import new_session, remove
    _sess = _sess or new_session("birefnet-general-lite")
    im = remove(Image.open(src).convert("RGB"), session=_sess, post_process_mask=True)
    im.save(out)
    return im


def split_cells(im, rows, cols):
    """Connected parts of the alpha mask, grouped by the grid cell their centre falls in."""
    a = np.array(im)[:, :, 3]
    mask = a > 40
    lab, n = ndimage.label(ndimage.binary_dilation(mask, iterations=6))
    H, W = mask.shape
    cells = {}
    for i, sl in enumerate(ndimage.find_objects(lab), 1):
        comp = (lab[sl] == i) & mask[sl]
        if comp.sum() < 0.002 * H * W:
            continue
        cy, cx = ndimage.center_of_mass(comp)
        r = min(rows - 1, int((sl[0].start + cy) / H * rows))
        c = min(cols - 1, int((sl[1].start + cx) / W * cols))
        m = cells.setdefault(r * cols + c, np.zeros_like(mask))
        m[sl] |= comp
    res = {}
    arr = np.array(im)
    for k, m in cells.items():
        piece = arr.copy()
        piece[:, :, 3] = np.where(m, arr[:, :, 3], 0)
        ys, xs = np.nonzero(m)
        bb = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
        res[k] = Image.fromarray(piece).crop(bb)
    return res


def bottom_centre(a, frac=0.03):
    ys, xs = np.nonzero(a > 40)
    y1 = ys.max()
    sel = ys >= y1 - max(2, int(frac * (y1 - ys.min())))
    return float(xs[sel].mean()), float(y1 + 1), float(xs[sel].max() - xs[sel].min() + 1)


def place(piece, scale, anchor_src, anchor_dst, size):
    w, h = piece.size
    p = piece.resize((max(1, round(w * scale)), max(1, round(h * scale))), Image.LANCZOS)
    canvas = Image.new("RGBA", size, (0, 0, 0, 0))
    ox, oy = round(anchor_dst[0] - anchor_src[0] * scale), round(anchor_dst[1] - anchor_src[1] * scale)
    canvas.alpha_composite(p, (max(0, ox), max(0, oy)), (max(0, -ox), max(0, -oy)))
    clipped = (ox < 0 or oy < 0 or ox + p.width > size[0] or oy + p.height > size[1])
    return canvas, clipped


def norm_body(piece):
    a = np.array(piece)[:, :, 3]
    fx, fy, _ = bottom_centre(a, 0.06)
    H = a.shape[0]
    band = a[:, max(0, int(fx - 0.07 * H)):int(fx + 0.07 * H)] > 40  # head top: highest pixel near the body axis
    top = int(np.nonzero(band.any(1))[0].min())
    s = BODY_HEIGHT / (fy - top)
    return place(piece, s, (fx, fy), (BODY_W / 2, BODY_FEET), (BODY_W, BODY_H))


def norm_head(piece, scale_h):
    a = np.array(piece)[:, :, 3]
    nx, ny, _ = bottom_centre(a)
    return place(piece, HEAD_HEIGHT / scale_h, (nx, ny), HEAD_NECK, (HEAD_W, HEAD_H))


def norm_hand(piece, cuff):
    a = np.array(piece)[:, :, 3]
    wx, wy, _ = bottom_centre(a, 0.04)
    return place(piece, CUFF_W / cuff, (wx, wy), HAND_WRIST, (HAND_W, HAND_H))


def save(img, rel):
    p = LIB / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p, optimize=True)
    return rel


def main():
    entries, problems = [], []
    meta_of = {}
    for job in jobs():
        if not (RAW / f"{job['id']}.png").exists():
            problems.append(f"{job['id']}: not generated")
            continue
        meta = json.loads((RAW / f"{job['id']}.json").read_text())
        meta_of[job["id"]] = meta
        pieces = split_cells(cutout(job["id"]), job["rows"], job["cols"])
        src = {"raw": f"raw/{job['id']}.png", "prompt": job["prompt"], "model": meta.get("model"),
               "backend": meta.get("backend")}
        names = job["cells"]
        missing = [names[i] for i in range(len(names)) if i not in pieces]
        if missing:
            problems.append(f"{job['id']}: no cutout for {missing}")
        k = job["kind"]
        if k == "head":
            hs = sorted(np.array(p)[:, :, 3].shape[0] for p in pieces.values())
            med = hs[len(hs) // 2]
            for i, p in pieces.items():
                img, clip = norm_head(p, med)
                f = save(img, f"heads/{job['angle']}/{names[i]}.png")
                entries.append({"file": f, "kind": "head", "angle": job["angle"], "expression": names[i],
                                "size": [HEAD_W, HEAD_H], "anchors": {"neck": list(HEAD_NECK)}, "clipped": clip, **src})
        elif k == "body":
            for i, p in pieces.items():
                img, clip = norm_body(p)
                angle = names[i] if job["pose"] == "neutral" else job.get("angle", "front")
                pose = job["pose"] if job["pose"] == "neutral" else names[i]
                f = save(img, f"bodies/{angle}/{pose}.png")
                entries.append({"file": f, "kind": "body", "angle": angle, "pose": pose, "size": [BODY_W, BODY_H],
                                "anchors": {"feet": [BODY_W / 2, BODY_FEET],
                                            "head_top": [BODY_W / 2, BODY_FEET - BODY_HEIGHT]},
                                "clipped": clip, **src})
                if pose == "neutral" and angle in ("front", "34left", "34right"):
                    entries.append(make_torso(img, angle, src))
        elif k == "hand":
            cuffs = sorted(bottom_centre(np.array(p)[:, :, 3], 0.04)[2] for p in pieces.values())
            cuff = cuffs[len(cuffs) // 2]
            for i, p in pieces.items():
                img, clip = norm_hand(p, cuff)
                for side, im2 in (("right", img), ("left", img.transpose(Image.FLIP_LEFT_RIGHT))):
                    f = save(im2, f"hands/{side}/{names[i]}.png")
                    entries.append({"file": f, "kind": "hand", "side": side, "shape": names[i],
                                    "size": [HAND_W, HAND_H], "anchors": {"wrist": list(HAND_WRIST)},
                                    "mirrored_from_right": side == "left", "clipped": clip, **src})
        elif k == "arm":
            for i, p in pieces.items():
                a = np.array(p)[:, :, 3]
                _, _, w = bottom_centre(a, 0.04)
                s = CUFF_W / w
                img = p.resize((max(1, round(p.width * s)), max(1, round(p.height * s))), Image.LANCZOS)
                aa = np.array(img)[:, :, 3]
                bx, by, _ = bottom_centre(aa, 0.04)
                ys, xs = np.nonzero(aa > 40)
                tsel = ys <= ys.min() + max(2, int(0.04 * (ys.max() - ys.min())))
                top = [float(xs[tsel].mean()), float(ys.min())]
                for side, im2 in (("right", img), ("left", img.transpose(Image.FLIP_LEFT_RIGHT))):
                    W = img.width
                    t = top if side == "right" else [W - top[0], top[1]]
                    b = [bx, by] if side == "right" else [W - bx, by]
                    f = save(im2, f"arms/{side}/{names[i]}.png")
                    entries.append({"file": f, "kind": "arm", "side": side, "piece": names[i],
                                    "size": list(img.size), "anchors": {"proximal": t, "distal": b},
                                    "mirrored_from_right": side == "left", **src})
    lib = {"version": 1, "canvases": {
        "body": {"size": [BODY_W, BODY_H], "feet": [BODY_W / 2, BODY_FEET], "body_height": BODY_HEIGHT,
                 "neck_y": BODY_FEET - BODY_HEIGHT + NECK_FRAC * BODY_HEIGHT},
        "head": {"size": [HEAD_W, HEAD_H], "neck": list(HEAD_NECK), "height": HEAD_HEIGHT},
        "hand": {"size": [HAND_W, HAND_H], "wrist": list(HAND_WRIST), "cuff_width": CUFF_W}},
        "assets": entries, "problems": problems}
    lib["canvases"]["head"]["scale_on_body_canvas"] = head_scale(entries)
    (LIB / "library.json").write_text(json.dumps(lib, indent=1))
    sheets(entries)
    print(f"{len(entries)} assets; problems:", *problems, sep="\n  ")


def make_torso(body, angle, src):
    """Body without the head: everything above the neck line removed, with a 6 px soft edge."""
    neck_y = int(BODY_FEET - BODY_HEIGHT + NECK_FRAC * BODY_HEIGHT)
    m = Image.new("L", body.size, 0)
    ImageDraw.Draw(m).rectangle([0, neck_y, body.width, body.height], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(3))
    a = np.minimum(np.array(body)[:, :, 3], np.array(m))
    t = body.copy()
    t.putalpha(Image.fromarray(a.astype(np.uint8)))
    row = np.nonzero(np.array(body)[neck_y + 4, :, 3] > 40)[0]
    nx = float(row.mean()) if len(row) else BODY_W / 2
    f = save(t, f"torsos/{angle}.png")
    return {"file": f, "kind": "torso", "angle": angle, "size": [BODY_W, BODY_H],
            "anchors": {"neck": [nx, neck_y], "feet": [BODY_W / 2, BODY_FEET]},
            "derived_from": f"bodies/{angle}/neutral.png", **src}


def head_scale(entries):
    """Scale that puts a head asset onto the body canvas: head top to neck on the body is NECK_FRAC*1000 px;
    on the head canvas the head top to the collar cut is HEAD_HEIGHT minus the neck/collar part (about 22%)."""
    return round(NECK_FRAC * BODY_HEIGHT / (HEAD_HEIGHT * 0.78), 4)


def sheets(entries):
    (LIB / "sheets").mkdir(exist_ok=True)
    groups = {}
    for e in entries:
        parts = e["file"].split("/")
        key = parts[0] + (f"_{parts[1]}" if parts[0] in ("heads", "hands", "arms") else "")
        groups.setdefault(key, []).append(e)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    for name, es in sorted(groups.items()):
        thumbs = []
        for e in sorted(es, key=lambda e: e["file"]):
            im = Image.open(LIB / e["file"]).convert("RGBA")
            im.thumbnail((240, 300))
            tile = Image.new("RGB", (250, 330), (236, 236, 236))
            tile.paste(im, ((250 - im.width) // 2, (300 - im.height) // 2), im)
            label = "/".join(Path(e["file"]).with_suffix("").parts[-2:]) if name in ("bodies", "torsos") \
                else Path(e["file"]).stem
            ImageDraw.Draw(tile).text((6, 306), label, fill=(20, 20, 20), font=font)
            thumbs.append(tile)
        cols = min(6, len(thumbs))
        rows = (len(thumbs) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * 254, rows * 334 + 34), (255, 255, 255))
        ImageDraw.Draw(sheet).text((8, 8), name.replace("_", " / "), fill=(0, 0, 0), font=font)
        for i, t in enumerate(thumbs):
            sheet.paste(t, ((i % cols) * 254 + 2, (i // cols) * 334 + 34))
        sheet.save(LIB / "sheets" / f"{name}.jpg", quality=85)


if __name__ == "__main__":
    main()
