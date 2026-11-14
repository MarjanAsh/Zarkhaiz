# QA: outputdm_founder_reel_v015.mp4 (skill: video-export-qa, checks run with ffmpeg in the cloud container)

| Check | Result | Evidence |
|---|---|---|
| Container, H.264, yuv420p, 1080x1920, 60 fps | PASS | probe.txt |
| AAC 48 kHz, A/V duration match | PASS | 38.750 vs 38.748 s |
| Full decode errors | PASS | 0 |
| blackdetect (>= 0.2 s) / freezedetect (>= 1 s) | PASS | 0 / 0 |
| Integrated loudness, true peak | PASS | -14.2 LUFS, -1.4 dBFS |
| No single-frame brightness dips (user rule) | PASS | 2325 frames, 0 dips |
| Hook visible at 0 s | PASS | open_0.jpg |
| Character: head outline stable while talking | PASS (by eye) | 12 frames at 10.0 s, every 4th frame: hair, eyes, glasses identical, only the mouth changes |
| Character: arm travels through in-between frames | PASS (by eye) | 12 frames from 1.0 s, every 3rd frame: the arm rises step by step, no dissolve |
| Character never covers lead content | WARN | contact.jpg: the presenting hand touches the corner of the OutputDM card (6 s) and the edge of the services list (24 s), as a pointing hand; no text is covered |
| Hands in the fastest frames of a move | WARN | soft for 2-3 frames (1/20 s), reads as motion blur |
| Captions inside 168-1330 px safe band | WARN | unchanged from v014 (1408-1498 px); user to decide |
| Lip sync | WARN | mouth patches switch on estimated word times (Gemini TTS has no timestamps) |
| Music ducking / intelligibility | NOT PERFORMED | needs listening |
