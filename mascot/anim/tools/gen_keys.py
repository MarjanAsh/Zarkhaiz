"""Generate the gesture keyframes as edits of raw/master.png (skips existing files).

Backend: the ChatGPT bridge (bridge_edit.py) by default; with KEYS_BACKEND=kie the same edits go through Kie.ai
(kie_edit.py, GPT Image 2 image-to-image, 6 credits = about $0.03 per image; the user allowed Kie for IMAGES only,
Nov 16). The v020 gestures (pointing, counting, thumbs-up, fist, chop, OK, stop, shrug) were made with Kie.
With KEYS_PARALLEL=4 the missing "end" keys are made first, four at a time, then the in-betweens.

Each gesture has an END pose and one MID pose (the animator's in-between, made with the end pose as a reference).
"L" is the arm on the viewer's left (his right arm), "R" the arm on the viewer's right.
Usage: python3 gen_keys.py [name ...]
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
import os
if os.environ.get("KEYS_BACKEND") == "kie":
    from kie_edit import edit
else:
    from bridge_edit import edit

RAW = Path(__file__).resolve().parents[1] / "raw"
MASTER = str(RAW / "master.png")
HALF = ("The second attached image shows the END of a motion. Make the frame EXACTLY HALFWAY through that motion, as an "
        "animator's in-between between the base image and the second image: ")
KEYS = {
    "presentL_end": "Change ONLY his right arm (the arm on the viewer's LEFT side): raise it so the forearm points out to the viewer's left at chest height with an open palm facing up, a presenting gesture toward the viewer's left. The other arm stays hanging exactly as it is.",
    "presentL_mid": HALF + "change ONLY that same arm, so the upper arm has swung a little away from the body, the elbow is bent about 45 degrees and the hand is at belt height, about halfway between its hanging position and its final position, palm starting to turn up. The other arm stays hanging exactly as in the base image.",
    "explain_end": "Change ONLY his two arms: both forearms raised in front of the belly, elbows bent about 90 degrees and kept close to the body, both hands open with palms facing up and slightly inward, fingers relaxed: a natural 'explaining while talking' gesture. Each hand stays on its own side of the body: the hands do not touch each other and do not cross the centre line of the body; they are about a shoulder width apart.",
    "explain_mid": HALF + "change ONLY the two arms, each one halfway between hanging and its final position: elbows bent about 45 degrees, hands at hip height a little in front of the body, palms starting to turn up. Each hand stays on its own side of the body.",
    "presentR_end": "Change ONLY his left arm (the arm on the viewer's RIGHT side): raise it so the forearm points out to the viewer's right at chest height with an open palm facing up, a presenting gesture toward the viewer's right. The other arm stays hanging exactly as it is.",
    "presentR_mid": HALF + "change ONLY that same arm (viewer's right side), so the upper arm has swung a little away from the body, the elbow is bent about 45 degrees and the hand is at belt height, about halfway between its hanging position and its final position, palm starting to turn up. The other arm stays hanging exactly as in the base image.",
    "waveL_end": "Change ONLY his right arm (the arm on the viewer's LEFT side): raised in a friendly wave, elbow bent and out to the side, the open hand beside his head at ear height with the palm facing the camera. The hand does not cover the face or the hair and stays clearly to the viewer's left of the head. The other arm stays hanging exactly as it is.",
    "waveL_mid": HALF + "change ONLY that same arm, halfway up: elbow bent about 90 degrees, forearm pointing out to the viewer's left and slightly up, the open hand at chest height, palm turning toward the camera. The other arm stays hanging exactly as in the base image.",
    # the wave is a long move, so it gets two more in-betweens: q1 (rest..mid) and q3 (mid..end)
    "waveL_q1": "The second attached image shows a LATER frame of a motion in which he raises his right arm (viewer's left) to wave. Make the frame EXACTLY HALFWAY between the base image (arm hanging) and that second image, as an animator's in-between: change ONLY that same arm: the upper arm has swung slightly away from the body, the elbow is bent about 40 degrees, the open hand is at belt height a little out to the viewer's left, fingers relaxed. The other arm stays hanging exactly as in the base image.",
    "waveL_q3": "The second and third attached images are two frames of a motion in which he raises his right arm (viewer's left) to wave: the second is earlier, the third is the final wave. Make the frame EXACTLY HALFWAY between those two, as an animator's in-between: change ONLY that same arm compared with the base image: the elbow is out to the viewer's left at chest height, the forearm points up and outward, the open hand is at shoulder height with the palm facing the camera. The other arm stays hanging exactly as in the base image.",
    # ---- v020 gestures (made with Kie) ----
    "pointcamL_end": "Change ONLY his right arm (the arm on the viewer's LEFT side): bend the elbow and raise the hand in front of the viewer's-left half of his chest, pointing the index finger straight at the camera (at the viewer), the other fingers curled, the hand seen foreshortened from the front. The hand stays on the viewer's left of the body's centre line and well below the chin. The other arm stays hanging exactly as it is.",
    "pointcamL_mid": HALF + "change ONLY that same arm (viewer's left side): the elbow bent about 50 degrees, the hand at belt height a little in front of the body, the index finger starting to straighten toward the camera. The other arm stays hanging exactly as in the base image.",
    "pointsideL_end": "Change ONLY his right arm (the arm on the viewer's LEFT side): stretch it out to the viewer's left at shoulder height, almost straight with a slightly bent elbow, the index finger pointing to the viewer's left (toward something beside him), the other fingers curled. The other arm stays hanging exactly as it is.",
    "pointsideL_mid": HALF + "change ONLY that same arm (viewer's left side): the upper arm lifted about 40 degrees away from the body, the elbow bent, the hand at waist height out to the viewer's left, the index finger starting to point to the viewer's left. The other arm stays hanging exactly as in the base image.",
    "countL_mid": "Change ONLY his right arm (the arm on the viewer's LEFT side): bend the elbow about 60 degrees so the forearm comes up and a little outward and the loosely closed hand is at belt height beside the body on the viewer's left, the back of the hand toward the viewer's left. It is the halfway frame of raising the hand to show a number with the fingers. The other arm stays hanging exactly as it is.",
    "count1L_end": "Change ONLY his right arm (the arm on the viewer's LEFT side): raise the forearm so the hand is beside the body at shoulder height on the viewer's left, palm facing the camera, showing the number ONE: only the index finger straight up, the other three fingers curled and held down by the thumb. The hand stays clear of the face and the hair. The other arm stays hanging exactly as it is.",
    "count2L_end": "Change ONLY his right arm (the arm on the viewer's LEFT side): raise the forearm so the hand is beside the body at shoulder height on the viewer's left, palm facing the camera, showing the number TWO: the index and middle fingers straight up and slightly apart, the ring and little fingers curled and held down by the thumb. The hand stays clear of the face and the hair. The other arm stays hanging exactly as it is.",
    "count3L_end": "Change ONLY his right arm (the arm on the viewer's LEFT side): raise the forearm so the hand is beside the body at shoulder height on the viewer's left, palm facing the camera, showing the number THREE: the index, middle and ring fingers straight up, the thumb holding down the little finger. The hand stays clear of the face and the hair. The other arm stays hanging exactly as it is.",
    "count4L_end": "Change ONLY his right arm (the arm on the viewer's LEFT side): raise the forearm so the hand is beside the body at shoulder height on the viewer's left, palm facing the camera, showing the number FOUR: the four fingers straight up and slightly apart, the thumb folded across the palm. The hand stays clear of the face and the hair. The other arm stays hanging exactly as it is.",
    "count5L_end": "Change ONLY his right arm (the arm on the viewer's LEFT side): raise the forearm so the hand is beside the body at shoulder height on the viewer's left, palm facing the camera, showing the number FIVE: an open hand with all five fingers straight and spread. The hand stays clear of the face and the hair. The other arm stays hanging exactly as it is.",
    "thumbsL_end": "Change ONLY his right arm (the arm on the viewer's LEFT side): bend the elbow and raise the hand in front of the viewer's-left half of his chest in a clear thumbs-up: a closed fist with the thumb pointing straight up, knuckles toward the camera. The other arm stays hanging exactly as it is.",
    "thumbsL_mid": HALF + "change ONLY that same arm (viewer's left side): the elbow bent about 50 degrees, the loosely closed hand at belt height a little in front of the body, the thumb starting to lift. The other arm stays hanging exactly as in the base image.",
    "fistL_end": "Change ONLY his right arm (the arm on the viewer's LEFT side): a happy fist pump: the elbow bent and out to the viewer's left, the closed fist raised beside the body at shoulder height on the viewer's left, knuckles toward the camera. The fist stays clear of the face and the hair. The other arm stays hanging exactly as it is.",
    "fistL_mid": HALF + "change ONLY that same arm (viewer's left side): the elbow bent about 60 degrees, the closing fist at waist height beside the body on the viewer's left, moving upward. The other arm stays hanging exactly as in the base image.",
    "pointsideR_end": "Change ONLY his left arm (the arm on the viewer's RIGHT side): stretch it out to the viewer's right at shoulder height, almost straight with a slightly bent elbow, the index finger pointing to the viewer's right (toward something beside him), the other fingers curled. The other arm stays hanging exactly as it is.",
    "pointsideR_mid": HALF + "change ONLY that same arm (viewer's right side): the upper arm lifted about 40 degrees away from the body, the elbow bent, the hand at waist height out to the viewer's right, the index finger starting to point to the viewer's right. The other arm stays hanging exactly as in the base image.",
    "thumbsR_end": "Change ONLY his left arm (the arm on the viewer's RIGHT side): bend the elbow and raise the hand in front of the viewer's-right half of his chest in a clear thumbs-up: a closed fist with the thumb pointing straight up, knuckles toward the camera. The other arm stays hanging exactly as it is.",
    "thumbsR_mid": HALF + "change ONLY that same arm (viewer's right side): the elbow bent about 50 degrees, the loosely closed hand at belt height a little in front of the body, the thumb starting to lift. The other arm stays hanging exactly as in the base image.",
    "chopR_end": "Change ONLY his left arm (the arm on the viewer's RIGHT side): an emphasising 'chop' gesture: the elbow bent about 90 degrees and close to the body, the forearm pointing forward and slightly up in front of the viewer's-right half of his belly, the hand flat and vertical like a blade (thumb on top, little finger down, fingers together pointing toward the camera). The hand stays on the viewer's right of the body's centre line. The other arm stays hanging exactly as it is.",
    "chopR_mid": HALF + "change ONLY that same arm (viewer's right side): the elbow bent about 45 degrees, the flat hand at hip height a little in front of the body, turning so the thumb is on top. The other arm stays hanging exactly as in the base image.",
    "okR_end": "Change ONLY his left arm (the arm on the viewer's RIGHT side): raise the forearm so the hand is beside the body at chest height on the viewer's right, making a clear OK sign toward the camera: the tips of the thumb and index finger touching in a circle, the other three fingers straight and spread upward. The other arm stays hanging exactly as it is.",
    "okR_mid": HALF + "change ONLY that same arm (viewer's right side): the elbow bent about 50 degrees, the relaxed hand at belt height beside the body on the viewer's right, the thumb and index finger starting to come together. The other arm stays hanging exactly as in the base image.",
    "stopR_end": "Change ONLY his left arm (the arm on the viewer's RIGHT side): a firm 'stop' gesture: the elbow bent, the open hand held up beside the body at shoulder height on the viewer's right and pushed a little toward the camera, palm facing the camera, fingers together pointing straight up. The hand stays clear of the face and the hair. The other arm stays hanging exactly as it is.",
    "stopR_mid": HALF + "change ONLY that same arm (viewer's right side): the elbow bent about 60 degrees, the open hand at waist height beside the body on the viewer's right, the palm turning toward the camera. The other arm stays hanging exactly as in the base image.",
    "count3R_end": "Change ONLY his left arm (the arm on the viewer's RIGHT side): raise the forearm so the hand is at chest height beside the body, palm facing the camera, showing the number three with the index, middle and ring fingers straight up and the thumb holding down the little finger. The other arm stays hanging exactly as it is.",
    "count3R_mid": HALF + "change ONLY that same arm (viewer's right side): the elbow bent about 60 degrees, the loosely closed hand at belt height beside the body on the viewer's right. The other arm stays hanging exactly as in the base image.",
    "shrug_end": "Change ONLY his two arms: a questioning shrug: both elbows bent and held a little away from the body, both forearms turned outward to the sides, both hands open at waist height with the palms facing up, fingers relaxed and spread, the hands wide apart (each hand well outside its own hip). Each hand stays on its own side of the body.",
    "shrug_mid": HALF + "change ONLY the two arms, each one halfway between hanging and its final position: elbows bent about 40 degrees, hands at hip height a little out to the sides, palms starting to turn up. Each hand stays on its own side of the body.",
}

# ---- v021 (Nov 24): the user said the arms still look unnatural. Two causes found in the v020 frames:
# 1. the rest pose is a stiff mannequin hang (straight arms, spread fingers) and it is on screen most of the time;
# 2. FILM melts the hand on the first step (hanging -> mid): the hand turns over and comes forward at once.
# So: a relaxed stance per arm (the new idle pose), and a quarter-way key (q1) before each core gesture's mid.
Q1 = ("The second attached image shows a LATER frame of a motion that starts from the base image. Make the frame "
      "EXACTLY HALFWAY between the base image and that second image, as an animator's in-between: ")
Q3 = ("The second and third attached images are two frames of one motion: the second is earlier, the third is the "
      "final pose. Make the frame EXACTLY HALFWAY between those two, as an animator's in-between: ")
Q1F = ("The second attached image shows a much LATER frame of a motion that starts from the base image; use it only to "
       "see the direction of the motion. Make a very EARLY frame of that motion, only a QUARTER of the way from the base "
       "image toward the second image: the arm has barely started to move and must look much closer to the base image "
       "than to the second image: ")
KEEP = " Head, face, torso, legs, the other arm, the framing and the scale stay exactly as in the base image."
KEYS.update({
    "relaxedL_end": "Change ONLY his right arm (the arm on the viewer's LEFT side) into a relaxed, natural standing pose: "
        "the upper arm hangs close to the side of the body, the elbow is softly bent about 20 degrees so the forearm angles a "
        "little forward, and the hand rests loosely in front of the side of the thigh, fingers gently curled together (not "
        "spread, not a fist), palm toward the leg. It must look calm and natural, not stiff." + KEEP,
    "relaxedR_end": "Change ONLY his left arm (the arm on the viewer's RIGHT side) into a relaxed, natural standing pose: "
        "the upper arm hangs close to the side of the body, the elbow is softly bent about 20 degrees so the forearm angles a "
        "little forward, and the hand rests loosely in front of the side of the thigh, fingers gently curled together (not "
        "spread, not a fist), palm toward the leg. It must look calm and natural, not stiff." + KEEP,
    "presentL_q1": Q1 + "change ONLY his right arm (viewer's LEFT side): the elbow bends about 20 degrees, the hand lifts a "
        "little forward and outward from the thigh to just below the hip, the palm starting to turn up, fingers relaxed and "
        "together. The hand keeps its full shape: five fingers, no blur." + KEEP,
    "presentR_q1": Q1 + "change ONLY his left arm (viewer's RIGHT side): the elbow bends about 20 degrees, the hand lifts a "
        "little forward and outward from the thigh to just below the hip, the palm starting to turn up, fingers relaxed and "
        "together. The hand keeps its full shape: five fingers, no blur." + KEEP,
    "explain_q1": Q1 + "change ONLY the two arms, each one a quarter of the way from hanging toward the explaining pose: "
        "elbows bent about 20 degrees, both hands lifted a little forward to just below the hips, palms starting to turn "
        "up, fingers relaxed. Each hand stays on its own side of the body. Both hands keep their full shape, no blur." + KEEP,
    "pointcamL_q1": Q1 + "change ONLY his right arm (viewer's LEFT side): the elbow bends about 25 degrees, the loosely "
        "closed hand lifts a little forward from the thigh to hip height, knuckles toward the viewer's left, the index "
        "finger not yet pointing. The hand keeps its full shape, no blur." + KEEP,
    # Nov 25: the first prompts overshot (fist came up to belt height, almost the mid key) in 3 tries each, so these
    # two say how SMALL the move is, in body landmarks, and that it must stay far from the second image.
    "thumbsL_q1": Q1F + "change ONLY his right arm (viewer's LEFT side): the upper arm still hangs straight down against "
        "the side of the body, only the elbow bends slightly (about 20 degrees), so the hand moves just ONE HAND'S WIDTH "
        "forward and up from where it hangs. The hand stays BELOW the bottom edge of the jacket, beside the upper thigh, "
        "never at belt height and never in front of the belly. The fingers curl loosely into a soft, half-closed hand, the "
        "thumb resting on the index finger. The hand keeps its full shape, no blur." + KEEP,
    "countL_q1": Q1F + "change ONLY his right arm (viewer's LEFT side): the upper arm still hangs straight down against "
        "the side of the body, only the elbow bends slightly (about 20 degrees), so the hand moves just ONE HAND'S WIDTH "
        "forward and up from where it hangs. The hand stays BELOW the bottom edge of the jacket, beside the upper thigh, "
        "never at belt height and never in front of the belly. The fingers curl loosely into a soft, half-closed hand, "
        "knuckles toward the viewer's left. The hand keeps its full shape, no blur." + KEEP,
    "countL_q3": Q3 + "change ONLY his right arm (viewer's LEFT side) compared with the base image: the forearm points up "
        "and a little outward, the hand is at chest height beside the body on the viewer's left, palm turning toward the "
        "camera, the fingers still loosely closed (no finger raised yet). The hand stays clear of the face." + KEEP,
    "shrug_q1": Q1 + "change ONLY the two arms, each a quarter of the way from hanging toward the shrug: elbows bent "
        "about 20 degrees, hands lifted a little out to the sides at upper-thigh height, palms starting to turn up, "
        "fingers relaxed. Each hand stays on its own side of the body; both hands keep their full shape." + KEEP,
})
REFS = {"waveL_q1": ["waveL_mid"], "waveL_q3": ["waveL_mid", "waveL_end"],
        **{f"{g}_q1": [f"{g}_mid"] for g in ("presentL", "presentR", "explain", "pointcamL", "thumbsL", "shrug")},
        "countL_q1": ["countL_mid"], "countL_q3": ["countL_mid", "count3L_end"]}
V021 = ["relaxedL_end", "relaxedR_end", "presentL_q1", "presentR_q1", "explain_q1", "pointcamL_q1", "thumbsL_q1",
        "countL_q1", "countL_q3", "shrug_q1"]

def one(name):
    out = RAW / f"{name}.png"
    if out.exists():
        return "skip " + name
    refs = REFS.get(name, [name.split("_")[0] + "_end"] if name.endswith("_mid") and (RAW / f"{name.split('_')[0]}_end.png").exists() else [])
    try:
        return f"ok {name} {edit(str(out), KEYS[name], [MASTER] + [str(RAW / f'{r}.png') for r in refs])}"
    except Exception as e:
        return f"FAIL {name} {e}"


if __name__ == "__main__" and os.environ.get("KEYS_PARALLEL"):
    from concurrent.futures import ThreadPoolExecutor
    names = sys.argv[1:] or list(KEYS)
    with ThreadPoolExecutor(int(os.environ["KEYS_PARALLEL"])) as ex:
        for group in ([n for n in names if not n.endswith("_mid") or n == "countL_mid"], [n for n in names if n.endswith("_mid") and n != "countL_mid"]):
            for r in ex.map(one, group):
                print(r, flush=True)
elif __name__ == "__main__":
    for name in (sys.argv[1:] or list(KEYS)):
        out = RAW / f"{name}.png"
        if out.exists():
            print("skip", name); continue
        refs = REFS.get(name, [name.split("_")[0] + "_end"] if name.endswith("_mid") else [])
        imgs = [MASTER] + [str(RAW / f"{r}.png") for r in refs]
        try:
            print("ok", name, edit(str(out), KEYS[name], imgs), flush=True)
        except Exception as e:
            print("FAIL", name, e, flush=True)
            if "USAGE LIMIT" in str(e):
                break
