import os

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QStyle

from vidalign.constants import COLOURS
from vidalign.widgets.modules import StyledButton


class VideoClipConfig(QtWidgets.QFrame):
    on_load = QtCore.Signal()
    on_save = QtCore.Signal()
    on_reset = QtCore.Signal()
    on_output_directory_changed = QtCore.Signal(str)

    def __init__(self, output_dir):
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()

        title_label = QtWidgets.QLabel('Videos/Clips')
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setFixedHeight(30)

        self.layout.addWidget(title_label)

        self.layout.addLayout(self._make_file_handling_layout())

        self.layout.addLayout(self._make_output_directory_layout())

        self.setObjectName('vcconfig')
        self.setStyleSheet(f"""
            QFrame#vcconfig {{
                border: 2px solid {COLOURS['neutral']};
                border-radius: 5px;
            }}
        """)

        self._update_output_dir(output_dir)

        self.setLayout(self.layout)

    def _update_output_dir(self, output_dir):
        label_txt = self.ellipsize_path(
            output_dir) if output_dir else 'Not set'
        tooltip_txt = output_dir or 'No output directory set'

        self.output_dir_label.setText(label_txt)
        self.output_dir_label.setToolTip(tooltip_txt)

    @classmethod
    def ellipsize_path(cls, path, max_len=30):
        # Remove directories from a path and replace with ellipses, prioritising the tail of the path
        out_path = path

        if len(path) > max_len:
            parts = os.path.normpath(path).split(os.path.sep)

            # Iterate over the path, alternating between adding the left and right missing parts
            i = 0
            left_idx = 1
            right_idx = len(parts) - 1

            prospective_str = os.path.sep.join(
                (*parts[:left_idx], '...', *parts[right_idx:]))
            out_path = prospective_str
            while len(prospective_str) < max_len:
                out_path = prospective_str
                if i % 2 == 0:
                    left_idx += 1
                else:
                    right_idx -= 1
                prospective_str = os.path.sep.join(
                    (*parts[:left_idx], '...', *parts[right_idx:]))
                i += 1

        return out_path

    def _make_file_handling_layout(self):
        layout = QtWidgets.QVBoxLayout()

        btn_layout = QtWidgets.QHBoxLayout()

        load_btn = StyledButton(None)
        load_btn.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogOpenButton
        ))
        load_btn.setToolTip('Load clips')
        load_btn.clicked.connect(self.on_load)
        btn_layout.addWidget(load_btn)

        save_btn = StyledButton(None)
        save_btn.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_DialogSaveButton
        ))
        save_btn.setToolTip('Save clips')
        save_btn.clicked.connect(self.on_save)
        btn_layout.addWidget(save_btn)

        save_btn = StyledButton(None)
        save_btn.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_BrowserReload
        ))
        save_btn.setToolTip('Reset clips')
        save_btn.clicked.connect(self.on_reset)
        btn_layout.addWidget(save_btn)

        layout.addLayout(btn_layout)

        return layout

    def _make_output_directory_layout(self):
        """A directory selection dialog for the output directory."""
        layout = QtWidgets.QHBoxLayout()

        self.output_dir_label = QtWidgets.QLabel()
        self.output_dir_label.setText('Output directory: not set')
        layout.addWidget(self.output_dir_label)

        # Picker using QFileDialog
        self.file_dialog = QtWidgets.QFileDialog()
        self.file_dialog.setFileMode(QtWidgets.QFileDialog.Directory)
        self.file_dialog.setOption(QtWidgets.QFileDialog.ShowDirsOnly, True)
        self.file_dialog.setWindowTitle('Select output directory')
        self.file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)

        # Connect the signal
        self.file_dialog.fileSelected.connect(self.on_output_directory_changed)

        # Add the button
        btn = StyledButton('Select output directory')
        btn.clicked.connect(self.on_browse_button_clicked)
        layout.addWidget(btn)

        return layout

    @QtCore.Slot()
    def on_browse_button_clicked(self):
        self.file_dialog.exec()
