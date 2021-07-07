#!/usr/bin/env python3

import argparse
from os import cpu_count
from os.path import join
from tempfile import mkdtemp


def parse_cli():
	""" Configure all arguments that can be used """

	parser = argparse.ArgumentParser()

	# IO
	# ---> input and output files
	parser.add_argument("input_file", type = str)
	parser.add_argument("output_file", type = str)
	# ---> external binaries
	parser.add_argument("--ffmpeg", type = str, default = "external_binaries/bin/ffmpeg")
	parser.add_argument("--aomenc", type = str, default = "external_binaries/bin/aomenc")
	parser.add_argument("--SvtAv1EncApp", type = str, default = "external_binaries/bin/SvtAv1EncApp")
	parser.add_argument("--mkvmerge", type = str, default = "mkvmerge")
	parser.add_argument("--vspipe", type = str, default = "external_binaries/bin/vspipe")
	# ---> temporary files and directories
	temp_folder = mkdtemp()
	audio_default = join(temp_folder, 'audio.opus')
	parser.add_argument("--temp_folder", type = str, default = temp_folder)
	parser.add_argument("--temp_audio", type = str, default = audio_default)

	# General parameters
	# ---> encoding
	parser.add_argument("-e", "--encoder", type = str, default = "aomenc", choices = ["aomenc", "SVT-AV1"])
	parser.add_argument("-q", "--cq_level", type = int, default = 34, choices = range(0,63+1))
	parser.add_argument("-n", "--number_of_splits", type = int, default = cpu_count(), choices = range(1,cpu_count()+1))
	parser.add_argument("-c", "--cpu_used", type = int, default = 6, choices = range(0,9+1))
	# ---> splitting
	parser.add_argument("-k", "--keyframe_detection", type = str, default = "OpenCV_scenedetect",
								choices = ["AOM_1st_PASS", "OpenCV_scenedetect"])
	parser.add_argument("-s", "--splitting_method", type = str, default = "Vapoursynth",
								choices = ["ffmpeg_trim", "Vapoursynth", "MagicYUV"])
	parser.add_argument("-t", "--threads_per_split", type = int, default = 1, choices = range(1,4+1))

	return parser
