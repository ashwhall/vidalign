"""
A crude script to run encode tasks by loading a videoclip config file and printing progress to stdout.
"""


from time import sleep
from sys import argv
from PySide6.QtWidgets import QApplication
from vidalign.model import Model
from vidalign.controllers import MainController
from vidalign.views.main_view import MainView


def main(p):
    app = QApplication()
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
                print(new_line, end='\r')
                last_line = new_line
        sleep(0.25)
    print('Finished!')


if __name__ == '__main__':
    p = argv[1]
    main(p)
