#!/usr/bin/env python3

from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

def single_threaded_job(job):
	frame_encoded = job.run_job()
	return frame_encoded

def run_parallel_encoding(parameters, jobs):
	jobs.sort(reverse = True, key = lambda j : j.get_number_of_frames())
	total_number_of_frames = sum([j.get_number_of_frames() for j in jobs if j.get_type() == "Video"])

	with tqdm(total = total_number_of_frames) as bar:
		with ThreadPoolExecutor(max_workers = parameters.number_of_splits) as pool:
			futures = [pool.submit(single_threaded_job, job) for job in jobs]
			for future in as_completed(futures):
				encoded_frames = future.result()
				bar.update(encoded_frames)
