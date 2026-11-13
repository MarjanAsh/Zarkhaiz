# OutputDM / Zarkhaiz Mascot Asset Library

A modular, reusable asset gallery for the Zarkhaiz mascot, built with ChatGPT (`gpt-image-2`) via Creative Bridge and isolated with Apple Vision transparent cutouts.

Designed for dynamic script animation across ongoing video series, reels, and explainers.

---

## Directory Structure

```
mascot/library/
├── LIBRARY.md              # Complete catalog and integration guide
├── expressions/            # High-res transparent head/portrait expressions (1024x1024)
├── angles/                 # Full-body and medium shots at multiple camera angles
├── hands/                  # Isolated gesture hands and cuffs (alpha cutouts)
├── poses/                  # Dynamic full-body action poses (standing, walking, seated, laptop)
└── reference/              # Master reference files for model generation
    ├── source_apose.webp
    └── sheet1_ref.jpg
```

---

## 1. Facial Expressions (`expressions/`)

All files are high-resolution transparent PNG cutouts (1024x1024) calibrated to match the character's lighting and styling.

| Asset File | Expression | Script Intent / Dialogue Cues |
|---|---|---|
| `neutral_smile.png` | Calm confident smile | Default opening, listening, neutral anchor |
| `talking_open.png` | Natural mid-speech talking | Regular voiceover dialogue, continuous narration |
| `talking_wide.png` | Emphatic wide-mouth talking | Keyword highlights, punchlines, loud syllables |
| `excited.png` | Wide bright celebratory smile | Wins, "ek system!", breakthroughs, high energy |
| `serious.png` | Firm, focused executive gaze | Problem identification, serious business insights |
| `thinking.png` | Inquisitive glance up/side | Questions, pondering ("Marketing pe paisa lag raha hai...?") |
| `surprised.png` | Wide-eyed shock ('O' mouth) | Comedic realization, shock statistics ("Customers nahi aa rahe?!") |
| `concerned.png` | Empathetic furrowed brow | Addressing pain points, leaks ("kho dete hain") |
| `laughing.png` | Authentic joyous laugh | Light-hearted moments, relatable humor |
| `confident_grin.png` | Self-assured leadership smirk | CTA, company authority ("OutputDM dot com") |

---

## 2. Camera & Body Angles (`angles/`)

Multi-angle body representations allowing 3D-like orientation changes:

| Asset File | Angle | Description |
|---|---|---|
| `three_quarter_left.png` | 3/4 Facing Left | 45-degree turn facing left, dynamic hand gestures |
| `three_quarter_right.png`| 3/4 Facing Right | 45-degree turn facing right, engaged conversational pose |
| `profile_left.png`       | 90° Profile Left | True side profile facing left, ideal for split-screen layouts |
| `profile_right.png`      | 90° Profile Right | True side profile facing right |

---

## 3. Full-Body Poses (`poses/`)

Complete acting poses ready to drop directly onto timelines:

| Asset File | Pose Type | Use Case |
|---|---|---|
| `walking_front.png` | Walk cycle toward camera | Hero entrance, dynamic pacing, intro scene |
| `seated_desk.png`   | Executive at desk | Podcast-style intro, consultation discussion |
| `standing_laptop.png` | Holding open slim laptop | Tech demos, dashboard presentations, reviews |
| `confident.png`     | Classic front pose | Standard narration anchor |
| `arms_crossed.png`  | Arms folded firmly | Statement of reliability, track record |
| `explain.png`       | Both hands gesturing | Educational segments, step-by-step breakdowns |
| `point_screen.png`  | Directing to screen content | Callouts, floating UI cards |
| `point_camera.png`  | Pointing at viewer | Direct viewer ask, CTA ("Aap ka plan") |
| `presenting.png`    | Open palm to content | Revealing graphs, statistics, brand logos |
| `idea.png`          | Finger raised | Core concept ("Since 2018", key rule) |
| `back_look.png`     | Turning around | Reveal transition, teaser shots |
| `peace.png`         | Peace sign / sign-off | Friendly outro, social media signoff |

---

## 4. Hand Variations (`hands/`)

Isolated hand cutouts for puppet assembly or bespoke overlays:

- `hand_open.png`: Clean open palm (presenting / welcoming)
- `hand_point_forward.png`: Pointing directly at camera
- `hand_fist.png`: Determined fist
- `hand_thumbs_up.png`: Thumbs up confirmation
- `hand_rest_left.png` & `hand_rest_right.png`: Relaxed resting hands

---

## Dynamic Composition Example

In video render engines (such as HyperFrames, HTML Canvas, or Remotion):

```javascript
// Example: Dynamic Expression & Pose Switching on Word Timings
function drawActor(t) {
  let pose = 'poses/confident.png';
  let expr = 'expressions/neutral_smile.png';

  if (t >= t_walk && t < t_intro) {
    pose = 'poses/walking_front.png';
    expr = 'expressions/talking_open.png';
  } else if (t >= t_problem) {
    pose = 'poses/explain.png';
    expr = 'expressions/concerned.png';
  } else if (t >= t_stats) {
    pose = 'poses/standing_laptop.png';
    expr = 'expressions/excited.png';
  }

  // Composite layers
  renderLayer(pose);
  if (hasHeadSwap) renderHead(expr);
}
```
