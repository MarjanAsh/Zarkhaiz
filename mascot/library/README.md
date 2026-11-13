# Mascot asset library

A reusable set of character pieces for the video series: heads with expressions at five angles, full bodies at six
angles plus acting poses, separate arms and hands, and head-less torsos. A script picks pieces per word or per scene
and composites them, instead of rendering one fixed reel.

Status and history: see `mascot/README.md` (section "Asset library").

## Folders

| Path | What | Canvas and anchor |
|---|---|---|
| `raw/<job>.png` + `.json` | generated originals (never edited) and their prompt, backend, model, bridge job id | as generated |
| `heads/<angle>/<expression>.png` | head + neck + collar | 640x720, neck point (320, 700), head+neck height 620 px |
| `bodies/<angle>/<pose>.png` | full body | 820x1240, head top to sole 1000 px, soles at y=1215, leg centre x=410 (same as `mascot/character/CHARACTER.md`) |
| `torsos/<angle>.png` | neutral body with the head removed at the neck line | 820x1240, neck point in `library.json` |
| `hands/<side>/<shape>.png` | hand with a short sleeve cuff | 480x560, wrist (cuff end centre) at (240, 540), cuff width 130 px |
| `arms/<side>/<piece>.png` | sleeve pieces (upper arm, forearm, whole arm), no hand | trimmed; anchors `proximal` (shoulder/elbow end) and `distal`, sleeve end 130 px wide = hand cuff |
| `sheets/*.jpg` | contact sheet per folder | |
| `library.json` | every asset with kind, angle, expression/pose/shape, side, anchors, size, prompt, model | |
| `tools/` | `jobs.py` (the prompts), `gen.py` (generate), `post.py` (cut, normalize, sheets, library.json) | |

Names:
- angles: `front`, `34left`, `34right`, `profileleft`, `profileright`, `back` (bodies only). Left/right are the
  viewer's: `34left` faces the viewer's left.
- head expressions: `neutral`, `smile`, `laugh`, `talk_a`, `talk_o`, `talk_teeth`, `talk_e`, `surprised`, `thinking`,
  `concerned`, `smirk`, `wink`. No angry face, ever (user rule).
- body poses: `neutral` (every angle) and `presenting`, `point_camera`, `point_side`, `thumbs_up`, `arms_crossed`,
  `thinking_chin`, `shrug`, `victory`, `waving`, `explain_both`, `walk_front`, `walk_side`.
- hands: `open_palm`, `back`, `point`, `fist`, `thumbs_up`, `relaxed`, `peace`, `ok`, `marker`, `open_palm_side`,
  `point_up`, `grab`. `side` is the character's own hand. Left hands and left arms are mirrored right ones
  (`mirrored_from_right: true`), which is anatomically correct for a bare hand and a plain sleeve.

## How a script uses it

1. Scene angle: pick the body angle per shot (`front` for talking to camera, `34left`/`34right` when he looks at a card
   on that side, `profile*` for walking in or a side gag, `back` for an entrance). Keep one angle per shot.
2. Pose per phrase: if a full acting pose fits the meaning (`thumbs_up` on "zabardast", `point_camera` on "aap",
   `shrug` on a question, `victory` on the payoff), show `bodies/<angle>/<pose>.png` and hold it at least 0.35 s.
   Every body shares the canvas, so swapping files reads as movement; never rescale one body on its own.
3. Face per word: for close-ups and the rig, put a head on `torsos/<angle>.png`: place the head so its neck point
   (320, 700) lands on the torso's `anchors.neck`, scaled by `canvases.head.scale_on_body_canvas`. Change the head
   file per word: `talk_a` / `talk_o` / `talk_e` / `talk_teeth` on spoken syllables (vowel a/aa → `talk_a`, o/u →
   `talk_o`, i/e → `talk_e`, consonants → `talk_teeth`, pauses → `neutral` or `smile`), and an emotion head on
   emphasis words (`laugh`, `surprised`, `concerned`, `smirk`, `wink`, `thinking`). The mouth moves only by switching
   files; never warp the face (user rule).
4. Arms and hands: for rig shots, join an arm piece's `distal` anchor to a hand's `wrist` (both 130 px wide at the
   joint) and the `proximal` anchor to the torso shoulder. Swap the hand shape on the word (`point` on "yeh",
   `thumbs_up`, `ok`, `marker` while explaining on a board).
5. Query `library.json`, for example in JS:
   `lib.assets.find(a => a.kind === 'head' && a.angle === '34left' && a.expression === 'talk_o').file`.

## Rebuilding

```
pip install rembg scipy pillow            # rembg downloads birefnet-general-lite (224 MB) on first use
python3 mascot/library/tools/gen.py --par 2                       # only jobs whose raw/<job>.png is missing
python3 mascot/library/tools/gen.py --only pose_shrug --redo      # regenerate one (the old raw is kept as _takeN)
python3 mascot/library/tools/post.py                              # cut, normalize, sheets, library.json
```

`raw/cutout/` (background-removed cache) and `raw/.providers.json` (provider cool-downs) are local, not committed.

## Providers and automatic fallback (user request, 2026-11-13)

The user asked: when one provider's limit runs out, move to the next one automatically. `gen.py` does this.
Each job tries the providers in `--providers` order (default `gemini,openai,bridge`):

| Provider | What it calls | References | Marked exhausted when |
|---|---|---|---|
| `gemini` | `generateContent` on gemini-3-pro-image, then gemini-3.1-flash-image, then gemini-2.5-flash-image (each model has its own quota) | 4 refs inline | HTTP 429 (per-day or `limit: 0` = 6 h cool-down; per-minute = 2 min), 401/403/404 |
| `openai` | `/v1/images/edits` gpt-image-2, then gpt-image-1.5 | 4 refs uploaded | `insufficient_quota` / no credits (whole account), `rate_limit` (that model, 2 min) |
| `bridge` | ChatGPT bridge (Codex `image_gen`, ChatGPT plan) | only if the bridge supports image upload (below) | "usage limit" reply, or no image upload |
| `bridge-noref` | same, text prompt only | none: the face will drift; use only on request | "usage limit" |

A provider marked exhausted is skipped by later jobs until its cool-down ends (`--reset` forgets the cool-downs).
Transient errors get one retry on the same provider. Every raw `.json` records the provider and model used.

Keys: the network proxy injects them; nothing in the repo reads or stores a key. Gemini needs its key under the
header `x-goog-api-key` (fixed in the "AI Tools" environment on 2026-11-13) and billing on the Google AI Studio
project: the free tier allows 0 image requests, which is the 429 seen on 2026-11-13. The OpenAI API key has no
credits. The proxy sends one key per host, so a second OpenAI API key cannot sit next to the first one in the
environment: replace the exhausted key with the new one (Network secrets, host `api.openai.com`, header
`Authorization`, prefix `Bearer`). A second ChatGPT account (plan sign-in) belongs on the bridge (below).

### Bridge upgrade (needed for the bridge to use reference images)
The bridge today takes only `{"prompt"}` (bodies over roughly 100-500 KB get HTTP 400) and Codex cannot fetch URLs from its
sandbox, so it cannot see the character references. Change on the VPS (`~/chatgpt-bridge`):
1. Accept `"images": [{"name": "source.jpg", "data": "<base64>"}]` in `POST /jobs` (allow bodies up to ~3 MB),
   save each file into the job directory and pass each one to Codex: `codex exec -i source.jpg -i sheet1.jpg ... "<prompt>"`.
2. Return `"images": true` from `GET /health`. `gen.py` sends images to the bridge only when it sees this.
3. Optional, for a second ChatGPT account: keep one `CODEX_HOME` per account (`CODEX_HOME=~/.codex2 codex login`) and,
   when a job fails with "usage limit", rerun it with the next `CODEX_HOME`.
