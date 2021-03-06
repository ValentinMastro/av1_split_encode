#!/usr/bin/env python3

import subprocess

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


def convert_from_y4m_to_magicyuv(magicyuv_file_path):
	""" Using magicyuv codec instead of yuv uses between 4 and 10 times less space,
	is lossless and is low-latency """

	y4m_file_path = magicyuv_file_path + ".y4m"

	command = ['ffmpeg', '-y', '-loglevel', 'quiet',
				'-i', y4m_file_path,
				'-c:v', 'magicyuv', magicyuv_file_path]

	process = subprocess.Popen(command)
	process.wait()

	subprocess.Popen(['rm', y4m_file_path]).wait()


def open_y4m_file_in_RAM(y4m_header, split):
	file = open(split.split_source_file + ".y4m", "wb")
	file.write(y4m_header.signature)
	file.write(y4m_header.params_bytes)
	return file

def read_frame(pipe_data, y4m_header):
	l = y4m_header.width
	h = y4m_header.height

	begin_data = pipe_data.read(6)
	assert(begin_data == b'FRAME\n')

	frame_data = pipe_data.read(l * h * 3 // 2) # chroma 4:2:0

	return begin_data + frame_data


def generate_source_splits(data, begin, end):
	""" Cut source file and write it on disk (can be RAM disk) """

	command = ['ffmpeg', '-y',
				'-loglevel', 'quiet',
				'-i', data.source_file,
				'-vf', 'trim=start_frame=' + str(begin) + ':end_frame=' + str(end) + \
				',setpts=PTS-STARTPTS',
				'-f', 'yuv4mpegpipe',
				'-pix_fmt', 'yuv420p',
				'-']

	process = subprocess.Popen(command, stdout = subprocess.PIPE, stderr = subprocess.PIPE)

	with process.stdout as pipe_data:
		# header of the yuv4mpegpipe stream
		signature = pipe_data.read(10)
		assert(signature == b'YUV4MPEG2 ')

		""" Each parameter in the header is a set of bytes in ascii.
		It ends with a \n """
		byte = b''
		parameters = b''

		while (byte != b'\n'):
			parameters += byte
			byte = pipe_data.read(1)

		y4m_header = Y4M(signature, parameters)

		#
		current_frame = begin
		current_split_index = [s.start_frame for s in data.splits].index(begin)
		current_split = data.splits[current_split_index]

		file = open_y4m_file_in_RAM(y4m_header, current_split)

		while (True):
			frame = read_frame(pipe_data, y4m_header)

			if (current_frame in data.keyframes and current_frame != begin):
				file.close()
				convert_from_y4m_to_magicyuv(current_split.split_source_file)

				current_split_index += 1
				current_split = data.splits[current_split_index]

				file = open_y4m_file_in_RAM(y4m_header, current_split)

			file.write(frame)
			current_frame += 1

			if (current_frame == end):
				file.close()
				convert_from_y4m_to_magicyuv(current_split.split_source_file)
				break

	process.terminate()
