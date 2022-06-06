from PySide6 import QtCore, QtWidgets
from PySide6.QtGui import QGuiApplication

from vidalign.model import Model
from vidalign.utils.video import Video


class VideoDropperController(QtCore.QObject):
    def __init__(self, model: Model):
        super().__init__()

        self._model = model

    @QtCore.Slot(list)
    def on_videos_dropped(self, value):
        existing_video_paths = set(video.path for video in self._model.videos)

        new_vid_list = [*self._model.videos]

        should_select_first_video = len(new_vid_list) == 0

        progress = QtWidgets.QProgressDialog('Loading videos...', 'Cancel', 0, len(value))
        progress.setWindowTitle('Loading videos')
        progress.setCancelButton(None)
        progress.setWindowModality(QtCore.Qt.ApplicationModal)
        progress.show()

        progress.setValue(0)

        for i, vid_path in enumerate(value):
            progress.setValue(i)
            progress.setWindowTitle(f'Loading video {i+1}/{len(value)}')
            progress.setLabelText(f'Loading {vid_path}')
            progress.show()
            QGuiApplication.processEvents()
            if vid_path not in existing_video_paths:
                vid = Video(vid_path)
                vid.preload_metadata()
                new_vid_list.append(vid)

        self._model.videos = new_vid_list
        # Select the video if it's the first added
        if len(new_vid_list) == 1:
            self._model.current_video = new_vid_list[0]

        progress.setValue(len(value))

        if should_select_first_video and new_vid_list:
            self._model.current_video = new_vid_list[0]
