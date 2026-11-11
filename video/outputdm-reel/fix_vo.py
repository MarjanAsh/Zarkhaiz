"""Clean the Gemini voice lines: drop the click each take ends with, and repair line 3.

usage: python fix_vo.py   (lemo-opuscar venv; reads the untouched takes in vo/raw, writes vo/*.wav and vo/dur.json)
Every take ends with a short click after a silence; this cuts it off. Line 3 was re-recorded (v009) with
Gemini TTS and trimmed to the first complete take, so it ends on a spoken "kaam kar rahe hain".
"""
import json
import numpy as np, soundfile as sf

def take(i):   # the untouched Gemini take
    return sf.read(f"vo/raw/{i}.wav", dtype="float32")

def speech_end(x, sr):
    """End of speech: the start of the last silence longer than 0.2 s, but only when what follows it is a
    short click (under 0.45 s). A take with no click (or a pause inside the sentence) is left whole."""
    h = int(sr * .01); r = np.array([np.sqrt(np.mean(x[j:j + h] ** 2)) for j in range(0, len(x) - h, h)])
    quiet = r < .04 * r.max(); end = len(r)
    run = 0
    for k in range(len(r) - 1, -1, -1):
        if quiet[k]: run += 1
        else:
            if run >= 20:
                if len(r) - (k + 1 + run) <= 45: end = k + 1
                break
            run = 0
    return end * h

def fade(x, sr, a=.008, b=.03):
    x = x.copy(); na, nb = int(a * sr), int(b * sr)
    x[:na] *= np.linspace(0, 1, na); x[-nb:] *= np.linspace(1, 0, nb); return x

durs = {}
clean = {}
for n in range(1, 10):
    i = f"l{n:02d}"; x, sr = take(i)
    e = speech_end(x, sr); clean[i] = fade(x[: e + int(.05 * sr)], sr, .002, .04)
for i, x in clean.items():
    sf.write(f"vo/{i}.wav", x, sr); durs[i] = round(len(x) / sr, 3)
json.dump(durs, open("vo/dur.json", "w"), indent=1); print(durs)
