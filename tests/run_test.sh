#!/usr/bin/bash

rm -rf encoded
mkdir -p encoded
N=0
FFMPEG="$PWD/../ffmpeg_build/bin/ffmpeg"

for file in sources/*
do
	N=$(($N+1))
	python ../split.py "$file" "encoded/$N.mkv" -q 48 --threads_per_split 1 --cpu_use 9 --clean_at_the_end 
	"$FFMPEG" 
done