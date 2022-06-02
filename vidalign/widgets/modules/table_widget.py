from dataclasses import dataclass
from typing import TypeVar, Generic, List
from PySide6.QtWidgets import (QTableWidget, QTableWidgetItem)
from PySide6 import QtCore

T = TypeVar('T')


class TableWidget(QTableWidget, Generic[T]):

    @dataclass
    class Column:
        title: str
        key: str
        width: float
        placeholder: str = '--'

    item_selected = QtCore.Signal(object)  # Just pretend that it's a `T` instead of `object`

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

    def resizeEvent(self, event):
        for i, column in enumerate(self.columns):
            self.setColumnWidth(i, column.width * self.width())
        super().resizeEvent(event)

    def selectionChanged(self, selected=None, deselected=None):
        if self.selectedItems():
            self.selected_row = self.row(self.selectedItems()[0])
            self.item_selected.emit(self.data[self.selected_row])

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
                if value is None:
                    value = column.placeholder
                self.setItem(i, j, QTableWidgetItem(str(value)))
            
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
