"""Face patches for the master head: only the mouth (or the face interior) changes, the head outline never does.

Library heads (mascot/library/heads/front/*.png) are registered to the master's own head with an ECC affine fit on the
eyes/forehead region, colour-matched on a ring around the patch, and blended in through a feathered ellipse:
  mouth patch  (talk_a, talk_o, talk_e, smile): below the nose only, so the eyes and glasses stay the master's;
  face patch   (laugh, surprised, concerned): eyes to chin, inside the face, for the few expression changes.
Returns RGBA patches on the 820x1240 body canvas (transparent outside the ellipse).
"""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

LIB = Path(__file__).resolve().parents[2] / "library"
MOUTH = dict(c=(.5, .69), r=(.165, .095))
FACE = dict(c=(.5, .585), r=(.225, .225))
KIND = {"talk_a": MOUTH, "talk_o": MOUTH, "talk_e": MOUTH, "talk_teeth": MOUTH, "smile": MOUTH,
        "laugh": FACE, "surprised": FACE, "concerned": FACE}


def _gray(a):
    return cv2.cvtColor(a[:, :, :3], cv2.COLOR_RGB2GRAY).astype(np.float32) / 255


def patches(master_rgba, exprs=tuple(KIND)):
    lib = json.loads((LIB / "library.json").read_text())
    f = next(a for a in lib["assets"] if a["file"] == "bodies/front/neutral.png")["head_fit"]
    s = f["scale"]; W, H = round(640 * s), round(720 * s); x0, y0 = round(f["left"]), round(f["top"])
    mh = master_rgba[y0:y0 + H, x0:x0 + W]
    reg = np.zeros((H, W), np.uint8); reg[int(.30 * H):int(.60 * H), int(.22 * W):int(.78 * W)] = 255
    out = {}
    for e in exprs:
        he = np.array(Image.open(LIB / "heads" / "front" / f"{e}.png").convert("RGBA").resize((W, H), Image.LANCZOS))
        w = np.eye(2, 3, dtype=np.float32)
        cc, w = cv2.findTransformECC(_gray(mh), _gray(he), w, cv2.MOTION_AFFINE,
                                     (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 300, 1e-6), reg, 5)
        al = cv2.warpAffine(he, w, (W, H), flags=cv2.INTER_LINEAR + cv2.WARP_INVERSE_MAP, borderMode=cv2.BORDER_REPLICATE)
        k = KIND[e]
        pm = np.zeros((H, W), np.float32)
        cv2.ellipse(pm, (int(k["c"][0] * W), int(k["c"][1] * H)), (int(k["r"][0] * W), int(k["r"][1] * H)), 0, 0, 360, 1, -1)
        pm = cv2.GaussianBlur(pm, (0, 0), 4.5)
        ring = (cv2.GaussianBlur((pm > .05).astype(np.float32), (0, 0), 5) > .05) & (pm < .4)
        gain = (mh[:, :, :3][ring].mean(0) + 1) / (al[:, :, :3][ring].mean(0) + 1)
        rgb = np.clip(al[:, :, :3] * gain, 0, 255).astype(np.uint8)
        full = np.zeros(master_rgba.shape, np.uint8)
        full[y0:y0 + H, x0:x0 + W, :3] = rgb
        full[y0:y0 + H, x0:x0 + W, 3] = (pm * (mh[:, :, 3] / 255.) * 255).astype(np.uint8)
        out[e] = (full, round(float(cc), 3))
    return out, (x0, y0, W, H)


if __name__ == "__main__":
    import sys
    master = np.array(Image.open(LIB / "bodies/front/neutral.png").convert("RGBA"))
    P, (x0, y0, W, H) = patches(master)
    tiles = [master[y0:y0 + H, x0:x0 + W, :3]]
    for e, (p, cc) in P.items():
        a = p[y0:y0 + H, x0:x0 + W, 3:4] / 255.
        tiles.append((tiles[0] * (1 - a) + p[y0:y0 + H, x0:x0 + W, :3] * a).astype(np.uint8)); print(e, cc)
    rows = [np.concatenate(tiles[:5], 1), np.concatenate(tiles[5:] + [tiles[0]] * (10 - len(tiles)), 1)]
    im = Image.fromarray(np.concatenate(rows, 0)[:, :, :3])
    im.resize((im.width * 3 // 2, im.height * 3 // 2), Image.LANCZOS).save(sys.argv[1], quality=92)
