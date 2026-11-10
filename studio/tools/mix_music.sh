#!/bin/bash
# usage: mix_music.sh <in.mp4> <music.mp3> <out.mp4>
set -e
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$1"); FO=$(python3 -c "print(round($D-5,2))")
ffmpeg -y -loglevel error -i "$1" -stream_loop -1 -i "$2" -filter_complex "[1:a]atrim=0:$D,asetpts=PTS-STARTPTS,loudnorm=I=-27:TP=-6,equalizer=f=1800:width_type=o:w=1.6:g=-6,afade=t=in:d=2,afade=t=out:st=$FO:d=5,aformat=channel_layouts=stereo[m];[0:a]asplit=2[v][sc];[m][sc]sidechaincompress=threshold=0.02:ratio=6:attack=30:release=500:makeup=1[md];[v][md]amix=inputs=2:normalize=0:duration=first,loudnorm=I=-14:TP=-1.5:LRA=11[a]" -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -ar 48000 -movflags +faststart "$3"
