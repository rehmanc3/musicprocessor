from __future__ import annotations
import PySimpleGUI as sg
from pathlib import Path
import threading
from .batch import run_batch

sg.theme("SystemDefaultForReal")

layout = [
    [sg.Text("Music Stem Isolation Tool", font=("Segoe UI", 14, "bold"))],
    [sg.Text("Input folder"), sg.Input(key="-IN-"), sg.FolderBrowse()],
    [sg.Text("Output folder"), sg.Input(key="-OUT-"), sg.FolderBrowse()],
    [sg.Text("ONNX models"), sg.Input(key="-MODEL-", default_text=str(Path("models/models.onnx"))), sg.FileBrowse(file_types=(("ONNX", "*.onnx"),))],
    [sg.Text("Device"), sg.Combo(["cpu", "cuda"], default_value="cpu", key="-DEV-")],
    [sg.Text("Overlap"), sg.Slider(range=(0.0, 0.9), orientation='h', resolution=0.05, default_value=0.25, key="-OV-")],
    [sg.Text("Frame (sec)"), sg.Slider(range=(1, 15), orientation='h', resolution=1, default_value=5, key="-FR-")],
    [sg.ProgressBar(100, orientation='h', size=(40, 20), key='-PROG-')],
    [sg.Button("Run Batch", key="-RUN-"), sg.Button("Exit")]
]

window = sg.Window("Stem Isolation (ONNX)", layout)


def _run(values, progress):
    try:
        run_batch(
            input_dir=values['-IN-'],
            output_dir=values['-OUT-'],
            model_path=values['-MODEL-'],
            device=values['-DEV-'],
            overlap=float(values['-OV-']),
            frame_len=int(values['-FR-'])*44100,
        )
    finally:
        progress.update_bar(100)


while True:
    event, values = window.read(timeout=200)
    if event in (sg.WINDOW_CLOSED, "Exit"):
        break
    if event == "-RUN-":
        progress = window['-PROG-']
        progress.update_bar(0)
        threading.Thread(target=_run, args=(values, progress), daemon=True).start()

window.close()