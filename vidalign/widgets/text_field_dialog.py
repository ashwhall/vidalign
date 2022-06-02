from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QLabel, QDialog, QDialogButtonBox, QVBoxLayout, QLineEdit)


class TextFieldDialog(QDialog):
    submitted = QtCore.Signal(str)

    def __init__(self, label, initial_value=None):
        super().__init__()
        
        self.setWindowTitle(label)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.setFixedSize(300, 100)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(QLabel(f'{label}: '))

        self.text_field = QLineEdit()
        self.text_field.setText(initial_value)
        self.text_field.setFocus()
        self.text_field.returnPressed.connect(self.accept)
        layout.addWidget(self.text_field)

        layout.addWidget(button_box)

        self.setLayout(layout)

    def accept(self):
        self.submitted.emit(self.text_field.text())
        super().accept()
        