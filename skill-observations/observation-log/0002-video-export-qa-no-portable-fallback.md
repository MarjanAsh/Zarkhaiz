---
id: 2
title: "video-export-qa hard-wires a local Mac toolchain and cannot run in a cloud container"
status: open
type: open-source
skill: [video-export-qa]
proposes_skill: []
target_file: []
siblings_checked: "no family registry; video-pipeline-doctor, video-transcribe, video-edit read the same toolchain.env — assumed same issue, not checked"
area: "section 1, Automated pass"
date: 2026-11-14
session_context: "QA of the founder reel v013/v014 (video/outputdm-reel/qa/v014/qa.md)"
parked_until:
resolved:
resolution:
reference: video/outputdm-reel/qa/v014/qa.md
commands_verified: "ls /Users/zarkhaiz/.video-pipeline — run, No such file or directory"
next_actor: review
---

**Issue:** The skill's only automated path is `source /Users/<user>/.video-pipeline/toolchain.env` + `vp-py qa_check.py`.
In a cloud container neither exists, so the agent had to re-create every check by hand with ffmpeg; the skill gives
no fallback.

**Suggested improvement:** Add a "No toolchain" fallback block to section 1 with the plain ffmpeg/ffprobe commands
for each check (probe, decode, blackdetect, freezedetect, ebur128 with true peak, silencedetect, A/V duration), or
ship `qa_check.py` inside the skill's own `scripts/`.

**Principle:** A skill whose core step depends on one machine's install path must carry a portable fallback, or it
silently stops working everywhere else.
