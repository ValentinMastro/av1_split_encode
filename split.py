#!/usr/bin/env python3

import os
from json import load

class Split:
	def __init__(self, start_frame, end_frame, split_number, data):
		self.split_number = split_number
		self.start_frame = start_frame
		self.end_frame = end_frame

		number = str(self.split_number).zfill(5)

		first_pass_path = "splits_log/" + number + ".log"
		ivf_2_pass_path = "splits_ivf/" + number + ".ivf"
		source_file_path = "splits_source/" + number + ".mkv"
		json_file_path = "splits_json/" + number + ".json"

		for path in [first_pass_path, ivf_2_pass_path, source_file_path, json_file_path]:
			data.temp_dir.create(path, wipe = False)

		self.tmp_first_pass_path = data.temp_dir.getsyspath(first_pass_path)
		self.tmp_ivf_2_pass_path = data.temp_dir.getsyspath(ivf_2_pass_path)
		self.split_source_file = data.temp_dir.getsyspath(source_file_path)
		self.json_file_path = data.temp_dir.getsyspath(json_file_path)

		self.vp_script_path = data.vp_script_path

		self.threads = data.threads_per_split
		self.vmaf_score = -1

		if (self.threads == 0):
			length = self.end_frame - self.start_frame

			if (length >= 1000):
				self.threads = 4
			elif (length <= 50):
				self.threads = 1
			elif (length > 50 and length <= 300):
				self.threads = 2
			else:
				self.threads = 3


	def get_dict(self):
		return {'number': self.split_number, 'start': self.start_frame, 'end': self.end_frame}

	def get_magicyuv_pipe_command(self, data):
		command_ffmpeg = [data.ffmpeg, '-y', '-loglevel', 'quiet',
				'-i', self.split_source_file, '-f', 'yuv4mpegpipe', '-pix_fmt', 'yuv420p', '-']
		return command_ffmpeg

	def get_vapoursynth_pipe_command(self):
		command_vspipe = ["vspipe", "--start", str(self.start_frame),
				"--end", str(self.end_frame - 1), '--y4m', self.vp_script_path, '-c', '-']
		return command_vspipe

	def get_aomenc_second_pass_command(self, data, t):
		command_aomenc = [data.aomenc, '-t', str(t), '--pass=2', '--passes=2',
				'--cpu-used=' + str(data.cpu_use), '--end-usage=q', '--cq-level=' + str(data.q),
				'--auto-alt-ref=1', '--lag-in-frames=35', '--bit-depth=10',
				'--frame-boost=1', '--arnr-maxframes=15',
				'--enable-fwd-kf=1', '--enable-qm=1', '--enable-chroma-deltaq=1', '--quant-b-adapt=1',
				'--fpf=' + self.tmp_first_pass_path, '-o', self.tmp_ivf_2_pass_path, '-']

		return command_aomenc

	def get_second_pass_command_with_magicyuv(self, data, t):
		command_magicyuv = self.get_magicyuv_pipe_command(data)
		command_aomenc = self.get_aomenc_second_pass_command(data, t)
		return " ".join(command_magicyuv) + " | " + " ".join(command_aomenc)

	def get_second_pass_command_with_vapoursynth(self, data, t):
		command_vspipe = self.get_vapoursynth_pipe_command()
		command_aomenc = self.get_aomenc_second_pass_command(data, t)
		return " ".join(command_vspipe) + " | " + " ".join(command_aomenc)

	def compute_vmaf(self):
		command_vmaf = ["bash", "vmaf.sh",  self.split_source_file, self.tmp_ivf_2_pass_path, self.json_file_path]
		os.system(" ".join(command_vmaf))

		# Read vmaf score
		with open(self.json_file_path, "r") as json_file:
			json_data = load(json_file)
			self.vmaf_score = float(json_data["pooled_metrics"]["vmaf"]["mean"])
