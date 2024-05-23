from PySide6 import QtCore, QtWidgets

from vidalign.controllers import ClipListController
from vidalign.model import Model
from vidalign.widgets import TableWidget


class ClipListView(QtWidgets.QWidget):
    def __init__(self, model: Model, controller: ClipListController):
        super().__init__()
        self._model = model
        self._controller = controller

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self._table = TableWidget([
            TableWidget.Column('Clip', 'name', 0.4),
            TableWidget.Column('Start', 'start_frame', 0.2),
            TableWidget.Column('End', 'end_frame', 0.2),
            TableWidget.Column('Duration', 'duration', 0.2)
        ], self._model.clips)
        self.layout.addWidget(self._table)
        self.setLayout(self.layout)

        self.connect_signals()

    def connect_signals(self):
        # Connect widgets to controller
        self._table.item_selected.connect(self._controller.on_clip_selected)
        self._table.item_double_clicked.connect(
            self._controller.on_clip_double_clicked)

        # Listen for model event signals
        self._model.clip_list_changed.connect(self.on_clip_list_changed)
        self._model.current_clip_changed.connect(self.on_current_clip_changed)

    @QtCore.Slot(list)
    def on_clip_list_changed(self, value):
        self._table.update_rows(value)

    @QtCore.Slot(list)
    def on_current_clip_changed(self, value):
        self._table.set_selected_item(value)
