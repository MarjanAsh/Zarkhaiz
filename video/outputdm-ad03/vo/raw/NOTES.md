# ad03 voiceover: raw takes (2026-11-27)

Same method as ad 02 (`../../../outputdm-ad02/vo/raw/NOTES.md`): Gemini TTS, voice **Charon**, model
**`gemini-3.1-flash-tts-preview`** (the model of ad 02's lines, so the voice matches), spoken from the Urdu `say` field of
`../../lines.json`, `tts_gemini.py`'s STYLE prompt and trim (24 kHz mono, silence trimmed). Takes were made through a scratch
wrapper that sends ONE request per call with the same STYLE and adds only a line direction:
l01 "confident and punchy; short dramatic pause after 'پھر بھی کہتا ہوں' before 'نئی ویب سائٹ مت بنوائیں'";
l07 "warm, relaxed and unhurried". The model had quota all the way (one 429, the per-minute limit, waited out); no other model used.

New lines: l01, l02, l03, l05, l06, l07. **l04, l08, l09, l10 are the ad 02 takes, copied, not regenerated.**

Check per take: transcript by `gemini-3.5-flash-lite`, duration against word count (words / 2.6 + 0.3 s; over 1.6 = runaway),
pauses over 0.25 s, clipped samples, and the last 0.15 s (for the end noise burst).

| line | tries | duration | ratio | transcript match | notes |
|---|---|---|---|---|---|
| l01 | 1 | 4.95 s | 1.01 | yes | pause 0.62 s after "بناتا ہوں..." and **0.52 s before "نئی ویب سائٹ مت بنوائیں"** (the hook pause). |
| l02 | 2 | 3.53 s | 0.62 | yes | fast in both tries (3.46 s / 3.53 s), words complete; try 2 kept for its cleaner ending. Watch the pace in the edit. |
| l03 | 3 | 5.61 s | 0.99 | yes | tries 1 and 2 opened unclear ("teen cheezein" heard as "peeche" / "pin dizen", also on the opening cut alone); try 3 clearly "تین چیزیں". "پیج" is heard as "پیٹ" in every try (the transcriber; check by ear). |
| l04 | (ad 02) | 5.20 s | | | |
| l05 | 1 | 4.95 s | 1.09 | yes | |
| l06 | 1 | 5.33 s | 0.74 | yes | the question "ٹھیک ہے؟" transcribed with a full stop: the rising intonation is not confirmed. |
| l07 | 1 | 5.53 s | 0.73 | yes | directed warm and relaxed; pauses 0.26 s and 0.46 s (before "یہی نارمل..."). |
| l08 | (ad 02) | 6.39 s | | | |
| l09 | (ad 01/02) | 3.37 s | | | **ends in the loud clipped burst** (18 clipped samples, from ~3.20 s) |
| l10 | (ad 01/02) | 1.96 s | | | **ends in the loud clipped burst** (22 clipped samples, from ~1.80 s) |

No runaway, no repeated or dropped words. The six new takes have no clipped samples and no end burst.
`dur.json` holds all ten durations as the files are (measured; l09/l10 with the burst included).

## Open
- **l09 and l10 still end in the burst** (known from ad 02): cut them before the mix (l09 at 3.20 s, l10 at 1.75 s) or regenerate.
- Nobody has listened yet: l01's punch, l06's question intonation and l07's warmth are judged from timing and transcript only.
