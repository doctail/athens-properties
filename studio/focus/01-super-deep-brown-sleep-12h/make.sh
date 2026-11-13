#!/usr/bin/env bash
# Focus Flow Lab — video 01. Run from the repo root:  bash studio/focus/01-super-deep-brown-sleep-12h/make.sh
# Output: video.mp4 (12 h, ~0.8 GB, not committed: too big for git) next to this file. ~75 min of CPU.
set -euo pipefail
here="$(cd "$(dirname "$0")" && pwd)"
bash "$here/../../tools/focus/noise.sh" brown 12 "$here/video.mp4" 150
