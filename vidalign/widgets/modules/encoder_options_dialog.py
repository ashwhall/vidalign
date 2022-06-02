from functools import partial
from PySide6 import QtWidgets, QtCore
from vidalign.widgets.modules import StyledButton
from vidalign.utils.encoders import Encoder


class EncoderOptionsDialog(QtWidgets.QDialog):
    on_save_encoder_options = QtCore.Signal(Encoder)

    def __init__(self, encoder: Encoder):
        super().__init__()
        self._encoder = encoder

        self.setWindowTitle(f'Encoder Options ({encoder.name})')
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setMinimumWidth(720)
        self.layout = QtWidgets.QVBoxLayout()

        encoder_param_dict = self._encoder.enc_params

        # self.layout.addWidget(QtWidgets.QLabel('Parameters'))

        self.param_grid = QtWidgets.QGridLayout()
        self.param_grid.addWidget(self.bold_label('Name'), 0, 0)
        self.param_grid.addWidget(self.bold_label('Flag'), 0, 1)
        self.param_grid.addWidget(self.bold_label('Value'), 0, 2)
        self.param_grid.addWidget(self.bold_label('Default'), 0, 3, 1, 2)
        # One label and editable text field per param
        for i, (param_name, param) in enumerate(encoder_param_dict.items()):
            row = i + 1
            name_lbl  = QtWidgets.QLabel(str(param_name))
            name_lbl.setToolTip(str(param.hint))
            self.param_grid.addWidget(name_lbl, row, 0)
            flag_lbl  = QtWidgets.QLabel(str(param.flag))
            self.param_grid.addWidget(flag_lbl, row, 1)
            value_edit = QtWidgets.QLineEdit(str(param.value) if param.value is not None else '')
            self.param_grid.addWidget(value_edit, row, 2)
            default_lbl = QtWidgets.QLabel(str(param.default))
            self.param_grid.addWidget(default_lbl, row, 3)
            reset_btn = StyledButton('Restore default', StyledButton.Style.NEGATIVE)
            reset_btn.setMinimumWidth(140)
            reset_btn.clicked.connect(partial(self.reset_param, param_name))
            self.param_grid.addWidget(reset_btn, row, 4)

        # Make all param_grid widgets the same height
        for i in range(self.param_grid.rowCount()):
            for j in range(self.param_grid.columnCount()):
                if item := self.param_grid.itemAtPosition(i, j):
                    item.widget().setFixedHeight(30)

        self.layout.addLayout(self.param_grid)

        btn_layout = QtWidgets.QHBoxLayout()
        # Cancel button
        self.cancel_btn_widget = StyledButton('Cancel', StyledButton.Style.NEGATIVE)
        self.cancel_btn_widget.clicked.connect(self.close)
        btn_layout.addWidget(self.cancel_btn_widget)
        # Save button
        self.save_btn_widget = StyledButton('Save', StyledButton.Style.POSITIVE)
        self.save_btn_widget.clicked.connect(self.save_encoder_options)
        btn_layout.addWidget(self.save_btn_widget)
        self.layout.addLayout(btn_layout)

        self.setLayout(self.layout)

    @classmethod
    def bold_label(cls, text):
        lbl = QtWidgets.QLabel(text)
        font = lbl.font()
        font.setBold(True)
        lbl.setFont(font)
        return lbl

    @QtCore.Slot()
    def save_encoder_options(self):
        # Get the new value from each row in the grid
        for row in range(1, self.param_grid.rowCount()):
            param_name = self.param_grid.itemAtPosition(row, 0).widget().text()
            value = self.param_grid.itemAtPosition(row, 2).widget().text()

            self._encoder.set_param(param_name, value)
        
        self.on_save_encoder_options.emit(self._encoder)
        self.close()

    @QtCore.Slot(str)
    def reset_param(self, param_name):
        self._encoder.reset_param_to_default(param_name)

        for i in range(self.param_grid.rowCount()):
            if self.param_grid.itemAtPosition(i, 0).widget().text() == param_name:
                self.param_grid.itemAtPosition(i, 2).widget().setText(self._encoder.enc_params[param_name].value)
                break