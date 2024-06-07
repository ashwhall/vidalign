from typing import List

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QStyle

from vidalign.constants import COLOURS
from vidalign.utils.encoders.encoder import Encoder
from vidalign.widgets import EncodingProgressDialog
from vidalign.widgets.modules import EncoderOptionsDialog, StyledButton


class EncodingConfig(QtWidgets.QFrame):
    on_load = QtCore.Signal()
    on_save = QtCore.Signal()
    on_load_default = QtCore.Signal()

    on_view_encode_commands = QtCore.Signal()
    on_run_encode_commands = QtCore.Signal(bool)
    on_cancel_encode = QtCore.Signal()
    on_finalise_encoding = QtCore.Signal()
    on_encoder_changed = QtCore.Signal(Encoder)

    def __init__(self, output_dir: str, encoders: List[Encoder], current_encoder: Encoder):
        super().__init__()
        self._output_dir = output_dir
        self._encoders = encoders
        self._current_encoder = current_encoder
        self._skip_existing = False

        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addLayout(self._make_encoder_layout())

        options_btn = StyledButton('Encoder options')
        options_btn.clicked.connect(self.on_open_encoder_options)
        self.layout.addWidget(options_btn)
        self.layout.addLayout(self._make_export_buttons())

        self.setObjectName('encconfig')
        self.setStyleSheet(f"""
            QFrame#encconfig {{
                border: 2px solid {COLOURS['neutral']};
                border-radius: 5px;
            }}
        """)

        self.encoding_dialog = None

        self.setLayout(self.layout)

    def _set_skip_existing(self, overwrite: bool):
        self._skip_existing = overwrite

    def _make_encoder_layout(self):
        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel('Encoder Settings')
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setFixedHeight(30)
        layout.addWidget(label)

        # Add a dropdown for the encoder
        encoder_layout = QtWidgets.QHBoxLayout()
        encoder_layout.addWidget(QtWidgets.QLabel('Encoder:'))
        self.encoder_dropdown = QtWidgets.QComboBox()
        encoder_names = [enc.name for enc in self._encoders]
        self.encoder_dropdown.addItems(encoder_names)
        self.encoder_dropdown.setCurrentIndex(
            encoder_names.index(self._current_encoder.name))
        self.encoder_dropdown.currentIndexChanged.connect(
            self._on_encoder_idx_changed)
        encoder_layout.addWidget(self.encoder_dropdown)
        layout.addLayout(encoder_layout)

        btn_layout = QtWidgets.QHBoxLayout()

        load_btn = StyledButton(None)
        load_btn.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogOpenButton
        ))
        load_btn.setToolTip('Load encoding settings')
        load_btn.clicked.connect(self.on_load)
        btn_layout.addWidget(load_btn)

        save_btn = StyledButton(None)
        save_btn.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogSaveButton
        ))
        save_btn.setToolTip('Save encoding settings')
        save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(save_btn)

        reset = StyledButton(None)
        reset.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_BrowserReload
        ))
        reset.setToolTip('Reset encoding settings to default')
        reset.clicked.connect(self.on_load_default)
        btn_layout.addWidget(reset)

        layout.addLayout(btn_layout)

        return layout

    def _make_export_buttons(self):
        layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel('Export')
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setFixedHeight(30)
        layout.addWidget(label)

        view_commands_btn = StyledButton('View encode commands')
        view_commands_btn.clicked.connect(self.on_view_encode_commands)
        layout.addWidget(view_commands_btn)

        skip_existing_check = QtWidgets.QCheckBox('Skip existing')
        skip_existing_check.setChecked(self._skip_existing)
        skip_existing_check.stateChanged.connect(
            self._set_skip_existing
        )
        layout.addWidget(skip_existing_check)

        run_commands_btn = StyledButton('Run encode commands')
        run_commands_btn.clicked.connect(
            lambda: self.on_run_encode_commands.emit(self._skip_existing))
        layout.addWidget(run_commands_btn)

        return layout

    @QtCore.Slot(float, list)
    def _update_encoding_progress(self, percentage: float, stdout_lines: List[str]):
        if percentage is None and self.encoding_dialog:
            # Close the dialog as there's nothing going
            self.encoding_dialog.close()
            self.encoding_dialog = None
        elif self.encoding_dialog is None and percentage is not None:
            # Display the commands in a dialog, one per line
            self.encoding_dialog = EncodingProgressDialog(
                self._output_dir, percentage, stdout_lines)
            self.encoding_dialog.on_cancel_encode.connect(
                self.on_cancel_encode)
            self.encoding_dialog.on_finalise_encoding.connect(
                self.on_finalise_encoding)
            self.encoding_dialog.exec()
        elif self.encoding_dialog and percentage is not None:
            # Update the dialog contents
            self.encoding_dialog.set_values(percentage, stdout_lines)

    def _update_output_dir(self, output_dir):
        self._output_dir = output_dir

    @QtCore.Slot()
    def _update_encoders(self, encoders):
        self._encoders = encoders
        encoder_names = [enc.name for enc in self._encoders]
        self.encoder_dropdown.clear()
        self.encoder_dropdown.addItems(encoder_names)
        self.encoder_dropdown.setCurrentIndex(
            encoder_names.index(self._current_encoder.name))

    def _update_current_encoder(self, encoder):
        self._current_encoder = encoder
        encoder_names = [enc.name for enc in self._encoders]
        self.encoder_dropdown.setCurrentIndex(
            encoder_names.index(self._current_encoder.name))

    @QtCore.Slot()
    def _on_encoder_idx_changed(self, idx):
        self.on_encoder_changed.emit(self._encoders[idx])

    @QtCore.Slot()
    def on_open_encoder_options(self):
        # Display the commands in a dialog, one per line
        self.options_dialog = EncoderOptionsDialog(self._current_encoder)
        self.options_dialog.on_save_encoder_options.connect(
            self.on_encoder_changed)
        self.options_dialog.exec()
