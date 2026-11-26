"""Clean the Gemini voice lines of ad 01 (same method as the founder reel): drop the click a take can end with.

usage: python fix_vo.py   (lemo-opuscar venv; reads the untouched takes in vo/raw, writes vo/*.wav and vo/dur.json)
Optional: SPEED=1.06 python fix_vo.py   speeds every line up a little (ffmpeg atempo, pitch kept) for ad pacing.
"""
import os, subprocess
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
speed = float(os.environ.get("SPEED", "1"))
ids = [l["id"] for l in json.load(open("lines.json"))]
for i in ids:
    x, sr = take(i)
    e = speech_end(x, sr); x = fade(x[: e + int(.05 * sr)], sr, .002, .04)
    sf.write(f"vo/{i}.wav", x, sr)
    if speed != 1:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", f"vo/{i}.wav", "-filter:a", f"atempo={speed}", "-ar", str(sr), "-ac", "1", "-c:a", "pcm_s16le", f"vo/{i}_s.wav"], check=True)
        os.replace(f"vo/{i}_s.wav", f"vo/{i}.wav")
    y, _ = sf.read(f"vo/{i}.wav"); durs[i] = round(len(y) / sr, 3)
json.dump(durs, open("vo/dur.json", "w"), indent=1); print(durs, round(sum(durs.values()), 2), "s of speech")
