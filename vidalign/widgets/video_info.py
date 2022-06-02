from PySide6 import QtCore
from PySide6.QtWidgets import (QLabel, QFrame,
                               QHBoxLayout, QSizePolicy)
from vidalign.constants import COLOURS
from vidalign.widgets.modules import StyledButton


class VideoInfo(QFrame):
    set_video_alias = QtCore.Signal()
    sync_frame_set = QtCore.Signal()
    video_removed = QtCore.Signal()
    jump_to_sync_frame = QtCore.Signal()

    def __init__(self, video):
        super().__init__()
        self.video = video

        self.layout = QHBoxLayout()

        self.label = QLabel()
        self.layout.addWidget(self.label)

        rename_button = StyledButton('Set Alias')
        rename_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        rename_button.setMinimumWidth(150)
        rename_button.clicked.connect(self.set_video_alias)
        self.layout.addWidget(rename_button)

        set_sync_button = StyledButton('Jump to Sync Frame')
        set_sync_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        set_sync_button.setMinimumWidth(150)
        set_sync_button.clicked.connect(self.on_jump_to_sync_frame)
        self.layout.addWidget(set_sync_button)

        set_sync_button = StyledButton('Set Sync Frame', StyledButton.Style.PRIMARY)
        set_sync_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        set_sync_button.setMinimumWidth(120)
        set_sync_button.clicked.connect(self.on_set_sync_frame)
        self.layout.addWidget(set_sync_button)

        remove_button = StyledButton('Remove Video', StyledButton.Style.NEGATIVE)
        remove_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        remove_button.setMinimumWidth(115)
        remove_button.clicked.connect(self.on_remove_video)
        self.layout.addWidget(remove_button)

        self.update_ui()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(50)

        self.setObjectName('videoInfo')
        self.setStyleSheet(f"""
                QFrame#videoInfo {{
                border: 2px solid {COLOURS['neutral']};
                border-radius: 5px;
            }}
        """)

        self.setLayout(self.layout)

    def on_set_sync_frame(self):
        self.sync_frame_set.emit()

    def on_jump_to_sync_frame(self):
        self.jump_to_sync_frame.emit()

    def on_remove_video(self):
        self.video_removed.emit()

    def set_video(self, video):
        self.video = video
        self.update_ui()

    def update_ui(self):
        if self.video:
            self.label.setText(f'Selected: {self.video.name}')
        else:
            self.label.setText('No video selected')
