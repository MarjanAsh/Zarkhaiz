"""Mouth shapes from the voice itself (any language, no model): one shape per video frame.

For every frame (default 60 fps) the audio around it is measured: loudness, how much of the energy sits in the high
band (s, z, sh, f -> teeth), in the low band with little above it (m, n, b closures -> closed), and the first two
formants from LPC for vowels (aa -> talk_a, ee/e -> talk_e, oo/o -> talk_o). Short flickers are removed so every
shape is held at least MIN_HOLD frames, the way a 2D animator times mouth charts.

Shapes are the library mouth patches of mascot/anim (talk_a, talk_o, talk_e, talk_teeth) plus "closed" (no patch:
the master's own closed smile).

Usage: python3 lipsync.py voice.wav out.json [--fps 60] [--offset 0]
"""
import argparse
import json

import numpy as np
import soundfile as sf
from scipy.signal import lfilter, resample_poly

MIN_HOLD = 2          # frames at 60 fps (33 ms); 3 merged real closures away
MAX_CLOSED = 6        # frames


def lpc(x, order):
    r = np.correlate(x, x, "full")[len(x) - 1:len(x) + order]
    if r[0] <= 0:
        return None
    a = np.zeros(order + 1); a[0] = 1; e = r[0]
    for i in range(1, order + 1):
        k = -(r[i] + a[1:i] @ r[i - 1:0:-1]) / e
        a[1:i + 1] = a[1:i + 1] + k * a[i - 1::-1][:i]
        e *= 1 - k * k
        if e <= 0:
            return None
    return a


def formants(x, sr):
    x = lfilter([1, -.63], 1, x) * np.hamming(len(x))
    a = lpc(x, 2 + sr // 1000)
    if a is None:
        return []
    rts = [r for r in np.roots(a) if np.imag(r) >= 0.01]
    fr = sorted(np.angle(rts) * sr / (2 * np.pi))
    bw = [-.5 * sr / (2 * np.pi) * np.log(abs(r)) for r in rts]
    out = [f for f, b in sorted(zip(np.angle(rts) * sr / (2 * np.pi), bw)) if 200 < f < 4000 and b < 500]
    return out


def analyse(wav, fps=60):
    y, sr = sf.read(wav)
    if y.ndim > 1:
        y = y.mean(1)
    y11 = resample_poly(y, 11025, sr)              # formants at 11 kHz
    n = int(len(y) / sr * fps) + 1
    win, win11 = int(.03 * sr), int(.03 * 11025)
    feats = []
    for i in range(n):
        c = int(i / fps * sr)
        seg = y[max(0, c - win // 2): c + win // 2]
        if len(seg) < win // 2:
            feats.append(None); continue
        spec = np.abs(np.fft.rfft(seg * np.hanning(len(seg)))) ** 2
        f = np.fft.rfftfreq(len(seg), 1 / sr)
        tot = spec[(f > 80)].sum() + 1e-12
        hi = spec[f > 3500].sum() / tot
        lo = spec[(f > 80) & (f < 400)].sum() / tot
        mid = spec[(f > 400) & (f < 3000)].sum() / tot
        rms = np.sqrt(np.mean(seg ** 2)) + 1e-9
        c11 = int(i / fps * 11025)
        s11 = y11[max(0, c11 - win11 // 2): c11 + win11 // 2]
        fm = formants(s11, 11025) if len(s11) > 100 else []
        feats.append(dict(db=20 * np.log10(rms), hi=hi, lo=lo, mid=mid, f=fm[:3]))
    peak = max(ft["db"] for ft in feats if ft)
    shapes = []
    for ft in feats:
        if not ft or ft["db"] < peak - 30:
            shapes.append("closed"); continue
        rel = ft["db"] - peak
        if ft["hi"] > .35:
            shapes.append("talk_teeth"); continue
        f1 = ft["f"][0] if len(ft["f"]) > 0 else 500
        f2 = ft["f"][1] if len(ft["f"]) > 1 else 1500
        if ft["lo"] > .85 and ft["mid"] < .1 and rel < -9:   # quiet murmur with nothing above 400 Hz: m / n / b
            shapes.append("closed"); continue
        if rel < -20:
            shapes.append("talk_teeth"); continue
        if ft["lo"] > .7 and ft["mid"] < .2:             # loud and low: a nasal or rounded vowel (Urdu main, oo, o)
            shapes.append("talk_o" if f2 < 1300 else "talk_e"); continue
        if f1 > 620:
            shapes.append("talk_a")
        elif f2 > 1850:
            shapes.append("talk_e")
        elif f2 < 1150:
            shapes.append("talk_o")
        else:
            shapes.append("talk_a" if f1 > 480 else "talk_e")
    # hold every shape at least MIN_HOLD frames: merge short runs into the stronger neighbour
    runs = []
    for s in shapes:
        if runs and runs[-1][0] == s:
            runs[-1][1] += 1
        else:
            runs.append([s, 1])
    changed = True
    while changed:
        changed = False
        for i, (s, k) in enumerate(runs):
            if k < MIN_HOLD and len(runs) > 1:
                j = i - 1 if i > 0 and (i == len(runs) - 1 or runs[i - 1][1] >= runs[i + 1][1]) else i + 1
                runs[j][1] += k; del runs[i]
                # merge equal neighbours
                merged = []
                for r in runs:
                    if merged and merged[-1][0] == r[0]:
                        merged[-1][1] += r[1]
                    else:
                        merged.append(r)
                runs[:] = merged
                changed = True
                break
    # a closed mouth inside speech lasts at most MAX_CLOSED frames (long closures read as the voice running on its own)
    out = []
    for i, (s, k) in enumerate(runs):
        inner = 0 < i < len(runs) - 1
        speech_gap = inner and all(not feats[j] or feats[j]["db"] > peak - 30 for j in range(len(out), len(out) + k))
        if s == "closed" and speech_gap and k > MAX_CLOSED:
            out += ["closed"] * MAX_CLOSED + ["talk_teeth"] * (k - MAX_CLOSED)
        else:
            out += [s] * k
    return out, feats


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("wav"); ap.add_argument("out")
    ap.add_argument("--fps", type=int, default=60)
    a = ap.parse_args()
    shapes, _ = analyse(a.wav, a.fps)
    json.dump({"fps": a.fps, "shapes": shapes}, open(a.out, "w"))
    runs, t = [], 0
    for s in shapes:
        if runs and runs[-1][0] == s:
            runs[-1][2] += 1
        else:
            runs.append([s, t, 1])
        t += 1
    print(" ".join(f"{s.replace('talk_', '')}@{st / a.fps:.2f}" for s, st, k in runs))
