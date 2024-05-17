from PySide6 import QtCore

from vidalign.model import Model


class ClipInfoController(QtCore.QObject):
    def __init__(self, model: Model):
        super().__init__()

        self._model = model

    @QtCore.Slot()
    def on_new_clip(self):
        self._model.new_clip()
        # Select the newly-created clip
        self._model.current_clip = self._model.clips[-1]

    @QtCore.Slot()
    def on_rename_clip(self, name):
        self._model.rename_clip(self._model.current_clip, name)

    @QtCore.Slot()
    def on_delete_clip(self):
        self._model.delete_clip(self._model.current_clip)

    @QtCore.Slot(int)
    def on_set_clip_start(self):
        if self._model.current_clip is not None:
            self._model.set_clip_start(self._model.current_clip)

    @QtCore.Slot(int)
    def on_set_clip_end(self):
        if self._model.current_clip is not None:
            self._model.set_clip_end(
                self._model.current_clip)

    @QtCore.Slot(int)
    def on_set_clip_duration(self, duration: int):
        if self._model.current_clip is not None and not self._model.current_clip.start_frame is None:
            self._model.set_clip_duration(self._model.current_clip, duration)

    @QtCore.Slot(int)
    def on_jump_clip_start(self):
        if self._model.current_clip is not None:
            self._model.seek_absolute_frame_rel(
                self._model.current_clip.start_frame)

    @QtCore.Slot(int)
    def on_jump_clip_end(self):
        if self._model.current_clip is not None:
            self._model.seek_absolute_frame_rel(
                self._model.current_clip.end_frame)
