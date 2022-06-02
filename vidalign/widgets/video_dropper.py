import os

from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QLabel,
                               QHBoxLayout, QWidget, QSizePolicy)
from vidalign.constants import COLOURS

class VideoDropper(QWidget):
    ACCEPTED_EXTENSIONS = (
        'mp4',
        'avi',
        'mkv',
        'mov',
        'mxf',
    )
    videos_dropped = QtCore.Signal(list)

# TODO: Select the clip if it's the first created
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.label = QLabel(self)
        self.label.setText('Drop videos here')

        self.layout.addWidget(self.label)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        self._reset()

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.minimumWidth = 150
        self.label.setMinimumWidth(self.minimumWidth)

        self.setLayout(self.layout)

    def set_style(self, style):
        self.setStyleSheet(f"""
            QWidget {{
                border: 3px dashed {COLOURS[style]};
                border-radius: 5px;
            }}
        """)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls and self.video_urls_from_event(event):
            self.label.setText('Drop to add video(s)')
            self.set_style('positive')
        else:
            self.label.setText('No videos found')
            self.set_style('negative')
        event.accept()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls:
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    @classmethod
    def video_urls_from_event(cls, event):
        """Get the fully-resolved paths of the dropped files, descending directories if necessary."""
        urls = []
        event_urls = [str(url.toLocalFile()) for url in event.mimeData().urls()]

        idx = 0
        while idx < len(event_urls):
            url = event_urls[idx]
            if url.lower().endswith(cls.ACCEPTED_EXTENSIONS):
                urls.append(url)
            elif os.path.isdir(url):
                event_urls.extend([
                    os.path.join(url, sub_url)
                    for sub_url in os.listdir(url)])
            idx += 1

        return urls

    def dropEvent(self, event):
        if event.mimeData().hasUrls and (urls := self.video_urls_from_event(event)):
            event.setDropAction(Qt.CopyAction)
            event.accept()
            self.videos_dropped.emit(urls)
        else:
            event.ignore()
        self._reset()

    def _reset(self):
        self.label.setText('Drop videos here')
        self.set_style('neutral')

    # Reset after finished dropping
    def dragLeaveEvent(self, event):
        self._reset()
        event.accept()
