#!/usr/bin/env python3

import os
import struct

def generate_first_pass_log_for_each_split(data, list_of_frame_dicts):
	""" For each split, the first pass log file is generated """

	keys = list_of_frame_dicts[-1].keys()

	for split in data.splits:
		begin = split.start_frame
		end = split.end_frame
		length = end - begin

		split_first_pass_stats = list_of_frame_dicts[begin:end]

		# Reset index
		for (i, frame_dict) in enumerate(split_first_pass_stats):
			frame_dict["frame"] = i

		# Computing end of sequence stats
		end_of_sequence = {}
		for key in keys:
			end_of_sequence[key] = sum([frame[key] for frame in split_first_pass_stats])

		# Write in the new logfile
		data_to_write_in_log_file = split_first_pass_stats + [end_of_sequence]
		with open(split.tmp_first_pass_path, 'wb') as log_file:
			for struct_data_unpacked in data_to_write_in_log_file:
				struct_data_packed = struct.pack('26d', *struct_data_unpacked.values())
				log_file.write(struct_data_packed)
