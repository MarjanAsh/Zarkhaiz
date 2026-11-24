"""Build the animated character (v015): arm clips from GPT keyframes + FILM in-betweens, and face patches.

Usage: python3 build_anim.py            (needs raw/*.png from gen_keys.py, torch, opencv, the FILM model)
Writes ../out/: per side (L = viewer's left half, R = viewer's right half) key and in-between frames as RGBA WebP
halves of the 820x1240 body canvas, face patches, and anim.json (transitions as frame lists).

How a frame is made
 - Every key is an edit of the same master image, so only the arm differs. "Paste-back": the key is kept only inside
   the blob where it really differs from the master (the old and the new arm position); everything else is the
   master's own pixels, so head, torso and legs are identical in every frame.
 - In-betweens: FILM interpolates rest -> mid -> end inside the gesture's box. Transitions between two gestures go
   end -> mid -> (FILM) other mid -> other end, so every interpolated step is a small move.
 - Alpha: the master's alpha outside the box; inside it a white key (the generated background is pure white),
   with the colour un-premultiplied so no white fringe shows on the dark stage.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import edges  # noqa: E402
import faces  # noqa: E402
import film  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RAW, OUT = ROOT / "raw", ROOT / "out"
LIB = ROOT.parent / "library"
W, H, MID = 820, 1240, 410
OVER = 3                      # the halves overlap by a few identical pixels, so no seam can open when scaled
N = 9                         # in-betweens per segment
COUNTS = [f"count{i}L" for i in range(1, 6)]
GEST = {"L": ["presentL", "explain", "waveL", "pointcamL", "pointsideL", *COUNTS, "thumbsL", "fistL", "shrug"],
        "R": ["presentR", "explain", "pointsideR", "thumbsR", "chopR", "okR", "stopR", "count3R", "shrug"]}
NAME = {"presentL": "present", "presentR": "present", "explain": "explain", "waveL": "wave",
        # v020 (keys made with Kie): the state names the director uses
        "pointcamL": "point_camera", "pointsideL": "point_side", "pointsideR": "point_side", "thumbsL": "thumbs_up",
        "thumbsR": "thumbs_up", "fistL": "fist_pump", "chopR": "chop", "okR": "ok", "stopR": "stop", "count3R": "count3",
        "shrug": "shrug", **{g: g[:-1] for g in COUNTS}}
# keys of each gesture in order from rest to the end pose (the wave is a long move and has four). A name with an
# underscore is a whole key file name: the five counts share one in-between (countL_mid).
CHAIN = {g: ["mid", "end"] for g in NAME}
CHAIN["waveL"] = ["q1", "mid", "q3", "end"]
for g in COUNTS:
    CHAIN[g] = ["countL_mid", "end"]
# gestures that share the arm position (only the fingers differ): one blob and box for all, and neighbours change
# directly end -> end (1 -> 2 -> 3 without the hand dropping)
FAMILY = [COUNTS]
# gesture pairs that get a direct clip (through each one's first key). Every other pair goes through the rest pose
# without stopping there; add a pair here when a storyboard needs it often.
PAIRS = {"L": [("presentL", "explain"), ("presentL", "waveL"), ("explain", "waveL"), ("explain", "pointcamL"),
               ("presentL", "pointsideL"), ("presentL", "count1L"), ("explain", "count1L"), ("explain", "thumbsL"),
               ("explain", "shrug"), ("presentL", "pointcamL")],
         "R": [("presentR", "explain"), ("explain", "chopR"), ("explain", "shrug"), ("presentR", "pointsideR"),
               ("explain", "okR"), ("explain", "stopR"), ("presentR", "thumbsR")]}


def kn(g, nm):
    return nm if "_" in nm else f"{g}_{nm}"


def canvas(p):
    return np.array(Image.open(p).convert("RGB").crop((4, 0, 1020, 1536)).resize((W, H), Image.LANCZOS))


def blob(key, master, side):
    """Where the key really differs from the master on this side: big blobs only (thin re-render edges dropped)."""
    d = cv2.GaussianBlur(np.abs(key.astype(np.float32) - master).sum(2), (0, 0), 5) > 42
    d = cv2.morphologyEx(d.astype(np.uint8), cv2.MORPH_OPEN, np.ones((9, 9), np.uint8))
    if side == "L":
        d[:, MID - 8:] = 0
    else:
        d[:, :MID + 8] = 0
    n, lab, st, _ = cv2.connectedComponentsWithStats(d)
    m = np.zeros_like(d)
    if n > 1:
        # the arm is always one big blob (20 000 px or more). Image models also re-render small patches elsewhere
        # (shoes, hair, collar: under 3 000 px): those are kept only next to the arm, where they may be fingers.
        big = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA]))
        m[lab == big] = 1
        near = cv2.dilate(m, np.ones((61, 61), np.uint8))
        for i in range(1, n):
            a = st[i, cv2.CC_STAT_AREA]
            if i != big and (a > 5000 or (a > 700 and (near[lab == i]).any())):
                m[lab == i] = 1
    return cv2.dilate(m, np.ones((33, 33), np.uint8))


def main():
    OUT.mkdir(exist_ok=True)
    lib_master = np.array(Image.open(LIB / "bodies/front/neutral.png").convert("RGBA"))
    a_m = lib_master[:, :, 3].astype(np.float32) / 255
    master = canvas(RAW / "master.png").astype(np.float32)
    cleaned = set(json.loads((OUT / ".edges.json").read_text())) if (OUT / ".edges.json").exists() else set()
    meta = {"canvas": [W, H], "half": {"L": [0, MID + OVER], "R": [MID - OVER, W]}, "frames": {}, "trans": {}, "faces": {}}

    def save(side, name, rgb, box):
        """rgb: full-canvas frame on white. Alpha: master outside the box, white key inside. Save this side's half."""
        x0, y0, x1, y1 = box
        a = a_m.copy()
        rgbf = rgb.astype(np.float32).copy()
        sub = rgbf[y0:y1, x0:x1]
        dist = 255 - sub.min(2)
        ak = np.clip((dist - 10) / 40, 0, 1)
        ak = ak * ak * (3 - 2 * ak)
        a[y0:y1, x0:x1] = ak
        un = (sub - (1 - ak[:, :, None]) * 255) / np.maximum(ak[:, :, None], .05)
        rgbf[y0:y1, x0:x1] = np.where(ak[:, :, None] > .02, np.clip(un, 0, 255), sub)
        out = np.dstack([rgbf, a * 255]).astype(np.uint8)
        hx0, hx1 = meta["half"][side]
        (OUT / side).mkdir(exist_ok=True)
        # the cutout edge is cleaned here, at every save (v020 fix: a key that was saved again by a later build kept
        # its raw jagged edge, because edges.py had it in its "done" list; the rest pose showed a dotted white fringe)
        Image.fromarray(edges.clean(out[:, hx0:hx1])).save(OUT / side / f"{name}.webp", "WEBP", quality=90, method=6)
        cleaned.add(f"{side}/{name}.webp")
        return f"{side}/{name}.webp"

    for side, gests in GEST.items():
        gests = [g for g in gests if all((RAW / f"{kn(g, nm)}.png").exists() for nm in CHAIN[g])]
        keys, boxes, fam_u = {}, {}, {}
        for fam in FAMILY:                                # one union blob for a whole family
            mem = [g for g in fam if g in gests]
            if mem:
                names = {kn(g, nm) for g in mem for nm in CHAIN[g]}
                u = np.maximum.reduce([blob(canvas(RAW / f"{n_}.png"), master, side) for n_ in sorted(names)])
                for g in mem:
                    fam_u[g] = u
        for g in gests:
            ks = {kn(g, nm): canvas(RAW / f"{kn(g, nm)}.png") for nm in CHAIN[g]}
            u = fam_u[g] if g in fam_u else np.maximum.reduce([blob(k, master, side) for k in ks.values()])
            ys, xs = np.nonzero(u)
            box = [max(0, int(xs.min()) - 6), max(0, int(ys.min()) - 6), min(W, int(xs.max()) + 7), min(H, int(ys.max()) + 7)]
            if side == "L":
                box[2] = min(box[2], MID - 4)
            else:
                box[0] = max(box[0], MID + 4)
            boxes[g] = box
            f = cv2.GaussianBlur(u.astype(np.float32), (0, 0), 3)[:, :, None]   # union blob: the hanging arm is removed
            for nm, k in ks.items():                                             # in every key of the gesture
                keys[nm] = master * (1 - f) + k * f
            print(side, g, "box", box, flush=True)
        keys["rest"] = master
        save(side, "key_rest", master, [0, 0, 1, 1])     # every key is saved again with a clean edge (cheap, no FILM)
        for g in gests:
            for nm in CHAIN[g]:
                save(side, f"key_{kn(g, nm)}", keys[kn(g, nm)], boxes[g])

        def seg(a, b, box):
            """Frame files for a -> b (both keys), ends included; FILM runs only inside the box."""
            name = f"{a}__{b}"
            if name in meta["frames"].get(side, {}):
                return meta["frames"][side][name]
            x0, y0, x1, y1 = box
            done = [f"{side}/{name}_{i:02d}.webp" for i in range(N)]
            if all((OUT / f).exists() for f in done):        # cached: FILM is the slow part
                files = [f"{side}/key_{a}.webp"] + done + [f"{side}/key_{b}.webp"]
                meta["frames"].setdefault(side, {})[name] = files
                return files
            mids = film.interpolate(keys[a][y0:y1, x0:x1].astype(np.uint8), keys[b][y0:y1, x0:x1].astype(np.uint8), N)
            files = [save(side, f"key_{a}", keys[a], box if a != "rest" else [0, 0, 1, 1])]
            for i, m in enumerate(mids):
                fr = master.copy()
                fr[y0:y1, x0:x1] = m
                files.append(save(side, f"{name}_{i:02d}", fr, box))
            files.append(save(side, f"key_{b}", keys[b], box if b != "rest" else [0, 0, 1, 1]))
            meta["frames"].setdefault(side, {})[name] = files
            print("  seg", side, name, len(files), flush=True)
            return files

        up = {}
        for g in gests:                                   # rest -> key -> ... -> end
            chain = ["rest"] + [kn(g, nm) for nm in CHAIN[g]]
            fr = []
            for a, b in zip(chain, chain[1:]):
                sg = seg(a, b, boxes[g])
                fr += sg if not fr else sg[1:]
            up[g] = fr
            meta["trans"][f"{side}:rest>{NAME[g]}"] = fr
            meta["trans"][f"{side}:{NAME[g]}>rest"] = fr[::-1]
        direct = {}
        for g, h in PAIRS[side]:                          # chosen pairs: a direct clip through each one's first key
            if g in gests and h in gests:
                bx = [min(boxes[g][0], boxes[h][0]), min(boxes[g][1], boxes[h][1]),
                      max(boxes[g][2], boxes[h][2]), max(boxes[g][3], boxes[h][3])]
                mm = seg(kn(g, CHAIN[g][0]), kn(h, CHAIN[h][0]), bx)
                direct[(g, h)] = up[g][::-1][:len(up[g]) - N - 2] + mm + up[h][N + 2:]
        for fam in FAMILY:                                # family neighbours: end -> end, longer steps chain them
            mem = [g for g in fam if g in gests]
            step = {i: seg(kn(mem[i], "end"), kn(mem[i + 1], "end"), boxes[mem[i]]) for i in range(len(mem) - 1)}
            for i in range(len(mem)):
                for j in range(i + 1, len(mem)):
                    path = []
                    for k_ in range(i, j):
                        path += step[k_] if not path else step[k_][1:]
                    direct[(mem[i], mem[j])] = path
        for i, g in enumerate(gests):
            for h in gests[i + 1:]:
                path = direct.get((g, h)) or (direct.get((h, g)) or [])[::-1] or up[g][::-1] + up[h][1:]
                meta["trans"][f"{side}:{NAME[g]}>{NAME[h]}"] = path
                meta["trans"][f"{side}:{NAME[h]}>{NAME[g]}"] = path[::-1]
        meta.setdefault("states", {})[side] = {"rest": f"{side}/key_rest.webp",
                                               **{NAME[g]: f"{side}/key_{kn(g, 'end')}.webp" for g in gests}}

    # face patches (cropped to the head box)
    P, (x0, y0, w, h) = faces.patches(lib_master)
    (OUT / "face").mkdir(exist_ok=True)
    for e, (p, cc) in P.items():
        Image.fromarray(p[y0:y0 + h, x0:x0 + w]).save(OUT / "face" / f"{e}.webp", "WEBP", quality=92, method=6)
        meta["faces"][e] = {"src": f"face/{e}.webp", "kind": "mouth" if faces.KIND[e] is faces.MOUTH else "face", "cc": cc}
    meta["face_box"] = [x0, y0, w, h]
    (OUT / "anim.json").write_text(json.dumps(meta, indent=1))
    (OUT / ".edges.json").write_text(json.dumps(sorted(cleaned)))
    print(edges.run(), "older frames edge-cleaned")
    n = sum(1 for _ in OUT.rglob("*.webp")); mb = sum(p.stat().st_size for p in OUT.rglob("*.webp")) / 1e6
    print(f"{n} files, {mb:.1f} MB, {len(meta['trans'])} transitions")


if __name__ == "__main__":
    main()
