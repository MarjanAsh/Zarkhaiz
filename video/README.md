# OutputDM founder reel

A 38-second vertical reel (1080x1920, 30 fps) that introduces Zarkhaiz as the founder of
OutputDM (Output Digital Marketing Pvt Ltd), using five full-body office mascot cutouts, the OutputDM logo
and a Google AI Studio (Gemini TTS) voiceover in Urdu.

360 + lip-sync test clip (2026-11-19): `turn360/out/zarkhaiz_turn360_v002.mp4`, see `turn360/README.md`.

Final files: `outputdm-reel/out/outputdm_founder_reel_v020.mp4` (1080x1920, 60 fps, 48 kHz: the acting system from `mascot/anim`: lip-sync generated from the voice, 29 expressions, 17 new arm gestures, head and body acting, all chosen by `mascot/anim/tools/director.py` from the script and the real word times; QA: `outputdm-reel/qa/v020/qa.md`). v019 to v012 kept.

## Script (Roman Urdu captions; spoken from Urdu script for natural pronunciation)

| # | Scene | Line |
|---|---|---|
| 1 | Problem | Marketing pe paisa lag raha hai, lekin customers nahi aa rahe? |
| 2 | Founder | Assalam o Alaikum! Main Zarkhaiz, OutputDM ka founder. |
| 3 | Since 2018 | 2018 se, Lahore se, Pakistan aur UAE ke businesses ke saath kaam kar rahe hain. |
| 4 | Growth leaks | Zyada tar businesses teen jagah customers kho dete hain. |
| 5 | Growth leaks | Log aap ko dhoond nahi paate, aa kar rukte nahi, ya follow-up hi nahi hota. |
| 6 | One system | Hum content, ads, website, SEO aur automation ko ek system mein jodte hain. |
| 7 | Only what you need | Aur sirf wohi karte hain jo aap ke business ko waqai chahiye. |
| 8 | CTA | Free Digital Growth Review ke liye abhi WhatsApp karein. |
| 9 | CTA | OutputDM dot com. |

All claims come from outputdm.com: Lahore, since 2018, Pakistan and UAE, the three growth leaks
(visibility, conversion, follow-up), the services, the complimentary Digital Growth Review,
WhatsApp +92 344 4441724, @outputdm. Client names in the "brands" strip are the ones listed on the site.

## What the reference reels do (and what this reel copies)

Four of the five reference reels were downloaded and studied (the fifth kept redirecting to
Instagram login). All are from @sadiigraphics, made as code-animated explainers:

- Light, single-colour background with soft blurred colour blobs; one brand colour for accents.
- A 3D mascot cut out from its background, standing beside the content, never covering text.
- Big serif headline (Playfair Display style) + italic accent line; sans-serif body (Jost).
- Content arrives as cards: checklists that tick, numbered cards, badges, chips.
- A progress row of steps at the top, small section labels, thin rules.
- Captions under the visuals, 1-3 words at a time, the spoken word highlighted in a colour chip.
- Ends on a contact card (WhatsApp number) and a follow prompt.

This reel keeps that grammar but uses OutputDM's own look: dark warm background matching the
office mascot photos, gold/orange/red from the logo.

## Rebuild

Needs the lemo-opuscar toolkit (https://github.com/lemomo-ai/lemo-opuscar) cloned to
`/home/user/lemomo-ai/lemo-opuscar` with `npm install` and a `.venv` from its `requirements.txt`.

```sh
cd video/outputdm-reel
LIB=/home/user/lemomo-ai/lemo-opuscar
# 1. voiceover (Google AI Studio key in a file OUTSIDE the repo), kept untouched in vo/raw
GEMINI_KEY_FILE=/path/to/key python3 tts_gemini.py lines.json vo/raw --voice Charon
# 2. clean the takes (end click, the cut-off "hain" in line 3) -> vo/*.wav, vo/dur.json
$LIB/.venv/bin/python fix_vo.py
# 3. timeline (line, word and caption timings)
python3 build_timeline.py
# 4. sound cues, audio mix, frames, final mux
node $LIB/core/render/events.mjs . --size 1080x1920
$LIB/.venv/bin/python mix.py
node $LIB/core/render/video.mjs . --fps 30 --workers 3 --size 1080x1920 --out out/video.mp4
ffmpeg -i out/video.mp4 -i mix.wav -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 256k -shortest out/outputdm_founder_reel_v010.mp4
```

4K: the page layout stays 1080x1920 and is drawn at 2x. `page.mjs` in lemo-opuscar fixes `deviceScaleFactor: 1`;
change it to `+process.env.LEMO_DSF || 1`, then run the same `video.mjs` command with `LEMO_DSF=2` and
`--out out/video4k.mp4`. (Scaling the stage with a CSS transform instead left cut-off chips and seams.)

Review stills: `node $LIB/core/render/still.mjs . 3.2 7.6 12.5 --size 1080x1920 --out stills`

## Files

- `index.html`, `main.js`: the reel; `render(t)` draws any frame (lemo-opuscar page contract).
- `lines.json`: the script; `tts_gemini.py`: Gemini TTS; `vo/raw/`: the untouched takes; `fix_vo.py` -> `vo/`: the cleaned lines.
- `build_timeline.py` -> `timeline.json`; `events.json`: sound cues exported from the page.
- `mix.py`: voice + generated music bed (no samples) + sound effects, music ducked under the voice.
- `assets/`: the five mascot cutouts (`h_*.png`, from `mascot/office-v2`, background removed with rembg
  `birefnet-general-lite`, all cropped to the same 670x1510 frame) and the OutputDM logo.
- `fonts/`: Playfair Display and Jost (SIL Open Font License, see the licence files).

Note: `mux.sh` refuses `mix.wav` in this container (its decode check reads loudnorm's progress, which lags
~3 s at the end), so the final file is muxed directly with ffmpeg `loudnorm` to -14 LUFS, AAC 256k, video copied.

## Review

Gemini (gemini-3.5-flash) watched v001: 8.5/10, captions in sync within 0.1-0.2 s, no glitches.
v002 fixes what it flagged: the hook's accent line now matches the voice, the brand strip and
the "Aap ka plan" list are bigger and brighter, and only one caption word is highlighted at a time.

## v006: full-body cutouts that act with the words

Feedback on v005: drop the angry pose, the face animation looked fake, line 3 stopped at "kar rahe"
instead of "kar rahe hain", use only the five new office images as full cutouts that move with the words,
and make the motion graphics bigger.

- Character: only the five images in `mascot/office-v2` (side, back, smile, explaining, surprised). The angry
  and seated poses, the WebGL face rig and the LeapTalk talking-head panels are gone. Nothing inside the image
  is warped any more.
- `hero()` in `main.js`: all poses share one frame, so swapping the image reads as a pose change. Each scene has
  a track of `[time, pose, x]` keys tied to spoken words: he turns round to greet, looks across at the places,
  reacts with the surprised pose on each growth leak, steps toward the card he is presenting. Every word start
  gives a hop and a nod, each pose change lands with a squash, and moves lean with two footfalls.
- Bigger graphics: heavier cards and type, a giant outlined word behind each scene, a spend-vs-customers bar,
  a huge "3", leak bars that drain, a line that wires the five services together, three rows of brand chips.
- Voice: every Gemini take ended with a click after a silence, and in line 3 that click replaced the last word.
  `fix_vo.py` removes the clicks and splices "hain" in from the end of line 6 ("jodte hain"). It is a splice,
  not a new recording: with a Google AI Studio key, re-record line 3 with `tts_gemini.py --only l03`.
- Captions: the end of a sentence is no longer split from its verb ("kar rahe hain." is one caption).
- Limits: word times inside a line are estimated from word length (Gemini TTS gives no timestamps), and the
  character has five poses, so arms and legs change by pose swap, not by continuous movement.

## v007: line 3 voice fix, 4K

- The first splice for line 3 took 0.19 s from the end of line 6, which included the "t" of "jodte", so the
  line read "kaam kar rakte hain". `fix_vo.py` now takes only the last 0.125 s (the "hain" after the "t").
- Added the 4K render (see Rebuild). The mascot images are 1024x1536, so in 4K the character is slightly
  upscaled; text and graphics are drawn at full 4K.

## v008: no more blinking

- Each new caption faded in from zero, so the caption line blinked at every change (36 times). A new caption now
  replaces the old one at full opacity and only fades out in a pause.
- Every scene faded out completely before the next one came in, leaving a near-empty frame. Items now outlive
  their scene by 0.26 s (`LINGER`), so one scene dissolves into the next.
- Check used: mean brightness of every frame; no single-frame dips remain.

## v009: 17-pose character, rig-style motion, real line 3

Feedback: the character needed many more actions, smooth "Blender-like" movement that follows the words,
and the voice must say "kaam kar rahe hain".

- Character: 17 poses cut from the client's three pose sheets (`mascot/character`, see `CHARACTER.md`), all on
  one shared canvas with the feet in the same place (`cut_sheets.py`). The angry pose is left out. The office-v2
  set is retired.
- Motion (`hero()` / `drawHero()` in `main.js`): each scene has a track of `[time, pose, centre-x, flip]` keys
  tied to words (50 pose changes in the reel). Each change has an anticipation dip, a 0.16 s dissolve with a
  short blur and a spring settle (damping 0.55); steps lean and blur with their speed; the body breathes,
  shifts its weight and turns slightly in 3D; every word start gives a nod and a small lift.
- Stage: a gold perspective floor grid that slowly dollies, a horizon glow and a floor reflection.
- Voice: line 3 re-recorded with Gemini TTS (voice Charon) and trimmed to its first complete take; it ends on a
  spoken "hain" (checked by transcription: cutting the last 0.3 s removes the word). The v007 splice is gone.
- Limits: arms and legs move by switching between drawn poses, not by bending joints; the mouth moves only
  through poses with an open mouth.

## v010: puppet rig, body parts move instead of image swaps

The user asked (chat, Nov 13) for a character whose arms and head move smoothly, "like Blender", instead of
switching between pose images. He chose option 1, a 2D puppet rig, and sent one A-pose image with 4 gesture
hands. Rig details: `mascot/rig/RIG.md`.

- The character is now one rig: body, head, and per arm an upper arm, a forearm and hands, each turning
  on its joint. All 17 pose names in the scene tracks map onto 15 rig gestures (wave, point, present,
  explain, think, hand on chest, thumbs up, fist, victory, surprised, shrug...).
- Blender-style animation: eased keys, overlapping action (the shoulder leads and the elbow follows),
  a spring settle, breathing, idle sway, a head nod and a forearm beat on every spoken word.
- The face is never warped and the mouth does not move (the standing rule).
- Open: 2D only (no back view, no walking legs), and only a 1080p render so far; 4K uses the same
  command as before. Blender (`bpy`) can be installed here, but a true 3D animation needs a 3D model of the character first.

## v011: complete mascot library showcase (ChatGPT generated angles & poses)

Demonstrates the newly generated reusable mascot asset library (`mascot/library/`) in a full 38.7s vertical reel (1080x1920, 30 fps), using Python Pillow + FFmpeg rawvideo pipeline.

- Output file: `video/outputdm-reel/out/outputdm_mascot_library_showcase_v011.mp4`
- Stills: `video/outputdm-reel/stills/v011/` (`scene1_hook.jpg`, `scene2_walking.jpg`, `scene3_laptop.jpg`, `scene6_system.jpg`, `scene8_desk.jpg`)
- Renderer: `video/outputdm-reel/render_v011_showcase.py` (renders at ~35-40 fps directly without web browser overhead).
- Integrated Mascot Assets:
  - Scene 1 (Hook): `standing_explain` (3/4 angle) + Audit card.
  - Scene 2 (Founder Greeting): `walking_front` centered entrance + Founder Leadership badge.
  - Scene 3 (Since 2018): `standing_laptop` holding open laptop + Proven Track Record card.
  - Scene 4-5 (Growth Leaks): `three_quarter_left` looking across at the 3 leaks diagnostic cards.
  - Scene 6 (One System): `excited` celebration pose with 5 connected service pipeline nodes.
  - Scene 7 (Only What You Need): `seated_desk` consultation pose.
  - Scene 8-9 (CTA): `seated_desk` at office desk with prominent WhatsApp button & OutputDM badge.


## v012: the founder reel with the mascot asset library (bodies + swapped talking heads)

The user (Nov 13): the v010 rig's arms looked unnatural and the single front face/body angle was stiff; build a
reusable asset library (done: `mascot/library/`), complete the head/body composite test, then update the video.
(v011 is a separate library showcase another session pushed; v012 is the founder reel itself.)

- Character: library bodies (`prep_lib.py` copies them to `assets/lib/`, WebP, 2.9 MB). The arms are drawn in each
  body image, so they look natural; no rig joints. Angles: walking entrances use the side-on walk
  (`profileright/walk_side`, mirrored when he walks in from the right), the intro turns back -> 3/4 -> front, and
  "looking at the content" keys use the 3/4 body turned toward it.
- Head swap: each body has a fitted head position (`mascot/library/tools/composite.py`, `head_fit` in
  `library.json`). On every spoken word the head switches by syllable between `talk_a`, `talk_o`, `talk_e` and
  `talk_teeth` (vowel of each syllable; held across gaps under 0.12 s); between words it shows the pose's expression
  (smile, laugh, surprised, concerned, smirk). The mouth moves only by switching images; nothing is warped.
  `thinking_chin` and the back view keep their own head.
- The scene tracks still use the old 17 pose names; `LIBMAP` in `main.js` maps them to library bodies + expressions.
  Motion layers are the v009 ones (anticipation, 0.16 s dissolve, spring settle, lean, breathing, nod on words).
- Rebuild: `python3 prep_lib.py` first, then the usual steps (events, mix, video, mux) with `_v012` in the name.
- Open: no acting poses at 3/4 or profile angles yet (only neutral there); mouth timing follows estimated word
  times (Gemini TTS gives no timestamps); 4K not rendered for v012 yet (same command as before).

## v013: one ultra-smooth character, no swish on movements, 60 fps

User feedback on v012 (Nov 13): everything felt broken/choppy and not consistent; wants it ultra smooth; the swish
sound on every movement was very annoying, reduce it a lot.

Causes found: the character swapped body images ~50 times (each image generated separately, so each swap jumped),
the mouth cycled 4 shapes per syllable, every pose change had a dip, blur and spring squash, each scene had its own
character that faded in and out (7 times), and 47 whooshes (one per pose change).

- One character for the whole reel (`buildHero()` in `main.js`): the scene tracks are merged; he glides to each
  scene's mark (1.0 s smoothstep, starting 0.45 s before the scene so he is in place when its cards arrive).
- Far fewer pose changes: a pose is held at least 1.5 s (`MIN_HOLD`); the first key of every scene is kept.
  Changes are a 0.4 s smooth dissolve (new body over the old one), no blur, no anticipation dip, no squash.
- Intro no longer turns from the back view (it was a jump in the middle of the reel); he greets with a wave.
- Mouth: one open shape per word (`talk_a`, or `talk_o` for o/u words), closed between words when the gap is
  0.15 s or more; heads cross-fade over 0.07 s.
- Motion: slow breathing, a gentle sway, and a small smoothed lift/lean while he speaks (no nod on every word).
- Sound: the character makes no sound at all; whoosh 0.22 -> 0.06, pop .20 -> .12, thump .45 -> .30,
  ding .16 -> .12 (`mix.py`). Events: 84 -> 28 (pops/ticks on cards only).
- 60 fps render (`video.mjs --fps 60`).
- Open: 4K not rendered; poses at 3/4/profile angles beyond neutral still missing.

## Decision (Nov 14): use the installed skills first
The user's rule, now Rule 1 in `CLAUDE.md`: before working, look at all installed skills, plugins, connectors, then
MCP servers, and use the fitting ones (task-observer, video-pipeline-doctor, animate/choreograph, media-use,
video-export-qa for this reel). Next: run video-export-qa and a choreograph review on v013.

## v014: QA (video-export-qa) and choreography (choreograph) fixes on v013

Skills used, per the user's Rule 1: task-observer (observation workspace `skill-observations/` at the repo root,
2 observations logged), video-export-qa (its script lives on the user's Mac, so each check was run with ffmpeg),
choreograph (the character is support, never the lead).
- QA failures in v013, fixed: the first frame was empty (the hook now shows at 0 s, the character is already on
  stage); at 6 s the character stood over the OutputDM founder card (the key that moved him aside had been dropped
  by the 1.5 s hold rule: keys that move him more than 120 px are now always kept, and in the intro he steps aside
  on "Zarkhaiz", before the card arrives); audio was 96 kHz (now 48 kHz).
- Still WARN (user to decide): captions sit at 1408-1498 px, below the 168-1330 px safe band of the QA skill; the
  character's feet are at 1392 px, so moving them up means a smaller character or captions over him.
- NOT PERFORMED: music ducking by ear. Full table: `outputdm-reel/qa/v014/qa.md`.

## v015: the character is really animated (GPT keyframes through the bridge + in-between frames)

User (Nov 14): "bilkul smooth nahi hai", everything else is fine, work only on the character, use ChatGPT through the
bridge (no Muse), storyboards or whatever it takes.

Measured causes in v014: (1) every expression head was its own generated image and they did not line up (talk heads
5 px higher, some 17-23 px narrower), so the whole head jumped on every word; (2) pose changes were dissolves between
unrelated images, so arms never moved.

What changed (only the character; background, graphics, captions, voice and music are untouched):
- New character system `mascot/anim` (read its README). One master body; gesture keys are bridge EDITS of that master
  (only the arm changes); FILM in-between frames between the keys; each arm is its own half of the body, so the arms
  act independently. 11 bridge images, 166 frames, 3.8 MB in `assets/anim/`.
- Mouth: small patches over the master head (talk_a / talk_o / talk_e), so head, hair, eyes and glasses never move.
  Two expression patches: concerned on "lekin customers nahi aa rahe?" and "kho dete hain", laugh after the last line.
- Storyboard (bottom of `main.js`, `buildHero({L: [...], R: [...]}, faces)`): per arm `[time, state]` on spoken words.
  L (viewer's left arm): present on "paisa", explain on "lekin", wave on "Assalam o Alaikum", present on "Lahore",
  explain on "businesses", explain/present/explain through the leaks, present on "sirf", present on "WhatsApp",
  wave at the end. R: explain with L, present to the OutputDM card and to the services list.
- A held pose is one sharp key frame (mixing neighbouring frames there showed a doubled hand); life comes from slow
  breathing and sway of the whole body. Moves take 0.6-1.0 s on a smootherstep ease; neighbouring frames are mixed on
  a canvas with 'lighter' (CSS plus-lighter did not work in the render and made half the body see-through).
- Rebuild: see `mascot/anim/README.md`, then the usual events / mix / video (60 fps) / mux steps.
- Open: front view only; hands are soft for 2-3 frames in the fastest part of a move; no head turn or blink yet.

## v016: character clean-up (face, edges, stance)

User (Nov 14): v015 is better, but the face shows a "face inside a face", the outline looks cut-and-pasted and jagged,
and the stance is one stiff pose. Character only; background untouched.
- Face: the eyes-to-chin patches (concerned, laugh) were smaller than the master head, so the master's jaw and beard
  showed around them as a second face. They are no longer used: only mouth patches (talk_a / talk_o / talk_e, and
  smile after the last line).
- Edges: `mascot/anim/tools/edges.py` pulls the alpha of every frame in by about 2 px and feathers it (the white
  fringe of the generated background and the jagged rembg edge are gone). `build_anim.py` runs it at the end.
- Stance: a slow weight shift (lean about 1 degree and 9 px side to side, two periods mixed) on top of breathing.
- Declined, with the reason given to the user: installing OmniRoute / awesome-free-llm-apis as a router for Claude.
  A cloud session cannot change or monitor its own model and quota, the container is temporary, and such a router
  sends the user's work to third-party free endpoints.
- Open: real posture changes (hip shift, head turn, 3/4 stance) need new bridge keys of the whole body; blink.

## v017: a new face (the master's own face animated by LivePortrait)

User (Nov 14-15): everything else is fine, but the face is still very bad: its movement and its expression are both
wrong. Make the face again by any means (Blender, a GitHub repo, anything); if he does not speak word by word, a
correct expression is enough; do a critical analysis; research well-rated repos and install what is needed.

Critical analysis of the v016 face (frames compared):
- The mouth was a pasted patch cut from a *laughing* library head: on every word a wide open laugh popped in and out,
  and the jaw, cheeks and beard around it never moved. It read as a sticker.
- Eyes and brows were frozen for 39 s: no blink, no expression change, the same smile on "customers nahi aa rahe?".
- The head never moved on its own (only the whole body swayed).

What changed (only the head; body, arms, graphics, captions, voice and music are untouched):
- Tool: LivePortrait (github.com/KlingAIResearch/LivePortrait, MIT, about 19k stars), run on CPU. It re-poses ONE
  source photo, here `mascot/anim/raw/master.png`, so every frame is the same man, hair and glasses.
- `mascot/anim/tools/build_face.py` writes one head frame per 1/30 s of the reel from a parameter track:
  the mouth opens with the loudness of the real voiceover (`vo/*.wav`), rounder on o/u words; smile and brows change
  per line (engaged on line 1, concerned from "lekin" and on the leak lines, warm on the greeting, the system line and
  the CTA, biggest smile after the last line); blinks every 3-4.5 s; a small nod at each line start; a slow idle turn.
- In the page (`drawArm` in `main.js`) the master's head is removed from the body with `head/erase.png` and the head
  patch of that moment is added in its place, so there is no patch edge and no second face.
- The old mouth patches and the word-by-word mouth schedule are gone from the page.
- This replaces the old rule "never a face or mouth warp": the user asked for a new face by any means, and this
  model moves the whole face together (jaw, cheeks, eyes), which the v005 WebGL warp did not.

Research on the user's request (repos with high ratings):
- Chosen: LivePortrait, the best-rated tool made exactly for this job (expressions and mouth on one still portrait).
- Not used: Blender (needs a 3D model of the character; a flat cutout cannot give a moving face), ComfyUI and
  stable-diffusion-webui (100k+ stars, but they are hosts for models and need a GPU), SadTalker / Wav2Lip (older,
  lower quality mouths, change the identity more).
- The session ran on the `AI Video Editor` environment; the user approved adding the Hugging Face hosts
  (`huggingface.co`, `us.aws.cdn.hf.co` and its CDN names) and `download.pytorch.org` to it. The ChatGPT bridge is not
  reachable from that environment (it is on `zarkhaiz`), so no new GPT images were made.
- Rebuild: `mascot/anim/README.md` (Head), then `cp -r mascot/anim/out/head mascot/anim/out/face.json
  video/outputdm-reel/assets/anim/` and the usual events / mix / video (60 fps) / mux steps.
- Open: the mouth follows loudness, not exact letters (no lip-sync to each sound); the head runs at 30 fps inside the
  60 fps reel; 4K not rendered.

## v018: small expressions only, and a character that sits in the scene (not a sticker)

User (Nov 15) on v017: the face and body character is still weak; wants a more accurate, ultra smooth cartoon; only
a small expression, NOT a talking mouth; the character should be a smooth mascot, not cut out like a sticker.

What made v017 read as a sticker (frames checked): the figure was lit flat for a white studio and pasted on a dark
gold stage with a clean hard edge; the whole cutout rocked rigidly around its feet and turned like a card
(`rotate` + `rotateY` on one image); the mouth flapped with teeth on every sound; the head updated at 30 fps inside
a 60 fps reel.

What changed (character only):
- Mouth: closed for the whole reel. `build_face.py` now gives only small changes of smile and brows per line, blinks,
  a small nod at each line start and a slow head turn. The voice-driven mouth is removed.
- Smoothness: head frames are sampled 15 times a second (30 through blinks) and `drawPose` in `main.js` blends the two
  neighbouring frames by time, so the head moves on every one of the 60 frames a second.
- One figure: both body halves and the head are joined on one pose canvas (`drawPose`), then lit for the stage:
  a warm rim light along the outline (the gold light behind him), legs falling off into the dark floor, a little
  warm fill from the upper left, a soft warm glow, and a faint floor reflection under the shoes.
- Body motion: the rigid tilt and the card-like turn are gone. The pose is drawn row by row with a soft bend
  (`bend()` and the loop in `drawHero`): feet planted, hips shift slowly from one leg to the other, shoulders go a
  little the other way, the head follows, and the chest widens with each breath.
- Open: the legs and torso are still one drawn pose (no steps, no knee bend, no turn to 3/4). A fully fluid mascot
  needs either a rigged model of the character or a video-generation model driven from the master image; both need
  a GPU or a paid service, which this session did not have. 4K not rendered.

## Feedback on v018 (Nov 15), v019 not built yet
User: the face looks bigger than the body; the body should move too, through different angles; the rest of the
movement is smooth, make it smoother still; tell me what you will do BEFORE building; the character will be used for
a series, so make it perfect. The plan was given in chat and waits for the user's go-ahead:
1. head about 8-10 % smaller (scaled at the neck) with a comparison still for approval;
2. body turns front <-> 3/4 left/right from `mascot/library/bodies/34left|34right/neutral.png` with FILM in-betweens,
   each angle with its own LivePortrait head; if the turn ghosts, new in-between keys are needed from the ChatGPT
   bridge (only reachable from the `zarkhaiz` environment);
3. smoother: slower eased arm moves, head frames at 30 per second;
4. test stills and a 5 s test clip first, the full render only after the user approves.

### v019 tests so far (Nov 16), full reel NOT rendered yet
- The user chose head size B = 93 % (`HEAD_S = .93` in `main.js`, scaled at the collar) and wants the body to turn
  toward the content cards. Reference offered by the user, not received yet.
- `mascot/anim/tools/build_turn.py`: front -> 3/4 turns ("tl" toward the viewer's left, "tr" right) from the library
  3/4 bodies (narrowed to 91 % width so the build matches the front master) with 7 FILM in-betweens; each frame has its
  own head patch, erase mask, box and collar pivot in `out/turn.json`. The FILM model is also on Hugging Face:
  `https://huggingface.co/jkawamoto/frame-interpolation-pytorch/resolve/main/film_net_fp32.pt`.
- `main.js`: `buildHero(ARMS, ANGLES)` takes `[time, 'tl' | 'tr' | 'front']`; arm moves wait until he faces the
  front again; `composeFront` / `composeTurnFrame` / `turnAt` / `drawPose`. The storyboard there is still the TEST one
  (one turn at 0.15-2.3 s). `?dur=5` (video.mjs `--q 'dur=5'`) renders only the first 5 s.
- Sent to the user: `qa/v019_tests/head_sizes.jpg`, `turn_frames.jpg`, `turn_test_5s.mp4`. Waiting for the go-ahead.
- Still to do after approval: the real angle storyboard (turn to the cards at each scene start), a LivePortrait head
  for the 3/4 hold (blink and expression; now the face is still while he is turned), head frames at 30 per second,
  slower eased arm moves, full render, QA.

## v019: smaller head, slight body turns toward the cards (Nov 16)

Decisions the user made in chat:
- Head size B = 93 % (`HEAD_S = .93`).
- On the full 3/4 test clip: "do not turn him that much, and use the character as in this picture" (the first turn
  strip). Asked with numbered frames: the turn goes at most to frame 2 of 5 (a slight turn), and the body stays as
  drawn in the library (no narrowing; `SLIM = 1.0`).
- He turns toward the content cards. Mouth closed, small expressions (v018 rule stays).

What was built:
- `build_turn.py`: the slight turn = FILM frame 2 of the 8-step front -> 3/4 move, with 5 in-betweens of its own
  (7 frames per direction, `out/turn.json`).
- `angles.json` (in `video/outputdm-reel`): `{d, yaw, turns: [[time, "tl" | "tr" | "front"], ...]}`. The page reads it
  for the body and `build_face.py` reads it for the head, which turns 6 degrees with the body. Four turns: at the
  start (0.2-1.7 s), on "businesses" (10.7-12.4 s), in the system scene toward the list on the right (21.85-23.9 s)
  and before the CTA (31.55-33.0 s).
- `main.js`: while he is turned, each turn frame's own head is removed and the live LivePortrait head is put on that
  frame's collar point (`composeTurnFrame`, `liveHead`), so the face keeps blinking and smiling. The arm storyboard
  was rewritten around the turns (arms are at rest while he is turned; `buildHero` throws if they are not), and arm
  moves are about 25 % slower.
- Open: the user offered a reference for the character and has not sent it yet; no gestures while turned (the gesture
  keys exist only for the front view); legs still one pose; 4K not rendered.

## v020: the acting system (Nov 16)

The user's brief: the character still felt stiff; make it a far more expressive, dialogue-driven presenter (face and
lip-sync first, then hands and arms, head and torso, a selection engine, tests, documentation). Details of every part
are in `mascot/anim/README.md` (section v020) and `mascot/anim/manifest.json`.

Decisions the user made in chat (Nov 16):
- Lip-sync is wanted now (this replaces the v018 rule "no talking mouth"). The first test (a mouth shape per letter)
  was "not good at all"; the second (mouth generated from the voice, JoyVASA + LivePortrait) is "much better" and is
  the one used.
- No paid video generation anywhere. Kie may be used for IMAGES only (the gesture keys were made there: 31 images,
  186 credits). Higgsfield: images only too, but its connector was not connected in this session.
- The final work is handed over as a local file; the user updates the repository (this session had no push access).

What changed in this folder:
- `phonemes.json` (real word and sound times from the audio), `build_timeline.py` uses them: captions and scene cues
  now sit on the spoken words (the old estimate was up to 0.36 s early).
- `staging.json`: where he stands per scene. `acting.json`: the whole performance, written by the director.
- `main.js`: the hand-written arm storyboard is gone; the arms are read from `acting.json`. The body is drawn as in
  v019 (the lean / shrug / shoulder warps and the body turns of the first v020 render were removed, see below).
- `assets/anim/`: new arm frames (L, R), `anim.json`, the head frames of the talking face.
- Test clips: `qa/v020_tests/` (three lip-sync tests, the first 8 s of the reel).

What the director chose for this script (the log is printed by `director.py`): open hands on the question, wave on
"Assalam", presenting on "Zarkhaiz", "2018", "Lahore"; three fingers on "teen"; counting 1-2-3 on the three leaks
and 1 to 5 on the five services; one finger on "ek system"; chop on "sirf"; pointing at the camera on "aap" and
"abhi"; thumbs-up on "Free"; small nods, a look up on the question, chin forward on direct address.

Second render (same file name), after the user's review of the first: "shoulders and face break in many places, not
symmetric, cuts are visible, make it smooth". Fixed: every cutout edge is cleaned again (a build regression left a
dotted white fringe), the shoulder / lean warps are removed (they notched the outline), no body turns, no head tilt
or roll, head moves within 3.5 degrees, no one-brow accents. Details: `mascot/anim/README.md`, "Quality fix".

Rebuild: the steps in `mascot/anim/README.md` (v020), then as before:
```
node $LIB/core/render/events.mjs . --size 1080x1920 && $LIB/.venv/bin/python mix.py
node $LIB/core/render/video.mjs . --fps 60 --workers 3 --size 1080x1920 --out out/video_v020.mp4
ffmpeg -i out/video_v020.mp4 -i mix.wav -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 256k -ar 48000 -shortest out/outputdm_founder_reel_v020.mp4
```

Open:
- The second render waits for the user's verdict on smoothness and symmetry.
- Nobody has watched v020 in playback yet (checked on frames, sequences and measurements only): smoothness, the
  lip-sync against the sound and the music mix need the user's eyes and ears.
- Tests with other kinds of dialogue (excited, serious warning) were not made: a new voiceover needs the Gemini TTS
  key, which this session did not have.
- Limits of the character system: `mascot/anim/README.md`, "Limits (v020)".
- Captions still sit at about 1408-1498 px, below the 168-1330 px safe band (unchanged since v014, user to decide).

## v021 (in progress, Nov 24): natural arms
The user (Nov 24): "baazu abhi bhi unnatural lag rahe hain, theek karo", then shared five design links
(motion-primitives.com, haikei.app, realtimecolors.com, godly.website, replit.com) to take help from. The user chose the
free ChatGPT bridge for the new images.

What the v020 frames showed (`mascot/anim/README.md`, v021):
- the hand melts on the first interpolated step of most gestures (hanging -> mid), and a gesture-to-gesture clip
  (explain -> wave) makes the hand vanish and reappear;
- the idle pose is a stiff mannequin hang, on screen most of the time;
- poses changed every 0.6-0.7 s (the v013 rule says held 1.5 s); one arm did everything.

Done so far (free, no new images):
- `director.py`: a calm-arms pass that rewrites only the arm track (face, head, gaze and blinks are unchanged, so the
  v020 head frames stay valid; checked): poses held 1.5 s, finger counting steps every 0.6 s, the greeting / "you" /
  benefit gestures win over a gesture just before, rarely natural gestures mapped to core ones. Its log is printed
  as "calm arms (v021)".
- `main.js`: spring timing for the arm clips (damping 0.8, from motion-primitives' spring transitions: quick start,
  long settle) and a short blend between neighbouring frames (the long 50/50 mix read as a doubled hand).
- `build_anim.py` / `gen_keys.py`: a relaxed stance per arm as the new idle pose and quarter-way keys (q1) before the
  core gestures; they are used automatically once the 10 keys in `gen_keys.V021` exist.

Open: the 10 keys. The bridge answered 404 on `/health` and `/jobs` on Nov 24, also from the "AI Tools" environment
that holds its token (session "v021 arm keys through the ChatGPT bridge" is waiting). Once the keys exist:
`python3 mascot/anim/tools/build_anim.py`, copy `mascot/anim/out` to `video/outputdm-reel/assets/anim` as in Rebuild,
run `director.py`, render, QA. From the links: haikei-style SVG backgrounds and a realtimecolors check of the palette
are possible later; godly.website redirects to a host that does not resolve; replit adds nothing to this pipeline.
