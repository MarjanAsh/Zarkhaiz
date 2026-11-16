"""Write mascot/anim/manifest.json: every control, preset, clip and gesture of the animated character, with the
capability counts used for the before/after comparison (v019 -> v020). Run after build_anim.py.

Usage: python3 manifest.py
"""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import expressions as E
import director as D

ROOT = Path(__file__).resolve().parents[1]
anim = json.loads((ROOT / "out" / "anim.json").read_text())

arm_states = {s: sorted(k for k in anim["states"][s] if k != "rest") for s in ("L", "R")}
clips = {}
for k, fr in anim["trans"].items():
    side, ab = k.split(":")
    clips.setdefault(side, {})[ab] = len(fr)

face_controls = {
    "eye": "lid opening: 0 closed, .30 open, up to .42 wide; blinks close it for .23 s",
    "gx": "gaze left (-) / right (+), about +-12", "gy": "gaze down (-) / up (+), about +-10",
    "brow": "both eyebrows: + raised, - lowered and drawn together, +-25",
    "brow_l": "the eyebrow on the viewer's left alone", "brow_r": "the eyebrow on the viewer's right alone",
    "smile": "mouth corners: -0.6 frown .. 1.3 broad smile", "pout": "lips pushed forward",
    "lip": "emotional mouth opening (only while he is not speaking)",
    "speech mouth": "21 expression keypoints generated from the voice (lips, jaw, cheeks), 25 per second",
    "pitch": "head down (+) / up (-), +-6 degrees", "yaw": "head turn, +-7 degrees plus the body-turn yaw",
    "roll": "head tilt, +-4 degrees",
}
head_events = {"nod": "pitch down and back", "shake": "two quick yaw swings: no", "tilt": "roll to one side and back",
               "forward": "chin a little down, toward the viewer", "look_up": "pitch up and back", "look_down": "pitch down and back"}
body_controls = {
    "lean_fwd": "upper body toward the camera (grows up to 2.8 %, drops up to 9 px), hips and feet stay",
    "lean_back": "the opposite: a small recoil", "shrug": "both shoulders up to 9 px, the neck shortens",
    "shoulder_l": "the shoulder on the viewer's left alone", "shoulder_r": "the shoulder on the viewer's right alone",
    "weight shift": "automatic: hips drift from one leg to the other, feet planted",
    "breathing": "automatic: the chest widens slightly with each breath",
    "turn tl / tr": "slight whole-body turn toward the cards (5 in-between frames), only while both arms rest",
    "glide": "he moves across the stage between scenes (1 s, eased)",
}
# v019, counted from the v019 files: anim.json states; build_face.py track (smile, brow, lids for blinks, pitch, yaw,
# roll; closed mouth; a nod per line); main.js (weight shift, breathing, body turn, glide)
before = {"arm states L": 3, "arm states R": 2, "hand shapes": 2, "expression presets": 0, "face controls used": 6,
          "mouth shapes": 1, "head events": 1, "body controls": 4, "semantic gestures": 0, "director rules (concepts)": 0,
          "word times": "estimated from word length"}
hand_shapes = sorted({"open palm up (present, explain, shrug)", "open hand facing camera (wave, count 5)", "stop palm",
                      "index pointing at camera", "index pointing sideways", "one finger", "two fingers", "three fingers",
                      "four fingers", "thumbs-up", "closed fist", "flat blade hand (chop)", "OK sign", "relaxed hanging hand"})
after = {"arm states L": len(arm_states["L"]), "arm states R": len(arm_states["R"]), "hand shapes": len(hand_shapes),
         "expression presets": len(E.PRESETS) - 1, "face controls used": len(face_controls),
         "mouth shapes": "continuous (generated from the voice)", "head events": len(head_events),
         "body controls": len(body_controls), "semantic gestures": len(D.GESTURES),
         "director rules (concepts)": len(D.CONCEPT_GESTURES), "word times": "measured from the audio (forced alignment)"}

m = {
    "character": "OutputDM founder mascot, front view, one master image (raw/master.png)",
    "rig": {"root": "stage position (glide)", "hips": "weight shift, body turn", "torso": "lean, breathing",
            "shoulders": ["shrug", "shoulder_l", "shoulder_r"],
            "arms": {"L (viewer's left = his right arm)": arm_states["L"], "R (viewer's right = his left arm)": arm_states["R"]},
            "neck/head": list(head_events) + ["pitch", "yaw", "roll"],
            "face": list(face_controls), "legs": "planted (no clips yet)"},
    "face_controls": face_controls,
    "expression_presets": {n: {"controls": c, "use": u} for n, (c, u) in E.PRESETS.items()},
    "intensity_levels": E.LEVELS,
    "head_events": head_events, "body_controls": body_controls, "hand_shapes": hand_shapes,
    "arm_clips": {s: {"states": arm_states[s], "transitions (frames)": clips.get(s, {})} for s in ("L", "R")},
    "gestures": {g: {"purpose": v["purpose"], "arm candidates": v["arm"], "face": v["face"], "head": v["head"], "body": v["body"],
                     "hold s": v["hold"], "clip length s": v["dur"], "emotions": v["emotions"], "max repeats in a row": v["repeat"]}
                 for g, v in D.GESTURES.items()},
    "concepts": {c: {"cue words": D.CUES.get(c, "from the script structure"), "gestures": g, "priority": D.PRIORITY[c]}
                 for c, g in D.CONCEPT_GESTURES.items()},
    "capability": {"before v019": before, "after v020": after},
}
(ROOT / "manifest.json").write_text(json.dumps(m, indent=1, ensure_ascii=False))
print(json.dumps(m["capability"], indent=1))
