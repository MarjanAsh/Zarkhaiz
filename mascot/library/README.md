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
python3 mascot/library/tools/gen.py --backend bridge --par 2      # only jobs whose raw/<job>.png is missing
python3 mascot/library/tools/gen.py --only pose_shrug --redo      # regenerate one (the old raw is kept as _takeN)
python3 mascot/library/tools/post.py                              # cut, normalize, sheets, library.json
```

`raw/cutout/` is a local cache of background-removed images and is not committed.
