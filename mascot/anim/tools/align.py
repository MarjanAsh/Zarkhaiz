"""Real word and sound timings for the voiceover: forced alignment of each line's audio to its Roman Urdu text.

Why: Gemini TTS gives no timestamps, so timeline.json estimates word times from word length. For lip-sync and for
gestures that land on a word, the times must come from the audio itself. torchaudio's MMS_FA aligner (free, CPU,
1100+ languages on romanised text) aligns every letter of the romanised line to the audio.

Usage: python3 align.py            (reads video/outputdm-reel/lines.json, vo/*.wav, timeline.json)
Output: video/outputdm-reel/phonemes.json
  {"lines": {"l01": {"t0": <line start in the reel>, "words": [{"w": "Marketing", "t0":, "t1":,
                     "ph": [[letter, t0, t1], ...]}]}}}       times are seconds in the reel
Numbers and abbreviations are spoken differently from how the caption spells them: SAY maps a caption word to the
romanised sounds that are really spoken.
"""
import json, re, sys, wave
from pathlib import Path

import numpy as np
import torch, torchaudio

REEL = Path(__file__).resolve().parents[3] / "video" / "outputdm-reel"
SAY = {"2018": "do hazar athara", "uae": "yu e i", "seo": "es i o", "outputdm": "aut put di em", "follow-up": "falo ap",
       "whatsapp": "wats ep", "ads": "eds", "website": "web sait", "businesses": "biznesiz", "business": "biznes",
       "customers": "kastamarz", "marketing": "markiting", "automation": "otomeshan", "review": "rivyu",
       "digital": "dijital", "growth": "groth", "free": "fri", "system": "sistam", "content": "kantent",
       "founder": "faundar", "alaikum": "alaikum", "assalam": "asalam", "com": "kam", "dot": "dat"}


def read_wav(p):
    w = wave.open(str(p))
    a = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768
    if w.getnchannels() > 1:
        a = a.reshape(-1, w.getnchannels()).mean(1)
    return torch.from_numpy(a)[None], w.getframerate()


def main():
    lines = json.loads((REEL / "lines.json").read_text())
    TL = {l["id"]: l for l in json.loads((REEL / "timeline.json").read_text())["lines"]}
    bundle = torchaudio.pipelines.MMS_FA
    model = bundle.get_model(with_star=False).eval()
    tok, aligner = bundle.get_tokenizer(), bundle.get_aligner()
    out = {}
    for ln in lines:
        wav, sr = read_wav(REEL / "vo" / f"{ln['id']}.wav")
        wav = torchaudio.functional.resample(wav, sr, bundle.sample_rate)
        caps = ln["text"].split()
        spoken = []          # (caption word index, romanised piece)
        for i, c in enumerate(caps):
            key = re.sub(r"[^a-z0-9-]", "", c.lower())
            for piece in SAY.get(key, re.sub(r"[^a-z]", "", key)).split():
                spoken.append((i, piece))
        with torch.inference_mode():
            em, _ = model(wav)
        spans = aligner(em[0], tok([p for _, p in spoken]))
        k = wav.size(1) / em.size(1) / bundle.sample_rate
        t0 = TL[ln["id"]]["t0"]
        words = [{"w": c, "ph": []} for c in caps]
        for (i, piece), sp in zip(spoken, spans):
            for ch, s in zip(piece, sp):
                words[i]["ph"].append([ch, round(t0 + s.start * k, 3), round(t0 + s.end * k, 3), round(float(s.score), 2)])
        for w in words:
            w["t0"], w["t1"] = w["ph"][0][1], w["ph"][-1][2]
        out[ln["id"]] = {"t0": t0, "words": words}
        print(ln["id"], " ".join(f"{w['w']}@{w['t0']:.2f}" for w in words), flush=True)
    (REEL / "phonemes.json").write_text(json.dumps({"lines": out}, ensure_ascii=False))


if __name__ == "__main__":
    main()
