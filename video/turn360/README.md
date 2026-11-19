# Zarkhaiz 360 + lip-sync test clip

5.3 s, 1080x1920, 60 fps. The mascot turns a full 360 on a gold turntable (degree counter 0-360), lands on the front and
says "Assalam o Alaikum! Main Zarkhaiz, OutputDM ka founder." (voice `outputdm-reel/vo/l02.wav`), waving and then
presenting with both hands, mouth shapes on every frame.

Final file: `out/zarkhaiz_turn360_v002.mp4` (QA: `qa/v002/qa.md`). v001 had a coarser mouth (closures merged away).

- Character: `assets/char.webm` (VP9 with alpha) built by `mascot/turn/tools/compose_char.py` (see `mascot/turn/README.md`).
- Stage: `compositions/turn.html` (turntable, speed arcs, counter; the angle curve must match compose_char.py),
  captions: `compositions/captions.html`, voice at 1.80 s in `index.html`.
- Render: `npx hyperframes render -f 60 -o out/zarkhaiz_turn360_v00N.mp4`; preview: `npx hyperframes preview`.
- `seedance_prompt.json`: the same shot as a Seedance 2.x prompt (EN + ZH) for Dreamina, with the library front body
  and the turnaround sheet as image references. That is how the reference reels were made.

User decisions (2026-11-19): the reference reels are about the character only (full 360, very good lip sync), not
the theme; 5 second test; GPT through the bridge (not reachable from this session, see mascot/turn/README.md).
