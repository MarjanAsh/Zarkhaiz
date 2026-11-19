# Zarkhaiz / OutputDM: notes for every Claude session

## Rule 1 (the user's first and fixed rule, 2026-11-14): look at everything installed before working
Before any work in a session, and again before each new kind of task:
1. Look through the user's **skills, plugins and connectors** first (the skills list in the system prompt,
   `ListSkills` / `ListPlugins` / `ListConnectors` where available), including the user's own customised ones.
2. Then look at the **MCP servers and their tools** (the deferred tools list, `ToolSearch`).
3. Pick the ones that fit the task and use them smartly. Start with `anthropic-skills:task-observer` (its own rule:
   before the first tool call of a session). For video work this means at least `video-pipeline-doctor` (new
   container), `animate` / `choreograph` (motion), `media-use` (cutouts, images, audio) and `video-export-qa`
   (after every render, before delivering).
4. Only then do the work. In the reply, say which skills, plugins, connectors and MCP tools were used and why
   any obvious one was skipped.
Why: in the 2026-11-13 session none of the user's 100+ installed skills were used, the work took the expensive
route (the v012 choppy reel), and the user's credits ran out.

Read this first, then `video/README.md` (the reel, its version history and how to rebuild it)
and `mascot/README.md` (the character images).

## Where the work is
- 360 + lip-sync test clip (2026-11-19): `video/turn360/` (HyperFrames project, 5.3 s, 1080x1920, 60 fps), character
  from `mascot/turn/` (read its README: library angles + FILM turnaround, voice-driven mouth shapes, limits). The user's
  reference reels were Seedance 2.5 (Dreamina / ArtCraft) and Gemini (Veo) videos, not Claude; a ready Dreamina prompt is
  `video/turn360/seedance_prompt.json`. Next step for a slow clean 360: 16 body angles through the bridge.
- Branch: `ccr-e371ce1b-168zzm`. Continue on it unless the user names another branch.
- Current reel: `video/outputdm-reel/out/outputdm_founder_reel_v016.mp4` (1080x1920, 60 fps, 48 kHz): the animated
  character from `mascot/anim` (GPT keyframes through the bridge + FILM in-betweens, mouth patches), QA in
  `video/outputdm-reel/qa/v016/qa.md`. v015 to v012 kept.
- Skill observations (task-observer): `skill-observations/` at the repo root; run its session-start scan with that path. v010 (puppet rig), v009 (pose images, also 4K) and the v011 library showcase kept.
  `outputdm_founder_reel_v009_4k.mp4` (2160x3840), 39 s, Roman Urdu captions, Urdu voiceover.
- Character: from v015 `mascot/anim/` (read its README: one master body, bridge edits as keys, FILM in-betweens,
  mouth patches). v012-v014 used `mascot/library/` bodies + head swap (choppy: do not go back to swapping whole images). Before: puppet rig `mascot/rig/RIG.md` (v010),
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
- Smooth character (v015): never swap whole body or head images. Poses are edits of ONE master, arms move through
  in-between frames, only the mouth patch changes on words. No eyes-to-chin face patches (they read as a face inside
  the face); every frame's cutout edge is cleaned by `mascot/anim/tools/edges.py`.
- Ultra smooth (v013): one character for the whole reel, poses held >= 1.5 s with 0.4 s dissolves, no sound on
  character movements (the swish annoyed the user), render at 60 fps.

## Tools (not in the repo, install in a new session)
- Render toolkit lemo-opuscar: clone https://github.com/lemomo-ai/lemo-opuscar to
  `/home/user/lemomo-ai/lemo-opuscar`, `npm install`, a `.venv` from `requirements.txt`.
  For 4K, its `core/render/page.mjs` needs `deviceScaleFactor: +process.env.LEMO_DSF || 1`
  (see `video/README.md`, Rebuild).
- Character animation build: `pip install torch --index-url https://download.pytorch.org/whl/cpu`, `opencv-python-headless`,
  and the FILM model in `/home/user/models/` (commands in `mascot/anim/README.md`).
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
