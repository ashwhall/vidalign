from PySide6.QtWidgets import QApplication
from vidalign.model import Model
from vidalign.controllers import MainController
from vidalign.views.main_view import MainView


def main():
    app = QApplication()
    model = Model()
    main_controller = MainController(model)
    main_view = MainView(model, main_controller)
    main_view.show()
    app.exec()


if __name__ == '__main__':
    main()
