"""Mix voiceover + procedural music bed + sound effects into mix.wav (48 kHz stereo).

usage: python mix.py   (reads timeline.json, events.json, vo/*.wav; run with the lemo-opuscar venv)
The music is generated here (no samples): electric-piano chords, sub bass and light drums,
ducked under the voice.
"""
import json, os, sys
import numpy as np
import soundfile as sf
import soxr

sys.path.insert(0, os.environ.get("LEMO_CORE", "/home/user/lemomo-ai/lemo-opuscar/core/audio"))
import sfx
from sfx import SR, add, lp, hp, noise, env_exp, t_, thump, limit

TL = json.load(open("timeline.json"))
EV = json.load(open("events.json"))["ev"]
DUR = TL["dur"]
N = int(DUR * SR) + SR
music = np.zeros((N, 2)); voice = np.zeros((N, 2)); fx = np.zeros((N, 2))

# ---------- voice ----------
for ln in TL["lines"]:
    x, r = sf.read(f"vo/{ln['id']}.wav", dtype="float32")
    if x.ndim > 1: x = x.mean(1)
    if r != SR: x = soxr.resample(x, r, SR)
    x = hp(x, 70)
    x = x / (np.abs(x).max() + 1e-9) * .9
    add(voice, x, ln["t0"], 1.0, 0.0)

# ---------- music ----------
BPM = 96; beat = 60 / BPM; bar = 4 * beat
def midi(n): return 440 * 2 ** ((n - 69) / 12)
# D minor: Dm9 - Bbmaj7 - F/A - C(add9)
CH = [(50, [62, 65, 69, 72, 64]), (46, [62, 65, 69, 70]), (45, [60, 65, 69, 72]), (48, [60, 64, 67, 74])]

def epiano(f, d, v):
    tt = t_(d)
    x = (np.sin(2 * np.pi * f * tt) + .28 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt / .25)
         + .08 * np.sin(2 * np.pi * 3 * f * tt) * np.exp(-tt / .12)) * np.exp(-tt / 1.1)
    x *= 1 + .12 * np.sin(2 * np.pi * 4.5 * tt)
    a = int(.006 * SR); x[:a] *= np.linspace(0, 1, a)
    return x * v

def pad(fs, d, v):
    tt = t_(d); x = np.zeros_like(tt)
    for f in fs:
        for det in (-.12, .12):
            ph = (tt * f * (1 + det / 100)) % 1
            x += 2 * ph - 1
    x = lp(x, 900)
    e = np.minimum(1, tt / .6) * np.minimum(1, (d - tt) / .6)
    return x / len(fs) * e * v

def sub(f, d, v):
    tt = t_(d); return np.sin(2 * np.pi * f * tt) * np.exp(-tt / .9) * np.minimum(1, tt / .01) * v

def hat(v):
    d = .05; return hp(noise(d), 7000) * env_exp(d, .012) * v

def snap(v):
    d = .18; return (hp(noise(d), 1500) * env_exp(d, .045)) * v

end_music = TL["lines"][-1]["t1"] + 0.4     # groove stops after the last line, a final chord rings out
nbars = int(end_music / bar) + 1
for b in range(nbars):
    t0 = b * bar; root, notes = CH[b % 4]
    add(music, pad([midi(n) for n in notes[:4]], bar + .3, .10), t0, 1, 0)
    for k, n in enumerate(notes):                     # stabs on 1 and the and-of-2
        for off in (0, 1.5 * beat):
            add(music, epiano(midi(n), 1.6, .07), t0 + off + k * .012, 1, (k - 2) * .18)
    add(music, sub(midi(root - 12), bar * .5, .28), t0, 1, 0)
    add(music, sub(midi(root - 12), bar * .45, .22), t0 + 2 * beat, 1, 0)
    if t0 > .4:
        for q in range(4):
            if q in (0, 2): add(music, thump(.30, 58), t0 + q * beat, 1, 0)
            if q in (1, 3): add(music, snap(.10), t0 + q * beat, 1, .1)
        for e in range(8):
            if e % 2: add(music, hat(.05 + .02 * (e == 7)), t0 + e * beat / 2, 1, .35)
# final chord
add(music, pad([midi(n) for n in CH[0][1][:4]], 3.2, .12), end_music, 1, 0)
for k, n in enumerate(CH[0][1]):
    add(music, epiano(midi(n), 3.0, .08), end_music + k * .03, 1, (k - 2) * .2)

# fade in / out
tt = np.arange(N) / SR
music *= np.minimum(1, tt / .5)[:, None] * np.clip((DUR - tt) / 1.2, 0, 1)[:, None]

# duck the music under the voice
venv = np.abs(voice[:, 0])
k = int(.08 * SR); venv = np.convolve(venv, np.ones(k) / k, mode="same")
duck = 1 - .5 * np.clip(venv / .05, 0, 1)
k2 = int(.25 * SR); duck = np.convolve(duck, np.ones(k2) / k2, mode="same")
music *= duck[:, None]

# ---------- sound effects ----------
SFX = {
    "whoosh": lambda: sfx.whoosh(.4, .22),
    "pop": lambda: sfx.pop(.20),
    "tick": lambda: sfx.click(1.3, .16),
    "ding": lambda: sfx.ding(.16),
    "thump": lambda: sfx.thump(.45, 60),
    "click": lambda: sfx.click(1.0, .25),
}
for e in EV:
    f = SFX.get(e["type"])
    if f: add(fx, f(), e["t"], 1, 0)

mix = voice * 1.0 + music * .55 + fx * .9
mix = np.stack([limit(mix[:, c], .95) for c in range(2)], 1)
mix = mix[: int(DUR * SR)]
sf.write("mix.wav", mix.astype(np.float32), SR, subtype="PCM_24")
print("mix.wav", round(len(mix) / SR, 2), "s  peak", round(float(np.abs(mix).max()), 3))
