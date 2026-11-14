"""Clean the cutout edge of every built frame in ../out (L/, R/): pull the alpha in by about 2 px and feather it,
so the white fringe of the generated background and the jagged rembg edge are gone on the dark stage.

Usage: python3 edges.py     (in place; each file is processed once, tracked in out/.edges.json)
The cut side of a half (the body's centre line) is not touched: the border is replicated before eroding.
"""
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

OUT = Path(__file__).resolve().parents[1] / "out"


def clean(rgba):
    a = rgba[:, :, 3]
    k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    e = cv2.erode(a, k, borderType=cv2.BORDER_REPLICATE)
    e = cv2.GaussianBlur(e, (0, 0), 1.1, borderType=cv2.BORDER_REPLICATE)
    out = rgba.copy()
    out[:, :, 3] = np.minimum(a, e)
    return out


def run():
    log = OUT / ".edges.json"
    done = set(json.loads(log.read_text())) if log.exists() else set()
    n = 0
    for p in sorted(list((OUT / "L").glob("*.webp")) + list((OUT / "R").glob("*.webp"))):
        key = str(p.relative_to(OUT))
        if key in done:
            continue
        Image.fromarray(clean(np.array(Image.open(p).convert("RGBA")))).save(p, "WEBP", quality=90, method=6)
        done.add(key); n += 1
    log.write_text(json.dumps(sorted(done)))
    return n


if __name__ == "__main__":
    print(run(), "frames cleaned")
