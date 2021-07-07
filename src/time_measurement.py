#!/usr/bin/env python3

from time import time
import cv2

class Timer:
	def __init__(self, parameters):
		self.start_of_encode = time()
		self.end_of_encode = 0
		self.parameters = parameters

		capture = cv2.VideoCapture(self.parameters.input_file)
		self.video_fps = capture.get(5)
		self.total_number_of_frames = capture.get(7)


	def display_time_measurement(self):
		self.end_of_encode = time()
		duration = self.end_of_encode - self.start_of_encode

		hours = int(duration // 3600)
		minutes = int((duration % 3600) // 60)
		seconds = int((duration % 3600) % 60)

		encoding_fps = self.total_number_of_frames / duration
		relative_speed = encoding_fps / self.video_fps

		print(f"Time elapsed : {hours:02d}:{minutes:02d}:{seconds:02d}")
		print(f"{encoding_fps:2.2f} fps (x{relative_speed:1.2f})")
