# Zarkhaiz / OutputDM: notes for every Claude session

Read this first, then `video/README.md` (the reel, its version history and how to rebuild it)
and `mascot/README.md` (the character images).

## Where the work is
- Branch: `ccr-e371ce1b-168zzm`. Continue on it unless the user names another branch.
- Current reel: `video/outputdm-reel/out/outputdm_founder_reel_v008.mp4` (1080x1920) and
  `outputdm_founder_reel_v008_4k.mp4` (2160x3840), 38 s, Roman Urdu captions, Urdu voiceover.

## The user's standing rules for the reel
- Character: only the five full-body cutouts in `mascot/office-v2` (side, back, smile, explaining,
  surprised). Never the angry pose, never a face or mouth animation.
- The character moves with the spoken words (pose and position changes on words), not just fading in.
- Motion graphics are big and bold.
- Line 3 must say "kaam kar rahe hain".
- No blinking: check every frame's brightness for single-frame dips before delivering a render.

## Tools (not in the repo, install in a new session)
- Render toolkit lemo-opuscar: clone https://github.com/lemomo-ai/lemo-opuscar to
  `/home/user/lemomo-ai/lemo-opuscar`, `npm install`, a `.venv` from `requirements.txt`.
  For 4K, its `core/render/page.mjs` needs `deviceScaleFactor: +process.env.LEMO_DSF || 1`
  (see `video/README.md`, Rebuild).
- Gemini TTS needs a Google AI Studio key in a file outside the repo (`GEMINI_KEY_FILE`). Never commit keys.

## Keep the hand-off current (required)
The user moves between sessions and Claude accounts; the chat does not travel, only this repo does.
After every change you make:
1. Update `video/README.md` (or `mascot/README.md`): a new version section saying what changed, why,
   and what is still open. Update the "Final files" line when the output changes.
2. Update this file if the branch, the current files, the rules or the tools change.
3. Commit and push, with the README update in the same push as the work.
Write any decision the user made in chat into the README, so the next session knows it.
