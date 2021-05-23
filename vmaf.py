#!/usr/bin/env python3

import os
from json import load
import sys

def compute_mean_of_list(frame_list, metric):
	mean = 0
	nb_elements = 0

	for frame in frame_list:
		mean += float(frame["metrics"][metric])
		nb_elements += 1

	return mean / nb_elements

class Vmaf_split:
	def __init__(self, number, begin, end, vmaf):
		self.number = number
		self.begin = begin
		self.end = end
		self.vmaf = vmaf
		self.compute_means()

	def compute_means(self):
		self.vmaf_score = compute_mean_of_list(self.vmaf, "vmaf")
		self.ssim_score = compute_mean_of_list(self.vmaf, "ssim")
		self.psnr_score = compute_mean_of_list(self.vmaf, "psnr")

	def __repr__(self):
		return f"split n°{self.number} : {self.vmaf_score}"

def get_split_sizes_from_splits_log_files(last_split_number):
	split_sizes = []

	for split_number in range(1, last_split_number+1):
		number = str(split_number).zfill(5)
		log_file_path = "/tmp/av1_split_encode/splits_log/" + number + ".log"
		log_size = os.path.getsize(log_file_path)

		split_sizes.append((log_size // 232) - 1)

	return split_sizes

def keyframes(split_sizes):
	kf = [0]

	for size in split_sizes:
		next_kf = kf[-1] + size
		kf.append(next_kf)

	return kf

def load_vmaf(vmaf_path):
	with open(vmaf_path, "r") as vmaf_file:
		vmaf = load(vmaf_file)

	return vmaf["frames"]

def cut_vmaf_by_splits(vmaf, kf):
	splits = []
	for i in range(len(kf)-1):
		splits.append( Vmaf_split(i+1, kf[i], kf[i+1], vmaf[kf[i]:kf[i+1]])  )
	return splits

if __name__ == '__main__':
	split_sizes = get_split_sizes_from_splits_log_files(int(sys.argv[1]))
	kf = keyframes(split_sizes)
	vmaf = load_vmaf(str(sys.argv[2]))
	splits = cut_vmaf_by_splits(vmaf, kf)

	sorted_list = splits.copy()
	sorted_list = [ e for e in sorted_list]
	sorted_list.sort(reverse = True, key = lambda x : x.vmaf_score )

	for i in sorted_list:
		print(i)
