import cv2
import numpy as np
import os


MISSING_FRAME = np.asarray(cv2.imread(os.path.join('vidalign', 'utils', 'missing-frame.jpg')))


class VideoReader:
    def __init__(self, path):
        self.path = path
        self.current_frame = 0

        # Cache one frame to avoid re-reading the same frame
        self.cached_frame = None
        self.cached_frame_number = -1

        self._closed = False
        self._cap = None
        self._frame_count = None
        self.open()
        self.fps = self._cap.get(cv2.CAP_PROP_FPS)

    def open(self):
        if self._closed or getattr(self, '_cap', None) is None:
            self._cap = cv2.VideoCapture(self.path)
            self._frame_count = int(self._cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self._closed = False

    def close(self):
        if getattr(self, 'vr', None) is not None:
            self._cap.release()
            del self._cap
        self._closed = True

    def grab(self, frame=None):
        """Fetch the current frame"""
        self.open()

        self.current_frame = frame if frame is not None else self.current_frame
        if self.current_frame >= len(self):
            return None

        # Cache this frame if we haven't already
        if self.cached_frame is None or self.cached_frame_number != self.current_frame:
            if self._cap.get(cv2.CAP_PROP_POS_FRAMES) != self.current_frame:
                self._cap.set(cv2.CAP_PROP_POS_FRAMES, self.current_frame)

            ret, frame = self._cap.read()

            if not ret:
                frame = MISSING_FRAME
                # Resize the missing frame to the size of the video if we can
                if self.cached_frame is not None:
                    frame = cv2.resize(frame, (self.cached_frame.shape[1], self.cached_frame.shape[0]))

            self.cached_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.cached_frame = np.array(self.cached_frame)
            self.cached_frame_number = self.current_frame

        return self.cached_frame

    def step(self):
        self.seek_relative(1)

    def is_finished(self):
        return self.current_frame >= len(self)

    def __len__(self):
        if not self._cap:
            self.open()
        return self._frame_count

    def seek_relative(self, frames):
        self.current_frame += frames
        if self.current_frame < 0:
            self.current_frame = 0
        if self.current_frame >= len(self):
            self.current_frame = len(self) - 1

    def seek_absolute(self, frame):
        self.current_frame = frame
        if self.current_frame < 0:
            self.current_frame = 0
        if self.current_frame >= len(self):
            self.current_frame = len(self) - 1

    def frames_to_seconds(self, frame):
        return frame / self.fps

    def get_thumbnail(self, height=75):
        curr_frame = self.current_frame
        self.seek_absolute(0)
        frame = self.grab()
        self.seek_absolute(curr_frame)
        width = int(frame.shape[1] * height / frame.shape[0])
        return cv2.resize(frame, (width, height))