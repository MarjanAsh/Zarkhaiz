# QA: outputdm_founder_reel_v018.mp4 (2026-11-15)

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
| Mouth closed, small expressions, eye blink | PASS | face_sequence.jpg (10 frames at 20 fps from 8.4 s), contact.jpg |
| Character lit for the stage (rim light, dark legs, reflection) | PASS | body_sequence.jpg |
| No patch edge at the neck or the body centre line | PASS | body_sequence.jpg, face_sequence.jpg |
| Brand chips pass behind the character at about 9-13 s | WARN | contact.jpg, third frame; the same in v013-v017 |
| Captions inside the 168-1330 px safe band | WARN | captions sit at about 1408-1498 px, unchanged since v014 (user to decide) |
| Motion smoothness in playback | NOT PERFORMED | judged from stills and sequences only; needs watching |
| Caption spelling against the script | NOT PERFORMED | captions and script unchanged since v016 |
| Music ducking by ear | NOT PERFORMED | needs listening; the mix is unchanged since v016 |
