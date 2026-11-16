"""Lip-sync: mouth shapes for Roman Urdu speech, as LivePortrait parameters over time.

Input is phonemes.json from align.py (every romanised letter of the voiceover with its real start and end time).
Letters are grouped into sounds (Roman Urdu digraphs: aa, ee, oo, ai, au, sh, ch, kh, gh, th, dh, ph, bh), each sound
maps to a viseme, and the visemes are turned into smooth parameter curves:
  - vowels carry the jaw (they are the targets the mouth travels to);
  - lip closures (m, b, p) must really close, so they pull the opening to zero for their whole length;
  - other consonants only pull the mouth part of the way (co-articulation), so the mouth does not flap per letter;
  - the opening follows the loudness of the voice a little, and the mouth rests closed in pauses.
Nothing here is random.

Visemes (name: lip opening, aaa, eee, woo) were tuned on raw/master.png, see out/visemes.jpg:
"""
import json, math, wave
from pathlib import Path

import numpy as np

# name: (lip, aaa, eee, woo)   lip = how far the lips are apart (LivePortrait lip retargeting, 0 = closed)
VIS = {
    "rest": (0.00, 0, 0, 0),
    "A":    (0.30, 10, 0, 0),     # a, aa: open jaw
    "E":    (0.17, 2, 9, 0),      # e, i, ee, ai, y: spread lips
    "O":    (0.20, 3, 0, 8),      # o, u, oo, au, w: rounded lips
    "MBP":  (0.00, 0, 0, 0),      # m, b, p: lips pressed together
    "FV":   (0.05, 0, 3, 0),      # f, v: lower lip to the teeth, almost closed
    "L":    (0.14, 3, 2, 0),      # l, t, d, n, r: tongue sounds, a little open
    "S":    (0.08, 0, 6, 0),      # s, z, sh, ch, j: teeth together, lips spread
    "K":    (0.12, 4, 0, 0),      # k, g, kh, gh, h, q: back of the mouth, a little open
}
DIGRAPHS = {"aa": "A", "ee": "E", "oo": "O", "ai": "E", "au": "O", "sh": "S", "ch": "S", "kh": "K", "gh": "K",
            "th": "L", "dh": "L", "ph": "FV", "bh": "MBP"}
SINGLE = {**{c: "A" for c in "a"}, **{c: "E" for c in "eiy"}, **{c: "O" for c in "ouw"}, **{c: "MBP" for c in "mbp"},
          **{c: "FV" for c in "fv"}, **{c: "L" for c in "ltdnr"}, **{c: "S" for c in "szjcx"}, **{c: "K" for c in "kgqh"}}
VOWELS = {"A", "E", "O"}


def sounds(words):
    """[(viseme, t0, t1)] for one line's words (letters merged into digraphs)."""
    out = []
    for w in words:
        ph = w["ph"]
        i = 0
        while i < len(ph):
            two = ph[i][0] + ph[i + 1][0] if i + 1 < len(ph) else ""
            if two in DIGRAPHS:
                out.append((DIGRAPHS[two], ph[i][1], ph[i + 1][2])); i += 2
            else:
                out.append((SINGLE.get(ph[i][0], "L"), ph[i][1], ph[i][2])); i += 1
    return out


def loudness(wav_path, t0):
    """RMS envelope of one line's audio: f(t in the reel) -> 0..1."""
    w = wave.open(str(wav_path))
    sr = w.getframerate()
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    hop = sr // 100
    rms = np.sqrt(np.array([np.mean(a[i:i + 2 * hop] ** 2) for i in range(0, len(a) - hop, hop)]) + 1e-9)
    rms = rms / (np.percentile(rms, 95) + 1e-6)
    return lambda t: float(np.clip(rms[min(len(rms) - 1, max(0, int((t - t0) * 100)))], 0, 1.2)) if 0 <= t - t0 < len(rms) / 100 else 0.0


class Mouth:
    """mouth = Mouth(reel_dir); mouth.at(t) -> {"lip":, "aaa":, "eee":, "woo":} for the reel time t."""

    def __init__(self, reel, strength=1.0):
        reel = Path(reel)
        P = json.loads((reel / "phonemes.json").read_text())["lines"]
        self.s, self.loud = [], []
        for lid, ln in P.items():
            self.s += sounds(ln["words"])
            self.loud.append(loudness(reel / "vo" / f"{lid}.wav", ln["t0"]))
        self.s.sort(key=lambda x: x[1])
        self.k = strength

    def _raw(self, t):
        """Weighted mix of the sounds near t. Each sound has a bell around its middle; closures weigh most."""
        acc = np.zeros(4); wsum = 0.0; close = 0.0
        for v, a, b in self.s:
            if b < t - .25:
                continue
            if a > t + .25:
                break
            mid, half = (a + b) / 2, max(.045, (b - a) / 2)
            sig = half * (1.25 if v in VOWELS else .8)
            w = math.exp(-((t - mid) / sig) ** 2) * (1.0 if v in VOWELS else .55)
            if v == "MBP":
                # lips shut for the whole closure, opening just before the next sound
                c = 1.0 if a - .01 <= t <= b - .015 else math.exp(-(min(abs(t - a), abs(t - b)) / .035) ** 2)
                close = max(close, c)
                w *= 2
            acc += w * np.array(VIS[v]); wsum += w
        speaking = min(1.0, wsum / .5)                 # fades to rest when no sound is near
        p = acc / wsum * speaking if wsum > 1e-6 else acc
        p[0] *= (1 - close); p[1] *= (1 - close)
        return p

    def at(t_self, t):
        self = t_self
        # a short average (3 samples, 33 ms) removes single-frame flicker without blurring the closures
        p = (self._raw(t - .017) + 2 * self._raw(t) + self._raw(t + .017)) / 4
        ld = max(f(t) for f in self.loud)
        gain = self.k * (.75 + .35 * min(1.0, ld))     # louder syllables open a little more
        return {"lip": round(float(p[0] * gain), 3), "aaa": round(float(p[1] * gain), 1),
                "eee": round(float(p[2] * self.k), 1), "woo": round(float(p[3] * self.k), 1)}
