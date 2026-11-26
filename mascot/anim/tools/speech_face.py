"""The talking face: audio-driven mouth (audio_motion.py) turned into LivePortrait parameters for a reel time.

  sp = Speech(master_exp)          master_exp = Face.info['exp'][0] as numpy (21, 3)
  sp.at(t) -> {"exp_delta": (21, 3), "pitch":, "yaw":, "roll":}

What is taken from the generated motion (chosen on test stills, qa/v020_tests):
  - lips and jaw (keypoints 6, 12, 14, 17, 19, 20): the generated shape itself while he speaks (as JoyVASA's own
    pipeline does), faded back to the master's own mouth in pauses, so a held smile is not lost;
  - cheeks and the rest: the generated offset from rest;
  - eyes and lids (11, 13, 15, 16): NOT taken (the generated lids droop and close for long); blinks and gaze come
    from the expression system;
  - brows (1, 2): half, they give a little life on stressed syllables;
  - head rotation: about half, smoothed, added to the acting head moves.
"""
from pathlib import Path
import os
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
LIP = [6, 12, 14, 17, 19, 20]
EYE = [11, 13, 15, 16]
BROW = [1, 2]


def _smooth(x, k):
    w = np.hanning(2 * k + 3)[1:-1]; w /= w.sum()
    return np.convolve(np.pad(x, k, mode="edge"), w, mode="valid")


class Speech:
    def __init__(self, master_exp, path=None, head=.5, mouth=1.0):
        tag = os.environ.get("ANIM_TAG", "")
        d = np.load(path or ROOT / "out" / ("speech_" + tag if tag else "speech") / "motion.npz")
        self.fps = float(d["fps"])
        e, rest = d["exp"].copy(), d["rest"]
        gate = np.clip(_smooth(np.maximum.reduce([np.roll(d["speaking"], s) for s in range(-3, 4)]), 3) / .12, 0, 1)
        rel = e.copy()
        rel[:, EYE] = 0
        rel[:, BROW] *= .5
        lips = (e[:, LIP] + rest[LIP] - np.asarray(master_exp)[LIP]) * mouth      # absolute shape, as an offset from the master
        rel[:, LIP] = lips * gate[:, None, None]
        self.exp = rel.astype(np.float32)
        self.pose = {k: _smooth(d[k], 4) * head * _smooth(gate, 6) for k in ("pitch", "yaw", "roll")}
        self.gate = gate

    def at(self, t):
        x = t * self.fps
        i = int(max(0, min(len(self.exp) - 2, np.floor(x)))); f = float(min(1, max(0, x - i)))
        mix = lambda a: a[i] * (1 - f) + a[i + 1] * f
        return {"exp_delta": mix(self.exp), **{k: float(mix(v)) for k, v in self.pose.items()}, "speaking": float(mix(self.gate))}
