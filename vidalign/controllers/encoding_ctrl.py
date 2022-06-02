from PySide6 import QtCore

from vidalign.model.model import Model
from vidalign.utils.video import Video


class EncodingController(QtCore.QObject):
    def __init__(self, model: Model):
        super().__init__()

        self._model = model
    
    @QtCore.Slot(list)
    def on_view_encode_commands(self, value):
        existing_video_paths = set(video.path for video in self._model.videos)
        new_vid_list = [*self._model.videos]
        for vid_path in value:
            if vid_path not in existing_video_paths:
                new_vid_list.append(Video(vid_path))

        self._model.videos = new_vid_list
