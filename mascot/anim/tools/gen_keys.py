"""Generate the gesture keyframes as edits of raw/master.png through the ChatGPT bridge (skips existing files).

Each gesture has an END pose and one MID pose (the animator's in-between, made with the end pose as a reference).
"L" is the arm on the viewer's left (his right arm), "R" the arm on the viewer's right.
Usage: python3 gen_keys.py [name ...]
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
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
}
REFS = {"waveL_q1": ["waveL_mid"], "waveL_q3": ["waveL_mid", "waveL_end"]}

if __name__ == "__main__":
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
