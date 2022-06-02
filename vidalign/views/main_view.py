from PySide6 import QtWidgets, QtCore
from vidalign.controllers import *
from vidalign.model.model import Model
from vidalign.views import *
from PySide6.QtCore import Qt

from vidalign.views import ConfigView


class MainView(QtWidgets.QWidget):
    def __init__(self, model: Model, controller: MainController):
        super().__init__()
        self._model = model
        self._controller = controller

        self.setMinimumSize(QtCore.QSize(640, 480))
        self.resize(1400, 900)
        self.setWindowTitle('Vidalign')

        outer_layout = QtWidgets.QSplitter(Qt.Vertical)

        top_layout = self.make_top_layout()
        outer_layout.addWidget(top_layout)

        bottom_layout = self.make_bottom_layout()
        outer_layout.addWidget(bottom_layout)

        outer_layout.setSizes((0.7 * self.height(), 0.3 * self.height()))

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(outer_layout)
        self.setLayout(layout)

    def make_top_layout(self):
        layout = QtWidgets.QSplitter(Qt.Horizontal)

        video_player_view = VideoPlayerView(self._model, VideoPlayerController(self._model))
        layout.addWidget(video_player_view)

        config_view = ConfigView(self._model, ConfigController(self._model))
        layout.addWidget(config_view)

        layout.setSizes((0.8 * self.width(), 0.2 * self.width()))

        return layout

    def make_bottom_layout(self):
        layout = QtWidgets.QSplitter(Qt.Horizontal)

        video_dropper_view = VideoDropperView(self._model, VideoDropperController(self._model))
        layout.addWidget(video_dropper_view)

        layout.addWidget(self.make_video_column())

        layout.addWidget(self.make_clip_column())

        layout.setSizes((0.1 * self.width(), 0.45 * self.width(), 0.45 * self.width()))
        return layout

    def make_video_column(self):
        layout = QtWidgets.QVBoxLayout()

        video_info_view = VideoInfoView(self._model, VideoInfoController(self._model))
        layout.addWidget(video_info_view)

        video_list_view = VideoListView(self._model, VideoListController(self._model))
        layout.addWidget(video_list_view)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget

    def make_clip_column(self):
        layout = QtWidgets.QVBoxLayout()

        video_info_view = ClipInfoView(self._model, ClipInfoController(self._model))
        layout.addWidget(video_info_view)

        clip_list_view = ClipListView(self._model, ClipListController(self._model))
        layout.addWidget(clip_list_view)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        return widget
