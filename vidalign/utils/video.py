import os
from dataclasses import dataclass
from vidalign.utils.video_reader import VideoReader


@dataclass
class Video:
    path: str
    alias: str = None
    frame_count: int = None
    sync_frame: int = None
    _reader: VideoReader = None

    @property
    def reader(self):
        if self._reader is None:
            self._reader = VideoReader(self.path)
            self.frame_count = len(self._reader)
        self._reader.open()
        return self._reader

    def close(self):
        self._reader.close()

    @property
    def name(self):
        return os.path.basename(self.path)

    @property
    def frame_rate(self):
        return self.reader.fps

    def __len__(self):
        if self.reader is None:
            return None
        return self.frame_count

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
        return self.path is not None and self.frame_count is not None and self.sync_frame is not None and self.alias is not None

    def to_dict(self):
        return {
            'path': self.path,
            'frame_count': self.frame_count,
            'sync_frame': self.sync_frame,
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            path=data['path'],
            frame_count=data['frame_count'],
            sync_frame=data['sync_frame'],
        )