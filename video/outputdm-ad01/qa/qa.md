# QA: outputdm_ad01_v001.mp4 (2026-11-26)

Checks run with ffmpeg/ffprobe and Python, as for the reel (the video-export-qa skill is not available here,
observation 0002).

| Check | Result | Evidence |
|---|---|---|
| Container, H.264, yuv420p | PASS | ffprobe |
| Size, frame rate | PASS | 1080x1920 (9:16), 60 fps, 2836 frames |
| Audio | PASS | AAC 48 kHz |
| A/V duration match | PASS | video 47.267 s, audio 47.264 s |
| Full decode | PASS | 0 errors |
| Black frames / freezes | PASS | none |
| Single-frame brightness dips or flashes ("no blinking") | PASS | 0 of 2836 |
| Single-frame jumps above the caption band | PASS | 0 |
| Loudness / true peak | PASS | -14.4 LUFS integrated, -1.4 dBFS |
| Hook on screen at frame 0 | PASS | contact.jpg: "Main agency chalata hoon..." + red "AGENCY OWNER KA SACH" |
| The nine beats in order | PASS | contact.jpg: confession hook, curiosity gap (redacted card), solution (system checklist), credibility (founder card), fear removal (crossed budget / technical), objection (bubble -> free review), lifestyle (phone 7:30 with messages), authority (industries, Pakistan / UAE, brand wall), CTA (WhatsApp, logo, site, follow) |
| Line 4 says "kaam kar rahe hain" | PASS (alignment) | spliced from the reel's own take; forced alignment reads "yahi kaam kar rahe hain" in order |
| Face whole, joined, same person | PASS (stills) | faces.jpg (4 moments, talking and pointing) |
| Claims | PASS | only facts the reel already states; no numbers, results or guarantees |
| Lip-sync and motion in playback | NOT PERFORMED | needs watching |
| Voice by ear (l01 punch, l07 warmth, the line-4 splice) | NOT PERFORMED | needs listening |
