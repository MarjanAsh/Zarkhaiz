# Zarkhaiz / OutputDM: notes for every Claude session

Read this first, then `video/README.md` (the reel, its version history and how to rebuild it)
and `mascot/README.md` (the character images).

## Where the work is
- Branch: `ccr-e371ce1b-168zzm`. Continue on it unless the user names another branch.
- Current reel: `video/outputdm-reel/out/outputdm_founder_reel_v012.mp4` (1080x1920): mascot library bodies + swapped talking heads
  (`video/README.md`, v012). v010 (puppet rig), v009 (pose images, also 4K) and the v011 library showcase kept.
  `outputdm_founder_reel_v009_4k.mp4` (2160x3840), 39 s, Roman Urdu captions, Urdu voiceover.
- Character: from v012 the mascot library (`mascot/library/`, bodies + head swap). Before: puppet rig `mascot/rig/RIG.md` (v010),
  the 17 pose images `mascot/character/CHARACTER.md` (v009).
- Mascot asset library v1 (the user's direction from 2026-11-13: build reusable assets, no rendering for now):
  `mascot/library/` (117 assets, `library.json`, contact sheets in `sheets/`), read `mascot/library/README.md`.

## The user's standing rules for the reel
- Character: the mascot library from v012 (rig in v010, 17 poses before). Never the angry pose, never a
  face or mouth warp; the mouth moves only by switching images (open-mouth pose or swapped talking head).
- The character moves with the spoken words (pose and position changes on words), not just fading in.
- Motion graphics are big and bold.
- Line 3 must say "kaam kar rahe hain".
- No blinking: check every frame's brightness for single-frame dips before delivering a render.

## Tools (not in the repo, install in a new session)
- Render toolkit lemo-opuscar: clone https://github.com/lemomo-ai/lemo-opuscar to
  `/home/user/lemomo-ai/lemo-opuscar`, `npm install`, a `.venv` from `requirements.txt`.
  For 4K, its `core/render/page.mjs` needs `deviceScaleFactor: +process.env.LEMO_DSF || 1`
  (see `video/README.md`, Rebuild).
- Gemini TTS: the Google AI Studio key is a network secret on the `zarkhaiz` and `AI Tools` environments (header
  `x-goog-api-key`); pass any dummy file as `GEMINI_KEY_FILE`, the proxy adds the real key. Image generation
  needs billing on that key (free tier limit is 0). Never commit keys.
- Image generation for the mascot library: `mascot/library/tools/gen.py` falls back automatically
  gemini → openai → ChatGPT bridge (zarkhaiz.duckdns.org, token injected by the proxy). Status is in `mascot/library/README.md`;
  the bridge upgrade for the VPS (given to ChatGPT there by the user) is `mascot/library/bridge/GPT_INSTRUCTIONS.md`.

## Keep the hand-off current (required)
The user moves between sessions and Claude accounts; the chat does not travel, only this repo does.
After every change you make:
1. Update `video/README.md` (or `mascot/README.md`): a new version section saying what changed, why,
   and what is still open. Update the "Final files" line when the output changes.
2. Update this file if the branch, the current files, the rules or the tools change.
3. Commit and push, with the README update in the same push as the work.
Write any decision the user made in chat into the README, so the next session knows it.
