"""Copy the mascot library pieces the reel uses into assets/lib/ (v012).

Usage: python3 prep_lib.py     (reads ../../mascot/library/library.json; needs Pillow)

- bodies: the head-less body where a head fit exists (the head is drawn on top), else the full body;
  820x1240 canvas, feet at (410, 1215), saved as WebP.
- heads: every expression of the angles used, scaled to 2/3 (enough for a 4K render), WebP.
- assets/lib/lib.json: per body its file, whether it is head-less, and the head fit (left, top, scale) on the
  820x1240 canvas; head canvas 640x720 in the fit's units.
"""
import json
from pathlib import Path

from PIL import Image

HERE = Path(__file__).resolve().parent
LIB = HERE.parents[1] / "mascot" / "library"
OUT = HERE / "assets" / "lib"
BODIES = ["front/neutral", "front/presenting", "front/explain_both", "front/thinking_chin", "front/shrug",
          "front/waving", "front/point_side", "front/point_camera", "front/arms_crossed", "front/victory",
          "front/thumbs_up", "front/walk_front", "34left/neutral", "34right/neutral", "back/neutral",
          "profileright/walk_side", "profileright/neutral", "profileleft/neutral"]
HEAD_SCALE = 2 / 3


def main():
    lib = json.loads((LIB / "library.json").read_text())
    bodies = {f"{a['angle']}/{a['pose']}": a for a in lib["assets"] if a["kind"] == "body"}
    out = {"canvas": [820, 1240], "feet": [410, 1215], "head_canvas": [640, 720], "bodies": {}, "heads": {}}
    angles = set()
    for key in BODIES:
        a = bodies[key]
        f = a.get("head_fit")
        src = LIB / (f["headless"] if f else a["file"])
        dst = OUT / "bodies" / f"{key.replace('/', '_')}.webp"
        dst.parent.mkdir(parents=True, exist_ok=True)
        Image.open(src).save(dst, "WEBP", quality=92, method=6)
        out["bodies"][key] = {"src": str(dst.relative_to(HERE)), "headless": bool(f)}
        if f:
            out["bodies"][key]["fit"] = {k: f[k] for k in ("angle", "left", "top", "scale")}
            angles.add(f["angle"])
    for a in lib["assets"]:
        if a["kind"] == "head" and a["angle"] in angles:
            im = Image.open(LIB / a["file"])
            im = im.resize((round(im.width * HEAD_SCALE), round(im.height * HEAD_SCALE)), Image.LANCZOS)
            dst = OUT / "heads" / a["angle"] / f"{a['expression']}.webp"
            dst.parent.mkdir(parents=True, exist_ok=True)
            im.save(dst, "WEBP", quality=92, method=6)
            out["heads"].setdefault(a["angle"], []).append(a["expression"])
    (OUT / "lib.json").write_text(json.dumps(out, indent=1))
    n = sum(1 for _ in OUT.rglob("*.webp"))
    size = sum(p.stat().st_size for p in OUT.rglob("*.webp")) / 1e6
    print(f"{len(out['bodies'])} bodies, {n - len(out['bodies'])} heads, {size:.1f} MB")


if __name__ == "__main__":
    main()
