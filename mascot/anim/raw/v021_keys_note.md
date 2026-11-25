# v021 keys (Nov 25): how they were made and checked

All 10 keys of `V021` in `../tools/gen_keys.py` were made through the ChatGPT bridge (Codex image tool, edit mode), with
`master.png` and the gesture's mid key fetched by Codex from this repo and sha-checked. Contact sheet: `v021_keys_sheet.jpg`.

Check against `master.png` (mean absolute difference, 0-255, head = top 30 % of the figure, legs = bottom 35 %;
existing keys give head 2.1-2.6, legs 1.7-2.2). The figure's top and bottom are at the master's rows in every key.

| key | tries | head | legs | note |
|---|---|---|---|---|
| relaxedL_end | 1 | 2.04 | 1.78 | calm: softly bent elbow, curled fingers in front of the thigh |
| relaxedR_end | 1 | 1.74 | 1.57 | same, other arm |
| presentL_q1 | 3 | 2.28 | 1.89 | still a bit past a quarter (about a third of the way to the mid) |
| presentR_q1 | 3 | 2.14 | 2.24 | good quarter-way move |
| explain_q1 | 3 | 2.25 | 1.73 | about a third of the way, hands forward at hip height |
| pointcamL_q1 | 2 | 2.28 | 1.66 | fist at hip height, short of the mid |
| thumbsL_q1 | 3 (kept try 2) | 2.11 | 1.64 | overshoots: fist near belt height, close to the mid |
| countL_q1 | 3 | 2.34 | 1.85 | fist at hip height; still close to the mid |
| countL_q3 | 2 (1st: download reset) | 3.27 | 2.40 | good halfway pose; hair a little fuller, smile a little wider |
| shrug_q1 | 1 | 2.07 | 1.79 | good quarter-way move |

The bridge tends to overshoot the q1 keys (the arm goes about a third to a half of the way, not a quarter). If the
thumbs and count q1 frames look too close to their mids in the animation, a firmer q1 prompt ("the hand moves only a
hand's width from the thigh") is the next thing to try.
