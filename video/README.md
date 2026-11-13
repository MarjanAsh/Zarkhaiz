# OutputDM founder reel

A 38-second vertical reel (1080x1920, 30 fps) that introduces Zarkhaiz as the founder of
OutputDM (Output Digital Marketing Pvt Ltd), using five full-body office mascot cutouts, the OutputDM logo
and a Google AI Studio (Gemini TTS) voiceover in Urdu.

Final files: `outputdm-reel/out/outputdm_founder_reel_v013.mp4` (1080x1920, 60 fps, one smooth library character). v012 (library, choppy) kept. v010 (puppet rig), v009 (pose images, also 4K) and the v011 library showcase stay in out/ for comparison.

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
