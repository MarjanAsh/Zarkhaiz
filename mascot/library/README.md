# Mascot asset library

A reusable set of character pieces for the video series: heads with expressions at five angles, full bodies at six
angles plus acting poses, separate arms and hands, and head-less torsos. A script picks pieces per word or per scene
and composites them, instead of rendering one fixed reel.

Status and history: see `mascot/README.md` (section "Asset library").

## What is in it (v1, 2026-11-13)
117 assets from 27 generated sheets, all made with the ChatGPT bridge (Codex `image_gen`, ChatGPT plan) with the
four identity references uploaded (`refs/source.jpg` = `mascot/rig/source.webp`, `mascot/character/refs/sheet1-3.jpg`).
Every sheet was checked by eye: same face, glasses, beard, hair, black suit and shirt, gold pocket square, watch; no
angry face. None was rejected or regenerated.

| Kind | Count | Contents |
|---|---|---|
| heads | 60 | 5 angles x 12 expressions |
| bodies | 18 | neutral at 6 angles (front, 34left, 34right, profileleft, profileright, back) + 12 front acting poses (`walk_side` is in `profileright`) |
| torsos | 3 | front, 34left, 34right (cut from the neutral bodies) |
| hands | 24 | 12 shapes, right + mirrored left |
| arms | 12 | 6 sleeve pieces, right + mirrored left |

Contact sheets: `sheets/heads_<angle>.jpg`, `sheets/bodies.jpg`, `sheets/torsos.jpg`, `sheets/hands_<side>.jpg`,
`sheets/arms_<side>.jpg`.

Known limits:
- Acting poses exist only facing front (plus `walk_side` in profile). Other angles need new jobs in `tools/jobs.py`.
- Torsos keep a thin strip of beard and neck at the cut; a head placed on top covers it.
- `canvases.head.scale_on_body_canvas` (0.41) is an estimate from the proportions; check it on the first composite.
- Arm pieces are scaled so the sleeve end matches the hand cuff (130 px); their length relative to a body is not
  normalized yet. The puppet rig in `mascot/rig` can keep using its own arms until a composite test is done.

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
User decision (2026-11-13): fix the bridge (option 1); the user has ChatGPT on the VPS apply the change.
Hand the VPS assistant `bridge/GPT_INSTRUCTIONS.md`: it holds all the code and steps.
- Part A (required, config only): `bridge/fix_vps.sh` sets `[sandbox_workspace_write] network_access = true` in
  Codex's `config.toml`. Codex's shell failed on every job with `bwrap: loopback: Failed RTM_NEWADDR`, which comes
  from building an offline network namespace; with network access on, that step is skipped. Tested here with Codex
  0.169: workspace-write + network_access=false has no network, =true gives curl 200 and still blocks writes outside
  the workspace. The script was tested on six config.toml cases (none, plain, existing section, last section,
  indented key, broken file: left untouched).
- Part B (recommended, bridge code): `POST /jobs` accepts `"images"` (saved to `refs/`, passed as
  `codex exec -i a -i b -- "<prompt>"`; without `--` Codex swallows the prompt as an image), `/health` reports
  `"images": true`, and several ChatGPT accounts (`CODEX_HOMES`) are rotated on "usage limit".

`gen.py` picks the bridge mode by itself: `upload` when `/health` has `"images": true`; otherwise `url` (Codex
curls the four reference images from GitHub raw URLs, which works after Part A); `bridge-noref` only on request.
If Codex answers NO_REFS, the bridge is skipped for 30 minutes (`--reset` clears it).
