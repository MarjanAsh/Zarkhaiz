"""Lay the voiceover lines on a timeline and derive word / caption timings.

usage: python3 build_timeline.py   (reads lines.json + vo/dur.json, writes timeline.json)

Word times are estimated inside each line from word length (Gemini TTS gives no
word timestamps); captions show 1-3 words at a time with the spoken word highlighted.
"""
import json, re

LEAD, GAP, SCENE_GAP, TAIL = 0.5, 0.22, 0.45, 2.8

lines = json.load(open("lines.json"))
dur = json.load(open("vo/dur.json"))

t = LEAD
out_lines, words, chunks, scenes = [], [], [], []
prev_scene = None
for ln in lines:
    if prev_scene is not None:
        t += SCENE_GAP if ln["scene"] != prev_scene else GAP
    d = dur[ln["id"]]
    t0, t1 = round(t, 3), round(t + d, 3)
    out_lines.append({"id": ln["id"], "scene": ln["scene"], "text": ln["text"], "t0": t0, "t1": t1})
    if ln["scene"] != prev_scene:
        scenes.append({"name": ln["scene"], "t0": t0})
    # word weights: letters + a little for each word boundary; punctuation adds a pause
    toks = ln["text"].split()
    wts = []
    for w in toks:
        core = re.sub(r"[^\w-]", "", w)
        wt = max(len(core), 2) + 1.6
        if re.search(r"[,.!?;:]$", w):
            wt += 2.2
        wts.append(wt)
    span = d * 0.97
    acc, wl = 0.0, []
    tot = sum(wts)
    for w, wt in zip(toks, wts):
        a = t0 + span * acc / tot
        acc += wt
        b = t0 + span * acc / tot
        wl.append({"w": w, "t0": round(a, 3), "t1": round(b, 3), "line": ln["id"]})
    words += wl
    # caption chunks: up to 3 words / 20 chars, break after punctuation
    cur = []
    for w in wl:
        cur.append(w)
        text = " ".join(x["w"] for x in cur)
        if len(cur) == 3 or len(text) >= 17 or re.search(r"[,.!?]$", w["w"]):
            chunks.append(cur); cur = []
    if cur:
        chunks.append(cur)
    t += d
    prev_scene = ln["scene"]

total = round(t + TAIL, 3)
for i, s in enumerate(scenes):
    s["t1"] = scenes[i + 1]["t0"] if i + 1 < len(scenes) else total
cap = []
for i, c in enumerate(chunks):
    nxt = chunks[i + 1][0]["t0"] if i + 1 < len(chunks) else c[-1]["t1"] + 0.6
    end = min(nxt, c[-1]["t1"] + 0.5)
    cap.append({"t0": c[0]["t0"], "t1": round(end, 3), "words": c})

json.dump({"dur": total, "lines": out_lines, "words": words, "chunks": cap, "scenes": scenes},
          open("timeline.json", "w"), indent=1, ensure_ascii=False)
print("dur", total)
for s in scenes:
    print(f'{s["name"]:8s} {s["t0"]:6.2f} → {s["t1"]:6.2f}')
