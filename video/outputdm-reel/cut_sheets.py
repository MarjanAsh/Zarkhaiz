"""Cut the 18 poses out of the three character sheets: background removed, labels dropped,
every pose scaled to the same body height and placed feet-down on one shared canvas."""
import sys, numpy as np
from PIL import Image
from rembg import remove, new_session
from scipy import ndimage
ROOT = sys.argv[1] if len(sys.argv) > 1 else "../../mascot/character"   # usage: python cut_sheets.py (lemo-opuscar venv)
NAMES = {
 "sheet1": ["point_screen", "explain", "arms_crossed", "laugh", "oh_no", "peace"],
 "sheet2": ["confident", "side_point", "back_look", "idea", "surprised", "triumph"],
 "sheet3": ["thinking", "presenting", "point_camera", "victory", None, "panic"],  # None: angry pose, never used
}
BODY, W, H, FEET = 1000, 820, 1240, 1215
sess = new_session("birefnet-general-lite")
for sheet, names in NAMES.items():
    im = Image.open(f"{ROOT}/refs/{sheet}.jpg").convert("RGB")
    a = np.asarray(remove(im, session=sess, only_mask=True)).astype(np.float32) / 255
    a[1025:1095] = 0; a[1905:] = 0                       # label rows
    lab, n = ndimage.label(a > 0.5)
    sizes = ndimage.sum(np.ones_like(a), lab, range(1, n + 1))
    big = [i + 1 for i, s in enumerate(sizes) if s > 20000]
    cents = {i: ndimage.center_of_mass(a > 0.5, lab, i) for i in big}
    # cell order: row (y < 1050) then x
    order = sorted(big, key=lambda i: (cents[i][0] > 1050, cents[i][1]))
    assert len(order) == 6, (sheet, len(order))
    owner = np.zeros_like(lab)
    for i in big: owner[lab == i] = i
    for j, s in enumerate(sizes):                            # small detached bits -> nearest figure
        if 50 < s <= 20000:
            cy, cx = ndimage.center_of_mass(a > 0.5, lab, j + 1)
            k = min(big, key=lambda i: (cents[i][0] - cy) ** 2 + (cents[i][1] - cx) ** 2)
            owner[lab == j + 1] = k
    owner = ndimage.grey_dilation(owner, size=5) * (a > 0.02)  # keep the soft edge with its figure
    rgb = np.asarray(im)
    for idx, name in zip(order, names):
        if not name: continue
        m = (owner == idx) * a
        ys, xs = np.nonzero(m > 0.5)
        y0, y1 = ys.min(), ys.max()
        low = m[int(y1 - 0.22 * (y1 - y0)):y1 + 1] > 0.5
        legx = np.nonzero(low)[1].mean()
        band = m[:, int(legx - 55):int(legx + 55)] > 0.5
        head = np.nonzero(band.any(1))[0].min()
        s = BODY / (y1 - head)
        rgba = np.dstack([rgb, (m * 255).astype(np.uint8)])
        x0, x1 = xs.min(), xs.max()
        crop = Image.fromarray(rgba[y0:y1 + 1, x0:x1 + 1], "RGBA")
        crop = crop.resize((max(1, round(crop.width * s)), max(1, round(crop.height * s))), Image.LANCZOS)
        out = Image.new("RGBA", (W, H))
        px = round(W / 2 - (legx - x0) * s); py = round(FEET - (y1 - y0) * s)
        out.alpha_composite(crop, (max(px, 0), max(py, 0)), (max(-px, 0), max(-py, 0)))
        if px < 0 or py < 0 or px + crop.width > W: print("  clipped", name, px, py, crop.width)
        out.save(f"{ROOT}/poses/{name}.png", optimize=True)
        print(name, "scale", round(s, 3), "body px", y1 - head)
