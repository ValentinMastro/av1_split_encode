#!/usr/bin/env python3

from src.command_line_interface import parse_cli
from src.process_arguments_from_command_line import process_cli
from src.check_external_files import check_if_everything_is_ready
from src.keyframes import detect_keyframes
from src.splits_creation import create_splits_from_keyframes
from src.encoding_jobs_creation import generate_encoding_jobs_from_splits
from src.parallel_encoding import run_parallel_encoding
from src.concatenate import concatenate_temp_files
from src.time_measurement import Timer


def main(args):
	parameters = process_cli(args)
	timer = Timer(parameters)

	keyframes = detect_keyframes(parameters)
	splits = create_splits_from_keyframes(parameters, keyframes)
	encoding_jobs = generate_encoding_jobs_from_splits(parameters, splits)
	run_parallel_encoding(parameters, encoding_jobs)
	concatenate_temp_files(parameters, encoding_jobs)

	timer.display_time_measurement()
	exit(0)

if __name__ == '__main__':
	# Parse command line arguments
	args = parse_cli().parse_args()
	# Check if modules used are installed and if external binaries used exists
	#check_if_everything_is_ready(args)
	# Launch main program
	main(args)
