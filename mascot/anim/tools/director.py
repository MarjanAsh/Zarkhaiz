"""The acting director: script + real word times -> what the face, head, arms and body do, and when (from reel v020).

It replaces the hand-written storyboard in main.js. Nothing is random: the same script and audio give the same acting.

Input (a reel folder):
  lines.json        the script (text per line; optional "emotion": preset name, "energy": 0..1 to override)
  phonemes.json     real word times from the audio (tools/align.py)
  staging.json      optional: {"scene": "left" | "right" | "centre"} = where he stands; cards are on the other side
  ../../mascot/anim/out/anim.json   which arm clips exist (the director only uses gestures that are built)
Output: acting.json
  face   [{t, expr, k}]                    expression keys (preset name, intensity 0..1); glide .45 s
  accents[{t, d, brow, smile}]             short face accents on stressed words
  head   [{t, d, kind, amp}]               nod | shake | tilt | look_up | look_down | forward
  gaze   [{t, d, gx, gy}]                  eyes off the camera for a moment (to the cards, up while thinking)
  blinks [t]
  arms   {"L": [[t, state, d]], "R": ...}  arm clip starts (state "rest" returns); d = clip length in seconds
  turns  [[t, "tl" | "tr" | "front"]]     slight body turns toward the cards, only while both arms rest
  body   [{t, d, kind, amp}]               lean_fwd | lean_back | shrug | shoulder_l | shoulder_r | sway
  log    [{line, word, t, concept, gesture, why}]    why each choice was made (read this to check the acting)

How it decides (five levels):
  1 sentence  intent of the line from its words and punctuation (greeting, question, problem, list, claim, cta...)
  2 words     cue words (Roman Urdu and English) -> concepts: number, you, negation, contrast, emphasis, positive...
  3 emotion   a base expression and energy per line from the intent; cues add accents
  4 timing    every gesture's stroke lands on its word (real time from the audio); a clip starts early enough to
              arrive; faster when the energy is high, slower when the line is serious
  5 continuity one arm does one thing at a time; gestures keep a minimum spacing; the same gesture is not repeated
              when another one with the same meaning exists; arms return to rest in pauses; stillness is allowed
Priority when cues collide: speech sync > meaning > emotion > emphasis > continuity > variety.
"""
import json, math, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ---------- level 2: cue words -> concepts ----------
NUM = {"ek": 1, "aik": 1, "one": 1, "pehla": 1, "pehli": 1, "do": 2, "two": 2, "doosra": 2, "dusra": 2, "teen": 3, "three": 3,
       "teesra": 3, "chaar": 4, "char": 4, "four": 4, "paanch": 5, "panch": 5, "five": 5}
CUES = {
    "greet":    "assalam salam alaikum hello hi khushamdeed welcome".split(),
    "you":      "aap aapke aapka aapki tum tumhara apna apne you your".split(),
    "self":     "main mein hum hamara hamari hamare i we our".split(),
    "negation": "nahi nahin na mat never kabhi bilkulnahi no not".split(),
    "contrast": "lekin magar but however halanke".split(),
    "question": "kya kyun kyon kaise kab kahan kaun kitna kitne why how what when where".split(),
    "emphasis": "sirf waqai bilkul zaroor bohat bahut sab sabse hamesha must important zaroori hi wohi".split(),
    "positive": "free behtareen zabardast kamyab kamyabi best asaan growth faida munafa".split(),
    "problem":  "kho nuqsan mushkil masla masle problem rukte ruk ghalat zaya barbad kam".split(),
    "cta":      "abhi karein kijiye kijiay whatsapp call message follow visit rabta click".split(),
    "connect":  "jodte jorte milate ikattha".split(),
}
SELF_AMBIGUOUS = {"mein"}          # "mein" is mostly "in"; only "main" counts as "I"
WORD2CONCEPT = {w: c for c, ws in CUES.items() for w in ws if w not in SELF_AMBIGUOUS}
PRIORITY = {"number": 9, "greet": 9, "cta": 8, "you": 7, "question": 7, "list": 6, "emphasis": 6, "negation": 6,
            "brand": 5, "positive": 5, "connect": 5, "problem": 4, "contrast": 4, "self": 3, "place": 3}

# ---------- the semantic gesture library ----------
# arm: candidate arm clips in order of preference. "@content" = the arm on the side of the cards, "@free" = the other
# arm, "L"/"R" fixed (L = the arm on the viewer's left = his right hand, the natural hand for counting and pointing),
# "both" = the same state on both arms. A candidate is used only if its clip exists in anim.json.
# hold: seconds the pose is held after the stroke (min, max); dur: clip length range; k: default intensity.
G = lambda **kw: kw
GESTURES = {
    "wave_hello":     G(purpose="greeting, goodbye", arm=[("L", "wave")], face=("happy", .8), head=("nod", .7), body=None, hold=(.5, .9), dur=(.7, 1.2), emotions="warm", repeat=0),
    "count":          G(purpose="a number or a list item: 1 to 5 fingers", arm=[("L", "count{n}"), ("R", "count{n}"), ("@content", "present")], face=("explaining", .6), head=("nod", .4), body=None, hold=(.7, 1.4), dur=(.45, .8), emotions="any", repeat=1),
    "point_you":      G(purpose="you, your business: the viewer", arm=[("L", "point_camera"), ("R", "point_camera"), ("both", "explain")], face=("reassuring", .6), head=("forward", .6), body=("lean_fwd", .6), hold=(.5, 1.0), dur=(.45, .8), emotions="warm", repeat=1),
    "point_content":  G(purpose="look at this: a card, a name, a place on screen", arm=[("@content", "point_side"), ("@content", "present")], face=("explaining", .5), head=None, body=None, hold=(.7, 1.6), dur=(.5, .9), emotions="any", repeat=2, gaze="content"),
    "present_item":   G(purpose="a list item or a fact appears", arm=[("@content", "present"), ("@free", "present")], face=("explaining", .5), head=("nod", .3), body=None, hold=(.6, 1.4), dur=(.5, .9), emotions="any", repeat=2, gaze="content"),
    "explain_open":   G(purpose="explaining, describing, 'we do this'", arm=[("both", "explain")], face=("explaining", .6), head=None, body=None, hold=(.8, 2.0), dur=(.6, 1.0), emotions="any", repeat=1),
    "question_shrug": G(purpose="a question, uncertainty", arm=[("both", "shrug"), ("both", "explain")], face=("questioning", .8), head=("tilt", .8), body=("shrug", .8), hold=(.6, 1.1), dur=(.5, .9), emotions="any", repeat=0),
    "emphasis_chop":  G(purpose="an important word: only, really, must", arm=[("R", "chop"), ("L", "fist_pump"), ("both", "explain")], face=("serious", .5), head=("nod", .9), body=("lean_fwd", .5), hold=(.4, .8), dur=(.4, .7), emotions="any", repeat=1),
    "stop_no":        G(purpose="no, never, stop", arm=[("R", "stop"), ("L", "count5")], face=("disagreeing", .6), head=("shake", .9), body=("lean_back", .4), hold=(.5, .9), dur=(.4, .7), emotions="cool", repeat=0),
    "head_no":        G(purpose="a soft 'not': face and head only, the arms stay", arm=[], face=("worried", .5), head=("shake", .6), body=None, hold=(0, 0), dur=(0, 0), emotions="cool", repeat=9),
    "thumbs_good":    G(purpose="good, free, the benefit", arm=[("L", "thumbs_up"), ("R", "thumbs_up"), ("@content", "present")], face=("happy", .8), head=("nod", .6), body=None, hold=(.6, 1.1), dur=(.45, .8), emotions="warm", repeat=0),
    "ok_precise":     G(purpose="exactly, precisely, just right", arm=[("R", "ok"), ("both", "explain")], face=("confident", .6), head=("nod", .4), body=None, hold=(.5, 1.0), dur=(.45, .8), emotions="any", repeat=0),
    "celebrate":      G(purpose="a win, the payoff", arm=[("L", "fist_pump"), ("L", "thumbs_up"), ("L", "wave")], face=("celebrating", .8), head=("look_up", .5), body=("lean_back", .3), hold=(.5, 1.0), dur=(.5, .9), emotions="warm", repeat=0),
    "brand_present":  G(purpose="his own name, the company", arm=[("@free", "present"), ("@content", "present")], face=("proud", .7), head=("nod", .5), body=None, hold=(.7, 1.4), dur=(.5, .9), emotions="warm", repeat=1),
    "bring_together": G(purpose="joining things into one", arm=[("both", "explain")], face=("confident", .6), head=("nod", .5), body=("lean_fwd", .4), hold=(.7, 1.4), dur=(.6, 1.0), emotions="any", repeat=1),
    "problem_face":   G(purpose="a loss or a problem: face and body only", arm=[], face=("worried", .7), head=("tilt", .5), body=("lean_back", .4), hold=(0, 0), dur=(0, 0), emotions="cool", repeat=9),
    "contrast_turn":  G(purpose="but, however: the thought turns", arm=[], face=("skeptical", .5), head=("tilt", .7), body=("shoulder_l", .6), hold=(0, 0), dur=(0, 0), emotions="any", repeat=9),
    "self_nod":       G(purpose="I, we: a small nod, the arms stay", arm=[], face=("confident", .5), head=("nod", .5), body=None, hold=(0, 0), dur=(0, 0), emotions="warm", repeat=9),
    "call_to_action": G(purpose="do it now: message, call, follow", arm=[("L", "point_camera"), ("R", "point_camera"), ("@content", "present"), ("both", "explain")], face=("excited", .6), head=("forward", .8), body=("lean_fwd", .8), hold=(.6, 1.2), dur=(.45, .8), emotions="warm", repeat=1),
    "return_neutral": G(purpose="back to the resting stance", arm=[("L", "rest"), ("R", "rest")], face=("slight_smile", .6), head=None, body=None, hold=(0, 0), dur=(.5, 1.0), emotions="any", repeat=9),
}
# concept -> gestures with that meaning, strongest first (variety picks among them)
CONCEPT_GESTURES = {
    "greet": ["wave_hello"], "number": ["count"], "you": ["point_you"], "question": ["question_shrug"],
    "list": ["count", "present_item", "point_content"], "emphasis": ["emphasis_chop", "ok_precise"],
    "negation": ["head_no", "stop_no"], "positive": ["thumbs_good", "present_item"], "problem": ["problem_face"],
    "contrast": ["contrast_turn"], "cta": ["call_to_action", "point_you"], "brand": ["brand_present"],
    "connect": ["bring_together", "explain_open"], "self": ["self_nod"], "place": ["present_item", "point_content"],
}
# level 1/3: intent of a line -> base expression, intensity, energy (0 calm .. 1 high)
INTENT = {"greeting": ("happy", .75, .7), "question": ("questioning", .6, .55), "problem": ("worried", .55, .45),
          "list": ("explaining", .6, .6), "claim": ("confident", .65, .55), "cta": ("excited", .55, .8),
          "explain": ("explaining", .55, .5), "brand": ("proud", .6, .6)}


def norm(w):
    return re.sub(r"[^a-z0-9-]", "", w.lower())


def line_intent(text, concepts):
    c = set(concepts)
    if "greet" in c:
        return "greeting"
    if text.rstrip().endswith("?"):
        return "question"
    if "cta" in c:
        return "cta"
    if text.count(",") >= 2:
        return "list"
    if "problem" in c or ("negation" in c and "positive" not in c):
        return "problem"
    if "brand" in c and len(text.split()) <= 4:
        return "brand"
    if "self" in c or "connect" in c:
        return "claim"
    return "explain"


def direct(reel, anim_json=None, brands=("outputdm", "zarkhaiz"), places=("lahore", "pakistan", "uae", "2018")):
    reel = Path(reel)
    lines = json.loads((reel / "lines.json").read_text())
    PH = json.loads((reel / "phonemes.json").read_text())["lines"]
    stage = json.loads((reel / "staging.json").read_text()) if (reel / "staging.json").exists() else {}
    anim = json.loads(Path(anim_json or ROOT / "out" / "anim.json").read_text())
    have = {s: set(anim["states"][s]) for s in ("L", "R")}
    nfr = lambda s, a, b: len(anim["trans"].get(f"{s}:{a}>{b}", [])) or 20
    clip = lambda s, a, b: .45 + .016 * nfr(s, a, b)                 # natural length of an arm clip

    out = {"face": [{"t": -9, "expr": "slight_smile", "k": .6}], "accents": [], "head": [], "gaze": [], "blinks": [],
           "arms": {"L": [], "R": []}, "body": [], "turns": [], "log": []}
    state = {"L": "rest", "R": "rest"}
    free = {"L": -9.0, "R": -9.0}          # when each arm has finished its current move
    pending = {"L": None, "R": None}       # a planned return to rest (cancelled if a new gesture comes first)
    last_stroke = -9.0
    history = []                           # gesture ids in order of use
    strokes = []                           # times that must stay free of blinks
    last = {"head": -9.0, "body": -9.0}

    def arm_move(side, to, t_start, d):
        out["arms"][side].append([round(t_start, 3), to, round(d, 3)])
        state[side] = to; free[side] = t_start + d

    def flush(side, before=1e9):
        """Carry out a planned return to rest if it starts before `before`."""
        if pending[side] is not None and pending[side] < before and state[side] != "rest":
            arm_move(side, "rest", max(pending[side], free[side] + .1), min(1.1, clip(side, state[side], "rest")))
        if pending[side] is not None and pending[side] < before:
            pending[side] = None

    for li, ln in enumerate(lines):
        words = PH[ln["id"]]["words"]
        toks = [norm(w["w"]) for w in words]
        side_of = stage.get(ln["scene"], "right")
        content = {"right": "L", "left": "R"}.get(side_of)          # the arm toward the cards
        # ---- level 2: cues ----
        cues = []
        commas = [i for i, w in enumerate(words) if w["w"].rstrip().endswith(",")]
        is_list = ln["text"].count(",") >= 2
        for i, (tok, w) in enumerate(zip(toks, words)):
            c = None; n = None
            nx = toks[i + 1] if i + 1 < len(toks) else ""
            if tok in NUM and tok not in ("ek", "do"):
                c, n = "number", NUM[tok]
            elif tok == "ek" and nx in ("system", "hi", "jagah", "cheez", "baat"):
                c, n = "number", 1
            elif tok == "do" and nx in ("jagah", "cheezein", "baatein", "tareeqe"):
                c, n = "number", 2
            elif tok in brands:
                c = "brand"
            elif tok in places:
                c = "place"
            elif tok in WORD2CONCEPT:
                c = WORD2CONCEPT[tok]
            if c:
                cues.append({"i": i, "w": w["w"], "t": w["t0"], "t1": w["t1"], "c": c, "n": n})
        if is_list:            # each item of a comma list: the word before each comma, and the item after the last one
            j = commas[-1] + 1
            while j < len(words) - 1 and toks[j] in ("aur", "ya", "and", "or"):
                j += 1
            items = commas + [min(len(words) - 1, j)]
            for k_, i in enumerate(items):
                cues = [q for q in cues if q["i"] != i or PRIORITY[q["c"]] > PRIORITY["list"]]
                if not any(q["i"] == i for q in cues):
                    cues.append({"i": i, "w": words[i]["w"], "t": words[i]["t0"], "t1": words[i]["t1"], "c": "list",
                                 "n": k_ + 1 if len(items) <= 5 else None})
        intent = ln.get("intent") or line_intent(ln["text"], [q["c"] for q in cues])
        expr, k, energy = INTENT[intent]
        expr, energy = ln.get("emotion", expr), ln.get("energy", energy)
        t0, t1 = words[0]["t0"], words[-1]["t1"]
        out["face"].append({"t": round(t0 - .3, 3), "expr": expr, "k": k})
        if intent == "question":       # the question lands at the end of the line: a tilt and a shrug on the last words
            j = max(0, len(words) - 2)
            cues.append({"i": j, "w": words[j]["w"], "t": words[j]["t0"], "t1": t1, "c": "question", "n": None})
        cues.sort(key=lambda q: q["t"])
        for q in cues:
            q["rank"] = PRIORITY[q["c"]]
            q["armed"] = bool(GESTURES[CONCEPT_GESTURES[q["c"]][0]]["arm"])
        # ---- levels 4-5: schedule ----
        speed = 1.15 - .35 * energy                                  # clip length factor: high energy = faster
        min_gap = 1.25 - .45 * energy                                # seconds between two arm strokes
        for q in cues:
            cands = CONCEPT_GESTURES[q["c"]]
            # variety: do not repeat the previous gesture if this meaning has another one
            gid = next((g for g in cands if not history or history[-1] != g or GESTURES[g]["repeat"] >= 2), cands[0])
            g = GESTURES[gid]
            why = []
            stroke = q["t"] + min(.12, (q["t1"] - q["t"]) * .35)     # the stressed part of the word
            arm_used = None
            if g["arm"]:
                # a stronger cue close by wins the arms; this one keeps face and head only
                rival = next((r for r in cues if r is not q and abs(r["t"] - q["t"]) < min_gap and r["armed"]
                              and (r["rank"] > q["rank"] or (r["rank"] == q["rank"] and r["t"] < q["t"] and q["c"] not in ("list", "number")))), None)
                if rival and not (q["c"] in ("list", "number") and rival["c"] in ("list", "number")):
                    why.append(f"arms left to '{rival['w']}' ({rival['c']})")
                elif stroke - last_stroke < (.45 if q["c"] in ("list", "number") else .6 if q["rank"] >= 8 else min_gap):
                    why.append("too soon after the last stroke: face and head only")
                else:
                    for side, st in g["arm"]:
                        if "{n}" in st:
                            if q["n"] is None:
                                continue
                            st = st.format(n=q["n"])
                        sides = {"@content": [content or "L"], "@free": ["R" if (content or "L") == "L" else "L"], "both": ["L", "R"]}.get(side, [side])
                        if not all(st in have[s] for s in sides):
                            continue
                        plan, late = [], 0.0
                        for s in sides:
                            # go home first only if there is time to rest in between; otherwise move pose to pose
                            if pending[s] is not None and state[s] != "rest":
                                d_home = min(1.1, clip(s, state[s], "rest")); d_out = clip(s, "rest", st) * speed
                                if max(pending[s], free[s] + .1) + d_home + .35 <= stroke - d_out * .9:
                                    flush(s)
                                else:
                                    pending[s] = None
                            if state[s] == st:
                                plan.append((s, None, 0)); continue
                            d = max(g["dur"][0], min(g["dur"][1], clip(s, state[s], st) * speed))
                            ts = max(stroke - d * .9, free[s] + .1)
                            if ts + d - stroke > .3:                 # late: shorten the move as far as it stays natural
                                d = max(g["dur"][0], d - (ts + d - stroke - .3))
                            late = max(late, ts + d - stroke)
                            plan.append((s, ts, d))
                        if late > .32:
                            why.append(f"{st} would arrive {late:.2f} s late"); continue
                        for s, ts, d in plan:
                            if ts is not None:
                                arm_move(s, st, ts, d)
                            pending[s] = max(free[s], stroke) + g["hold"][1] * (1.25 - .5 * energy)
                        for s in ("L", "R"):                       # the other arm goes home unless it shares the pose
                            if s not in sides and state[s] != "rest" and pending[s] is None:
                                pending[s] = free[s] + .1
                        for s in ("L", "R"):
                            if s not in sides:
                                flush(s, stroke)
                        arm_used = f"{'+'.join(sides)}:{st}"
                        last_stroke = stroke; strokes.append(stroke)
                        if st != g["arm"][0][1].replace("{n}", str(q["n"])):
                            why.append("first choice not built, used the next one")
                        break
                    else:
                        why.append("no arm clip for this gesture is built")
            # face, head, body and gaze go with the word even when the arms stay; they are spaced out too
            strong = arm_used is not None or q["rank"] >= 6
            if g["face"] and strong:
                fx, fk = g["face"]
                out["accents"].append({"t": round(stroke - .18, 3), "d": round(.6 + .5 * (1 - energy), 2), "expr": fx, "k": round(fk * (.7 + .5 * energy), 2)})
            if g["head"] and stroke - last["head"] > (1.0 if strong else 1.8):
                kind = g["head"][0]
                out["head"].append({"t": round(stroke - .12, 3), "d": {"shake": .8, "nod": .5, "tilt": .9, "forward": .7, "look_up": .8}.get(kind, .6), "kind": kind, "amp": round(g["head"][1] * (.7 + .5 * energy), 2)})
                last["head"] = stroke
            if g["body"] and stroke - last["body"] > 1.6:
                out["body"].append({"t": round(stroke - .2, 3), "d": 1.0 if g["body"][0] != "shrug" else .9, "kind": g["body"][0], "amp": round(g["body"][1] * (.7 + .5 * energy), 2)})
                last["body"] = stroke
            if g.get("gaze") == "content" and content and arm_used:
                out["gaze"].append({"t": round(stroke - .25, 3), "d": .7, "gx": -9 if content == "L" else 9, "gy": -1})
            if q["c"] == "question":
                out["gaze"].append({"t": round(stroke - .3, 3), "d": .6, "gx": 5, "gy": 5})
            history.append(gid)
            out["log"].append({"line": ln["id"], "word": q["w"], "t": round(stroke, 2), "concept": q["c"], "gesture": gid,
                               "arms": arm_used or "-", "why": "; ".join(why)})
            for s in ("L", "R"):
                flush(s, stroke)
        # ---- after the line: the arms go home in the pause (a planned return is kept, at the latest shortly after) ----
        for s in ("L", "R"):
            if state[s] != "rest":
                pending[s] = min(pending[s] if pending[s] is not None else 1e9, max(free[s] + .5, t1 + .2))
        out["face"].append({"t": round(t1 + .25, 3), "expr": "slight_smile", "k": .6})
    for s in ("L", "R"):
        flush(s)
        out["arms"][s].sort(key=lambda x: x[0])

    dur = max(w["t1"] for l in PH.values() for w in l["words"]) + 2.8
    # ---- body turns: he turns slightly toward the cards only while both arms rest for long enough ----
    TD = .8
    busy = sorted((a[0] - .15, a[0] + a[2] + .1, a[1]) for s in ("L", "R") for a in out["arms"][s])
    rest_from, st2 = {"L": -1.0, "R": -1.0}, {"L": "rest", "R": "rest"}
    ev = sorted((a[0], s, a[1], a[2]) for s in ("L", "R") for a in out["arms"][s])
    gaps, tcur, at_rest = [], 0.0, True
    for t, s, to, d in ev:
        both_rest = st2["L"] == "rest" and st2["R"] == "rest"
        if both_rest and to != "rest":
            gaps.append((max(rest_from["L"], rest_from["R"]), t))
        st2[s] = to
        if to == "rest":
            rest_from[s] = t + d
    if st2["L"] == "rest" and st2["R"] == "rest":
        gaps.append((max(rest_from["L"], rest_from["R"]), dur))
    scene_of = lambda t: next((l["scene"] for l in reversed(lines) if PH[l["id"]]["words"][0]["t0"] - .6 <= t), lines[0]["scene"])
    for a, b in gaps:
        a, b = max(a, 0.1) + .2, b - .2
        side = stage.get(scene_of(a + .5), "right")
        if b - a >= 2 * TD + .5 and side in ("left", "right"):
            hold = min(b - a - 2 * TD, 2.2)
            out["turns"] += [[round(a, 2), "tl" if side == "right" else "tr"], [round(a + TD + hold, 2), "front"]]

    # ---- blinks: every 2.6 to 4.8 s, moved off the strokes, preferring pauses between lines ----
    pauses = []
    ids = [l["id"] for l in lines]
    for a, b in zip(ids, ids[1:]):
        pauses.append((PH[a]["words"][-1]["t1"] + PH[b]["words"][0]["t0"]) / 2)
    t = 1.4
    while t < dur:
        near = min(pauses, key=lambda p: abs(p - t)) if pauses else t
        bt = near if abs(near - t) < .7 else t
        while any(abs(bt - s) < .3 for s in strokes):
            bt += .17
        if not out["blinks"] or bt - out["blinks"][-1] > 1.6:
            out["blinks"].append(round(bt, 3))
        t = bt + 2.6 + 2.2 * ((math.sin(bt * 12.9898) * 43758.5453) % 1)
    out["face"].sort(key=lambda x: x["t"])
    return out


def stats(a):
    used = sorted({x[1] for s in ("L", "R") for x in a["arms"][s] if x[1] != "rest"})
    return {"arm moves": sum(len(a["arms"][s]) for s in ("L", "R")), "arm gestures used": used,
            "gesture ids used": sorted({l["gesture"] for l in a["log"]}),
            "expressions used": sorted({f["expr"] for f in a["face"]} | {x["expr"] for x in a["accents"]}),
            "head events": len(a["head"]), "body events": len(a["body"]), "gaze events": len(a["gaze"]), "blinks": len(a["blinks"])}


if __name__ == "__main__":
    reel = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT.parents[1] / "video" / "outputdm-reel"
    a = direct(reel)
    (reel / "acting.json").write_text(json.dumps(a, indent=1, ensure_ascii=False))
    for l in a["log"]:
        print(f"{l['line']} {l['t']:6.2f} {l['word']:<12} {l['concept']:<9} {l['gesture']:<15} {l['arms']:<18} {l['why']}")
    print(json.dumps(stats(a), indent=1))
