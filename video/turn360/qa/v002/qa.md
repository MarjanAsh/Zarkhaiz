# QA: zarkhaiz_turn360_v002.mp4 (2026-11-19)

| Check | Result | Evidence |
|---|---|---|
| Container, codec | PASS | H.264 yuv420p, 1080x1920, 60/1 fps, 318 frames; AAC 48 kHz stereo |
| A/V duration match | PASS | video 5.300 s, audio 5.300 s |
| Full decode | PASS | `ffmpeg -v error -f null` printed nothing |
| Black frames (d >= 0.2 s) | PASS | blackdetect: 0 |
| Freeze (>= 1 s) | PASS | freezedetect: 0 (the last 0.4 s is a deliberate smile hold under the caption) |
| Single-frame brightness dips (user's no-blink rule) | PASS | YAVG per frame (`yavg.txt`): no frame 1.5 below both neighbours |
| Loudness | PASS | -13.7 LUFS integrated, true peak -1.7 dBTP |
| Frames at the busiest moments | PASS (looked) | `../v001/contact.jpg` (same stage; v002 only changes mouth timing) |
| Captions inside the 168-1330 px band, not over the face | PASS (looked) | captions 300-530 px, head top about 560 px |
| Caption spelling | PASS (compared by hand) | Roman Urdu line from `video/outputdm-reel/lines.json` l02 |
| Caption sync | PASS | word starts from Whisper base on `vo_l02.wav` + the voice's loudness |
| Lip sync | PASS (looked) | `lips_salam.jpg` (1.88-2.52 s), `lips_founder.jpg` (4.38-4.92 s): open on vowels, closed on the m of "Main"/"DM" and the pause |
| Listening | NOT PERFORMED | no one has listened to the mix yet; voice only, no music |

Known soft spots (not failures): across the back of the turn (about 0.85-1.15 s) FILM blends two separate drawings 90 degrees
apart, so arms show a faint double image under the motion blur; the raised hand snaps up in two frames at about 2.1 s
(the dissolving FILM frames of that clip are skipped on purpose).
