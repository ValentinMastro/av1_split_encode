#!/usr/bin/env python3

import argparse
import os
from json import load

from first_pass_keyframes import create_splits_from_first_pass_keyframes
from first_pass_logfile import generate_first_pass_log_for_each_split


class Encoding_data:
	def __init__(self, arguments):
		# IO
		self.source_file = arguments.source_file
		self.destination_file = arguments.destination_file
		self.ffmpeg = "ffmpeg"
		self.ffprobe = "ffprobe"
		self.aomenc = "aomenc"
		self.temp_folder = "/tmp/av1_split_encode/"
		os.system("mkdir -p {}".format(self.temp_folder))
		self.first_pass_log_file = "{}keyframes.log".format(self.temp_folder)

		# Encoding parameters
		self.q = arguments.q
		self.total_number_of_frames = self.get_total_number_of_frames()
		self.cpu_use = 4

		# Splitting parameters
		self.keyframes = []
		self.splits = []

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



def parse_arguments():
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

	return parser.parse_args()



def first_pass(data):
	""" Generate first pass log file of the entire source file """

	if (not os.path.isfile(data.first_pass_log_file)):
		first_pass_pipe = "{} -loglevel quiet -i {} -map 0:v -vf 'setpts=PTS-STARTPTS' ".format(data.ffmpeg, data.source_file) + \
						  "-f yuv4mpegpipe -pix_fmt yuv420p -"
		first_pass_aomenc = "{} -t 12 --pass=1 --passes=2 ".format(data.aomenc) + \
						  "--auto-alt-ref=1 --lag-in-frames=35 --end-usage=q --cq-level=22 --bit-depth=10 " + \
						  "--fpf={} -o /dev/null -".format(data.first_pass_log_file)

		first_pass_command = first_pass_pipe + " | " + first_pass_aomenc
		os.system(first_pass_command)



def main_encoding(data):
	first_pass(data)
	list_of_frame_dicts = create_splits_from_first_pass_keyframes(data)
	generate_first_pass_log_for_each_split(data, list_of_frame_dicts)



if __name__ == '__main__':
	arguments = parse_arguments()
	data = Encoding_data(arguments)
	main_encoding(data)
