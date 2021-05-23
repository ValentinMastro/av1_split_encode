#!/usr/bin/bash

if [ "$#" -ne 3 ]
then
	echo "Wrong number of arguments"
	echo "Usage: bash vmaf.sh REF TEST JSON_PATH"
	exit 1
fi

REFERENCE="$1"
TEST="$2"
JSON="$3"

FFMPEG="./ffmpeg_build/bin/ffmpeg"

QUIET="-y -loglevel quiet"
DECODER="-c:v libdav1d -framethreads 1"

FILTERS="[0:v]setpts=PTS-STARTPTS[ref];[1:v]setpts=PTS-STARTPTS[test];[test][ref]libvmaf=psnr=1:ssim=1:n_threads=1:log_fmt=json:log_path=$JSON:model_path=./ffmpeg_build/share/model/vmaf_v0.6.1.json"

"$FFMPEG" $QUIET -r 24000/1001 -i "$REFERENCE" $DECODER -r 24000/1001 -i "$TEST" -filter_complex "$FILTERS" -f null - 
