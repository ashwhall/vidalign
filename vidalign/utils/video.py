import os
from dataclasses import dataclass
from vidalign.utils.video_reader import VideoReader
from PySide6.QtGui import QImage, QPixmap, QKeySequence


@dataclass
class Video:
    path: str
    alias: str = None
    sync_frame: int = None
    _reader: VideoReader = None
    _qt_thumb = None

    @property
    def reader(self):
        if self._reader is None:
            self._reader = VideoReader(self.path)
        self._reader.open()
        return self._reader

    def close(self):
        self._reader.close()

    def preload_metadata(self):
        _ = len(self)
        _ = self.qt_thumb

    @property
    def qt_thumb(self):
        if self._qt_thumb is None:
            thumb_img = self.reader.get_thumbnail()
            height, width, _ = thumb_img.shape
            bytesPerLine = 3 * width
            self._qt_thumb = QImage(thumb_img, width, height, bytesPerLine, QImage.Format_RGB888)
        return self._qt_thumb

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def frame_rate(self):
        return self.reader.fps

    def __len__(self):
        return len(self.reader)

    def abs_to_rel(self, frame):
        """Convert an absolute frame number to sync-frame-relative"""
        if self.sync_frame is None:
            return None
        return frame - self.sync_frame

    def rel_to_abs(self, frame):
        """Convert a sync-frame-relative frame number to absolute"""
        if self.sync_frame is None:
            return None
        return frame + self.sync_frame
    
    def frames_to_seconds(self, frame):
        return self.reader.frames_to_seconds(frame)
        
    def seconds_to_timestamp(self, seconds: float):
        """Seconds to HH:MM:SS.mmm"""
        hours = int(seconds / 3600)
        minutes = int((seconds - hours * 3600) / 60)
        seconds = seconds - hours * 3600 - minutes * 60
        return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

    def complete(self):
        return self.path is not None and len(self) and self.sync_frame is not None and self.alias is not None

    def to_dict(self):
        return {
            'path': self.path,
            'frame_count': len(self),
            'sync_frame': self.sync_frame,
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            path=data['path'],
            frame_count=data['frame_count'],
            sync_frame=data['sync_frame'],
        )