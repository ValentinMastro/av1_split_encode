#!/usr/bin/env python3

from split import main_encoding, Encoding_data, parse_arguments
import PySimpleGUI as sg
from os import cpu_count

def gui():
	# Theme of the window
	sg.theme('DarkAmber')

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
				[sg.Slider(range = (1, 4), default_value = 2, size = (20,15), orientation = 'horizontal',
         			font = ('Helvetica', 12), resolution = 1, k = '--threads_per_split'), sg.Text("--threads_per_split", font = ('Helvetica', 15) )],
				[sg.Output(size = (80, 30), echo_stdout_stderr = True)],
				[sg.Button(button_text = "Encode", key = "_START_")]]

	# Create main window
	window = sg.Window("AV1 SPLIT ENCODE", widgets)

	while True:
		event, values = window.read()
		if (event == sg.WIN_CLOSED):
			break
		if (event == "_START_"):
			parser = parse_arguments(gui = True)
			args = parser.parse_args([values["source"], values["dest"], "-q", str(int(values["-q"])), "-t", str(int(values["-t"])), "--cpu_use", str(int(values["--cpu_use"])),
			 			"--frame_limit", str(int(values["--frame_limit"])), "--threads_per_split", str(int(values["--threads_per_split"]))])
			main_encoding(Encoding_data(args))
			window.Refresh()

	window.close()

if __name__ == '__main__':
	gui()
