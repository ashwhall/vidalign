from PySide6 import QtCore, QtWidgets

from vidalign.controllers import ClipInfoController
from vidalign.model import Model
from vidalign.widgets import ClipInfo, TextFieldDialog


class ClipInfoView(QtWidgets.QWidget):
    def __init__(self, model: Model, controller: ClipInfoController):
        super().__init__()
        self._model = model
        self._controller = controller

        self.layout = QtWidgets.QVBoxLayout()
        self._clip_info = ClipInfo(self._model.current_clip)
        self.layout.addWidget(self._clip_info)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.connect_signals()

    def connect_signals(self):
        # Connect widgets to controller
        self._clip_info.new_clip.connect(self._controller.on_new_clip)
        self._clip_info.rename_clip.connect(self.on_rename_clip)
        self._clip_info.delete_clip.connect(self._controller.on_delete_clip)

        self._clip_info.set_clip_start.connect(
            self._controller.on_set_clip_start)
        self._clip_info.set_clip_end.connect(self._controller.on_set_clip_end)

        self._clip_info.set_clip_duration.connect(
            self._controller.on_set_clip_duration)

        self._clip_info.jump_clip_start.connect(
            self._controller.on_jump_clip_start)
        self._clip_info.jump_clip_end.connect(
            self._controller.on_jump_clip_end)

        # Listen for model event signals
        self._model.current_clip_changed.connect(self.on_current_clip_changed)

    @QtCore.Slot()
    def on_rename_clip(self):
        if not self._model.current_clip is not None:
            return

        dialog = TextFieldDialog('Clip name', self._model.current_clip.name)
        dialog.submitted.connect(self._controller.on_rename_clip)
        dialog.exec()

    @QtCore.Slot(list)
    def on_current_clip_changed(self, value):
        self._clip_info.set_clip(value)
