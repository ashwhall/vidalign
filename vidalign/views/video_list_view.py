from PySide6 import QtWidgets, QtCore, QtGui
import numpy as np

from vidalign.controllers import VideoListController
from vidalign.model import Model
from vidalign.widgets import TableWidget


class VideoListView(QtWidgets.QWidget):
    def __init__(self, model: Model, controller: VideoListController):
        super().__init__()
        self._model = model
        self._controller = controller


        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        self._table = TableWidget([
            TableWidget.Column('Thumbnail', 'qt_thumb', 0.1, None, type=QtGui.QImage),
            TableWidget.Column('Video', 'name', 0.3),
            TableWidget.Column('Alias', 'alias', 0.3),
            TableWidget.Column('Frames', '__len__', 0.15, '?'),
            TableWidget.Column('Sync Frame', 'sync_frame', 0.15)
        ], self._model.videos)
        
        self.layout.addWidget(self._table)
        self.setLayout(self.layout)

        self.connect_signals()

    def connect_signals(self):
        # Connect widgets to controller
        self._table.item_selected.connect(self._controller.on_video_selected)

        # Listen for model event signals
        self._model.video_list_changed.connect(self.on_video_list_changed)
        self._model.current_video_changed.connect(self.on_current_video_changed)

    @QtCore.Slot(list)
    def on_video_list_changed(self, value):
        self._table.update_rows(value)
    
    @QtCore.Slot(list)
    def on_current_video_changed(self, value):
        self._table.set_selected_item(value)
