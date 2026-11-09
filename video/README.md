# OutputDM founder reel

A 43-second vertical reel (1080x1920, 30 fps) that introduces Zarkhaiz as the founder of
OutputDM (Output Digital Marketing Pvt Ltd), using his office mascot images, the OutputDM logo
and a Google AI Studio (Gemini TTS) voiceover in Urdu.

Final file: `outputdm-reel/out/outputdm_founder_reel_v005_rigged.mp4`

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
# 1. voiceover (Google AI Studio key in a file OUTSIDE the repo)
GEMINI_KEY_FILE=/path/to/key python3 tts_gemini.py lines.json vo --voice Charon
# 2. timeline (line, word and caption timings)
python3 build_timeline.py
# 3. sound cues, audio mix, frames, final mux
LIB=/home/user/lemomo-ai/lemo-opuscar
node $LIB/core/render/events.mjs . --size 1080x1920
$LIB/.venv/bin/python mix.py
node $LIB/core/render/video.mjs . --fps 30 --workers 4 --size 1080x1920 --out out/video.mp4
sh $LIB/core/render/mux.sh out/video.mp4 mix.wav out/outputdm_founder_reel_v002.mp4 30 1
```

Review stills: `node $LIB/core/render/still.mjs . 3.2 7.6 12.5 --size 1080x1920 --out stills`

## Files

- `index.html`, `main.js`: the reel; `render(t)` draws any frame (lemo-opuscar page contract).
- `lines.json`: the script; `tts_gemini.py`: Gemini TTS; `vo/`: the voice lines.
- `build_timeline.py` -> `timeline.json`; `events.json`: sound cues exported from the page.
- `mix.py`: voice + generated music bed (no samples) + sound effects, music ducked under the voice.
- `assets/`: mascot cutouts (from `mascot/office-v1`, background removed with rembg) and the OutputDM logo.
- `fonts/`: Playfair Display and Jost (SIL Open Font License, see the licence files).

Note: in this container `mux.sh` refused `mix.wav` (its decode check reads loudnorm's progress,
which lags ~3 s at the end), so the final file was muxed directly with a two-pass ffmpeg
`loudnorm` to -14 LUFS (true peak -1.5 dB), AAC 256k, video stream copied.

## Review

Gemini (gemini-3.5-flash) watched v001: 8.5/10, captions in sync within 0.1-0.2 s, no glitches.
v002 fixes what it flagged: the hook's accent line now matches the voice, the brand strip and
the "Aap ka plan" list are bigger and brighter, and only one caption word is highlighted at a time.

## v005: rigged, moving mascot (made in code, no paid video model)

- `main.js` draws each mascot pose through a WebGL warp (`puppet()`): the head turns and nods around the
  neck, the jaw opens with the voice, eyelids blink, eyebrows lift on emphasis, the chest breathes.
  Face points per pose are in `RIG` (image pixels, read off gridded crops).
- `build_mouth.py` -> `talk/mouth.json`: mouth-open and speech-energy curves from the voiceover (60 fps).
- `actor()` crossfades poses for turns (back -> side -> front) and walks the character in.
- Intro, system and "only" scenes play real lip-synced clips from the free Hugging Face LeapTalk space
  (`motion/clips`, frames rebuilt by `talk_frames.sh`).
- Limits: arms and legs do not move separately (the source photos have crossed arms / hands in pockets),
  and the rigged mouth follows loudness, not exact Urdu phonemes.

Rebuild order: `tts_gemini.py`, `build_timeline.py`, `build_mouth.py`, `talk_frames.sh`, then events, mix, video, mux.
