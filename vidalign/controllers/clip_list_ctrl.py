from PySide6 import QtCore

from vidalign.model import Model


class ClipListController(QtCore.QObject):
    def __init__(self, model: Model):
        super().__init__()

        self._model = model

    @QtCore.Slot(list)
    def on_clip_selected(self, clip):
        self._model.current_clip = clip

    @QtCore.Slot(list)
    def on_clip_double_clicked(self, clip):
        if clip is not None:
            self._model.seek_absolute_frame_rel(
                clip.start_frame)
