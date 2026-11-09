#!/bin/sh
# Turn the LeapTalk talking-head clips into the 30 fps frame sequences the reel draws in its panels,
# and the portrait stills used where a scene has no clip yet. Writes talk/<scene>/ and talk/manifest.json.
# usage: sh talk_frames.sh   (run from video/outputdm-reel)
set -e
CLIPS=../motion/clips
PORTRAIT=../../mascot/office-v1/portrait
# scene:clip:size  (clip = file in $CLIPS without .mp4, or "-" for none yet)
for spec in hook:lt_hook:640 intro:test_leaptalk_l02:800 since:lt_since:640 leaks:lt_leaks:600 \
            system:lt_l06:600 only:lt_l07:620 cta:lt_cta:600; do
  sc=${spec%%:*}; rest=${spec#*:}; clip=${rest%%:*}; size=${rest#*:}
  mkdir -p talk/$sc; rm -f talk/$sc/f_*.jpg
  if [ -f "$CLIPS/$clip.mp4" ]; then
    ffmpeg -v error -y -i "$CLIPS/$clip.mp4" -vf "fps=30,scale=$size:$size:flags=lanczos,unsharp=5:5:0.5" -q:v 3 talk/$sc/f_%04d.jpg
  fi
done
# stills for scenes still waiting for a clip
ffmpeg -v error -y -i $PORTRAIT/p04_serious.png -vf scale=640:640:flags=lanczos -q:v 3 talk/hook/still.jpg
ffmpeg -v error -y -i $PORTRAIT/p05_smile.png   -vf scale=640:640:flags=lanczos -q:v 3 talk/since/still.jpg
ffmpeg -v error -y -i $PORTRAIT/p02_side.png    -vf scale=600:600:flags=lanczos -q:v 3 talk/leaks/still.jpg
ffmpeg -v error -y -i $PORTRAIT/p05_smile.png   -vf scale=600:600:flags=lanczos -q:v 3 talk/cta/still.jpg
python3 - <<'EOF'
import json, os
m = {s: {"frames": len([f for f in os.listdir(f"talk/{s}") if f.startswith("f_")])}
     for s in ["hook", "intro", "since", "leaks", "system", "only", "cta"]}
json.dump(m, open("talk/manifest.json", "w"), indent=1); print(m)
EOF
