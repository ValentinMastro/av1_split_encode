#!/usr/bin/env python3

from os.path import join, split
from os import makedirs, system
from sys import maxsize


def check_sub_directories(list_of_fullpath):
	for path in list_of_fullpath:
		head, tail = split(path)
		makedirs(head, exist_ok = True)

class Encoding_job:
	def __init__(self, parameters, split = None):
		self.parameters = parameters
		self.split = split

	def get_type(self):
		return "Abstract"

	def get_number_of_frames(self):
		return 0

	def generate_encode_command(self, pass_num):
		return []

	def run_job(self):
		pass


class Aomenc_job(Encoding_job):
	def __init__(self, parameters, split):
		super().__init__(parameters, split)

		self.first_pass_log_file = join(self.parameters.temp_folder,
										'log', f"{split.number_filled()}.log")
		self.second_pass_ivf_file = join(self.parameters.temp_folder,
										'ivf', f"{split.number_filled()}.ivf")

		check_sub_directories([self.first_pass_log_file, self.second_pass_ivf_file])

	def get_type(self):
		return "Video"

	def get_number_of_frames(self):
		return self.split.get_number_of_frames()

	def generate_encode_command(self, pass_num):
		options = [ '--lag-in-frames=35', '--bit-depth=10', '--frame-boost=1',
					'--auto-alt-ref=1', '--enable-fwd-kf=1']

		command = [	self.parameters.aomenc,
					'-t', str(self.parameters.threads_per_split),
					'--cpu-used=' + str(self.parameters.cpu_used),
					'--end-usage=q', '--cq-level=' + str(self.parameters.cq_level),
					'--passes=2', f'--pass={pass_num}'
					] + options + [
					'--fpf=' + self.first_pass_log_file,
					'-o', self.second_pass_ivf_file, '-',
					'2>', '/dev/null'
					]

		return command

	def run_job(self):
		for pass_num in (1,2):
			pipe = self.split.generate_pipe()
			encode_command = self.generate_encode_command(pass_num)
			system(" ".join(pipe) + " | " + " ".join(encode_command))

		return self.get_number_of_frames()


class Audio_job(Encoding_job):
	def __init__(self, parameters):
		super().__init__(parameters)

	def get_type(self):
		return "Audio"

	def get_number_of_frames(self):
		return maxsize

	def run_job(self):
		check_sub_directories([self.parameters.temp_audio])
		command = [	self.parameters.ffmpeg, '-y', '-loglevel', 'quiet',
					'-i', self.parameters.input_file, '-map', '0:a',
					'-c:a', 'libopus', '-b:a', '192k',
					self.parameters.temp_audio]

		system(" ".join(command))
		return 0
