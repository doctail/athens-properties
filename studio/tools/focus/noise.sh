#!/usr/bin/env bash
# Focus Flow Lab — long "noise + black screen" video, rendered locally with ffmpeg. Zero credits.
#
# Usage: noise.sh <color> <hours> <out.mp4> [lowpass_hz] [lufs]
#   color      brown | pink | white
#   hours      e.g. 10, 12 (decimals allowed: 0.01 = 36 s for a test)
#   lowpass_hz optional, e.g. 150 for "super deep" brown noise (default: none)
#   lufs       target loudness, default -23 (calm, no clipping; YouTube normalises to -14 anyway)
#
# Output: 1920x1080 black video at 1 fps (tiny file, YouTube accepts it), AAC 48 kHz stereo,
# 5 s fade-in so the first second does not "pop". The noise is generated for the full length,
# never looped, so there is no audible seam.
set -euo pipefail
color=${1:?color: brown|pink|white}; hours=${2:?hours}; out=${3:?out.mp4}
lp=${4:-}; lufs=${5:--23}
secs=$(python3 -c "print(int(round(float('$hours')*3600)))")
af="afade=t=in:d=5"
[ -n "$lp" ] && af="lowpass=f=${lp},lowpass=f=${lp},${af}"
# Two independent noise sources -> slightly decorrelated stereo, feels wider than mono.
ffmpeg -hide_banner -loglevel error -y \
  -f lavfi -i "color=c=black:s=1920x1080:r=1" \
  -f lavfi -i "anoisesrc=color=${color}:amplitude=0.6:sample_rate=48000:seed=11" \
  -f lavfi -i "anoisesrc=color=${color}:amplitude=0.6:sample_rate=48000:seed=29" \
  -filter_complex "[1:a][2:a]amerge=inputs=2,${af},loudnorm=I=${lufs}:TP=-3:LRA=7[a]" \
  -map 0:v -map "[a]" -t "$secs" \
  -c:v libx264 -preset veryfast -tune stillimage -crf 30 -pix_fmt yuv420p \
  -c:a aac -b:a 160k -ar 48000 -movflags +faststart "$out"
echo "ok: $out ($(du -h "$out" | cut -f1), ${secs}s, ${color}${lp:+ lowpass ${lp}Hz})"
