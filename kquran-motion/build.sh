#!/usr/bin/env bash
# Rebuilds kquran_promo.mp4 from scene.html + audio.py.
set -euo pipefail
cd "$(dirname "$0")"
WORK="${WORK:-$(mktemp -d)}"
NODE_PATH="${NODE_PATH:-$(npm root -g)}" node render.js "$WORK/frames" 30
python3 audio.py "$WORK/audio.wav"
ffmpeg -y -loglevel error -framerate 30 -i "$WORK/frames/f_%04d.png" -i "$WORK/audio.wav" \
  -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -movflags +faststart \
  -c:a aac -b:a 192k -shortest kquran_promo.mp4
echo "built kquran_promo.mp4"
