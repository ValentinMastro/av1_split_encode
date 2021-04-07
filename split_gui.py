#!/usr/bin/env python3

from split import main, Encoding_data, parse_arguments
import PySimpleGUI as sg
from os import cpu_count
import time

def gui():
	# Theme of the window
	sg.theme('DarkAmber')

	queue_display = [['_'*40, '___', '_'*40]]

	# Widgets
	widgets = [ [sg.Text("Fichier source")], [sg.In(key='source')], [sg.FileBrowse(target='source')],
				[sg.Text("Fichier destination")], [sg.In(key='dest')], [sg.FileSaveAs(target='dest')],
				[sg.Slider(range = (1, 50), default_value = 34, size = (20,15), orientation = 'horizontal',
         			font = ('Helvetica', 12), resolution = 1, k = '-q'), sg.Text("-q", font = ('Helvetica', 15), justification = 'right' )],
				[sg.Slider(range = (1, cpu_count()), default_value = cpu_count(), size = (20,15), orientation = 'horizontal',
         			font = ('Helvetica', 12), resolution = 1, k = '-t'), sg.Text("-t", font = ('Helvetica', 15) )],
				[sg.Slider(range = (1, 9), default_value = 4, size = (20,15), orientation = 'horizontal',
         			font = ('Helvetica', 12), resolution = 1, k = '--cpu_use'), sg.Text("--cpu_use", font = ('Helvetica', 15) )],
				[sg.Slider(range = (1000, 50000), default_value = 20000, size = (20,15), orientation = 'horizontal',
         			font = ('Helvetica', 12), resolution = 1000, k = '--frame_limit'), sg.Text("--frame_limit", font = ('Helvetica', 15) )],
				[sg.Slider(range = (0, 4), default_value = 2, size = (20,15), orientation = 'horizontal',
         			font = ('Helvetica', 12), resolution = 1, k = '--threads_per_split'), sg.Text("--threads_per_split", font = ('Helvetica', 15) )],
				[sg.Checkbox("No audio encoded", k = "--no_audio", enable_events = True)],
				[sg.Checkbox("Audio only", k = "--audio_only", enable_events = True)],
				[sg.Checkbox("Interlaced video stream", k = "--interlaced", enable_events = True)],
				[sg.Button(button_text = "Add to queue", key = "_QUEUE_")],
				[sg.Table(queue_display, headings = ["Source", "-->", "Destination"], k = "queue_list", num_rows = 3, row_height = 15, auto_size_columns = True, vertical_scroll_only = False, hide_vertical_scroll = True)],
				[sg.Button(button_text = "Encode", key = "_START_")]]

	# Create main window
	window = sg.Window("AV1 SPLIT ENCODE", widgets)

	args_queue = []

	while True:
		event, values = window.read()
		if (event == sg.WIN_CLOSED):
			break

		if (event == "_QUEUE_"):
			parser = parse_arguments(gui = True)
			list_of_values = [values["source"], values["dest"], "-q", str(int(values["-q"])), "-t", str(int(values["-t"])), "--cpu_use", str(int(values["--cpu_use"])),
			 			"--frame_limit", str(int(values["--frame_limit"])), "--threads_per_split", str(int(values["--threads_per_split"])), '--clean_at_the_end']

			# Parsing boolean values
			for bool_check in ('--no_audio', '--audio_only', '--interlaced'):
				if (values[bool_check]):
					list_of_values.append(bool_check)

			args = parser.parse_args(list_of_values)

			# Adding the job to queue
			args_queue.append(args)

			# Updating display
			queue_display.append([str(values["source"]), "-->", str(values["dest"])])
			window["queue_list"].update(queue_display)
			window.Refresh()



		if (event == "_START_"):
			for arguments in args_queue:
				begin = time.time()
				main(args)
				end = time.time()
				window.Refresh()

		if (event == "--no_audio"):
			if (values["--no_audio"]):
				window["--audio_only"].update(False)

		if (event == "--audio_only"):
			if (values["--audio_only"]):
				window["--no_audio"].update(False)

	window.close()

if __name__ == '__main__':
	gui()
