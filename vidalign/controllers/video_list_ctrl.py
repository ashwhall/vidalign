from PySide6 import QtCore

from vidalign.model.model import Model


class VideoListController(QtCore.QObject):
    def __init__(self, model: Model):
        super().__init__()

        self._model = model

    @QtCore.Slot(list)
    def on_video_selected(self, value):
        self._model.current_video = value
