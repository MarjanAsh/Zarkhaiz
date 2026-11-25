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
| thumbsL_q1 | 3 + 1 with the firmer Q1F prompt | 2.24 | 1.65 | redone (Nov 25): hand below the jacket beside the thigh, half-closed; a small first move |
| countL_q1 | 3 + 1 with the firmer Q1F prompt | 2.03 | 1.70 | redone (Nov 25): same small first move, knuckles to the viewer's left |
| countL_q3 | 2 (1st: download reset) | 3.27 | 2.40 | good halfway pose; hair a little fuller, smile a little wider |
| shrug_q1 | 1 | 2.07 | 1.79 | good quarter-way move |

The bridge tends to overshoot the q1 keys (the arm goes about a third to a half of the way, not a quarter). The user
asked to redo thumbsL_q1 and countL_q1 with a firmer prompt: `Q1F` in `gen_keys.py` (the mid is only a direction hint,
the frame must look much closer to the base; the hand moves one hand's width and stays below the jacket hem). Both
came out right on the first try. If presentL_q1 or explain_q1 look too far along in the animation, give them Q1F too.
