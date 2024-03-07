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
from argparse import ArgumentParser
from PySide6.QtWidgets import QApplication
from vidalign.model import Model
from vidalign.controllers import MainController
from vidalign.views.main_view import MainView

app = QApplication()


def parse_args():
    parser = ArgumentParser(
        description='Run encoding tasks from a videoclip config file')
    parser.add_argument('path', help='Path to the videoclip config file')
    parser.add_argument('--recurse', action='store_true',
                        help='Recursively search subdirectories')
    parser.add_argument('--skip-existing', action='store_true',
                        help='Skip output video files that already exist')
    return parser.parse_args()


def run(p, skip_existing):
    model = Model()
    main_controller = MainController(model)
    main_view = MainView(model, main_controller)

    main_view._config_view._controller.on_load_encoder_config(p)

    def print_prog(percent, lines):
        print(percent)
        for line in lines:
            print(line, flush=True)
    model.encoding_progress_changed.connect(print_prog)

    model.start_encoding_tasks(skip_existing=skip_existing)

    sleep(0.25)

    def fmt_line(percent, line):
        return f'Total: {int(round(percent * 100))}% | Task: {line}'

    last_line = 'Starting...'
    while model.encoding_percentage < 1:
        if len(model.encoding_stdout_lines) > 0:
            new_line = fmt_line(model.encoding_percentage,
                                model.encoding_stdout_lines[-1])
            if new_line != last_line:
                print(new_line, end='\r', flush=True)
                last_line = new_line
        sleep(0.25)
    print('Finished!')


def run_dir(p, recurse, skip_existing):
    """
    Find files ending with .vc.json and run them. If recurse is True, search subdirectories.
    If skip_existing is True, don't write video files that already exist.
    """
    paths = []
    for root, dirs, files in os.walk(p):
        for f in files:
            if f.endswith('.vc.json'):
                paths.append(os.path.join(root, f))
        if not recurse:
            break
    for i, p in enumerate(paths):
        print(f'Running for file {i+1}/{len(paths)}: {p}')
        run(p, skip_existing)


if __name__ == '__main__':
    args = parse_args()

    p = args.path

    if os.path.isdir(p):
        run_dir(p, args.recurse, args.skip_existing)
    else:
        if args.recurse:
            print('Ignoring --recurse flag as you did not select a directory')
        run(p, args.skip_existing)
