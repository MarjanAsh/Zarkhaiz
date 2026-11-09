"""Mouth-open and emphasis curves for the rigged mascot, from the voiceover.

usage: python build_mouth.py  (lemo-opuscar venv; reads timeline.json + vo/, writes talk/mouth.json)
v = fast mouth opening 0..1 at 60 fps, s = slow speech energy (head nods, eyebrows).
"""
import json
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt
FPS = 60
TL = json.load(open("timeline.json"))
n = int(TL["dur"] * FPS) + 2
v = np.zeros(n)
for ln in TL["lines"]:
    x, sr = sf.read(f"vo/{ln['id']}.wav", dtype="float32")
    x = sosfilt(butter(2, [180, 3200], "band", fs=sr, output="sos"), x)
    hop = sr // FPS
    rms = np.array([np.sqrt(np.mean(x[i:i + hop * 2] ** 2)) for i in range(0, len(x) - hop, hop)])
    rms = np.clip(rms / (np.percentile(rms, 92) + 1e-9), 0, 1) ** 0.7
    rms[rms < 0.12] = 0
    i0 = int(ln["t0"] * FPS)
    v[i0:i0 + len(rms)] = np.maximum(v[i0:i0 + len(rms)], rms[: n - i0])
# attack / release smoothing so the jaw moves like a jaw
out = np.zeros(n); e = 0.0
for i in range(n):
    k = 0.55 if v[i] > e else 0.28
    e += (v[i] - e) * k; out[i] = e
w = int(0.3 * FPS); slow = np.convolve(out, np.ones(w) / w, mode="same")
json.dump({"fps": FPS, "v": [round(float(a), 3) for a in out], "s": [round(float(a), 3) for a in slow]}, open("talk/mouth.json", "w"))
print("frames", n, "mean open", round(float(out.mean()), 3))
