from dataclasses import dataclass
from ipaddress import collapse_addresses
from typing import Generic, List, Type, TypeVar

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtWidgets import QTableWidget, QTableWidgetItem

T = TypeVar('T')


class TableWidget(QTableWidget, Generic[T]):

    @dataclass
    class Column:
        title: str
        key: str
        width: float
        placeholder: str = '--'
        type: Type = str

    # Just pretend that it's a `T` instead of `object`
    item_selected = QtCore.Signal(object)
    item_double_clicked = QtCore.Signal(object)

    def __init__(self, columns: List[Column], data: List[T] = []):
        super().__init__()
        # Disallow editing
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        # Select the whole row instead of indidivual cells
        self.setSelectionBehavior(QTableWidget.SelectRows)
        # Only allow selection of one row at a time
        self.setSelectionMode(QTableWidget.SingleSelection)

        self.columns = columns
        self.data: List[T] = data
        self.selected_row = -1
        self.update_rows(self.data)
        self.itemSelectionChanged.connect(self.selectionChanged)
        self.cellDoubleClicked.connect(self.onDoubleClick)

    def resizeEvent(self, event):
        for i, column in enumerate(self.columns):
            self.setColumnWidth(i, column.width * self.width())
        super().resizeEvent(event)

    # Single click
    def selectionChanged(self, selected=None, deselected=None):
        if self.selectedItems():
            self.selected_row = self.row(self.selectedItems()[0])
            self.item_selected.emit(self.data[self.selected_row])

    # Double click
    def onDoubleClick(self, row, column):
        if 0 <= row < len(self.data):
            self.item_double_clicked.emit(self.data[row])

    def set_selected_item(self, item: T):
        if item is None:
            self.selected_row = -1
        else:
            self.selected_row = self.data.index(item)
        self.update_rows(self.data)

    def update_rows(self, data: List[T] = []):
        requires_refresh = len(data) != len(self.data)
        if requires_refresh:
            self.clear()

        self.data = data
        self.setRowCount(len(self.data))

        self.setColumnCount(len(self.columns))
        self.setHorizontalHeaderLabels(col.title for col in self.columns)

        if self.selected_row >= len(self.data):
            self.selected_row -= 1

        for i, item in enumerate(self.data):
            for j, column in enumerate(self.columns):
                value = getattr(item, column.key, None)
                # Check if it's a function
                if callable(value):
                    value = value()

                if value is None:
                    value = column.placeholder

                if column.type == str:
                    widg_item = QTableWidgetItem(str(value))
                    self.setItem(i, j, widg_item)
                elif column.type == QtGui.QImage and value is not None:
                    widg_item = QtWidgets.QLabel()
                    widg_item.setPixmap(QtGui.QPixmap(value))
                    widg_item.setAlignment(
                        QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)
                    self.setCellWidget(i, j, widg_item)
                    # Increase the height of the row to fit the image
                    if value.height() > self.rowHeight(i):
                        self.setRowHeight(i, value.height())

            if i == self.selected_row:
                self.setVerticalHeaderItem(i, QTableWidgetItem('>'))
                if requires_refresh:
                    self.selectRow(i)
            else:
                self.setVerticalHeaderItem(i, QTableWidgetItem(str(i)))

    @QtCore.Slot()
    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        row = self.rowAt(event.y())
        if row >= 0:
            self.item_selected.emit(self.data[row])
            self.selected_row = row
