import fnmatch
import os

from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QLabel, QLineEdit, QSizePolicy, QVBoxLayout,
                               QWidget)

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

    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)

        self.layout = QVBoxLayout()
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

        # A filter text field
        self.filter_field = QLineEdit(self)
        self.filter_field.setPlaceholderText('Filter')
        self.filter_field.setToolTip(
            'Filter videos by filename, use * for wildcard. Default is *')
        self.filter_field.setMinimumWidth(self.minimumWidth)
        self.layout.addWidget(self.filter_field)

        self.setLayout(self.layout)

    def set_style(self, style):
        self.setStyleSheet(f"""
            QLabel {{
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

    def matches_filter(self, filename: str):
        """Returns True if the filename matches the filter"""
        filter_text = self.filter_field.text()
        if not filter_text:
            return True

        return fnmatch.fnmatch(filename, filter_text)

    def video_urls_from_event(self, event):
        """Get the fully-resolved paths of the dropped files, descending directories if necessary."""
        urls = []
        event_urls = [str(url.toLocalFile())
                      for url in event.mimeData().urls()]

        idx = 0
        while idx < len(event_urls):
            url = event_urls[idx]
            basename = os.path.basename(url)
            # Ignore hidden files/folders
            if basename.startswith('.'):
                idx += 1
                continue

            if os.path.isfile(url) and url.lower().endswith(self.ACCEPTED_EXTENSIONS):
                if self.matches_filter(basename):
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
