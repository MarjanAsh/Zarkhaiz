"""Cut the A-pose image (source.webp) into a 2D puppet rig.

usage: python3 cut_rig.py      (needs rembg; writes parts/*.png and rig.json next to this file)

Parts: body (torso + legs), head, and for each arm an upper arm, a forearm and hands. Hands are cut
from the skin pixels only, so every hand (the resting one and the 4 gesture hands) attaches to the
sleeve cuff at the wrist. All coordinates are in source pixels; rig.json gives each part's offset and pivot.
"""
import json, os
import numpy as np
from PIL import Image
from rembg import remove, new_session

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
os.makedirs('parts', exist_ok=True)
src = Image.open('source.webp').convert('RGB')
sess = new_session('isnet-general-use')

# full-body alpha; the hands come out faint in the full cut, so they get their own cut on a crop
full = np.array(remove(src.crop((0, 0, 800, src.height)), session=sess)).copy()
for b in [(60, 690, 200, 900), (660, 690, 800, 900)]:
    h = np.array(remove(src.crop(b), session=sess))
    reg = full[b[1]:b[3], b[0]:b[2]]
    reg[..., 3] = np.maximum(reg[..., 3], h[..., 3])
    reg[..., :3] = np.where(h[..., 3:] > reg[..., 3:], h[..., :3], reg[..., :3])
rgb = np.array(src.crop((0, 0, 800, src.height))).astype(int)
H, W = full.shape[:2]
A = full[..., 3].astype(np.float32)


def skin(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    return (r > 95) & (r > g + 12) & (r > b + 25)


yy, xx = np.mgrid[0:H, 0:W]
SK = skin(rgb)

# ---------- joints (source px, measured on the grid) ----------
J = {
    'neck': (435, 282),
    'L': {'sh': (268, 345), 'el': (196, 545), 'wr': (128, 742)},   # screen-left arm
    'R': {'sh': (604, 345), 'el': (672, 545), 'wr': (722, 742)},   # screen-right arm
}


def side_of(p, q, x, y):
    """>0 on the left of the directed line p->q"""
    return (q[0] - p[0]) * (y - p[1]) - (q[1] - p[1]) * (x - p[0])


def arm_mask(side):
    """the arm is everything outside the jacket edge: a slanted line from the shoulder seam to the armpit,
    then a vertical line down the jacket side"""
    op = A > 40
    if side == 'L':
        out = np.where(yy < 470, side_of((300, 300), (256, 470), xx, yy) > 0, xx < 253)
    else:
        out = np.where(yy < 470, side_of((572, 300), (616, 470), xx, yy) < 0, xx > 617)
    return out & op & (yy > 295) & (yy < 930)


def save(name, mask, alpha=None):
    a = (A if alpha is None else alpha) * mask
    ys, xs = np.where(a > 4)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    img = np.dstack([full[y0:y1, x0:x1, :3], a[y0:y1, x0:x1].clip(0, 255).astype(np.uint8)])
    Image.fromarray(img, 'RGBA').save(f'parts/{name}.png')
    return {'x': int(x0), 'y': int(y0), 'w': int(x1 - x0), 'h': int(y1 - y0)}


rig = {'canvas': [W, H], 'feet': [435, 1378], 'parts': {}, 'joints': J}
arms = {}
for s in 'LR':
    am = arm_mask(s)
    j = J[s]
    d = np.array(j['wr']) - np.array(j['el'])
    n = d / np.hypot(*d)
    proj_el = (xx - j['el'][0]) * n[0] + (yy - j['el'][1]) * n[1]
    proj_wr = (xx - j['wr'][0]) * n[0] + (yy - j['wr'][1]) * n[1]
    hand = am & ((proj_wr > 12) | (SK & (proj_wr > -25)))
    upper = am & (proj_el < 14)
    fore = am & (proj_el > -14) & ~hand
    arms[s] = am
    rig['parts'][f'upper{s}'] = save(f'upper{s}', upper)
    rig['parts'][f'fore{s}'] = save(f'fore{s}', fore)
    rig['parts'][f'hand{s}'] = save(f'hand{s}', hand)

head = (yy < 292) & (xx > 318) & (xx < 552) & ((yy < 245) | ((xx > 352) & (xx < 518)))
headm = head & ~arms['L'] & ~arms['R']
rig['parts']['head'] = save('head', headm)
body = ~arms['L'] & ~arms['R'] & (yy > 215)        # body keeps the beard bottom so a head tilt opens no gap
rig['parts']['body'] = save('body', body)

# ---------- gesture hands: skin only, wrist at the bottom centre of the skin ----------
G = {'open': (810, 60, 1050, 380), 'point': (820, 400, 1030, 630), 'fist': (815, 680, 1010, 905), 'thumb': (810, 925, 1030, 1205)}
rig['gestures'] = {}
for k, b in G.items():
    c = np.array(remove(src.crop(b), session=sess))
    a = c[..., 3].astype(np.float32) * skin(np.array(src.crop(b)).astype(int))
    ys, xs = np.where(a > 40)
    # wrist: the lowest skin rows; take the centre of the bottom 12 rows
    yb = ys.max()
    bottom = xs[ys > yb - 12]
    wx, wy = float(bottom.mean()), float(yb)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    img = np.dstack([c[y0:y1, x0:x1, :3], a[y0:y1, x0:x1].clip(0, 255).astype(np.uint8)])
    Image.fromarray(img, 'RGBA').save(f'parts/g_{k}.png')
    # wrist width (for scaling to the rig's wrist)
    ww = int(bottom.max() - bottom.min())
    rig['gestures'][k] = {'w': int(x1 - x0), 'h': int(y1 - y0), 'wrist': [round(wx - x0, 1), round(wy - y0, 1)], 'wristW': ww}
for s in 'LR':
    p = rig['parts'][f'hand{s}']
    ys, xs = np.where(np.array(Image.open(f'parts/hand{s}.png'))[..., 3] > 40)
    top = xs[ys < ys.min() + 12]
    rig['parts'][f'hand{s}']['wristW'] = int(top.max() - top.min())
json.dump(rig, open('rig.json', 'w'), indent=1)
print(json.dumps(rig['parts'], indent=0)); print(rig['gestures'])

# ---------- shoulder caps: a disc of the original shoulder pixels that turns with the arm and covers the seam ----------
for s in 'LR':
    cx, cy = J[s]['sh']
    r = 46
    disc = (((xx - cx) ** 2 + (yy - cy) ** 2) < r * r) & (A > 200)
    soft = np.clip((r - np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)) / 8, 0, 1) * 255
    rig['parts'][f'cap{s}'] = save(f'cap{s}', disc, alpha=np.minimum(A, soft))
json.dump(rig, open('rig.json', 'w'), indent=1)
