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
