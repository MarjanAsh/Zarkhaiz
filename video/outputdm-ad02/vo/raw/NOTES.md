# ad02 voiceover: raw takes (2026-11-26)

Same method as ad 01 (`../../../outputdm-ad01/vo/raw/NOTES.md`): Gemini TTS, voice **Charon**, spoken from the Urdu `say`
field of `../../lines.json`, `tts_gemini.py`'s STYLE prompt and trim (24 kHz mono, silence trimmed). Takes were made through a
scratch wrapper that sends ONE request per call with the same STYLE and adds only a line-specific direction:
l01 "confident and punchy, short dramatic pause after 'sach bataun?'"; l04 "say every word exactly, plural 'kar rahe hain'";
l07 "warm, relaxed and unhurried".

**Models.** `gemini-3.8-flash-tts` (the ad 01 model) had quota for one request today, then answered 429 (free tier daily
limit 10). The other Gemini TTS models in `GET /v1beta/models` were tried with the same voice:
`gemini-3.8-flash-lite-tts` made runaways and a loud clipped noise burst at the end of its takes (its quota also ran out,
limit 3); **`gemini-3.1-flash-tts-preview` made clean takes, so all eight final lines are from that one model** (same voice
throughout, but a different model from ad 01's l09/l10: listen for a timbre jump at the CTA).

Check per take: transcript by `gemini-3.5-flash-lite` (the full flash timed out), duration against word count
(words / 2.6 + 0.3 s; over 1.6 = runaway), pauses over 0.25 s, clipping and the last 0.6 s.

| line | final model | tries | duration | ratio | transcript match | notes |
|---|---|---|---|---|---|---|
| l01 | gemini-3.1-flash-tts-preview | 2 | 5.62 s | 1.06 | yes | try 1 (3.8-flash-tts, 5.39 s) ended in a clipped noise burst. Try 2: pause 0.50 s after "karta hoon...", **0.70 s before "Followers se business nahi chalta"**. Tone judged from timing only, nobody has listened yet. |
| l02 | gemini-3.1-flash-tts-preview | 2 | 4.55 s | 0.86 | yes | try 1 (3.8-lite) runaway 16.50 s |
| l03 | gemini-3.1-flash-tts-preview | 2 | 5.08 s | 0.89 | yes | try 1 (3.8-lite) runaway 20.23 s |
| l04 | gemini-3.1-flash-tts-preview | 1 | 5.20 s | 0.98 | yes | ends "kaam **kar rahe hain**" (plural, checked). "Zarkhaiz" transcribed as "Zerakhiz". |
| l05 | gemini-3.1-flash-tts-preview | 2 | 5.03 s | 0.78 | yes | try 1 (3.8-lite) runaway 18.17 s |
| l06 | gemini-3.1-flash-tts-preview | 2 | 6.14 s | 0.85 | yes | try 1 (3.8-lite, 6.79 s) words fine but a 0.17 s full-scale noise burst after the last word |
| l07 | gemini-3.1-flash-tts-preview | 2 | 5.77 s | 0.89 | yes | try 1 (3.8-lite, 6.67 s) same end burst. Try 2 directed warm and relaxed, longest pause 0.36 s. |
| l08 | gemini-3.1-flash-tts-preview | 1 | 6.39 s | 1.12 | yes | |
| l09 | (ad 01 take, not regenerated) | - | 3.37 s | | | **ends in the noise burst**: speech ends ~2.78 s, silence, then full-scale burst 3.20 s to the end |
| l10 | (ad 01 take, not regenerated) | - | 1.96 s | | | **ends in the noise burst**: speech ends ~1.55 s, burst from 1.80 s |

No take repeats or drops words. The eight new takes have no clipped samples; longest silence 0.70 s (l01, the scripted pause).
`dur.json` holds all ten durations as the files are (l09/l10 measured, burst included).

## Open
- **l09 and l10 (copied from ad 01) end in a loud clipped burst.** Cut them before the mix (l09 at 3.20 s, l10 at 1.75 s)
  or regenerate them. The same artefact is likely what ad 01's NOTES call "touch full scale on 4 to 11 samples": check the
  ends of every ad 01 take before its final mix.
- Nobody has listened to the takes; l01's punch and l07's warmth are judged from timing only.
