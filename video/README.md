# OutputDM founder reel

A 38-second vertical reel (1080x1920, 30 fps) that introduces Zarkhaiz as the founder of
OutputDM (Output Digital Marketing Pvt Ltd), using five full-body office mascot cutouts, the OutputDM logo
and a Google AI Studio (Gemini TTS) voiceover in Urdu.

Final files: `outputdm-reel/out/outputdm_founder_reel_v008.mp4` (1080x1920) and `outputdm_founder_reel_v008_4k.mp4` (2160x3840)

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
ffmpeg -i out/video.mp4 -i mix.wav -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 256k -shortest out/outputdm_founder_reel_v008.mp4
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
