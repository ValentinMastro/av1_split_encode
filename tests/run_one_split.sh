#!/usr/bin/bash

cd .. 

mkdir -p "/tmp/av1_split_encode"
LOG="/tmp/av1_split_encode/keyframes.log"

FFMPEG="ffmpeg_build/bin/ffmpeg"
AOMENC="ffmpeg_build/bin/aomenc"

TEST="$PWD/tests/sources/Arslan10bit.mkv"
RES="$PWD/tests/encoded/a.mkv"

# Run first pass
if [ ! -f "$LOG" ]
then
"$FFMPEG" -loglevel quiet -i "$TEST" -map 0:v -vf 'setpts=PTS-STARTPTS' -f yuv4mpegpipe -pix_fmt yuv420p - | aomenc -t 24 --pass=1 --passes=2 --auto-alt-ref=1 --lag-in-frames=35 --end-usage=q --cq-level=22 --bit-depth=10 --fpf="$LOG" -o /dev/null -
fi


SPLIT=32
NUMBER=`printf "%05d" "$SPLIT"`
IVF="test_$SPLIT.ivf"

if [ ! -f "/tmp/av1_split_encode/splits_ivf/$NUMBER.ivf" ]
then
python start_encode.py "$TEST" "$RES" -t 12 --split_number_only "$SPLIT"
fi

python second_pass_encode_vapoursynth.py "$TEST" "$SPLIT" "$IVF"