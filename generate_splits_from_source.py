#!/usr/bin/env python3

import subprocess
import os

class Y4M:
	""" Y4M header data """
	def __init__(self, signature, params_bytes):
		self.width = 0
		self.height = 0
		self.signature = signature
		self.params_bytes = params_bytes + b'\n'

		params = params_bytes.decode('ascii').split(" ")

		for param in params:
			if (param[0] == "W"):
				self.width = int(param[1:])
			elif (param[0] == "H"):
				self.height = int(param[1:])


def read_frame(pipe_data, y4m_header):
	l = y4m_header.width
	h = y4m_header.height

	begin_data = pipe_data.read(6)
	assert(begin_data == b'FRAME\n')

	frame_data = pipe_data.read(l * h * 3 // 2) # chroma 4:2:0

	return begin_data + frame_data


def open_magicyuv_file_in_RAM(y4m_header, split):
	""" We write yuv4mpegpipe data in the ffmpeg stdin pipe, and convert it in
	the magicyuv codec. """

	command = ['ffmpeg', '-y', '-loglevel', 'quiet',
				'-i', '-',
				'-c:v', 'magicyuv', '-pred', '3', split.split_source_file]

	magicyuv_process = subprocess.Popen(command, stdin = subprocess.PIPE)
	magicyuv_process.stdin.write(y4m_header.signature)
	magicyuv_process.stdin.write(y4m_header.params_bytes)

	return magicyuv_process


def get_header_of_yuv4mpegpipe(pipe_data):
	signature = pipe_data.read(10)
	assert(signature == b'YUV4MPEG2 ')

	""" Each parameter in the header is a set of bytes in ascii.
	It ends with a \n """
	byte = b''
	parameters = b''

	while (byte != b'\n'):
		parameters += byte
		byte = pipe_data.read(1)

	return Y4M(signature, parameters)


def generate_magicyuv_source_splits(data, begin, end):
	""" Cut source file and write it on disk (can be RAM disk) """

	filters = data.filters[:-1] + ['trim=start_frame=' + str(begin) + ":end_frame=" + str(end)] + [data.filters[-1]]

	command = ['ffmpeg', '-y', '-loglevel', 'quiet',
				'-i', data.source_file,
				'-vf', ",".join(filters),
				'-f', 'yuv4mpegpipe', '-pix_fmt', 'yuv420p', '-']

	process = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

	with process.stdout as pipe_data:
		y4m_header = get_header_of_yuv4mpegpipe(pipe_data)

		current_frame = begin
		current_split_index = [s.start_frame for s in data.splits].index(begin)
		current_split = data.splits[current_split_index]

		magicyuv_process = open_magicyuv_file_in_RAM(y4m_header, current_split)

		while (True):
			frame = read_frame(pipe_data, y4m_header)

			if (current_frame in data.keyframes and current_frame != begin):
				magicyuv_process.communicate()

				current_split_index += 1
				current_split = data.splits[current_split_index]

				magicyuv_process = open_magicyuv_file_in_RAM(y4m_header, current_split)

			magicyuv_process.stdin.write(frame)
			current_frame += 1

			if (current_frame == end):
				magicyuv_process.communicate()
				break

	process.terminate()
