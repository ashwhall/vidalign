"""
A crude script to run encode tasks by loading a videoclip config file and printing progress to stdout.
Run like:
python3 vidalign/encode_unattended.py path/to/config.vc.json
OR
python3 vidalign/encode_unattended.py dir/containing/configs
"""


from time import sleep
import os
from sys import argv
from PySide6.QtWidgets import QApplication
from vidalign.model import Model
from vidalign.controllers import MainController
from vidalign.views.main_view import MainView

app = QApplication()


def run(p):
    model = Model()
    main_controller = MainController(model)
    main_view = MainView(model, main_controller)

    main_view._config_view._controller.on_load_encoder_config(p)

    def print_prog(percent, lines):
        print(percent)
        for line in lines:
            print(line, flush=True)
    model.encoding_progress_changed.connect(print_prog)

    model.start_encoding_tasks()

    def fmt_line(percent, line):
        return f'Total: {int(round(percent * 100))}% | Task: {line}'

    last_line = 'Starting...'
    while model.encoding_percentage < 1:
        if len(model.encoding_stdout_lines) > 0:
            new_line = fmt_line(model.encoding_percentage, model.encoding_stdout_lines[-1])
            if new_line != last_line:
                print(new_line, end='\r', flush=True)
                last_line = new_line
        sleep(0.25)
    print('Finished!')


def run_dir(p):
    for f in os.listdir(p):
        if f.endswith('.vc.json'):
            print(f'Running {f}...')
            run(os.path.join(p, f))


if __name__ == '__main__':
    p = argv[1]

    if os.path.isdir(p):
        should_run = None
        while should_run not in ['y', 'n']:
            should_run = input(
                'You selected a directory - run for each *.vc.json file in this directory? (y/n) ')
            should_run = should_run.lower()
        if should_run == 'y':
            run_dir(p)
        else:
            print('Exiting...')
    else:
        run(p)
