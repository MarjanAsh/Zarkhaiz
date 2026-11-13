"""The generation jobs for the mascot library (one job = one generated image).

A job is either a single asset or a grid sheet (rows x cols cells, read left to right, top to bottom).
gen.py sends each job to the generator; post.py cuts the result into assets.
"""

RAW = "https://raw.githubusercontent.com/marjanash/zarkhaiz/ccr-e371ce1b-168zzm/"
REFS = [
    RAW + "mascot/library/refs/source.jpg",  # JPG copy of mascot/rig/source.webp (the A-pose)
    RAW + "mascot/character/refs/sheet1.jpg",
    RAW + "mascot/character/refs/sheet2.jpg",
    RAW + "mascot/character/refs/sheet3.jpg",
]

IDENTITY = (
    "Character: exactly the same 3D stylized animated man as in the reference images: same round full face, "
    "fair-wheatish skin, thick voluminous jet-black hair swept up and back, thick dark eyebrows, full neatly groomed "
    "black beard and moustache, thin clear rectangular glasses with silver rims, broad slightly heavy build. "
    "Outfit exactly as the references: black two-button suit jacket, black button-up shirt with collar, no tie, "
    "black trousers, black belt with silver buckle, black leather shoes, small gold pocket square in the left breast "
    "pocket (his left), dark wristwatch on his left wrist. Same high-end 3D animated feature-film render style, "
    "same proportions. Do not slim him, do not make him younger, do not change the face."
)
STUDIO = (
    "Plain flat pure white background (#FFFFFF), even soft studio light, no cast shadow and no floor shadow, "
    "no text, no labels, no watermark, no frame. Nothing cropped unless stated."
)

ANGLES = {
    "front": "facing the camera straight on",
    "34left": "three-quarter view, turned about 40 degrees so he faces the viewer's left",
    "34right": "three-quarter view, turned about 40 degrees so he faces the viewer's right",
    "profileleft": "exact side profile facing the viewer's left",
    "profileright": "exact side profile facing the viewer's right",
}

# 12 head expressions, two sheets of 6 per angle. Never an angry face.
EXPR_A = ["neutral", "smile", "laugh", "talk_a", "talk_o", "talk_teeth"]
EXPR_B = ["surprised", "thinking", "concerned", "smirk", "wink", "talk_e"]
EXPR_TEXT = {
    "neutral": "neutral relaxed face, mouth closed",
    "smile": "warm friendly closed-mouth smile",
    "laugh": "big happy laugh, mouth wide open, eyes squinting with joy",
    "talk_a": "talking, mouth open wide on an 'A' (aah) sound, relaxed brows",
    "talk_o": "talking, lips rounded on an 'O' sound",
    "talk_teeth": "talking, lips apart with teeth closed (as on 'S' or 'T')",
    "surprised": "surprised, eyebrows high, mouth open in a small 'oh'",
    "thinking": "thinking, eyes looking up and to the side, lips pressed, one brow raised (no hand)",
    "concerned": "concerned and a bit sad, brows tilted up in the middle, small frown (not angry)",
    "smirk": "confident one-sided smirk, slightly narrowed eyes",
    "wink": "playful wink with one eye closed and a smile",
    "talk_e": "talking, mouth open wide and flat on an 'E' (eee) sound",
}

POSES = {
    "presenting": "presenting: one arm extended to the side with an open palm up, as if showing something, smile",
    "point_camera": "pointing straight at the camera with his right index finger, confident smile",
    "point_side": "pointing to the viewer's right with an extended arm and index finger, looking that way, smile",
    "thumbs_up": "giving a thumbs up with his right hand at chest height, big smile",
    "arms_crossed": "arms crossed over the chest, confident smile",
    "thinking_chin": "thinking, right hand on his chin/beard, other arm across the waist, eyes looking up",
    "shrug": "shrugging, both palms up at waist height, shoulders raised, eyebrows up, small smile",
    "victory": "victory, both fists raised above his head, happy open-mouth cheer",
    "waving": "waving hello with his right hand raised beside his head, open palm, smile",
    "explain_both": "explaining with both hands in front of the chest, palms open and facing each other, mouth open talking",
    "walk_front": "walking toward the camera mid-stride, one leg forward, arms swinging naturally, smile",
    "walk_side": "walking mid-stride in exact side profile facing the viewer's right, arms swinging naturally",
}

HANDS_A = ["open_palm", "back", "point", "fist", "thumbs_up", "relaxed"]
HANDS_B = ["peace", "ok", "marker", "open_palm_side", "point_up", "grab"]
HAND_TEXT = {
    "open_palm": "open hand, palm facing the viewer, fingers up and slightly spread",
    "back": "open hand seen from the back (back of the hand to the viewer), fingers up",
    "point": "index finger pointing up, other fingers curled",
    "fist": "closed fist, knuckles to the viewer",
    "thumbs_up": "thumbs up, fingers curled",
    "relaxed": "relaxed hand, fingers gently curled, palm to the side",
    "peace": "peace / V sign with index and middle fingers, palm to the viewer",
    "ok": "OK sign, thumb and index finger forming a circle, other fingers up",
    "marker": "holding a black whiteboard marker like a pen",
    "open_palm_side": "flat open hand seen from the side (karate-chop edge to the viewer), fingers up",
    "point_up": "pointing up and slightly forward with the index finger, seen from the side",
    "grab": "hand half-open as if about to grab something, palm to the viewer",
}

ARMS = ["upper_down", "upper_out45", "upper_forward", "fore_straight", "fore_bent", "arm_full_straight"]
ARM_TEXT = {
    "upper_down": "upper arm only (shoulder to elbow) hanging straight down, seen from the front",
    "upper_out45": "upper arm only (shoulder to elbow) raised 45 degrees out to the side, seen from the front",
    "upper_forward": "upper arm only (shoulder to elbow) seen from the side, foreshortened as if reaching forward",
    "fore_straight": "forearm only (elbow to wrist cuff), straight, vertical",
    "fore_bent": "forearm only (elbow to wrist cuff) seen from the side, slightly turned",
    "arm_full_straight": "whole arm in sleeve from shoulder to wrist cuff, straight and vertical, no hand",
}


def _grid(names, texts, rows, cols):
    lines = []
    for i, n in enumerate(names):
        lines.append(f"row {i // cols + 1}, column {i % cols + 1}: {texts[n]}")
    return "; ".join(lines)


def jobs():
    out = []
    for ang, atext in ANGLES.items():
        for tag, names in (("a", EXPR_A), ("b", EXPR_B)):
            out.append({
                "id": f"heads_{ang}_{tag}", "kind": "head", "angle": ang, "rows": 2, "cols": 3,
                "cells": names, "size": "1536x1024",
                "prompt": (
                    f"An expression sheet: a grid of 2 rows x 3 columns, 6 head-and-neck busts of the same man, all "
                    f"{atext}, all the same size and the same head position in each cell, evenly spaced with clear white "
                    f"space between them, each bust cut cleanly just below the shirt collar (head, neck, collar only, no "
                    f"shoulders). Expressions: {_grid(names, EXPR_TEXT, 2, 3)}. Glasses on in every cell. {IDENTITY} {STUDIO}"
                ),
            })
    out.append({
        "id": "bodies_turn_a", "kind": "body", "rows": 1, "cols": 3, "cells": ["front", "34left", "34right"],
        "pose": "neutral", "size": "1536x1024",
        "prompt": (
            "A character turnaround sheet: 3 full-body figures of the same man side by side, head to toe with feet "
            "visible, all the same height and standing on the same baseline, evenly spaced: left figure facing the "
            "camera straight on; middle figure in three-quarter view facing the viewer's left; right figure in "
            "three-quarter view facing the viewer's right. Neutral relaxed standing pose, arms hanging naturally at "
            f"the sides, slight smile. {IDENTITY} {STUDIO}"
        ),
    })
    out.append({
        "id": "bodies_turn_b", "kind": "body", "rows": 1, "cols": 3, "cells": ["profileleft", "profileright", "back"],
        "pose": "neutral", "size": "1536x1024",
        "prompt": (
            "A character turnaround sheet: 3 full-body figures of the same man side by side, head to toe with feet "
            "visible, all the same height and standing on the same baseline, evenly spaced: left figure in exact side "
            "profile facing the viewer's left; middle figure in exact side profile facing the viewer's right; right "
            "figure seen from directly behind (back view, back of the head). Neutral relaxed standing pose, arms "
            f"hanging naturally at the sides. {IDENTITY} {STUDIO}"
        ),
    })
    for pose, ptext in POSES.items():
        out.append({
            "id": f"pose_{pose}", "kind": "body", "rows": 1, "cols": 1, "cells": [pose], "pose": pose,
            "angle": "side" if pose == "walk_side" else "front", "size": "1024x1536",
            "prompt": (
                f"One full-body image of the man, head to toe with both feet visible and some white space around him, "
                f"{ptext}. Natural, anatomically correct arms and hands with five fingers. {IDENTITY} {STUDIO}"
            ),
        })
    for tag, names in (("a", HANDS_A), ("b", HANDS_B)):
        out.append({
            "id": f"hands_{tag}", "kind": "hand", "rows": 2, "cols": 3, "cells": names, "side": "right",
            "size": "1536x1024",
            "prompt": (
                "A hand reference sheet: a grid of 2 rows x 3 columns, 6 separate RIGHT hands of the same man, each "
                "with a short piece of the black suit sleeve cuff (and black shirt cuff) at the bottom, the wrist at the "
                "bottom of each cell and the fingers toward the top, all the same size, evenly spaced with white space "
                f"between them. Hands: {_grid(names, HAND_TEXT, 2, 3)}. Skin tone and 3D style exactly as the reference "
                f"hands, five fingers on every hand, no watch. {STUDIO}"
            ),
        })
    out.append({
        "id": "arms_a", "kind": "arm", "rows": 2, "cols": 3, "cells": ARMS, "side": "right", "size": "1536x1024",
        "prompt": (
            "A rig parts sheet: a grid of 2 rows x 3 columns, 6 separate pieces of the man's RIGHT arm in the black "
            "suit jacket sleeve (matte black wool, same fabric as the references), with no hand (the sleeve ends in a "
            "clean cuff with a sliver of black shirt cuff), the shoulder or elbow end at the top of each cell, all at "
            f"the same scale, evenly spaced: {_grid(ARMS, ARM_TEXT, 2, 3)}. Cut ends are clean and rounded. {STUDIO}"
        ),
    })
    return out


if __name__ == "__main__":
    for j in jobs():
        print(j["id"], len(j["prompt"]))
