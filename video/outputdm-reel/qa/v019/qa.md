# QA: outputdm_founder_reel_v019.mp4 (2026-11-16)

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
| Head at 93 %, joined to the body without an edge, also while turned | PASS | turn_sequence.jpg, contact.jpg |
| Slight turn toward the cards, arms move only when he faces the front | PASS | turn_sequence.jpg (0-3.5 s at 4 frames a second) |
| Mouth closed, small expressions | PASS | contact.jpg |
| Brand chips pass behind the character at about 9-13 s | WARN | contact.jpg; the same since v013 |
| Captions inside the 168-1330 px safe band | WARN | captions sit at about 1408-1498 px, unchanged since v014 (user to decide) |
| Motion smoothness in playback | NOT PERFORMED | judged from stills and sequences only; needs watching |
| Caption spelling against the script | NOT PERFORMED | captions and script unchanged since v016 |
| Music ducking by ear | NOT PERFORMED | needs listening; the mix is unchanged since v016 |
