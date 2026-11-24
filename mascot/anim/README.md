# Animated character (from reel v015; the acting system from v020)

## v021 (Nov 24, in progress): natural arms
Causes found in the v020 frames and arm clips: FILM melts the hand on the first step (hanging -> mid: the hand turns
over and comes forward at once), a cross-gesture clip (explain_mid -> waveL_q1) makes the hand vanish and reappear,
the rest pose is a stiff hang, and the director changed pose every 0.6-0.7 s.
- New keys (`gen_keys.py`, list `V021`): `relaxedL_end`, `relaxedR_end` (the idle stance) and q1 keys for presentL,
  presentR, explain, pointcamL, thumbsL, shrug, plus `countL_q1` / `countL_q3` for the counts.
- `build_anim.py` uses them when they exist: CHAIN q1 -> mid -> end, a "relaxed" state per side, and direct clips
  relaxed -> each core gesture (through the gesture's first key), so the arm never drops to the stiff hang.
- `director.py`: `calm_arms()` (MIN_HOLD 1.5 s, finger steps 0.6 s, PRIO gestures, CORE / MAP per side) rewrites only
  `arms`; its log is `arm_log` in acting.json. The face, head, gaze and blinks stay as the main pass made them.
- `main.js`: `armSpring()` timing and a short neighbour blend in `drawArm()`.

## v020 (Nov 16): the acting system
The user asked for a far more expressive presenter: more hands, arms, shoulders and face, lip-sync, and gestures
chosen from the meaning of the words. What was added (all in `tools/`, the full list of controls is `manifest.json`,
written by `tools/manifest.py`):

| Part | File | What it does |
|---|---|---|
| Real word times | `align.py` | Forced alignment (torchaudio MMS_FA, free) of each voice line to its Roman Urdu text -> `video/outputdm-reel/phonemes.json`. Before, word times were guessed from word length and were up to 0.36 s early. `build_timeline.py` now uses these times for captions and scene cues. |
| Lip-sync | `audio_motion.py`, `speech_face.py` | The mouth, jaw and cheeks are generated from the voice by JoyVASA's motion generator (LivePortrait keypoints, 25 a second) -> `out/speech/motion.npz`. Lips use the generated shape while he speaks and return to the master's mouth in pauses; generated eyelids are not used. |
| Expressions | `expressions.py` | 12 independent face controls and 30 named presets (29 usable; `angry` is never chosen), intensity 25/50/75/100 %, blending. Sheets: `out/expressions.jpg`, `out/expression_levels.jpg`, `out/face_controls.jpg`. |
| Arms and hands | `gen_keys.py`, `kie_edit.py`, `build_anim.py` | 17 new arm clips. The viewer's left arm: point_camera, point_side, count1..count5, thumbs_up, fist_pump, shrug (+ present, explain, wave). The right arm: point_side, thumbs_up, chop, ok, stop, count3, shrug (+ present, explain). Keys were made with Kie (GPT Image 2 edits of the master, 31 images, 186 credits). |
| The director | `director.py` | Script + real word times -> `video/outputdm-reel/acting.json`: expression keys, accents, head events, gaze, blinks, arm clips with start and length, body events, body turns, and a log of why each choice was made. |
| Head build | `build_face.py` | The head frames now follow `acting.json` and the speech mouth (30 frames a second while he speaks, blinks or acts; 15 otherwise). |
| Page | `video/outputdm-reel/main.js` | Reads `acting.json` for the arms. The body is drawn exactly as in v019 (see "Quality fix" below). |

The first lip-sync try (`visemes.py`: a mouth shape per letter) was rejected by the user as not good at all; it is
kept only as a record. Do not use it.

### Rebuild for a new script (same character)
```
# once per container: see "Install" below
python3 mascot/anim/tools/align.py                 # phonemes.json (edit SAY in it for numbers and abbreviations)
(cd video/outputdm-reel && python3 build_timeline.py)
python3 mascot/anim/tools/audio_motion.py          # out/speech/motion.npz (about 20 s)
python3 mascot/anim/tools/director.py              # acting.json; READ THE LOG it prints
for k in 0 1; do LP_THREADS=2 python3 mascot/anim/tools/build_face.py --part $k 2 & done; wait
python3 mascot/anim/tools/build_face.py --finish   # about 45 min on 4 CPU cores for a 39 s reel
rm -rf video/outputdm-reel/assets/anim/head; cp -r mascot/anim/out/head video/outputdm-reel/assets/anim/head
cp mascot/anim/out/face.json mascot/anim/out/anim.json video/outputdm-reel/assets/anim/
```
Cheap test first: `build_face.py --upto 8.2` (and `--finish --upto 8.2`) renders only the first seconds.
Per-line overrides in `lines.json`: `"emotion": "<preset>"`, `"energy": 0..1`, `"intent": "question" | "cta" | ...`.
Where he stands per scene (the cards are on the other side): `video/outputdm-reel/staging.json`.
New cue words or gestures: `CUES`, `GESTURES`, `CONCEPT_GESTURES` in `director.py`. A new arm clip: add its keys to
`KEYS` in `gen_keys.py` and to `GEST`, `NAME` (and `PAIRS` for a direct clip) in `build_anim.py`.

### Install (v020 additions; free, CPU)
```
pip install torchaudio --index-url https://download.pytorch.org/whl/cpu; pip install transformers einops tqdm
git clone --depth 1 https://github.com/jdh-algo/JoyVASA /home/user/JoyVASA
# into /home/user/JoyVASA/pretrained_weights/:
#   JoyVASA/motion_generator/motion_generator_hubert_chinese.pt, JoyVASA/motion_template/motion_template.pkl
#     (https://huggingface.co/jdh-algo/JoyVASA/resolve/main/...)
#   "TencentGameMate:chinese-hubert-base"/{config.json,preprocessor_config.json,pytorch_model.bin}
#     (https://huggingface.co/TencentGameMate/chinese-hubert-base/resolve/main/...)
```
`align.py` downloads the MMS_FA model (1.2 GB) on first use.
New keys with Kie: `KEYS_BACKEND=kie KEYS_PARALLEL=4 python3 tools/gen_keys.py` with `KIE_API_KEY` set by the user's
kie-ai skill (never write the key into the repo). The user allowed Kie for IMAGES only, never video (Nov 16).
After generating, check every key against the master (a shifted or zoomed figure must be regenerated).

### Quality fix after the user's review of the first v020 render (Nov 16)
The user: "shoulders and face break in many places, it is not symmetric, cuts are visible; make it smooth". Causes and fixes:
- Dotted white fringe on the outline: `build_anim.py` re-saved `key_rest` and other keys without `edges.clean()`
  (the edge log skipped them). Now `save()` cleans every image at every save. Never save a cutout without it.
- Notches at the shoulders: the page's strip-based lean / shrug / one-shoulder warps (fractional source rows) broke
  the outline. They are REMOVED from `drawHero`; the row loop is the v019 one. Do not bring them back: shoulder
  motion has to come from arm clips (image keys), not from a warp of the cutout.
- Asymmetric face and ghosting: head roll and tilt are 0, yaw and pitch are held within 3.5 degrees, the head shake is
  slow and small, one-brow accents and body turns are off (`direct(..., turns=False)`), gestures use symmetric faces.
- Still there: the hand is soft or doubled for 2-3 frames in the fastest part of an arm move (FILM in-betweens, as
  in v019). The fix would be extra middle keys for those moves (paid images).

### Limits (v020)
- Front view only; no body turns in the reel (the turn frames of v019 are still in `out/turn/`).
- Each arm stays on its own side: no crossed arms, hand on chin, hands together or hand on chest.
- Legs are planted: no steps or walking clips.
- Brow and frown changes are small (LivePortrait limits on this face): curious, worried and skeptical read as subtle.
- Head rotation is held within 3.5 degrees and never tilts (the user wants a calm, symmetric face).
- The lip-sync model was trained mostly on Chinese and English speech; on this Urdu voice the user judged the test
  "kaafi behtar" (much better). It has no guarantee for other voices.
- Only pairs listed in `PAIRS` have a direct clip; other gesture-to-gesture moves pass through the rest pose.


Why: the user said the v012-v014 character was not smooth at all (2026-11-14) and asked to fix only the character,
using ChatGPT through the bridge. Measured causes: every expression head was a separately generated image (talk heads
5 px higher than neutral, surprised/concerned/smirk 17-23 px narrower), so the whole head jumped on every word; and
pose changes were dissolves between unrelated images, so the arms never travelled.

## How it works
- **One master body**: `raw/master.png` = `mascot/library/bodies/front/neutral.png` on white, 1024x1536.
- **Keys are edits of the master** through the bridge (`tools/gen_keys.py`, `tools/bridge_edit.py`: Codex image_gen in
  edit mode with the master attached). The edit keeps head, torso, legs and position almost pixel-identical and moves
  only the arm. Each gesture has an end pose and in-between poses ("mid"; the wave has q1, mid, q3), each made with
  the later pose attached as a reference ("make the frame exactly halfway").
- **Paste-back** (`tools/build_anim.py`): a key is used only inside the blob where it differs from the master (old and
  new arm position). Everything else is the master's own pixels, so nothing but the arm can move.
- **In-betweens**: FILM frame interpolation (`tools/film.py`, CPU) between neighbouring keys, 9 frames per step, only
  inside the gesture's box. A direct rest -> end interpolation ghosts (the hand fades out and in); with GPT in-betweens
  every step is small and the arm really travels. Gesture -> gesture goes through each gesture's first key.
- **Two independent arms**: the body canvas (820x1240) is split into the viewer's left half (L) and right half (R),
  overlapping by 3 identical pixels. Each half plays its own clips, so the arms combine freely.
- **Face, v015-v016 only, replaced by Head below** (`tools/faces.py`): library heads are registered to the master head (ECC on the eye region), colour-matched
  and blended through a feathered ellipse. Talking uses mouth-only patches (talk_a / talk_o / talk_e), so the head
  outline, hair, eyes and glasses never change. Face patches (concerned, laugh, surprised) cover eyes to chin for the
  few expression changes. Nothing is warped; the mouth changes by switching patches (the user's rule).
- **Alpha**: master alpha outside the gesture box, a white key inside it, colour un-premultiplied.

- **Edges** (`tools/edges.py`, run by the build): alpha pulled in about 2 px and feathered on every frame.
- From v016 the reel uses mouth patches only; the face patches (concerned, laugh, surprised) are built but unused,
  because they are smaller than the master head and read as a face inside the face.

## Head (from reel v017): LivePortrait
The v016 mouth patches looked pasted (a laughing mouth popping on a frozen face). From v017 the whole head is a
30 fps sequence of the master's own face re-posed by LivePortrait.
- `tools/lp_face.py`: `Face(master).render(lip=, smile=, brow=, eye=, woo=, pitch=, yaw=, roll=, ...)` -> the master
  image with that expression (the model's retargeting sliders, no driving video).
- `tools/build_face.py`: the parameter track for the reel (from v018 a closed mouth: small smile and brow keys per
  line, blinks, nods, idle turn; 15 frames a second, 30 through blinks, the page blends neighbours) -> `out/head/*.webp` (RGBA patches, box in `out/face.json`), `out/head/erase.png`.
  Frames are named by a hash of their parameters, so a rerun only renders what changed.
- Expressions are edited in `track()` in `build_face.py`: `keys = [(time, smile, brow), ...]`.
- Safe ranges seen on this face: lip 0-0.4, smile -0.3..1.3, brow -25..25, eye 0 (closed)..0.3, yaw/pitch +-5,
  roll +-3, woo up to 10. `aaa` above 30 breaks the mouth; smile with eye about 0.22 reads as a wink.
- Install and run (CPU, about 5 s per frame, about 45 min for the reel with two processes; 557 frames):
```
git clone --depth 1 https://github.com/KlingAIResearch/LivePortrait /home/user/LivePortrait
pip install torch torchvision opencv-python-headless onnx onnxruntime pyyaml scikit-image imageio lmdb tyro rich pykalman scipy
# weights (629 MB) from https://huggingface.co/KlingTeam/LivePortrait/resolve/main/ into LivePortrait/pretrained_weights/:
#   liveportrait/base_models/{appearance_feature_extractor,motion_extractor,spade_generator,warping_module}.pth
#   liveportrait/retargeting_models/stitching_retargeting_module.pth, liveportrait/landmark.onnx
#   insightface/models/buffalo_l/{2d106det,det_10g}.onnx
for k in 0 1; do LP_THREADS=2 python3 mascot/anim/tools/build_face.py --part $k 2 & done; wait
python3 mascot/anim/tools/build_face.py --finish
```
  Network: needs huggingface.co and us.aws.cdn.hf.co (allowed on the `AI Video Editor` environment since Nov 15).

## Body turns (from reel v019)
`tools/build_turn.py` makes the slight front -> 3/4 turn frames (`out/turn/`, `out/turn.json`) from the library 3/4
bodies with FILM; each frame has its own head patch, erase mask, box and collar pivot. The page puts the live head on
the pivot. Copy `out/turn.json` and `out/turn/t?_*` to `video/outputdm-reel/assets/anim/` (not the `_film` cache).

## Files
- `raw/`: master and the GPT keys (originals). `out/`: built frames (`L/`, `R/`), `face/`, `anim.json`
  (`trans["L:rest>present"]` = list of frame files; `states`, `half`, `face_box`).
- Gestures: L (viewer's left arm): present, explain, wave. R: present, explain. `explain` is one edit of both arms.

## Rebuild
```
pip install torch --index-url https://download.pytorch.org/whl/cpu; pip install opencv-python-headless
mkdir -p /home/user/models && curl -L -o /home/user/models/film_net_fp32.pt \
  https://github.com/dajes/frame-interpolation-pytorch/releases/download/v1.0.2/film_net_fp32.pt
python3 mascot/anim/tools/gen_keys.py          # only missing keys; one bridge job each
python3 mascot/anim/tools/build_anim.py        # FILM segments are cached in out/; about 1 minute per new segment
cp -r mascot/anim/out video/outputdm-reel/assets/anim
```
New gesture: add its keys to `KEYS` in `gen_keys.py` (end first, then in-betweens), to `GEST`, `NAME` and `CHAIN` in
`build_anim.py`, rebuild, then use it in the storyboard at the bottom of `video/outputdm-reel/main.js`.

## Limits
- Front view only. In the fastest frames of a move the hand is soft (reads as motion blur).
- Each arm stays on its own side of the body; a gesture that crosses the centre line needs a whole-body clip.
