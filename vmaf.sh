#!/usr/bin/bash

if [ "$#" == 3 ]
then
	THREADS=1
	QUIET="-loglevel quiet"
elif [ "$#" == 4 ]
then
	THREADS="$4"
	QUIET=""
else
	echo "Wrong number of arguments"
	echo "Usage: bash vmaf.sh REF TEST JSON_PATH [THREADS=1]"
	exit 1
fi

echo "Number of threads used : $THREADS"
echo "Computing VMAF..."


REFERENCE="$1"
TEST="$2"
JSON="$3"

FFMPEG="./ffmpeg_build/bin/ffmpeg"


DECODER="-c:v libdav1d -framethreads $THREADS"

FILTERS="[0:v]setpts=PTS-STARTPTS[ref];[1:v]setpts=PTS-STARTPTS[test];[test][ref]libvmaf=psnr=1:ssim=1:n_threads=$THREADS:log_fmt=json:log_path=$JSON:model_path=./ffmpeg_build/share/model/vmaf_v0.6.1.json"

"$FFMPEG" -y $QUIET -r 24000/1001 -i "$REFERENCE" $DECODER -r 24000/1001 -i "$TEST" -filter_complex "$FILTERS" -f null - 
