#!/usr/bin/env python3

from src.splits import Trim_split, Vapoursynth_split


def select_split_class(parameters, index, begin, end):
	if (parameters.splitting_method == "ffmpeg_trim"):
		return Trim_split(parameters, index, begin, end)
	elif (parameters.splitting_method == "Vapoursynth"):
		return Vapoursynth_split(parameters, index, begin, end)
	elif (parameters.splitting_method == "MagicYUV"):
		pass

def create_splits_from_keyframes(parameters, keyframes):
	splits = []
	for index in range(len(keyframes)-1):
		begin, end = keyframes[index], keyframes[index+1]
		splits.append(select_split_class(parameters, index, begin, end))

	return splits
