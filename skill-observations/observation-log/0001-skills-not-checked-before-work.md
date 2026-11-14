---
id: 1
title: "Installed skills never checked before a long multi-step media task"
status: open
type: open-source
skill: []
proposes_skill: []
target_file: [CLAUDE.md]
siblings_checked: "none — no skill family registry exists in this workspace; target is the project instructions file"
area: "session start / tool selection"
date: 2026-11-14
session_context: "Mascot asset library and founder reel v012-v013 (video/README.md, v012 and v013 sections)"
parked_until:
resolved:
resolution:
reference: CLAUDE.md
commands_verified: none
next_actor: review
---

**Issue:** Across a whole session (asset generation, compositing, two video renders) the agent never looked at the
user's 100+ installed skills. Skills that fitted the work (task-observer at session start, video-export-qa after each
render, animate/choreograph for motion, video-pipeline-doctor for a new container, media-use for cutouts) were not
loaded; the agent hand-built equivalents. The first reel came out choppy, a second render was needed, and the user's
credits ran out. The user only learned this by asking which skills were used.

**Suggested improvement:** Done as ordinary work: CLAUDE.md now opens with "Rule 1": list skills, plugins,
connectors, then MCP tools before any work and before each new kind of task, and report which were used. If this is
broken again, the fix must be structural (a SessionStart hook that prints the matching skills), not more text.

**Principle:** Installed skills are inert unless the agent checks them at the start of each task type; a project
instruction that forces that check, and a report of what was used, makes the omission visible.
