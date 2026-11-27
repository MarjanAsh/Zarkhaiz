"""Voiceover with Google AI Studio (Gemini TTS).

usage: python3 tts_gemini.py lines.json out_dir [--voice Charon] [--model gemini-3.8-flash-tts]

Reads the API key from the file named by $GEMINI_KEY_FILE (never from the repo).
Writes <id>.wav (24 kHz mono, silence trimmed) and dur.json for every line.
Each line is spoken from its "say" field (Urdu script, for natural pronunciation);
"text" is the Roman Urdu caption shown on screen.
"""
import argparse, base64, json, os, sys, time, urllib.request, urllib.error
import numpy as np
import soundfile as sf

STYLE = ("Speak in natural Pakistani Urdu as a confident, warm male agency founder "
         "talking to small business owners in an Instagram reel. Friendly, clear, "
         "medium-fast pace, energetic but never shouting. Say only this line:\n")


def tts(text, voice, model, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "contents": [{"parts": [{"text": STYLE + text}]}],
        "generationConfig": {
            "responseModalities": ["AUDIO"],
            "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}},
        },
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST",
                                 headers={"Content-Type": "application/json", "x-goog-api-key": key})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                d = json.load(r)
            part = d["candidates"][0]["content"]["parts"][0]["inlineData"]
            pcm = np.frombuffer(base64.b64decode(part["data"]), dtype="<i2").astype(np.float32) / 32768
            rate = 24000
            mt = part.get("mimeType", "")
            if "rate=" in mt:
                rate = int(mt.split("rate=")[1].split(";")[0])
            return pcm, rate
        except urllib.error.HTTPError as e:
            msg = e.read().decode(errors="ignore")[:300]
            if e.code in (429, 500, 502, 503) and attempt < 3:
                wait = 65 if e.code == 429 else 4 * (attempt + 1)   # free tier: per-minute quota
                print(f"  {e.code}, waiting {wait}s", flush=True)
                time.sleep(wait); continue
            sys.exit(f"TTS failed ({e.code}): {msg}")


def trim(x, rate, thr=0.01, pad=0.06):
    idx = np.where(np.abs(x) > thr)[0]
    if not len(idx):
        return x
    a = max(0, idx[0] - int(pad * rate)); b = min(len(x), idx[-1] + int(pad * rate))
    return x[a:b]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("lines"); ap.add_argument("out")
    ap.add_argument("--voice", default="Charon"); ap.add_argument("--model", default="gemini-3.8-flash-tts")
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    key = open(os.environ["GEMINI_KEY_FILE"]).read().strip()
    lines = json.load(open(a.lines)); os.makedirs(a.out, exist_ok=True)
    only = set(a.only.split(",")) if a.only else None
    durs = json.load(open(os.path.join(a.out, "dur.json"))) if os.path.exists(os.path.join(a.out, "dur.json")) else {}
    for ln in lines:
        if only and ln["id"] not in only:
            continue
        pcm, rate = tts(ln.get("say") or ln["text"], ln.get("voice", a.voice), a.model, key)
        pcm = trim(pcm, rate)
        sf.write(os.path.join(a.out, ln["id"] + ".wav"), pcm, rate)
        durs[ln["id"]] = round(len(pcm) / rate, 3)
        print(ln["id"], durs[ln["id"]], "s", flush=True)
        json.dump(durs, open(os.path.join(a.out, "dur.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
