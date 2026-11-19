# 360-degree turn + lip sync (2026-11-19)

Request (user, 2026-11-19): a character like the reference reels that can turn a full 360 and has the best possible
lip sync, made with the skills (FFmpeg, HyperFrames, motion, Remotion...), GPT through the bridge; a 5 second test.
The reference reels were only about the character, not the theme.

## What the reference reels actually are
Checked in Chrome on 2026-11-19 (captions and frames):
- kenai.film (Dfzu9N4BL7O, DfpC6MCBhdg, DfZSj78AdRp): "created using Seedance 2.5 on Dreamina".
- undergroundai_creative (DfSXcNEqmwr, Dfh0QE9KQ-L): "Made with Seedance 2.5 on ArtCraft Studios".
- growwithshanofficial (DdYuLwipxKJ): tutorial, ChatGPT writes the prompt, the video is made in the Gemini app (Veo).
- DfjRvvzunL7: age-restricted, not opened (needs an Instagram login).
None was made by Claude: the turn, voice and lip sync come from the paid video model. `video/turn360/seedance_prompt.json`
is a ready prompt (EN + ZH) for Dreamina with the library front body and turnaround sheet as image references.

## How this clip is built (no image or video generation, everything on CPU)
1. **Turnaround** `tools/build_turn.py`: the six library bodies (front 0, 34left 45, profileleft 90, back 180,
   profileright 270, 34right 315 degrees) + FILM in-between frames (7 per 45 degrees around the front, 3 elsewhere).
   FILM runs twice, on a black and on a white ground, and the alpha comes from the difference (exact for blends; a
   green-screen key left green hands). `Dense.frame_at(angle)` gives an RGBA frame for any angle.
2. **Lip sync** `tools/lipsync.py`: mouth shape per video frame from the voice itself (loudness, high band for s/z/f,
   low murmur for m/n/b, LPC formants for a / e / o), every shape held at least 3 frames, closures inside speech capped
   at 6 frames. Shapes are the mascot/anim mouth patches (talk_a, talk_o, talk_e, talk_teeth; closed = no patch).
   Word times for the captions: Whisper (base) on the same file.
3. **Character layer** `tools/compose_char.py`: wind-up, the 360 with a 180-degree-shutter motion blur (9 samples per
   frame), overshoot and settle, then the mascot/anim body (GPT-key arm clips): wave on "Assalam o Alaikum", both hands
   present on "Main Zarkhaiz, OutputDM ka founder", mouth patch every frame with a 2-frame cross-fade.
   The angle curve is duplicated in `video/turn360/compositions/turn.html` (turntable ticks + degree counter).
4. **Stage** `video/turn360/` (HyperFrames): brand stage, turntable ring, speed arcs, counter 0-360, word captions.

## Rebuild
```
pip install --break-system-packages torch --index-url https://download.pytorch.org/whl/cpu
pip install --break-system-packages opencv-python-headless soundfile scipy
mkdir -p /home/user/models && curl -L -o /home/user/models/film_net_fp32.pt \
  https://github.com/dajes/frame-interpolation-pytorch/releases/download/v1.0.2/film_net_fp32.pt
cd mascot/turn/tools
python3 build_turn.py                       # about 13 min on 2 CPUs (cached per segment)
python3 lipsync.py ../../../video/outputdm-reel/vo/l02.wav ../out/l02_mouth.json
python3 compose_char.py /tmp/char           # 318 PNG frames, 918x1388, 60 fps
ffmpeg -framerate 60 -i /tmp/char/c_%04d.png -c:v libvpx-vp9 -pix_fmt yuva420p -b:v 0 -crf 20 \
  ../../../video/turn360/assets/char.webm
cd ../../../video/turn360 && npx hyperframes render -f 60 -o out/zarkhaiz_turn360_v001.mp4
```

## Tried and not used
- `tools/turn.py`: a visual hull carved from the six silhouettes with view-dependent texturing. The hull fits the
  silhouettes (IoU about 0.9) but the six drawings do not agree inside (the 3/4 face is drawn nearly centred), so
  in-between angles showed two faces; FILM between neighbouring angles looks better.
- FILM on a green ground + chroma key: green hands and arm edges. Replaced by black/white difference matting.

## Limits (honest)
- The six library angles are separate GPT drawings, so FILM can only morph between them: the 45-degree steps near the
  front are clean, the 90-degree steps across the back are soft (ghosting), hidden by speed and motion blur. A slow,
  clean 360 needs more angles: 16 bodies at 22.5-degree steps through the ChatGPT bridge (upload mode with the four
  identity references, as for the library). The bridge answered `unauthorized` from this session's environment
  (the token is only injected in the zarkhaiz / AI Tools environments).
- A real 3D model (TRELLIS / Hunyuan3D on Hugging Face) was not tried: uploading the founder's images to a public
  Space was not allowed from this session. Needs the user's go.
- Lip sync uses the four existing mouth patches; more shapes (wide smile, f/v lip bite, closed m) would make it finer.
