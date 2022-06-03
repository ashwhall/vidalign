from PySide6 import QtWidgets, QtCore

from vidalign.controllers import ConfigController
from vidalign.model import Model
from vidalign.constants import COLOURS
from vidalign.widgets import EncodingConfig, VideoClipConfig


class ConfigView(QtWidgets.QWidget):
    def __init__(self, model: Model, controller: ConfigController):
        super().__init__()
        self._model = model
        self._controller = controller

        self.layout = QtWidgets.QVBoxLayout()

        self._encoding_config = EncodingConfig(self._model.output_directory, self._model.encoders, self._model.current_encoder)
        self.layout.addWidget(self._encoding_config)

        self._video_clip_config = VideoClipConfig(self._model.output_directory)
        self.layout.addWidget(self._video_clip_config)

        self.setObjectName('config')
        self.setStyleSheet(f"""
            QFrame#config {{
                border: 2px solid {COLOURS['neutral']};
                border-radius: 5px;
            }}
        """)
        
        self.setLayout(self.layout)

        self.connect_signals()

    
    def connect_signals(self):
        # Connect widgets to controller
        self._encoding_config.on_view_encode_commands.connect(self._controller.on_view_encode_commands)
        self._encoding_config.on_run_encode_commands.connect(self._controller.on_run_encode_commands)
        self._encoding_config.on_cancel_encode.connect(self._controller.on_cancel_encode)
        self._encoding_config.on_finalise_encoding.connect(self._controller.on_finalise_encoding)
        self._encoding_config.on_encoder_changed.connect(self._controller.on_current_encoder_changed)
        self._encoding_config.on_load.connect(self.on_load_encoder_config)
        self._encoding_config.on_save.connect(self.on_save_encoder_config)
        self._encoding_config.on_load_default.connect(self._controller.on_load_default)

        self._video_clip_config.on_output_directory_changed.connect(self._controller.on_output_directory_changed)
        self._video_clip_config.on_load.connect(self.on_load_video_clip_config)
        self._video_clip_config.on_save.connect(self.on_save_video_clip_config)
        self._video_clip_config.on_reset.connect(self._controller.on_reset_video_clip_config)

        # Listen for model event signals
        self._model.output_directory_changed.connect(self._video_clip_config._update_output_dir)
        self._model.output_directory_changed.connect(self._encoding_config._update_output_dir)
        self._model.encoding_progress_changed.connect(self._encoding_config._update_encoding_progress)
        self._model.encoder_dict_changed.connect(self._encoding_config._update_encoders)
        self._model.current_encoder_changed.connect(self._encoding_config._update_current_encoder)

    @QtCore.Slot()
    def on_load_video_clip_config(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter('Video/Clip JSON Files (*.vc.json)')
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        file_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        file_dialog.setWindowTitle('Load Video/Clip Config')
        file_dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, False)

        file_dialog.fileSelected.connect(self._controller.on_load_video_clip_config)
        file_dialog.exec()


    @QtCore.Slot()
    def on_save_video_clip_config(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter('Video/Clip JSON Files (*.vc.json)')
        file_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        file_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setWindowTitle('Save Video/Clip Config')
        file_dialog.setDefaultSuffix('vc.json')

        file_dialog.fileSelected.connect(self._controller.on_save_video_clip_config)
        file_dialog.exec()

    
    @QtCore.Slot()
    def on_load_encoder_config(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter('Encoder JSON Files (*.enc.json)')
        file_dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        file_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        file_dialog.setWindowTitle('Load Encoder Config')
        file_dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, False)

        file_dialog.fileSelected.connect(self._controller.on_load_encoder_config)
        file_dialog.exec()


    @QtCore.Slot()
    def on_save_encoder_config(self):
        file_dialog = QtWidgets.QFileDialog()
        file_dialog.setNameFilter('Encoder JSON Files (*.enc.json)')
        file_dialog.setFileMode(QtWidgets.QFileDialog.AnyFile)
        file_dialog.setViewMode(QtWidgets.QFileDialog.Detail)
        file_dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        file_dialog.setWindowTitle('Save Encoder Config')
        file_dialog.setDefaultSuffix('enc.json')

        file_dialog.fileSelected.connect(self._controller.on_save_encoder_config)
        file_dialog.exec()