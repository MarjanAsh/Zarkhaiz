# QA: outputdm_founder_reel_v017.mp4 (2026-11-15)

The video-export-qa script is not bundled in a cloud session, so each check was run with ffmpeg/ffprobe and Python.

| Check | Result | Evidence |
|---|---|---|
| Container, H.264, yuv420p | PASS | ffprobe: h264, yuv420p |
| Size, frame rate | PASS | 1080x1920, 60 fps, 2325 frames |
| Audio | PASS | AAC, 48 kHz |
| A/V duration match | PASS | video 38.750 s, audio 38.748 s |
| Full decode | PASS | no errors |
| Black frames (0.2 s or more) | PASS | none |
| Freezes (1 s or more) | PASS | none |
| Single-frame brightness dips (the "no blinking" rule) | PASS | 0 of 2325 frames |
| Loudness | PASS | -14.2 LUFS integrated |
| True peak | PASS | -1.4 dBTP |
| Hook visible at 0 s | PASS | contact.jpg, first frame |
| Face: same person, no patch edge, no second face | PASS | faces.jpg (9 moments), face_sequence.jpg |
| Face: expression changes with the lines | PASS | faces.jpg: concerned at 2.9 s and 15.5-19.5 s, smile at 5 s, 33 s, 37.5 s |
| Face: continuous motion and a blink | PASS | face_sequence.jpg (10 frames at 15 fps from 8.4 s) |
| Character never covers a card | PASS | contact.jpg |
| Captions inside the 168-1330 px safe band | WARN | captions sit at about 1408-1498 px, unchanged since v014 (user to decide) |
| Caption spelling against the script | NOT PERFORMED | captions and script unchanged since v016 |
| Lip sync to each sound | NOT PERFORMED | the mouth follows voice loudness by design, not letters |
| Music ducking by ear | NOT PERFORMED | needs listening; the mix is unchanged since v016 |
