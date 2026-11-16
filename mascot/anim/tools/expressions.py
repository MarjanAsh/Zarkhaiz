"""The expression system: independent face controls, named presets, intensity, blending (from reel v020).

Every expression is a set of CONTROL values, not an image. The controls are LivePortrait parameters of the one
master face (lp_face.Face.render), so they combine freely with each other and with the audio-driven mouth
(speech_face.py):

  eyes     eye   lid opening (0 closed .. EYE_OPEN open .. wider for surprise), gx / gy gaze left-right / up-down
  brows    brow (both), brow_l, brow_r (viewer's left / right alone): + raised, - lowered and drawn together
  mouth    smile (- frown .. + smile), pout, lip (emotional opening, only used while he is NOT speaking)
  head     pitch (+ down), yaw (+ viewer's right), roll (+ tilt)   small acting moves; the body turn is separate

  mix("curious", .5)                      -> control values at intensity 0.25 / 0.5 / 0.75 / 1.0
  blend(a, b, u)                          -> values between two expressions (use for transitions)
  apply(expr, speech)                     -> render parameters: the speech mouth is kept, the emotion adds the
                                             mouth corners (smile / frown) at reduced strength, never the opening

Values were tuned on raw/master.png; see out/expressions.jpg (all presets at 1.0) and out/expression_levels.jpg.
Safe ranges on this face: smile -0.6..1.3, brow -25..25, eye 0...42 (the lids are not linear: .30 is open, .27 a
squint, .24 already reads as closed, so squints stay at .26 or above), gx +-12, gy +-10, yaw/pitch +-6, roll +-4.
"""
EYE_OPEN = 0.30
CONTROLS = ("smile", "brow", "brow_l", "brow_r", "eye", "gx", "gy", "pout", "lip", "pitch", "yaw", "roll")
NEUTRAL = dict(smile=0.0, brow=0.0, brow_l=0.0, brow_r=0.0, eye=EYE_OPEN, gx=0.0, gy=0.0, pout=0.0, lip=0.0,
               pitch=0.0, yaw=0.0, roll=0.0)

# name: (controls at intensity 1.0, what it is for)
PRESETS = {
    "neutral":       ({}, "listening, between lines"),
    "slight_smile":  (dict(smile=.45), "default friendly face"),
    "happy":         (dict(smile=.9, brow=4, eye=.28), "good news, greeting"),
    "very_happy":    (dict(smile=1.3, brow=7, eye=.275, lip=.10), "payoff, big result"),
    "excited":       (dict(smile=1.0, brow=16, eye=.38, lip=.12, pitch=-2), "energy, announcement"),
    "confident":     (dict(smile=.55, brow=-3, eye=.29, pitch=-1.5), "claims, credentials"),
    "serious":       (dict(smile=-.45, brow=-16, eye=.29), "important statement"),
    "angry":         (dict(smile=-.5, brow=-22, eye=.275, pitch=2), "NOT for this character's reels (user rule); kept for completeness"),
    "frustrated":    (dict(smile=-.6, brow=-20, brow_l=-4, eye=.275, roll=2.5), "pain point"),
    "shocked":       (dict(smile=-.1, brow=24, eye=.42, lip=.22, pitch=-2.5), "big surprise"),
    "surprised":     (dict(brow=24, eye=.40, lip=.12, pitch=-1.5), "unexpected fact"),
    "confused":      (dict(smile=-.3, brow_l=24, brow_r=-16, eye=.29, roll=3.5, gx=3), "question he cannot answer"),
    "curious":       (dict(smile=.2, brow_l=24, brow_r=8, eye=.34, roll=-3, pitch=-1.5), "question, lean in"),
    "thinking":      (dict(smile=.05, brow_r=18, brow_l=-8, eye=.285, gx=9, gy=7, roll=2.5), "considering, looking up and away"),
    "worried":       (dict(smile=-.6, brow=20, brow_l=4, eye=.33, pitch=1.5), "risk, problem for the viewer"),
    "sad":           (dict(smile=-.6, brow=14, eye=.27, gy=-6, pitch=3.5), "loss"),
    "disappointed":  (dict(smile=-.55, brow=-8, eye=.27, gy=-5, pitch=2.5, roll=-2), "result that failed"),
    "skeptical":     (dict(smile=-.25, brow_l=25, brow_r=-16, eye=.275, yaw=-2.5, roll=2), "doubt about a claim"),
    "sarcastic":     (dict(smile=.5, brow_r=24, brow_l=-10, eye=.275, roll=-2.5), "ironic aside"),
    "proud":         (dict(smile=.8, brow=3, eye=.28, pitch=-3), "achievement"),
    "nervous":       (dict(smile=.3, brow=16, eye=.34, gx=-7), "awkward admission"),
    "embarrassed":   (dict(smile=.6, brow=6, eye=.27, gy=-6, pitch=3, roll=2), "self-deprecating"),
    "impressed":     (dict(smile=.4, brow=20, eye=.37, pitch=-1.5, lip=.06), "praise of something"),
    "explaining":    (dict(smile=.3, brow=6, eye=.31), "teaching, the default while speaking"),
    "questioning":   (dict(smile=.1, brow=20, eye=.34, roll=3, pitch=-1.5), "asking the viewer"),
    "disagreeing":   (dict(smile=-.5, brow=-14, eye=.285, yaw=3), "no, not this (with a head shake)"),
    "agreeing":      (dict(smile=.6, brow=5, eye=.29, pitch=2), "yes (with a nod)"),
    "celebrating":   (dict(smile=1.3, brow=14, eye=.30, lip=.16, pitch=-3), "win"),
    "suspicious":    (dict(smile=-.35, brow=-18, eye=.262, gx=-8, yaw=2.5), "something is off"),
    "reassuring":    (dict(smile=.65, brow=4, eye=.285, pitch=1, roll=-1.5), "calm promise, CTA"),
}
LEVELS = {"subtle": .25, "moderate": .5, "strong": .75, "exaggerated": 1.0}
# acting families, used by the selection engine to avoid jumping between opposite faces without passing neutral
WARM = {"slight_smile", "happy", "very_happy", "excited", "confident", "proud", "agreeing", "celebrating",
        "reassuring", "impressed", "explaining"}
COOL = {"serious", "frustrated", "worried", "sad", "disappointed", "skeptical", "disagreeing", "suspicious", "angry"}


def mix(name, k=1.0):
    """Control values of a preset at intensity k (a number or a level name)."""
    k = LEVELS.get(k, k)
    out = dict(NEUTRAL)
    for c, v in PRESETS[name][0].items():
        out[c] = NEUTRAL[c] + (v - NEUTRAL[c]) * k
    return out


def blend(a, b, u):
    """Between two control sets (u 0..1, already eased by the caller)."""
    return {c: a[c] + (b[c] - a[c]) * u for c in CONTROLS}


def add(a, **delta):
    """A control set with offsets added (blink, gaze dart, nod...)."""
    out = dict(a)
    for c, v in delta.items():
        out[c] = out[c] + v
    return out


def apply(expr, speech=None):
    """Render parameters for Face.render from a control set and (optionally) speech_face.Speech.at(t).

    While he speaks the mouth belongs to the speech: the emotion keeps only its mouth corners at 45 %, its opening
    (lip) and pout are dropped. Head rotations add up.
    """
    s = speech["speaking"] if speech else 0.0
    p = {c: expr[c] for c in ("brow", "brow_l", "brow_r", "gx", "gy")}
    p["smile"] = expr["smile"] * (1 - .55 * s)
    p["pout"] = expr["pout"] * (1 - s)
    lip = expr["lip"] * (1 - s)
    if lip > .01:
        p["lip"] = lip
    if abs(expr["eye"] - EYE_OPEN) > .012:
        p["eye"] = max(0.0, expr["eye"])
    for c in ("pitch", "yaw", "roll"):
        p[c] = expr[c] + (speech[c] if speech else 0.0)
    if speech:
        p["exp_delta"] = speech["exp_delta"]
    return p
