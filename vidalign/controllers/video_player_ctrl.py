from PySide6 import QtCore

from vidalign.model import Model


class VideoPlayerController(QtCore.QObject):
    def __init__(self, model: Model):
        super().__init__()

        self._model = model

    @QtCore.Slot()
    def on_video_play_pause(self):
        self._model.play_pause_video()

    @QtCore.Slot(list)
    def on_frame_changed(self, value):
        self._model.current_frame = value

    @QtCore.Slot()
    def on_video_started(self):
        self._model.play_video()

    @QtCore.Slot()
    def on_video_paused(self):
        self._model.pause_video()

    @QtCore.Slot()
    def on_video_stopped(self):
        self._model.stop_video()

    @QtCore.Slot()
    def on_seek_relative(self, frames):
        self._model.seek_relative(frames, pause=True)
    
    @QtCore.Slot()
    def on_seek_absolute(self, frames):
        self._model.seek_absolute(frames)
