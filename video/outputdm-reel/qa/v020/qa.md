# QA: outputdm_founder_reel_v020.mp4 (2026-11-16, second render after the user's review)

The first render was rejected by the user (shoulders and face break, not symmetric, cuts). The measured rows below were re-run on the second render.

The video-export-qa skill is not available in this session, so each check was run with ffmpeg/ffprobe and Python.

| Check | Result | Evidence |
|---|---|---|
| Container, H.264, yuv420p | PASS | ffprobe: h264, yuv420p |
| Size, frame rate | PASS | 1080x1920, 60 fps, 2325 frames |
| Audio | PASS | AAC, 48 kHz |
| A/V duration match | PASS | video 38.750 s, audio 38.748 s |
| Full decode | PASS | no errors |
| Black frames (0.2 s or more) | PASS | none |
| Freezes (1 s or more) | PASS | none |
| Single-frame brightness dips or flashes (the "no blinking" rule) | PASS | 0 of 2325 frames |
| Loudness | PASS | -14.2 LUFS integrated |
| True peak | PASS | -1.4 dBFS |
| Hook visible at 0 s | PASS | contact.jpg, first frame |
| Word times against the audio | PASS | for l01, l02, l03, l06, l09 the first aligned word starts within 0.13 s of the measured sound onset and the last ends within 0.06 s of the measured end |
| Gestures on their words | PASS (stills) | count 3 on "teen", 1-2-3 on the leaks, 1 to 5 on the services (list_count_sequence.jpg), chop on "sirf", pointing on "aap" and "abhi", thumbs-up on "Free" (emphasis_cta_sequence.jpg), wave on "Assalam" (question_wave_sequence.jpg) |
| No pose cut off by the frame | PASS | first render: the shrug's hand left the frame at the right edge; the director now rejects such poses (log: "shrug would leave the frame here"), re-rendered |
| Head joined to the body without an edge | PASS (stills) | zoomed frames of the 8 s test, contact.jpg |
| Character identity | PASS (stills) | every key image compared with the master; 3 Kie images with a shifted figure were regenerated |
| Cutout outline clean, shoulders whole (the user's complaint) | PASS (stills) | fix_zoom.jpg (6 moments at 2x), fix_arm_sequence.jpg (every 3rd frame of an arm move): no dotted fringe, no shoulder notch |
| Single-frame jumps (cuts) outside the caption band | PASS | frame-to-frame difference of all 2325 frames: 0 frames above 2.5x both neighbours |
| Symmetry | PASS (settings) | head roll 0, no tilt, no one-brow accents, no body turns; yaw and pitch within 3.5 degrees |
| Hands in the fastest part of an arm move | WARN | soft or doubled for 2-3 frames (fix_arm_sequence.jpg, frames 1 and 5), as in v019 |
| Brand chips pass behind the character at about 9-13 s | WARN | the same since v013 |
| Captions inside the 168-1330 px safe band | WARN | captions sit at about 1408-1498 px, unchanged since v014 (user to decide) |
| Motion smoothness in playback | NOT PERFORMED | judged from stills and sequences only; needs watching |
| Lip-sync against the sound in playback | NOT PERFORMED | the user judged the line-1 test clip "much better"; the full reel needs watching |
| Caption spelling against the script | NOT PERFORMED | captions and script unchanged since v016 |
| Music ducking by ear | NOT PERFORMED | needs listening; the mix code is unchanged since v016 |
