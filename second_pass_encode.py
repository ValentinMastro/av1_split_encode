#!/usr/bin/env python3

import concurrent.futures
import os

def single_threaded_job(args):
	split, data = args

	command = split.get_second_pass_command(data, 2)
	os.system(command)
	os.remove(split.split_source_file)

def encode_audio(data):
	command = [data.ffmpeg, '-loglevel', 'quiet',
				'-i', data.source_file,
				'-vn', '-c:a', 'libopus', '-b:a', '196k',
				data.opus_path]

	os.system(" ".join(command))


def second_pass_only(data, split):
	""" Used when we only want to encode one split """
	command = split.get_second_pass_command(data, 12)
	os.system(command)
	os.remove(split.split_source_file)


def second_pass_in_parallel(data, begin_mega_split, end_mega_split, audio):
	""" Goal is to encode splits file in parallel, using as many threads as possible """

	first_split_index = [s.start_frame for s in data.splits].index(begin_mega_split)
	last_split_index = [s.end_frame for s in data.splits].index(end_mega_split)

	splits_to_encode = data.splits[first_split_index:last_split_index+1]
	splits_to_reorder = splits_to_encode.copy()

	splits_to_reorder.sort(reverse = True, key = lambda s : s.end_frame - s.start_frame)

	with concurrent.futures.ThreadPoolExecutor(max_workers = data.number_of_threads) as pool:
		for split in splits_to_reorder:
			pool.submit(single_threaded_job, [split, data])

		if (audio):
			pool.submit(encode_audio, data)