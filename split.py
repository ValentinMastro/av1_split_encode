#!/usr/bin/env python3

import argparse
import os
from json import load
from platform import system

from first_pass_keyframes import create_splits_from_first_pass_keyframes
from first_pass_logfile import generate_first_pass_log_for_each_split
from cut_source_in_splits import generate_source_splits
from second_pass_encode import second_pass_in_parallel, second_pass_only
from concatenation_mkvmerge import concatenate


class Encoding_data:
	def __init__(self, arguments):
		# Binary file path
		self.ffmpeg = arguments.ffmpeg
		self.ffprobe = arguments.ffprobe
		self.aomenc = arguments.aomenc
		self.mkvmerge = arguments.mkvmerge

		# IO
		self.source_file = arguments.source_file
		self.destination_file = arguments.destination_file

		self.temp_folder = "/tmp/av1_split_encode/"
		os.system("mkdir -p {}".format(self.temp_folder))
		self.first_pass_log_file = "{}keyframes.log".format(self.temp_folder)
		self.concat_only = arguments.concat_only

		# Encoding parameters
		self.q = arguments.q
		self.total_number_of_frames = self.get_total_number_of_frames()
		self.cpu_use = arguments.cpu_use

		# Splitting parameters
		self.keyframes = []
		self.splits = []
		self.split_number_only = arguments.split_number_only
		self.frame_limit = arguments.frame_limit

		# Computer parameters
		self.number_of_threads = arguments.t

		# Audio parameters
		self.opus_path = self.temp_folder + "audio.opus"

	def get_total_number_of_frames(self):
		json_file_path = "{}pts.json".format(self.temp_folder)

		if (not os.path.isfile(json_file_path)):	# If json file does not exists
			command = "{}".format(self.ffmpeg) + " -loglevel quiet -i {} -map 0:v ".format(self.source_file) + \
				"-vf 'setpts=PTS-STARTPTS' -f yuv4mpegpipe -pix_fmt yuv420p - | " + \
				"{} ".format(self.ffprobe) + "-loglevel quiet -i - -show_frames -of json " + \
				"> {}".format(json_file_path)
			os.system(command)

		with open(json_file_path, 'rt') as json_file_data:
			json_dict = load(json_file_data)
			return len(json_dict["frames"])


def parse_arguments(gui = False):
	"""
	Configure and parse all arguments of the commande line interface (CLI)
	Output : args
	"""

	parser = argparse.ArgumentParser(description = "Transcode video file by " +
								"splitting it in RAM and encoding in parallel")
	parser.add_argument('source_file', type = str)
	parser.add_argument('destination_file', type = str)
	parser.add_argument('-q', type = int, default = 34,
					        help = "Anime 24 / Live action 34")
	parser.add_argument('-t', type = int, default = 11,
							help = "Number of threads")
	parser.add_argument('--cpu_use', type = int, default = 4,
							help = "Most optimized 4 and 6")
	parser.add_argument('--frame_limit', type = int, default = 20000)
	parser.add_argument('--split_number_only', type = int, default = 0)
	parser.add_argument('--concat_only', action = "store_true")
	parser.add_argument('--threads_per_split', type = int, default = 2)
	parser.add_argument('--ffmpeg', type = str, default = "ffmpeg")
	parser.add_argument('--aomenc', type = str, default = "aomenc")
	parser.add_argument('--ffprobe', type = str, default = "ffprobe")
	parser.add_argument('--mkvmerge', type = str, default = "mkvmerge")

	if (gui):
		return parser
	else:
		return parser.parse_args()


def first_pass(data):
	""" Generate first pass log file of the entire source file """

	if (not os.path.isfile(data.first_pass_log_file)):
		first_pass_pipe = "{} -loglevel quiet -i {} -map 0:v -vf 'setpts=PTS-STARTPTS' ".format(data.ffmpeg, data.source_file) + \
						  "-f yuv4mpegpipe -pix_fmt yuv420p -"
		first_pass_aomenc = "{} -t {} --pass=1 --passes=2 ".format(data.aomenc, data.number_of_threads) + \
						  "--auto-alt-ref=1 --lag-in-frames=35 --end-usage=q --cq-level=22 --bit-depth=10 " + \
						  "--fpf={} -o {} -".format(data.first_pass_log_file, data.destination_file)

		first_pass_command = first_pass_pipe + " | " + first_pass_aomenc
		os.system(first_pass_command)


def generate_keyframes_of_mega_splits(keyframes, frame_limit):
	""" We select keyframes that will delimit those 'mega splits' """
	cumulated_number_of_frames = 0
	mega_keyframes = []

	for index in range(len(keyframes)):
		if (index == 0):
			mega_keyframes.append(keyframes[index])
		elif (index == len(keyframes) - 1):
			mega_keyframes.append(keyframes[index])
		else:
			keyframe = keyframes[index]
			previous_keyframe = keyframes[index - 1]

			if (cumulated_number_of_frames + (keyframe - previous_keyframe) > frame_limit):
				mega_keyframes.append(previous_keyframe)
				cumulated_number_of_frames = 0

			cumulated_number_of_frames += keyframe - previous_keyframe

	return mega_keyframes


def main_encoding(data):
	first_pass(data)
	list_of_frame_dicts = create_splits_from_first_pass_keyframes(data)
	generate_first_pass_log_for_each_split(data, list_of_frame_dicts)

	if (data.split_number_only != 0):
		split = data.splits[data.split_number_only - 1]
		generate_source_splits(data, split.start_frame, split.end_frame)
		second_pass_only(data, split)
		exit(0)

	if (not data.concat_only):
		""" We want to write the splits of the source file directly in the RAM.
		However there probably won't be enough space in the RAM disk.
		Therefore we create 'mega splits' which will be processed one at a time """
		mega_keyframes = generate_keyframes_of_mega_splits(data.keyframes, frame_limit = data.frame_limit)

		for i in range(len(mega_keyframes) - 1):
			begin_mega_split = mega_keyframes[i]
			end_mega_split = mega_keyframes[i+1]

			generate_source_splits(data, begin_mega_split, end_mega_split)
			second_pass_in_parallel(data, begin_mega_split, end_mega_split, audio = (i == 0))

	# Concatenetion using mkvmerge
	concatenate(data)

if __name__ == '__main__':
	arguments = parse_arguments()
	data = Encoding_data(arguments)
	main_encoding(data)
