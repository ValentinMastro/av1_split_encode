#!/usr/bin/env python3

import concurrent.futures
import os

def single_threaded_job(args):
	split, data = args
	
	command = split.get_second_pass_command(data)
	os.system(command)
	os.remove(split.split_source_file)

def second_pass_in_parallel(data, begin_mega_split, end_mega_split):
	""" Goal is to encode splits file in parallel, using as many threads as possible """

	first_split_index = [s.start_frame for s in data.splits].index(begin_mega_split)
	last_split_index = [s.end_frame for s in data.splits].index(end_mega_split)

	splits_to_encode = data.splits[first_split_index:last_split_index+1]

	with concurrent.futures.ThreadPoolExecutor(max_workers = data.number_of_threads) as pool:
		for split in splits_to_encode:
			pool.submit(single_threaded_job, [split, data])
