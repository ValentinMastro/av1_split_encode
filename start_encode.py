#!/usr/bin/env python3

import argparse
import os
from json import load, dump
from fs.osfs import OSFS
from os import cpu_count
from time import time

from first_pass_keyframes import create_splits_from_first_pass_keyframes
from first_pass_logfile import generate_first_pass_log_for_each_split
from generate_splits_from_source import generate_magicyuv_source_splits
from second_pass_encode import second_pass_in_parallel, second_pass_only, encode_audio
from concatenation_mkvmerge import concatenate


class Time_Measuring_Data:
	""" A simple data class that aims to compute how fast we encode """

	def __init__(self):
		self.fp = [0, 0]		# First pass timers
		self.sp = [0, 0]		# Second pass timers
		self.n = 0				# total number of frames

	def begin_of_first_pass(self):
		self.fp[0] = time()

	def end_of_first_pass(self):
		self.fp[1] = time()

	def begin_of_second_pass(self):
		self.sp[0] = time()

	def end_of_second_pass(self):
		self.sp[1] = time()

	def __repr__(self):
		return f"First pass : {self.n / (self.fp[1] - self.fp[0]):2.2f} fps\n" + \
			f"Second pass : {self.n / (self.sp[1] - self.sp[0]):2.2f} fps\n" + \
			f"Total time : {self.sp[1] - self.fp[0]} s\n"

class Encoding_data:
	def __init__(self, arguments):
		# Binary file path
		self.ffmpeg = arguments.ffmpeg
		self.aomenc = arguments.aomenc
		self.mkvmerge = arguments.mkvmerge

		# IO
		self.source_file = arguments.source_file
		self.destination_file = arguments.destination_file
		self.initialize_filesystem()
		self.audio_only = arguments.audio_only
		self.no_audio = arguments.no_audio
		self.clean_at_the_end = arguments.clean_at_the_end

		# Splitting method
		self.split_method = arguments.split_method

		# Encoding parameters
		self.q = arguments.q
		self.total_number_of_frames = 0
		self.cpu_use = arguments.cpu_use

		# Filters and interlacing
		self.initialize_filters_on_source(arguments)

		# Splitting parameters
		self.concat_only = arguments.concat_only
		self.keyframes = []
		self.splits = []
		self.split_number_only = arguments.split_number_only
		self.frame_limit = arguments.frame_limit

		# Computer parameters
		self.number_of_threads = arguments.t
		self.threads_per_split = arguments.threads_per_split

		# Time measuring
		self.timer = Time_Measuring_Data()


	def initialize_filesystem(self):
		self.tmp = OSFS("/tmp")
		self.temp_dir = self.tmp.makedir("av1_split_encode", recreate = True)

		# Creating subdirectories
		self.temp_dir.makedir("splits_ivf", recreate = True)
		self.temp_dir.makedir("splits_log", recreate = True)
		self.temp_dir.makedir("splits_source", recreate = True)
		self.temp_dir.makedir("splits_json", recreate = True)

		# Creating empty files
		self.temp_dir.create("keyframes.log", wipe = False)
		self.temp_dir.create("audio.opus", wipe = False)
		self.temp_dir.create("splits.json", wipe = False)
		self.temp_dir.create("script.vpy", wipe = False)

		self.first_pass_log_file_path = self.temp_dir.getsyspath("keyframes.log")
		self.opus_path = self.temp_dir.getsyspath("audio.opus")
		self.splits_json = self.temp_dir.getsyspath("splits.json")
		self.vp_script_path = self.temp_dir.getsyspath("script.vpy")

		# generate vapoursynth script
		with open(self.vp_script_path, "w") as vp_script:
			vp_script.write("from vapoursynth import core\n")
			vp_script.write(f"video = core.ffms2.Source(source='{self.source_file}')\n")
			vp_script.write("video.set_output()\n")


	def get_total_number_of_frames(self):
		""" Uses the file size of keyframes.log to compute the total number
		of frames """

		log_size = self.temp_dir.getsize("keyframes.log")
		self.total_number_of_frames = (log_size // 232) - 1
		self.timer.n = (log_size // 232) - 1

	def initialize_filters_on_source(self, arguments):
		self.filters = []

		self.interlaced = arguments.interlaced
		self.has_to_be_cropped = not (arguments.crop is None)

		if (self.interlaced):
			self.filters.append("yadif")

		if (self.has_to_be_cropped):
			w, h, x, y = arguments.crop
			self.filters.append(f"crop={w}:{h}:{x}:{y}")

		self.filters.append("setpts=PTS-STARTPTS")

	def close(self):
		self.temp_dir.close()

		if (self.clean_at_the_end):
			self.tmp.removetree("av1_split_encode")

		self.tmp.close()


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
	parser.add_argument('-t', type = int, default = cpu_count(),
							help = "Number of threads")
	parser.add_argument('--cpu_use', type = int, default = 4,
							help = "Most optimized 4 and 6")
	parser.add_argument('--frame_limit', type = int, default = 20000)
	parser.add_argument('--split_number_only', type = int, default = 0)
	parser.add_argument('--concat_only', action = "store_true")
	parser.add_argument('--audio_only', action = "store_true")
	parser.add_argument('--no_audio', action = "store_true")
	parser.add_argument('--clean_at_the_end', action = "store_true")
	parser.add_argument('--threads_per_split', type = int, default = 2)
	parser.add_argument('--interlaced', action = "store_true")
	parser.add_argument('--crop', type = int, nargs = 4)
	parser.add_argument('--split_method', choices = ['RAM_magicyuv', 'Vapoursynth'], default = 'RAM_magicyuv')
	parser.add_argument('--ffmpeg', type = str, default = "ffmpeg")
	parser.add_argument('--aomenc', type = str, default = "aomenc")
	parser.add_argument('--mkvmerge', type = str, default = "mkvmerge")

	if (gui):
		return parser
	else:
		return parser.parse_args()


def first_pass(data):
	""" Generate first pass log file of the entire source file """

	data.timer.begin_of_first_pass()

	if (data.temp_dir.getsize("keyframes.log") == 0):
		filters = ",".join(data.filters)
		first_pass_pipe = "{} -loglevel quiet -i {} -map 0:v -vf '{}' ".format(data.ffmpeg, data.source_file, filters) + \
						  "-f yuv4mpegpipe -pix_fmt yuv420p -"
		first_pass_aomenc = "{} -t {} --pass=1 --passes=2 ".format(data.aomenc, data.number_of_threads) + \
						  "--auto-alt-ref=1 --lag-in-frames=35 --end-usage=q --cq-level=22 --bit-depth=10 " + \
						  "--fpf={} -o {} -".format(data.first_pass_log_file_path, data.destination_file)

		first_pass_command = first_pass_pipe + " | " + first_pass_aomenc
		os.system(first_pass_command)

	data.timer.end_of_first_pass()
	data.get_total_number_of_frames()


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


def save_splits_data(data):
	""" Write all splits data in a json file """
	splits_data = {'splits': [split.get_dict() for split in data.splits]}

	with open(data.splits_json, 'wt') as file:
		dump(splits_data, file)


def main_encoding(data):
	""" Main encoding process

	-> Fist pass
	-> Generation of splits using keyframes detected with first pass

	-> Writing of source splits in RAM
	-> Second pass in parallel 	(with audio)

	-> Concatenation with mkvmerge
	"""

	# FIRST PASS
	first_pass(data)

	# GENERATION OF SPLITS
	list_of_frame_dicts = create_splits_from_first_pass_keyframes(data)
	generate_first_pass_log_for_each_split(data, list_of_frame_dicts)
	save_splits_data(data)

	if (data.split_number_only != 0):
		split = data.splits[data.split_number_only - 1]
		generate_magicyuv_source_splits(data, split.start_frame, split.end_frame)
		second_pass_only(data, split)
		return


	data.timer.begin_of_second_pass()

	if (data.split_method == 'RAM_magicyuv'):
		""" We want to write the splits of the source file directly in the RAM.
		However there probably won't be enough space in the RAM disk.
		Therefore we create 'mega splits' which will be processed one at a time """

		mega_keyframes = generate_keyframes_of_mega_splits(data.keyframes, frame_limit = data.frame_limit)

		for i in range(len(mega_keyframes) - 1):
			begin_mega_split = mega_keyframes[i]
			end_mega_split = mega_keyframes[i+1]

			# WRITING SOURCE SPLITS IN RAM
			generate_magicyuv_source_splits(data, begin_mega_split, end_mega_split)
			# SECOND PASS IN PARALLEL
			second_pass_in_parallel(data, begin_mega_split, end_mega_split, audio = (i == 0 and not data.no_audio))

	elif (data.split_method == 'Vapoursynth'):
		second_pass_in_parallel(data, data.keyframes[0], data.keyframes[-1], audio = True)

	data.timer.end_of_second_pass()

	# CONCATENATION
	concatenate(data)


	""" End of the encoding process"""
	data.close()
	print(data.timer)
	return


def main(arguments):
	data = Encoding_data(arguments)

	if (data.audio_only):
		encode_audio(data)
		data.close()
		return

	if (data.concat_only):
		first_pass(data)
		list_of_frame_dicts = create_splits_from_first_pass_keyframes(data)
		concatenate(data)
		data.close()
		return

	main_encoding(data)

if __name__ == '__main__':
	arguments = parse_arguments()
	main(arguments)