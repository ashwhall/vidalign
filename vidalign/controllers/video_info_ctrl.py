from PySide6 import QtCore

from vidalign.model import Model


class VideoInfoController(QtCore.QObject):
    def __init__(self, model: Model):
        super().__init__()

        self._model = model

    @QtCore.Slot(list)
    def on_sync_frame_set(self):
        self._model.set_current_video_sync_frame()

    @QtCore.Slot(list)
    def on_current_video_removed(self):
        self._model.remove_current_video()

    @QtCore.Slot()
    def on_jump_to_sync_frame(self):
        if self._model.current_video and self._model.current_video.sync_frame is not None:
            self._model.seek_absolute(self._model.current_video.sync_frame)

    @QtCore.Slot(str)
    def on_set_video_alias(self, alias):
        self._model.set_current_video_alias(alias)