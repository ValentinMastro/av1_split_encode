#!/usr/bin/env python3

from os import system
from os.path import join
from src.encoding_jobs import Aomenc_job, Audio_job

def concatenate_temp_files(parameters, jobs):
	video = [job for job in jobs if isinstance(job, Aomenc_job)]
	video.sort(key = lambda j : j.split.split_number)
	audio = [job for job in jobs if isinstance(job, Audio_job)]

	number_of_splits = len(video)
	mkvmerge = " ".join([parameters.mkvmerge, '-q', '-o', parameters.output_file, '>', '/dev/null'])
	audio = " ".join([parameters.temp_audio])

	if (number_of_splits <= 1000):
		video_concat = " + ".join([j.second_pass_ivf_file for j in video])

	else:
		number_of_intermediate = (number_of_splits // 1000) + 1
		for i in range(number_of_intermediate):
			starts_with = i * 1000
			ends_with = min((i+1) * 1000 - 1, number_of_splits - 1) #inclusive

			intermediate_videos = video[starts_with:(ends_with+1)]
			intermediate_videos_concat = " + ".join(intermediate_videos.second_pass_ivf_file)
			intermediate_name = join(parameters.temp_folder, f"inter{i:02d}.ivf")

			inter_command = " ".join([parameters.mkvmerge, '-q', '-o', intermediate_name])
			os.system(" ".join([inter_command, intermediate_videos_concat]))

		video_concat = " + ".join([f"inter{i:02d}" for i in range(number_of_intermediate)])

	system(" ".join([mkvmerge, video_concat, audio, "2> /dev/null"]))
