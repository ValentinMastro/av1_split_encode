#!/usr/bin/env python3

import os

def concatenate(data):
	""" Use mkvmerge to concatenate the video and mux the audio stream in a
	single mkv file. It uses the following syntax :

	mkvmerge -q -o $OUTPUT_FILE$ $VIDEO_SPLIT_00001$ + ... + $LAST_VIDEO_SPLIT $AUDIO_SPLIT$
	"""

	start_of_the_command = [data.mkvmerge, '-q', '-o', data.destination_file]
	list_of_video_splits = [s.tmp_ivf_2_pass_path for s in data.splits]
	audio_stream = [data.opus_path]

	strings = [" ".join(start_of_the_command), " + ".join(list_of_video_splits), " ".join(audio_stream)]
	command = " ".join(strings)

	os.system(command)
