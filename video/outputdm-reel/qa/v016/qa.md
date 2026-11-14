# QA: outputdm_founder_reel_v016.mp4 (skill: video-export-qa, checks run with ffmpeg in the cloud container)

| Check | Result | Evidence |
|---|---|---|
| Container, H.264, yuv420p, 1080x1920, 60 fps | PASS | probe.txt |
| AAC 48 kHz, A/V duration match | PASS | 38.750 vs 38.748 s |
| Full decode errors | PASS | 0 |
| blackdetect (>= 0.2 s) / freezedetect (>= 1 s) | PASS | 0 / 0 |
| Integrated loudness, true peak | PASS | -14.2 LUFS, -1.4 dBFS |
| No single-frame brightness dips (user rule) | PASS | 2325 frames, 0 dips |
| Hook visible at 0 s | PASS | contact.jpg |
| Face: no nested face | PASS (by eye) | stills at 2.6 s and 38.4 s, zoomed 2x: only the mouth patch changes |
| Cutout edge | PASS (by eye) | same stills: no white fringe, feathered edge |
| Presenting hand near cards | WARN | touches the corner of the OutputDM card (6 s) and the edge of the services list (24 s); no text covered |
| Hands in the fastest frames of a move | WARN | soft for 2-3 frames |
| Captions inside 168-1330 px safe band | WARN | unchanged (1408-1498 px); user to decide |
| Lip sync | WARN | estimated word times |
| Music ducking / intelligibility | NOT PERFORMED | needs listening |
