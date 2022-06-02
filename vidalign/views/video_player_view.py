from PySide6 import QtWidgets, QtCore

from vidalign.controllers import VideoPlayerController
from vidalign.model.model import Model
from vidalign.utils.video import Video
from vidalign.widgets.modules import VideoPlayer


class VideoPlayerView(QtWidgets.QWidget):
    def __init__(self, model: Model, controller: VideoPlayerController):
        super().__init__()
        self._model = model
        self._controller = controller

        self.layout = QtWidgets.QVBoxLayout()
        self._video_player = VideoPlayer()
        self.layout.addWidget(self._video_player)
        self.setLayout(self.layout)

        self.connect_signals()

    def connect_signals(self):
        # Connect widgets to controller
        self._video_player.frame_changed.connect(self._controller.on_frame_changed)

        self._video_player.video_started.connect(self._controller.on_video_started)
        self._video_player.video_paused.connect(self._controller.on_video_paused)
        self._video_player.video_stopped.connect(self._controller.on_video_stopped)
        self._video_player.video_play_pause_toggle.connect(self._controller.on_video_play_pause)

        self._video_player.video_seeked_relative.connect(self._controller.on_seek_relative)
        self._video_player.video_seeked_absolute.connect(self._controller.on_seek_absolute)

        # Listen for model event signals
        self._model.current_frame_changed.connect(self.on_frame_changed)
        self._model.current_video_changed.connect(self.on_video_changed)
        self._model.video_started.connect(lambda: self.video_started_or_stopped(True))
        self._model.video_paused.connect(lambda: self.video_started_or_stopped(False))
        self._model.video_stopped.connect(lambda: self.video_started_or_stopped(False))

    @QtCore.Slot(Video)
    def on_video_changed(self, video):
        if video:
            self._model.ensure_frame_in_bounds()
            self._video_player.draw(video, self._model.current_frame)
        else:
            self._video_player.clear()

    @QtCore.Slot(list)
    def on_frame_changed(self, frame_num):
        if self._model.current_video:
            self._video_player.draw(self._model.current_video, frame_num)

    @QtCore.Slot(bool)
    def video_started_or_stopped(self, playing):
        self._video_player.started_or_stopped_playing(playing)
