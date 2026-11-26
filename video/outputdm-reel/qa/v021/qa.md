# QA: outputdm_founder_reel_v021.mp4 (2026-11-26)

v021 changes only the arms (relaxed stance, quarter-way keys, calm-arms director pass, spring timing, rigid hands);
the face, head, gaze and blinks are identical to v020 (acting.json compared), so the v020 head frames are reused.
The video-export-qa skill is not available in this session (observation 0002), so each check was run with
ffmpeg/ffprobe and Python, as for v020.

| Check | Result | Evidence |
|---|---|---|
| Container, H.264, yuv420p | PASS | ffprobe: h264, yuv420p |
| Size, frame rate | PASS | 1080x1920, 60 fps, 2325 frames |
| Audio | PASS | AAC, 48 kHz |
| A/V duration match | PASS | video 38.750 s, audio 38.748 s |
| Full decode | PASS | 0 errors |
| Black frames (0.2 s or more) | PASS | none |
| Freezes (1 s or more) | PASS | none |
| Single-frame brightness dips or flashes (the "no blinking" rule) | PASS | 0 of 2325 frames |
| Single-frame jumps above the caption band | PASS | 0 frames above 2.5x both neighbours |
| Loudness / true peak | PASS | -14.2 LUFS integrated, -1.4 dBFS |
| Hook visible at 0 s | PASS | contact.jpg |
| Idle arms relaxed, not the stiff hang | PASS (stills) | contact.jpg |
| Hands whole during arm moves (the user's complaint) | PASS (stills) | wave_before_after.jpg, hands_before_after.jpg: no broken or melted hand; the middle frame of a fast turn is a little soft |
| Poses held 1.5 s, finger counting every 0.6 s | PASS (schedule) | acting.json `arms` and `arm_log` |
| No pose cut off by the frame | PASS | the director's fits() check; contact.jpg |
| Motion smoothness and lip-sync in playback | NOT PERFORMED | judged from stills and sequences; needs watching |
| Captions inside the 168-1330 px safe band | WARN | unchanged since v014 (user to decide) |
