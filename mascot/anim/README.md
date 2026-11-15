# Animated character (from reel v015)

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
- `tools/build_face.py`: the parameter track for the reel (mouth from the voiceover loudness, expression keys per
  line, blinks, nods, idle turn) -> `out/head/*.webp` (RGBA patches, box in `out/face.json`), `out/head/erase.png`.
  Frames are named by a hash of their parameters, so a rerun only renders what changed.
- Expressions are edited in `track()` in `build_face.py`: `keys = [(time, smile, brow), ...]`.
- Safe ranges seen on this face: lip 0-0.4, smile -0.3..1.3, brow -25..25, eye 0 (closed)..0.3, yaw/pitch +-5,
  roll +-3, woo up to 10. `aaa` above 30 breaks the mouth; smile with eye about 0.22 reads as a wink.
- Install and run (CPU, about 5 s per frame, about 85 min for the reel with two processes; 1065 frames, 9.3 MB):
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
