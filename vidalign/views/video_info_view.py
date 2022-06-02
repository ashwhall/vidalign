from PySide6 import QtWidgets, QtCore

from vidalign.controllers import VideoInfoController
from vidalign.widgets import VideoInfo
from vidalign.model.model import Model
from vidalign.widgets.text_field_dialog import TextFieldDialog


class VideoInfoView(QtWidgets.QWidget):
    def __init__(self, model: Model, controller: VideoInfoController):
        super().__init__()
        self._model = model
        self._controller = controller

        self.layout = QtWidgets.QVBoxLayout()
        self._video_info = VideoInfo(self._model.current_video)
        self.layout.addWidget(self._video_info)
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.connect_signals()

    def connect_signals(self):
        # Connect widgets to controller
        self._video_info.sync_frame_set.connect(self._controller.on_sync_frame_set)
        self._video_info.video_removed.connect(self._controller.on_current_video_removed)
        self._video_info.jump_to_sync_frame.connect(self._controller.on_jump_to_sync_frame)
        self._video_info.set_video_alias.connect(self.on_set_video_alias)

        # Listen for model event signals
        self._model.current_video_changed.connect(self.on_current_video_changed)

    @QtCore.Slot(list)
    def on_current_video_changed(self, value):
        self._video_info.set_video(value)

    
    @QtCore.Slot()
    def on_set_video_alias(self):
        if not self._model.current_video:
            return

        dialog = TextFieldDialog('Video alias', self._model.current_video.alias)
        dialog.submitted.connect(self._controller.on_set_video_alias)
        dialog.exec()
