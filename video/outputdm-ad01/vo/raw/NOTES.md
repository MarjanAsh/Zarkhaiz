# ad01 voiceover: raw takes (2026-11-26)

Gemini TTS `gemini-3.8-flash-tts`, voice Charon, spoken from the Urdu `say` field of `../../lines.json`,
made with `tts_gemini.py` (unchanged). 24 kHz mono, silence trimmed. l01, l04, l07 and l10 were regenerated through a
scratch wrapper that calls the same `tts_gemini.tts()` with the same model and voice and gives only l01 and l07 their own
style line: l01 "confident, punchy, short dramatic pause after 'phir bhi kehta hoon'"; l07 "warm, relaxed, unhurried".

Check per take: transcript, duration against word count (about 2.6 words/s + 0.3 s; ratio over 1.6 means a runaway),
longest silence. **Transcripts came from `gemini-3.5-flash-lite`, not `gemini-3.5-flash`**: the free tier of
gemini-3.5-flash allows 20 requests a day and that quota was already used up. Lite sometimes answers in Devanagari or Roman
script; the words were compared, not the script.

| line | tries | duration | transcript match | notes |
|---|---|---|---|---|
| l01 | 2 | 5.77 s | yes | try 1 5.38 s, generic style. Try 2 directed: pause 0.44 s before "ads pe paisa lagana band karein" (the comma pause after "chalata hoon" is 0.50 s). Tone judged only from the timing, nobody has listened yet. |
| l02 | 1 | 4.72 s | yes | 0.76 s pause at "ads nahi..." as scripted |
| l03 | 1 | 5.67 s | yes | |
| l04 | 2 (3rd blocked) | 5.00 s | **no** | try 1 runaway (16.43 s). Try 2: every word present but it says "kaam kar **raha hoon**" instead of "kar **rahe hain**" (heard the same way on 3 transcriptions). "Zarkhaiz" was transcribed once as "Zarjis" and once as "Zarkhez". **Regenerate when the TTS quota resets.** |
| l05 | 1 | 4.76 s | yes | |
| l06 | 1 | 5.85 s | yes | rising question on "nahi chalega?" |
| l07 | 2 | 7.46 s | yes | try 1 5.85 s, generic. Try 2 directed warm and relaxed (ratio 1.09, longest pause 0.56 s). One transcript heard "aayein" for "aaye hon", the second heard "aaye hon". |
| l08 | 1 | 6.48 s | yes | |
| l09 | 1 | 3.37 s | yes | |
| l10 | 2 | 1.96 s | yes | try 1 runaway (9.51 s) |

No take repeats words or adds any, and the longest silence anywhere is 0.80 s (l08).

## Open
- **l04 needs a 3rd try.** The free-tier daily limit for gemini-3.8-flash-tts (10 requests) ran out on 2026-11-26 and resets
  about 21 h later. Run: `GEMINI_KEY_FILE=/tmp/k python3 tts_gemini.py lines.json vo/raw --voice Charon --only l04`, then
  check that it says "kar rahe hain".
- The raw takes touch full scale on 4 to 11 samples each (light peak clipping in Gemini's output). Leave headroom or limit
  them in the mix.
