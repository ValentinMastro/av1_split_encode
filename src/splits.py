#!/usr/bin/env python3

from os.path import join
from src.encoding_jobs import check_sub_directories

class Split:
	def __init__(self, parameters, split_number, begin, end):
		self.parameters = parameters

		self.split_number = split_number
		self.begin = begin		# First frame in the split
		self.end = end			# First frame after the split

	def number_filled(self):
		return f"{self.split_number:05d}"

	def get_number_of_frames(self):
		return self.end - self.begin

	def generate_pipe(self):
		pass

	def __repr__(self):
		return f"Split n°{self.split_number:05d}  [{self.begin:06d} --> {self.end:06d}]"


class Trim_split(Split):
	def __init__(self, parameters, split_number, begin, end):
		super().__init__(parameters, split_number, begin, end)

	def generate_pipe(self):
		pipe_command = [self.parameters.ffmpeg, '-y', '-loglevel', 'quiet',
				'-i', self.parameters.input_file, '-map', '0:v',
				'-vf', f"'trim=start_frame={self.begin}:end_frame={self.end},setpts=PTS-STARTPTS'",
				'-f', 'yuv4mpegpipe', '-pix_fmt', 'yuv420p', '-']
		return pipe_command


class Vapoursynth_split(Split):
	def __init__(self, parameters, split_number, begin, end):
		super().__init__(parameters, split_number, begin, end)

		# Generate Vapoursynth script
		self.script_path = join(self.parameters.temp_folder, "vpy", f"script{self.number_filled()}.vpy")
		check_sub_directories([self.script_path])
		with open(self.script_path, "w") as vp_script:
			vp_script.write("from vapoursynth import core\n")
			#vp_script.write(f"full_video = core.ffms2.Source(source='{self.parameters.input_file}')\n")
			vp_script.write(f"full_video = core.lsmas.LWLibavSource(r'{self.parameters.input_file}')\n")
			vp_script.write(f"split = full_video.std.Trim({self.begin}, {self.end - 1})\n")
			vp_script.write("split.set_output()\n")


	def generate_pipe(self):
		pipe_command = [self.parameters.vspipe, "--y4m", self.script_path, '-c', '-', '2>', '/dev/null']
		return pipe_command
