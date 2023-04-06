import os
from dataclasses import dataclass, field
from typing import Dict, Optional
from scipy.interpolate import interp1d
from PySide6.QtGui import QImage
from vidalign.utils.video_reader import VideoReader


@dataclass
class Box:
    x0: int
    y0: int
    x1: int
    y1: int

    def to_dict(self):
        return [self.x0, self.y0, self.x1, self.y1]

    @classmethod
    def from_dict(cls, data):
        return cls(
            x0=data[0],
            y0=data[1],
            x1=data[2],
            y1=data[3],
        )

    @property
    def x0y0(self):
        return [self.x0, self.y0]

    @property
    def x1y1(self):
        return [self.x1, self.y1]

    @property
    def xyxy(self):
        return [self.x0, self.y0, self.x1, self.y1]

    @property
    def xywh(self):
        return [self.x0, self.y0, self.w, self.h]

    @property
    def w(self):
        return self.x1 - self.x0

    @property
    def h(self):
        return self.y1 - self.y0


@dataclass
class MovingCrop:
    crop_frames: Dict[int, Box] = field(default_factory=dict)

    def to_dict(self):
        return {
            str(frame): box.to_dict()
            for frame, box in self.crop_frames.items()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            crop_frames={
                int(frame): Box.from_dict(box)
                for frame, box in data.items()
            }
        )

    def remove_crop(self, frame):
        if frame in self.crop_frames:
            del self.crop_frames[frame]

    def add_crop(self, frame, box):
        self.crop_frames[frame] = box

    def get_crop(self, frame):
        if frame in self.crop_frames:
            return self.crop_frames[frame], False

        frames = sorted(self.crop_frames.keys())
        if frame < frames[0]:
            return self.crop_frames[frames[0]], True
        if frame > frames[-1]:
            return self.crop_frames[frames[-1]], True

        # Interpolate
        x0s = [self.crop_frames[f].x0 for f in frames]
        y0s = [self.crop_frames[f].y0 for f in frames]
        x1s = [self.crop_frames[f].x1 for f in frames]
        y1s = [self.crop_frames[f].y1 for f in frames]

        x0_interp = interp1d(frames, x0s, kind='linear')
        y0_interp = interp1d(frames, y0s, kind='linear')
        x1_interp = interp1d(frames, x1s, kind='linear')
        y1_interp = interp1d(frames, y1s, kind='linear')

        return Box(
            x0=int(x0_interp(frame)),
            y0=int(y0_interp(frame)),
            x1=int(x1_interp(frame)),
            y1=int(y1_interp(frame)),
        ), True

    def get_maximum_crop_width(self):
        return max([box.w for box in self.crop_frames.values()])

    def get_maximum_crop_height(self):
        return max([box.h for box in self.crop_frames.values()])


@dataclass
class Video:
    path: str
    alias: str = None
    sync_frame: int = None
    _reader: VideoReader = None
    _qt_thumb = None
    _crop: Optional[MovingCrop] = None

    def __init__(self, path, alias=None, sync_frame=None, crop=None):
        self.path = path
        self.alias = alias
        self.sync_frame = sync_frame
        self._crop = crop

    @property
    def reader(self):
        if self._reader is None:
            self._reader = VideoReader(self.path)
        self._reader.open()
        return self._reader

    @property
    def crop(self):
        if self._crop is None:
            self._crop = MovingCrop()
            self._crop.add_crop(0, Box(0, 0, self.reader.width, self.reader.height))
        return self._crop

    def will_be_cropped(self):
        """Returns True if any of the crop frames are not the full frame"""
        if self.crop is None:
            return False
        return any([box.xyxy != [0, 0, self.reader.width, self.reader.height] for box in self.crop.crop_frames.values()])

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
            'alias': self.alias,
            'frame_count': len(self),
            'sync_frame': self.sync_frame,
            'crop': self.crop.to_dict() if self.crop is not None else None,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            path=data['path'],
            alias=data.get('alias', None),
            sync_frame=data.get('sync_frame', None),
            crop=MovingCrop.from_dict(data['crop']) if data.get('crop', None) is not None else None,
        )
