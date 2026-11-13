# Character puppet rig (from v010)

The user asked for the character to move its body parts smoothly instead of switching between pose images.
He sent one A-pose image plus 4 gesture hands (open, point, fist, thumbs up): `source.webp`.

`cut_rig.py` (needs `rembg`, system python3) cuts it into `parts/` and writes `rig.json`:

- `body` (torso + legs; keeps the beard bottom so a head tilt opens no gap), `head` (pivot: neck 435,282)
- per arm (`L` = screen-left, `R` = screen-right): `upper`, `fore`, `hand` (the resting hand, skin pixels only),
  `cap` (a soft disc of the shoulder that turns with the arm and covers the seam).
  Joints: shoulder, elbow, wrist in source pixels (`rig.json` → `joints`).
- `g_open`, `g_point`, `g_fist`, `g_thumb`: gesture hands, skin only, wrist at the bottom centre. They are drawn
  for the screen-left arm and mirrored for the screen-right arm, scaled by 0.62.

The reel copies these files to `video/outputdm-reel/assets/rig/`. In `main.js`, `POSE` lists the gestures as
[shoulder, elbow, hand] angles per arm (positive = arm lifts outward), plus head tilt and body lean;
`MAP` maps the old 17 pose names in the scene tracks onto them. A hero on the right half of the screen
gestures with its screen-left arm, so the arm never leaves the frame.

Motion: shoulder leads, elbow follows 60 ms later, both on a spring with overshoot. The hand swaps mid-move.
Breathing, idle arm sway, head nod on every word, and body lean are added on top. The face is never warped
and the mouth does not move.

Test one gesture: `node $LIB/core/render/still.mjs video/outputdm-reel 3 --q pose=wave --size 1080x1920`.

Limits: 2D only. Shoulder lift is kept at 52 degrees or less, because the jacket seam shows beyond that.
There is no back view and no walking legs.
