---
id: 3
title: "Smooth character motion from stills: edit one master image, interpolate between edits, patch only the mouth"
status: open
type: open-source
skill: []
proposes_skill: [character-animation-from-stills]
target_file: []
siblings_checked: "none — no family registry; media-use and animate were read as candidates, neither covers character animation from generated stills"
area: "character animation for explainer reels"
date: 2026-11-14
session_context: "Founder reel v012-v015 (video/README.md v015, mascot/anim/README.md)"
parked_until:
resolved:
resolution:
reference: mascot/anim/README.md
commands_verified: none
next_actor: review
---

**Issue:** Three reel versions swapped separately generated body and head images (dissolves, per-word head swaps).
The user rejected each as choppy. Measurement showed the swapped heads differed by 5-23 px, and dissolves give no arm
travel. What worked: (1) image-EDIT every pose from one master so only the arm differs, (2) paste the edit back only
where it differs, (3) ask the image model for in-between poses with the later pose as a reference, (4) frame
interpolation (FILM) between neighbouring keys, (5) mouth-only patches registered to the master head.

**Suggested improvement:** A skill for "animate a generated character": measure alignment before swapping images;
never swap whole images; master + edits + in-betweens + interpolation; mouth patches; split independent limbs into
regions; hold poses on one sharp key.

**Principle:** Separately generated images of one character never line up; motion needs frames that share every
pixel except the part that moves.

**Further instance (2026-11-15, reel v017):** the "patch only the mouth" half of this recipe failed on review: a mouth
cut from a different expression image read as a sticker on a frozen face. What worked was re-posing the one master
face with a portrait-animation model (LivePortrait retargeting parameters, no driving video): mouth from voice
loudness, expression keys per line, blinks, nods; the master's head is erased from the body by a soft mask and the
head patch added back additively. The skill should prefer whole-face re-posing over mouth patches.

**Further instance (2026-11-15, reel v018):** the user rejected the voice-driven talking mouth as well ("just small
expression, not talking mouth") and called the figure a "sticker". Two additions for the skill: (1) ask early whether
a still-based character should talk at all; small expressions with a closed mouth are often what is wanted;
(2) a cutout reads as a sticker when it is lit for a white studio and moved rigidly: light it for the scene (rim
light, falloff, reflection) and bend it row by row with planted feet instead of rotating the whole image.
