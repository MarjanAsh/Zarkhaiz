---
id: 4
title: "Frame interpolation between distant arm keys morphs the hand; the director also broke the project's own minimum-hold rule"
status: open
type: open-source
skill: []
proposes_skill: [character-animation-from-stills]
target_file: []
siblings_checked: "none: no skill family registry; the proposed skill is the same candidate as observation 0003"
area: "arm motion from image keys + rule-based gesture scheduling"
date: 2026-11-24
session_context: "user said the arms in reel v020 still look unnatural; frames of the v020 render and of the arm clips were inspected (mascot/anim, video/outputdm-reel/acting.json)"
parked_until:
resolved:
resolution:
reference: "mascot/anim/README.md (v020 Limits); video/outputdm-reel/acting.json"
commands_verified: none
---

**Issue:** The arm clips are frame interpolation (FILM) between edited keys of one master image. Where two keys are far
apart (explain -> wave), the interpolated frames do not move the arm along a path: the hand drops toward the hip,
melts into a white smear for a few frames and reappears raised. In playback this reads as a morphing, teleporting hand,
not a travelling arm. On top, the rule-based director scheduled gesture changes every 0.6-0.7 s (a count of five on
consecutive list items), although the project's own rule says a pose is held at least 1.5 s; and one arm hung in the
stiff rest pose for 19 s while the other did every gesture.

**Suggested improvement:** For a skill on animating a character from stills: (1) cap the hand travel between two
neighbouring keys (measure it; add a key where it is exceeded) and route large moves through arc keys, never let
the interpolator bridge a big move; (2) play one sharp frame at a time with eased timing, no additive cross-fade of
two interpolated frames; (3) the scheduler enforces the minimum hold as a hard check on its output, not as a value
in a table; (4) treat the rest pose as the most-seen pose and make it relaxed (bent elbows, closed hands).

**Principle:** Interpolators fill small gaps; they do not invent motion. Measure the gap before trusting the
in-between, and enforce timing rules on the generated schedule, where a violation is visible, rather than only in
the parameters that produce it.
