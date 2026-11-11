# Zarkhaiz character file

Read this before every video. It lists every pose of the OutputDM founder character, what each one is
for, and the rules for using them. The reel's code reads the same images from
`video/outputdm-reel/assets/char/` (copies of `poses/`).

## Source

- `refs/sheet1.jpg`, `refs/sheet2.jpg`, `refs/sheet3.jpg`: the three pose sheets the client supplied
  (6 poses each, labelled). Same outfit everywhere: black suit, black shirt, gold pocket square, black belt,
  watch, black shoes, clear glasses.
- `poses/*.png`: 17 cutouts (background removed with rembg `birefnet-general-lite`, labels dropped).
  Built by `video/outputdm-reel/cut_sheets.py`.

## Canvas (all poses share it)

- 820 x 1240 px, transparent. Body height (top of head to sole) is 1000 px in every pose.
- The feet sit on y = 1215, centred on x = 410 (the centre of the legs, not of the arms).
- Because every pose shares the canvas, swapping one image for another reads as the character moving.
  Never rescale one pose on its own.

## Poses

| File | What it shows | Use it on | Gesture direction (viewer's view) |
|---|---|---|---|
| `confident.png` | front, one palm open, other hand in pocket, smile | an opening line, a calm statement | none |
| `arms_crossed.png` | front, arms crossed, smile | the end of a sentence, a proud claim | none |
| `peace.png` | front, peace sign, smile | a greeting, a sign-off | raised hand on viewer's left |
| `point_camera.png` | front, pointing at the viewer | "aap", "you", a direct ask | toward camera |
| `point_screen.png` | 3/4, pointing to viewer's right, other palm open | pointing at a card or a word on screen | viewer's right (flip to point left) |
| `presenting.png` | 3/4, palm extended to viewer's left | showing a card, a list, a result | viewer's left (flip to present right) |
| `explain.png` | 3/4, both palms open toward viewer's left | explaining, lecturing | viewer's left |
| `side_point.png` | 3/4 side, pointing at camera, mouth open | enthusiasm, "this one" | toward camera |
| `idea.png` | finger up, eyebrows up | "2018", "teen", a new idea | up |
| `thinking.png` | hand on beard, looking up | a question, a problem being weighed | none |
| `laugh.png` | big laugh, hand on chest | a joke, a light moment | none |
| `surprised.png` | hands on head, mouth open | "customers?!", a shock | none |
| `oh_no.png` | hands on head, worried | a mistake, a loss ("kho dete hain") | none |
| `panic.png` | both palms up, shocked | the worst case, "nahi hota" | none |
| `victory.png` | both fists up, cheering | a win, "ek system" | none |
| `triumph.png` | 3/4, fists up, cheering | the payoff | none |
| `back_look.png` | back view, looking over the shoulder | an entrance: he turns round to the viewer | none |

## Rules

- Never the angry/frustrated pose (sheet 3, bottom middle). It is not cut and must not be used.
- No face or mouth animation that bends the image. The mouth moves only by switching to a pose with an open
  mouth (laugh, surprised, side_point, panic, victory) on emphasis words.
- Flipping (`scaleX(-1)`) is allowed only to aim a pointing or presenting gesture at the content; it moves the
  pocket square and watch to the other side, so do not flip in close-ups.
- One pose per spoken word or phrase at most; hold a pose at least 0.35 s.
- Pick the pose by the meaning of the word, then the gesture direction by where the content is on screen.

## Adding poses

Put a new sheet in `refs/`, add its names to `NAMES` in `video/outputdm-reel/cut_sheets.py`, run it, copy the
new PNGs to `video/outputdm-reel/assets/char/`, and add a row to the table above.
