# QA: outputdm_founder_reel_v014.mp4 (skill: video-export-qa, checks run with ffmpeg in the cloud container)

The skill's `qa_check.py` lives in the user's Mac toolchain (`~/.video-pipeline`), not in this container, so each
check from its list was run directly with ffmpeg/ffprobe.

| Check | Result | Evidence |
|---|---|---|
| Container, H.264, yuv420p, 1080x1920 | PASS | probe.txt |
| fps | PASS | 60/1 (user rule since v013) |
| AAC, sample rate | PASS | 48 kHz (v013 was 96 kHz: WARN, fixed with -ar 48000) |
| A/V duration match (<= 2 frames) | PASS | 38.750 vs 38.748 s |
| Full decode errors | PASS | 0 |
| blackdetect (>= 0.2 s) | PASS | 0 |
| freezedetect (>= 1 s) | PASS | 0 |
| Integrated loudness -14 +-2 LUFS | PASS | -14.2 LUFS |
| True peak <= -1 dBTP | PASS | -1.4 dBFS |
| Long silences | PASS | none >= 0.8 s at -45 dB |
| No single-frame brightness dips (user rule) | PASS | 2325 frames, 0 dips |
| Hook visible at 0 s | PASS | open_0.jpg (v013: FAIL, empty first frame) |
| Character never covers lead content | PASS | contact.jpg (v013: FAIL, he stood over the OutputDM founder card at 6 s) |
| Caption groups: overlap / length | PASS | 36 groups, 0 overlaps, max 24 chars; 2 groups under 0.5 s ("nahi,", "ads,") |
| Captions inside 168-1330 px safe band | WARN | captions sit at 1408-1498 px, below the band (the character's feet are at 1392); kept as in all versions, user to decide |
| Caption spelling | PASS (manual) | compared with lines.json by eye; no automatic Roman Urdu spell-check exists |
| Lip sync | WARN | mouth switches on estimated word times (Gemini TTS has no timestamps); frames checked by eye in v012 |
| Music ducking / intelligibility | NOT PERFORMED | needs listening or separate stems |
