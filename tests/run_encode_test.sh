#!/usr/bin/bash

if [ $# -eq 0 ]
then 
	MAX=5
else 
	MAX="$1"
fi

rm -rf encoded
mkdir -p encoded
N=0
FFMPEG="$PWD/../ffmpeg_build/bin/ffmpeg"

for file in sources/*
do
	N=$(($N+1))
	python ../start_encode.py "$PWD/$file" "encoded/$N.mkv" -q 48 --threads_per_split 1 --cpu_use 9 --clean_at_the_end --split_method 'Vapoursynth'

	if [ $N -eq $MAX ]
	then 
		exit 0
	fi
done
