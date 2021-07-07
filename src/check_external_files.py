#!/usr/bin/env python3

import sys
from os.path import exists


def check_individual_file(file_name):
	""" Exits if file does not exists """
	if (not exists(file_name)):
		print(f"[Error] {file_name} does not exists.\nTwo solutions :\n" + \
		 		"\t->run external_binaries/install.sh\n" + \
				"\t->Use an argument to change the binary's path",
				file = sys.stderr)
		exit(1)


def check_bin(args):
	""" This verifies that all the binaries used in this script exist """
	for file_name in (args.ffmpeg, args.aomenc, args.SvtAv1EncApp, args.mkvmerge):
		check_individual_file(file_name)


def check_modules():
	""" This verifies modules are installed"""
	pass


def check_if_everything_is_ready(args):
	"""
	Are modules used installes ?
	Are external binaries path corrects ?
	"""

	check_modules()
	check_bin(args)
