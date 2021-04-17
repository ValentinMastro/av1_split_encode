#!/usr/bin/env python3

import struct

def get_second_ref_usage_thresh(frame_since_last_keyframe):
	adapt_upto = 32
	min_second_ref_usage_thresh = 0.085
	second_ref_usage_thresh_max_delta = 0.035

	if (frame_since_last_keyframe >= adapt_upto):
		return min_second_ref_usage_thresh + second_ref_usage_thresh_max_delta
	else:
		return min_second_ref_usage_thresh + (float(frame_since_last_keyframe) / (adapt_upto - 1.0) ) * second_ref_usage_thresh_max_delta

def slide_transition(this_frame, last_frame, next_frame):
	VERY_LOW_II = 1.5
	ERROR_SPIKE = 5.0

	return (this_frame["intra_error"] < (this_frame["coded_error"] * VERY_LOW_II)) and (this_frame["coded_error"] > (last_frame["coded_error"] * ERROR_SPIKE)) and (this_frame["coded_error"] > (next_frame["coded_error"] * ERROR_SPIKE))

def DOUBLE_DIVIDE_CHECK(x):
    if x < 0:
        return x - 0.000001
    else:
        return x + 0.000001

def test_candidate_kf(n_frames, frame_number, frame_since_last_keyframe, list_of_frame_dicts):
	""" See <source>/av1/encoder/pass2_stategy.c """

	# The first frame is necessarily a keyframe
	if (frame_number == 0):
		return True
	# We skip the 16 last frames
	# 	SCENE_CUT_KEY_TEST_INTERVAL = 16
	if (frame_number + 16 > n_frames):
		return False

	#print("test frame : " + str(frame_number))
	MIN_INTRA_LEVEL = 0.25
	INTRA_VS_INTER_THRESH = 2.0
	VERY_LOW_INTER_THRESH = 0.05
	KF_II_ERR_THRESHOLD = 1.9
	ERR_CHANGE_THRESHOLD = 0.4
	II_IMPROVEMENT_THRESHOLD = 0.4
	KF_II_MAX = 128.0
	SCENE_CUT_KEY_TEST_INTERVAL = 16

	BOOST_FACTOR = 12.5


	last_frame = list_of_frame_dicts[frame_number - 1]
	this_frame = list_of_frame_dicts[frame_number]
	next_frame = list_of_frame_dicts[frame_number + 1]

	is_keyframe = False
	pcnt_intra = 1 - this_frame["pcnt_inter"]
	modified_pcnt_inter = this_frame["pcnt_inter"] - this_frame["pcnt_neutral"]
	second_ref_usage_thresh = get_second_ref_usage_thresh(frame_since_last_keyframe)
	total_frames_to_test = SCENE_CUT_KEY_TEST_INTERVAL
	count_for_tolerable_prediction = 3

	if 	(	(frame_since_last_keyframe >= 3) and \
			(this_frame["pcnt_second_ref"] < second_ref_usage_thresh) and \
			(next_frame["pcnt_second_ref"] < second_ref_usage_thresh) and \
			(	(this_frame["pcnt_inter"] < VERY_LOW_INTER_THRESH) or \
				slide_transition(this_frame, last_frame, next_frame) or \
				(	(pcnt_intra > MIN_INTRA_LEVEL) and \
					(pcnt_intra > (INTRA_VS_INTER_THRESH * modified_pcnt_inter)) and \
					((this_frame["intra_error"] / DOUBLE_DIVIDE_CHECK(this_frame["coded_error"])) < KF_II_ERR_THRESHOLD) and \
					(	(abs(last_frame["coded_error"] - this_frame["coded_error"]) / DOUBLE_DIVIDE_CHECK(this_frame["coded_error"]) > ERR_CHANGE_THRESHOLD) or \
						(abs(last_frame["intra_error"] - this_frame["intra_error"]) / DOUBLE_DIVIDE_CHECK(this_frame["intra_error"]) > ERR_CHANGE_THRESHOLD) or \
						((next_frame["intra_error"] / DOUBLE_DIVIDE_CHECK(next_frame["coded_error"])) > II_IMPROVEMENT_THRESHOLD))))):
		boost_score = 0.0
		old_boost_score = 0.0
		decay_accumulator = 1.0

		for i in range(total_frames_to_test):
			local_next_frame = list_of_frame_dicts[frame_number + 1 + i]
			next_iiratio = (BOOST_FACTOR * local_next_frame["intra_error"] / DOUBLE_DIVIDE_CHECK(local_next_frame["coded_error"]))

			if (next_iiratio > KF_II_MAX):
				next_iiratio = KF_II_MAX

			if (local_next_frame["pcnt_inter"] > 0.85):
				decay_accumulator *= local_next_frame["pcnt_inter"]
			else:
				decay_accumulator *= (0.85 + local_next_frame["pcnt_inter"]) / 2.0

			boost_score += (decay_accumulator * next_iiratio)

			if (	(local_next_frame["pcnt_inter"] < 0.05) or \
					(next_iiratio < 1.5) or \
					(	((local_next_frame["pcnt_inter"] - local_next_frame["pcnt_neutral"]) < 0.20) and \
						(next_iiratio < 3.0)	) or \
					((boost_score - old_boost_score) < 3.0) or \
					(local_next_frame["intra_error"] < 200)):
				break

			old_boost_score = boost_score

		if (boost_score > 30.0 and (i > count_for_tolerable_prediction)):
			is_keyframe = True
		else:
			is_keyframe = False

	return is_keyframe



def detect_keyframes(data):
	"""
	Given the log file generated by the first pass of aomenc,
	return the keyframes the encoder would choose.
	"""

	kf = data.keyframes
	n_frames = data.total_number_of_frames
	log_file = data.first_pass_log_file_path

	""" Each frame gets the same number of bytes data,
	which in the C code is a struct composed of 26 double.
	The size of each frame data is 28*sizeof(double) + sizeof(int64_t)
	= 28*8 + 8 = 232 bytes."""

	# Struct defined in <source>/av1/encoder/firstpass.h
	FIRSTPASS_STATS_STRUCT_KEYS = [
		"frame",
		"weight",
		"intra_error",
		"frame_avg_wavelet_energy",
		"coded_error",
		"sr_coded_error",
		"tr_coded_error",
		"pcnt_inter",
		"pcnt_motion",
		"pcnt_second_ref",
		"pcnt_third_ref",
		"pcnt_neutral",
		"intra_skip_pct",
		"inactive_zone_rows",
		"inactive_zone_cols",
		"MVr",
		"mvr_abs",
		"Mvc",
		"mvc_abs",
		"MVrv",
		"MVcv",
		"mv_in_out_count",
		"new_mv_count",
		"duration",
		"count",
		"raw_error_stdev",
		"is_flash", #int64_t
		"noise_var",
		"cor_coeff"
		]

	with open(log_file, 'rb') as log_data:
		# Reading of the entire log file -> data in a dict
		list_of_frame_dicts = []

		for i in range(n_frames+1):
			# +1 because the last 232 bytes are given to "end of sequence"
			frame_data = log_data.read(232)
			frame_stats = struct.unpack('26dq2d', frame_data)

			frame_dict = {}
			for index in range(len(FIRSTPASS_STATS_STRUCT_KEYS)):
				frame_dict[FIRSTPASS_STATS_STRUCT_KEYS[index]] = frame_stats[index]

			list_of_frame_dicts.append(frame_dict)

		""" Each frame is tested, using its data, in order to know if it will be
		considered a keyframe for aomenc. For that, we also need to know how far
		the current frame is of the last keyframe. """

		frame_since_last_keyframe = 0
		for frame_number in range(n_frames):
			is_keyframe = test_candidate_kf(n_frames, frame_number, frame_since_last_keyframe, list_of_frame_dicts)

			if (is_keyframe):
				kf.append(frame_number)
				frame_since_last_keyframe = 0

			frame_since_last_keyframe += 1

		kf.append(n_frames)

		return list_of_frame_dicts


class Split:
	def __init__(self, start_frame, end_frame, split_number, osfs_temp_dir, threads):
		self.split_number = split_number
		self.start_frame = start_frame
		self.end_frame = end_frame

		number = str(self.split_number).zfill(5)

		first_pass_path = "splits_log/" + number + ".log"
		ivf_2_pass_path = "splits_ivf/" + number + ".ivf"
		source_file_path = "splits_source/" + number + ".mkv"

		for path in [first_pass_path, ivf_2_pass_path, source_file_path]:
			osfs_temp_dir.create(path, wipe = False)

		self.tmp_first_pass_path = osfs_temp_dir.getsyspath(first_pass_path)
		self.tmp_ivf_2_pass_path = osfs_temp_dir.getsyspath(ivf_2_pass_path)
		self.split_source_file = osfs_temp_dir.getsyspath(source_file_path)

		self.threads = threads

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


	def get_second_pass_command(self, data, t):
		if (data.interlaced):
			command_ffmpeg = [data.ffmpeg, '-y', '-loglevel', 'quiet',
					'-i', self.split_source_file, '-vf', 'yadif',
					'-f', 'yuv4mpegpipe', '-pix_fmt', 'yuv420p', '-']
		else:
			command_ffmpeg = [data.ffmpeg, '-y', '-loglevel', 'quiet',
				'-i', self.split_source_file, '-f', 'yuv4mpegpipe', '-pix_fmt', 'yuv420p', '-']

		command_aomenc = [data.aomenc, '-t', str(t), '--pass=2', '--passes=2',
				'--cpu-used=' + str(data.cpu_use), '--end-usage=q', '--cq-level=' + str(data.q),
				'--auto-alt-ref=1', '--lag-in-frames=35', '--bit-depth=10', '--fpf=' + self.tmp_first_pass_path,
				'-o', self.tmp_ivf_2_pass_path, '-']

		return " ".join(command_ffmpeg + ['|'] + command_aomenc)


def generate_split_from_keyframes(data):
	kf = data.keyframes

	for i in range(len(kf) - 1):
		start = kf[i]
		end = kf[i+1]
		number = i+1 # begin at 1

		data.splits.append(Split(start, end, number, data.temp_dir, data.threads_per_split))


def create_splits_from_first_pass_keyframes(data):
	list_of_frame_dicts = detect_keyframes(data)
	generate_split_from_keyframes(data)

	return list_of_frame_dicts
