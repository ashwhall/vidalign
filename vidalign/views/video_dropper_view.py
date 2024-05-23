from PySide6 import QtWidgets
from PySide6.QtCore import Slot

from vidalign.controllers import VideoDropperController
from vidalign.model import Model
from vidalign.widgets import VideoDropper


class VideoDropperView(QtWidgets.QWidget):
    def __init__(self, model: Model, controller: VideoDropperController):
        super().__init__()
        self._model = model
        self._controller = controller

        self.layout = QtWidgets.QVBoxLayout()
        self._video_dropper = VideoDropper()
        self.layout.addWidget(self._video_dropper)
        self.setLayout(self.layout)

        self.connect_signals()

    def connect_signals(self):
        self._video_dropper.videos_dropped.connect(self._on_videos_dropped)

    @Slot(list)
    def _on_videos_dropped(self, value):
        self._controller.on_videos_dropped(value)
