#!/usr/bin/env python3

# scenedetect
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector


def keyframe_detection_with_aom_first_pass(parameters):
	pass

def keyframe_detection_with_scenedetect(parameters):
	video = VideoManager([parameters.input_file])
	scene = SceneManager()
	scene.add_detector(ContentDetector(threshold = 30.0))

	video.set_downscale_factor()
	video.start()
	scene.detect_scenes(frame_source = video)

	return scene.get_scene_list()

def detect_keyframes(parameters):
	"""
	Returns all the keyframes that will be used to cut the source file
	in splits

	There are two ways, depending of user's choice :
		-> computing first pass with aomenc and using the log file data
		-> using scene detection
	"""

	if (parameters.keyframe_detection == "AOM_1st_PASS"):
		keyframes = []
	elif (parameters.keyframe_detection == "OpenCV_scenedetect"):
		analysis_results = keyframe_detection_with_scenedetect(parameters)
		keyframes = [obj[0].frame_num for obj in analysis_results] + [analysis_results[-1][1].frame_num]

	return keyframes
