#!/usr/bin/env bash
# Build ad 01 end to end, after the voiceover takes are in vo/raw (made with tts_gemini.py on the "AI Tools"
# environment, which holds the Gemini key). Same character pipeline as the founder reel (mascot/anim/README.md):
#   voice -> word times -> lip-sync motion -> director (acting.json) -> head frames -> page render -> mix -> mux.
# Usage: bash make.sh [--test 8]      (--test N renders the head frames only up to N seconds, for a cheap check)
set -euo pipefail
cd "$(dirname "$0")"
AD=$(pwd); REPO=$(cd ../.. && pwd); T=$REPO/mascot/anim/tools
LIB=/home/user/lemomo-ai/lemo-opuscar
export PLAYWRIGHT_CHROME=${PLAYWRIGHT_CHROME:-/opt/pw-browsers/chromium_headless_shell-1243/chrome-headless-shell-linux64/chrome-headless-shell}
export REEL_DIR=$AD ANIM_TAG=ad01
UPTO=(); [ "${1:-}" = "--test" ] && UPTO=(--upto "$2")

$LIB/.venv/bin/python fix_vo.py                       # vo/raw -> vo/*.wav, vo/dur.json (SPEED=1.06 for a faster read)
rm -f phonemes.json; python3 build_timeline.py         # first pass: line times
python3 $T/align.py                                    # real word times -> phonemes.json
python3 build_timeline.py                              # second pass: captions on the real word times
python3 $T/audio_motion.py                             # lip-sync motion -> mascot/anim/out/speech_ad01/motion.npz
python3 $T/director.py "$AD" | tee director.log        # acting.json (read the log)
for k in 0 1; do LP_THREADS=2 python3 $T/build_face.py --part $k 2 "${UPTO[@]}" & done; wait
python3 $T/build_face.py --finish "${UPTO[@]}"
rm -rf assets/anim/head; cp -r $REPO/mascot/anim/out/head_ad01 assets/anim/head
cp $REPO/mascot/anim/out/face_ad01.json assets/anim/face.json
cp $REPO/mascot/anim/out/anim.json assets/anim/anim.json
node $LIB/core/render/events.mjs . --size 1080x1920
$LIB/.venv/bin/python mix.py
