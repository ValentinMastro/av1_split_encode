#!/usr/bin/env python3

import subprocess

def convert_from_y4m_in_magicyuv(y4m_file_path, magicyuv_file_path):
	""" Using magicyuv codec insted of yuv uses between 4 and 10 times less space,
	is lossless and is low-latency """

	command = ['ffmpeg', '-y', '-loglevel', 'quiet',
				'-i', y4m_file_path,
				'-c:v', 'magicyuv', magicyuv_file_path]

	process = subprocess.Popen(command)
	process.wait()

	subprocess.Popen(['rm', y4m_file_path]).wait()


def generate_source_splits(data):
	""" Cut source file and write it on disk (can be RAM disk) """

	command = ['ffmpeg', '-y',				# ffmpeg binary
				'-loglevel', 'quiet',	# pas d'affichage console
				'-i', source,			# Fichier d'entrée : source
				'-vf', 'trim=start_frame=' + begin + ':end_frame=' + end + \
				',setpts=PTS-STARTPTS',
				'-f', 'yuv4mpegpipe',	# Format Y4M pour pipe
				'-pix_fmt', 'yuv420p',	# Chroma 4:2:0 en progressif
				'-']					# Sortie en stdin
