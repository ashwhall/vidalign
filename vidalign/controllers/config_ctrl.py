import json

from PySide6 import QtCore, QtWidgets

from vidalign.model import Model
from vidalign.utils.encoders.encoder import Encoder


class ConfigController(QtCore.QObject):
    def __init__(self, model: Model):
        super().__init__()

        self._model = model

    @QtCore.Slot()
    def on_reset_video_clip_config(self):
        self._model.reset_video_clip_config()

    @QtCore.Slot()
    def on_load_video_clip_config(self, file_path):
        if file_path:
            with open(file_path, 'r') as f:
                data = json.load(f)
            self._model.from_dict(data)
            if self._model.current_video is None and self._model.videos:
                self._model.current_video = self._model.videos[0]
            if self._model.current_clip is None and self._model.clips:
                self._model.current_clip = self._model.clips[0]

    @QtCore.Slot()
    def on_save_video_clip_config(self, file_path):
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(self._model.video_clip_dict(), f, indent=2)

    @QtCore.Slot()
    def on_load_encoder_config(self, file_path):
        if file_path:
            with open(file_path, 'r') as f:
                data = json.load(f)
            self._model.from_dict(data)

    @QtCore.Slot()
    def on_save_encoder_config(self, file_path):
        if file_path:
            with open(file_path, 'w') as f:
                json.dump(self._model.encoders_dict(), f, indent=2)

    @QtCore.Slot()
    def on_view_encode_commands(self):
        is_ready, not_ready_msg = self._model.ready_to_encode()
        if not is_ready:
            QtWidgets.QMessageBox.warning(
                None,
                'Not ready to encode',
                f'Cannot start encoding: {not_ready_msg}'
            )
            return

        # Display the commands in a dialog, one per line
        cmds = self._model.get_encode_commands()
        if any(callable(cmd) for cmd in cmds):
            QtWidgets.QMessageBox.information(
                None,
                'No encode command for the selected encoder',
                'The selected encoder does not have an encode command. '
                'This is likely as it\'s a custom encoder, which can only be '
                'run within the VidAlign GUI.'
            )
            return
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle('FFmpeg commands')
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.resize(500, 500)
        layout = QtWidgets.QVBoxLayout()
        text_edit = QtWidgets.QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setPlainText('\n'.join([' '.join(cmd) for cmd in cmds]))
        layout.addWidget(text_edit)

        # Add a copy-to-clipboard button
        button = QtWidgets.QPushButton('Copy to clipboard')
        button.clicked.connect(
            lambda: QtWidgets.QApplication.clipboard().setText(text_edit.toPlainText()))
        layout.addWidget(button)

        dialog.setLayout(layout)
        dialog.exec()

    @QtCore.Slot()
    def on_run_encode_commands(self, skip_existing: bool):
        is_ready, not_ready_msg = self._model.ready_to_encode()
        if not is_ready:
            QtWidgets.QMessageBox.warning(
                None,
                'Not ready to encode',
                f'Cannot start encoding: {not_ready_msg}'
            )
            return

        self._model.start_encoding_tasks(skip_existing)

    @QtCore.Slot()
    def on_cancel_encode(self):
        self._model.cancel_encoding_tasks()

    @QtCore.Slot()
    def on_finalise_encoding(self):
        self._model.finalise_encoding()

    @QtCore.Slot()
    def on_output_directory_changed(self, path):
        self._model.output_directory = path

    @QtCore.Slot()
    def on_encoding_progress_changed(self, value):
        self._model.encoding_progress = value

    @QtCore.Slot(Encoder)
    def on_current_encoder_changed(self, value):
        self._model.current_encoder = value

    @QtCore.Slot()
    def on_load(self):
        pass

    @QtCore.Slot()
    def on_save(self):
        pass

    @QtCore.Slot()
    def on_load_default(self):
        self._model.current_encoder.reset_params_to_default()
        self._model.current_encoder = self._model.current_encoder
