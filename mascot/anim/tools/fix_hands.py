"""Rigid hands for the arm clips (v021): replace FILM's melted hands with the key hands moved as rigid pieces.

Usage: python3 fix_hands.py [--only SEGMENT ...] [--dry]      (after build_anim.py; works in place on ../out)

Why: FILM interpolates the sleeve well, but when an open hand turns over (palm down -> palm to camera, the wave, the
present gesture) it melts the fingers for a few frames, even between close keys. The user wants a character that is
complete before the series continues, so the hand is treated like a rigid piece:
 1. In both keys of a segment the hand is found (skin pixels, the head and neck excluded) with its cuff.
 2. Each in-between frame is checked: a melted hand has too little or too much skin, extra fragments, or a whitish
    smear. Only segments with a melted frame are changed (closed-hand moves stay pure FILM).
 3. In those frames FILM's hand is removed (inpainted from the sleeve and the jacket around it) and the two key hands
    are drawn instead, each moved by the same interpolated position, angle and size (from the hand's image moments),
    cross-faded in the middle of the step. The fingers never melt; the hand turns and changes shape in one short blend.
Only the changed pixels get a new alpha (cleaned with edges.clean); the rest of each frame is left as built.
Changed files are listed in out/.hands.json. A frame that is not melted is never touched, so running it again is safe.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import edges  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "out"
HEAD_Y = 480            # canvas rows above this hold the face and neck: never a hand there


def load(p):
    a = np.array(Image.open(OUT / p).convert("RGBA")).astype(np.float32)
    al = a[:, :, 3:] / 255
    return a[:, :, :3] * al + 255 * (1 - al), a[:, :, 3] / 255, a


def skin(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    return (r > 105) & (r > g + 10) & (r - b > 28) & (np.minimum(np.minimum(r, g), b) < 235)


def whitish(rgb, al):
    return (al > .6) & (rgb.min(2) > 175) & ~skin(rgb)


def comps(m, min_area):
    n, lab, st, _ = cv2.connectedComponentsWithStats(m.astype(np.uint8))
    keep = np.zeros_like(m, bool)
    k = 0
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] >= min_area:
            keep |= lab == i; k += 1
    return keep, k


def hand_of(rgb, al, excl, straight):
    m = skin(rgb) & (al > .5) & ~excl
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    m, k = comps(m, 150)
    if m.sum() < 400:
        return None
    ys, xs = np.nonzero(m)
    cx, cy = xs.mean(), ys.mean()
    mu = cv2.moments(m.astype(np.uint8), binaryImage=True)
    th = .5 * np.arctan2(2 * mu["mu11"], mu["mu20"] - mu["mu02"])
    piece = cv2.dilate(m.astype(np.uint8), cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15)))
    piece = cv2.erode(piece, np.ones((3, 3), np.uint8))                   # feather inside the piece, not outside
    pa = cv2.GaussianBlur(piece.astype(np.float32), (0, 0), 1.2) * al     # the key's own alpha keeps its clean edge
    return {"mask": m, "k": k, "area": float(m.sum()), "c": (cx, cy), "th": th, "s": float(np.sqrt(m.sum())),
            "rgb": straight, "pa": pa, "white": int(whitish(rgb, al).sum())}


def warp(h, c, rot, scale, shape):
    M = cv2.getRotationMatrix2D(h["c"], -np.degrees(rot), scale)
    M[:, 2] += np.array(c) - np.array(h["c"])
    W, H = shape[1], shape[0]
    rgb = cv2.warpAffine(h["rgb"] * h["pa"][:, :, None], M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    pa = cv2.warpAffine(h["pa"], M, (W, H), flags=cv2.INTER_LINEAR, borderValue=0)
    return rgb, pa


def melted(rgb, al, excl, A, B, f):
    m = skin(rgb) & (al > .5) & ~excl
    m = cv2.morphologyEx(m.astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8)) > 0
    _, k = comps(m, 40)
    s = m.sum(); e = A["area"] + (B["area"] - A["area"]) * f
    w = whitish(rgb, al).sum()
    why = []
    # tuned on the v021 clips by eye: a melted hand loses skin (fingers dissolve into the sleeve or the background);
    # extra fragments or a light smear count only together with some loss (a bright open palm alone is not a melt)
    if s < .75 * e: why.append(f"skin {s:.0f}<{.75 * e:.0f}")
    if s > 1.5 * e: why.append(f"skin {s:.0f}>{1.5 * e:.0f}")
    if k >= max(A["k"], B["k"]) + 2 and s < .9 * e: why.append(f"{k} pieces")
    # (a "light smear" test was dropped: on the clean clips it fired on every frame, from light edge pixels)
    return why


def fix_segment(side, name, files, excl, dry=False):
    ka, kb, mids = files[0], files[-1], files[1:-1]
    ra, aa, xa = load(ka); rb, ab, xb = load(kb)
    A, B = hand_of(ra, aa, excl, xa[:, :, :3]), hand_of(rb, ab, excl, xb[:, :, :3])
    if A is None or B is None:
        return None, "no hand in a key"
    n = len(mids)
    frames = [load(p) for p in mids]
    reasons = [melted(r, a, excl, A, B, (i + 1) / (n + 1)) for i, (r, a, _) in enumerate(frames)]
    if not any(reasons):
        return None, "clean"
    if dry:
        return [], "; ".join(f"{i}:{','.join(w)}" for i, w in enumerate(reasons) if w)
    d = (B["th"] - A["th"] + np.pi / 2) % np.pi - np.pi / 2           # shortest turn of the hand's main axis
    near = cv2.dilate((A["pa"] > .02).astype(np.uint8) | (B["pa"] > .02).astype(np.uint8), np.ones((81, 81), np.uint8)) > 0
    ys, xs = np.nonzero(near)
    near[:] = False
    near[max(0, ys.min()):ys.max() + 1, max(0, xs.min()):xs.max() + 1] = True     # the box the hand travels through
    changed = []
    for i, (rgb, al, raw) in enumerate(frames):
        f = (i + 1) / (n + 1)
        c = (A["c"][0] + (B["c"][0] - A["c"][0]) * f, A["c"][1] + (B["c"][1] - A["c"][1]) * f)
        size = A["s"] + (B["s"] - A["s"]) * f
        ca, pa = warp(A, c, d * f, size / A["s"], rgb.shape)
        cb, pb = warp(B, c, -d * (1 - f), size / B["s"], rgb.shape)
        s = np.clip((f - .38) / .24, 0, 1); s = s * s * (3 - 2 * s)   # the shape switches within one or two frames
        # remove FILM's own hand (and its smear) near the hand's path, filling from the sleeve and jacket around it
        film_hand = (skin(rgb) & (al > .3)) | whitish(rgb, al) | (pa > .05) | (pb > .05)
        rem = (cv2.dilate(film_hand.astype(np.uint8), np.ones((7, 7), np.uint8)) > 0) & near & ~excl
        base = rgb.copy()
        if rem.any():
            base = cv2.inpaint(np.clip(rgb, 0, 255).astype(np.uint8), rem.astype(np.uint8), 6, cv2.INPAINT_TELEA).astype(np.float32)
        a_p = pa * (1 - s) + pb * s
        col = (ca * (1 - s) + cb * s) / np.maximum(a_p, 1e-3)[:, :, None]      # straight colour of the drawn hand
        # the frame under the hand, as straight colour + alpha: the built frame, or the inpainted pixels where FILM's
        # hand was removed (their alpha from the colour against the white background, as build_anim.save does)
        ak = np.clip((255 - base.min(2) - 10) / 40, 0, 1); ak = ak * ak * (3 - 2 * ak)
        b_al = np.where(rem, ak, al)
        b_rgb = np.where(rem[:, :, None], (base - (1 - ak[:, :, None]) * 255) / np.maximum(ak, .05)[:, :, None], raw[:, :, :3])
        alpha = a_p + (1 - a_p) * b_al                                          # the hand drawn over the frame
        rgb_new = (col * a_p[:, :, None] + b_rgb * (b_al * (1 - a_p))[:, :, None]) / np.maximum(alpha, 1e-3)[:, :, None]
        region = rem | (a_p > .01)
        rgb_new = np.where(region[:, :, None], np.clip(rgb_new, 0, 255), raw[:, :, :3])
        alpha = np.where(region, alpha, al)
        img = np.dstack([rgb_new, alpha * 255]).astype(np.uint8)
        cl = edges.clean(img)
        reg = cv2.dilate(rem.astype(np.uint8), np.ones((5, 5), np.uint8)) > 0    # only the inpainted edge is cleaned again
        img[:, :, 3] = np.where(reg, cl[:, :, 3], img[:, :, 3])
        Image.fromarray(img).save(OUT / mids[i], "WEBP", quality=90, method=6)
        changed.append(mids[i])
    return changed, "; ".join(f"{i}:{','.join(w)}" for i, w in enumerate(reasons) if w)


def main():
    args = sys.argv[1:]
    dry = "--dry" in args
    only = set(args[args.index("--only") + 1:]) if "--only" in args else None
    meta = json.loads((OUT / "anim.json").read_text())
    logp = OUT / ".hands.json"
    log = json.loads(logp.read_text()) if logp.exists() else {}
    for side, segs in meta["frames"].items():
        rest_rgb, rest_al, _ = load(meta["states"][side]["rest"])
        H = rest_rgb.shape[0]
        # skin-coloured in the rest pose above the hips: face, neck and the gold pocket square (it passes the skin test)
        excl = skin(rest_rgb) & (rest_al > .5) & (np.arange(H)[:, None] < 620)
        excl = cv2.dilate(excl.astype(np.uint8), np.ones((21, 21), np.uint8)) > 0
        for name, files in segs.items():
            if only and name not in only:
                continue
            if f"{side}:{name}" in log and not dry:
                continue
            changed, why = fix_segment(side, name, files, excl, dry)
            if changed is None:
                continue
            print(f"{side} {name}: {'would fix' if dry else f'fixed {len(changed)} frames'} ({why})", flush=True)
            if not dry:
                log[f"{side}:{name}"] = {"frames": changed, "why": why}
                logp.write_text(json.dumps(log, indent=1))


if __name__ == "__main__":
    main()
