#!/usr/bin/env python3

from src.encoding_jobs import Aomenc_job, Audio_job


def select_encoding_job_class(parameters, split):
	if (parameters.encoder == "aomenc"):
		return Aomenc_job(parameters, split)
	elif (parameters.encoder == "SVT-AV1"):
		pass

def generate_encoding_jobs_from_splits(parameters, splits):
	jobs = []
	for split in splits:
		jobs.append(select_encoding_job_class(parameters, split))
	jobs.append(Audio_job(parameters))

	return jobs
