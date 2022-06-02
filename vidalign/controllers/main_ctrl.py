from PySide6 import QtCore


class MainController(QtCore.QObject):
    def __init__(self, model):
        super().__init__()

        self._model = model

    @QtCore.Slot(list)
    def on_videos_dropped(self, videos):
        self._model.videos = videos