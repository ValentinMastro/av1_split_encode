#!/usr/bin/env python3

import os

def concatenate(data):
	""" Use mkvmerge to concatenate the video and mux the audio stream in a
	single mkv file. It uses the following syntax :

	mkvmerge -q -o $OUTPUT_FILE$ $VIDEO_SPLIT_00001$ + ... + $LAST_VIDEO_SPLIT $AUDIO_SPLIT$
	"""

	list_of_video_splits = [s.tmp_ivf_2_pass_path for s in data.splits]

	if (data.no_audio):
		audio_stream = []
	else:
		audio_stream = [data.opus_path]

	number_of_splits = len(list_of_video_splits)

	""" It seems mkvmerge only accepts 1024 arguments at a time, so
	intermediate concatenated files are created to cover the issue. """

	# If there are fewer than 1000 splits, do like before : concat them immediatly
	if (number_of_splits <= 1000):
		start_of_the_command = [data.mkvmerge, '-q', '-o', data.destination_file]
		strings = [" ".join(start_of_the_command), " + ".join(list_of_video_splits), " ".join(audio_stream)]
		command = " ".join(strings)

		os.system(command)
	else:
		number_of_intermediate_concatenation = (number_of_splits // 1000) + 1

		for i in range(number_of_intermediate_concatenation):
			starting_split_number = i * 1000 + 1
			ending_split_number = min( (i+1) * 1000, number_of_splits)

			intermediate_splits = list_of_video_splits[(starting_split_number - 1):(ending_split_number - 1 + 1)]
			start_of_the_command = [data.mkvmerge, '-q', '-o', "/tmp/av1_split_encode/inter{}.ivf".format(i+1)]
			strings = [" ".join(start_of_the_command), " + ".join(intermediate_splits)]
			command = " ".join(strings)

			os.system(command)

		start_of_the_command = [data.mkvmerge, '-q', '-o', data.destination_file]
		strings = [" ".join(start_of_the_command),
				" + ".join(["/tmp/av1_split_encode/inter{}.ivf".format(i+1) for i in range(number_of_intermediate_concatenation)]),
				" ".join(audio_stream)]

		command = " ".join(strings)
		print(command)
		os.system(command)
