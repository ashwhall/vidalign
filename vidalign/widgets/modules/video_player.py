from math import ceil, log10
from typing import Optional

from PySide6 import QtCore
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFontDatabase, QImage, QKeySequence, QPixmap
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QSizePolicy, QSpinBox,
                               QStyle, QVBoxLayout, QWidget)

from vidalign.utils.video import Box, Video
from vidalign.widgets.modules import ImageViewer, StyledButton
from vidalign.widgets.modules.tick_slider import TickSlider

PLAYBACK_BTN_SIZE = (50, 40)
CROP_JUMP_BTN_SIZE = (80, 40)


def requires_video(fn):
    def wrapped(self=None, *args, **kwargs):
        if self.video is None:
            return
        return fn(self, *args, **kwargs)
    return wrapped


class VideoPlayer(QWidget):
    frame_changed = QtCore.Signal(int)
    video_started = QtCore.Signal()
    video_paused = QtCore.Signal()
    video_stopped = QtCore.Signal()
    video_play_pause_toggle = QtCore.Signal()
    video_seeked_absolute = QtCore.Signal(int)
    video_seeked_relative = QtCore.Signal(int)

    class Button(StyledButton):
        def __init__(self, text=None):
            super().__init__(text=text)
            self.setText(text)
            self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            self.setFixedHeight(40)

    def __init__(self):
        super().__init__()
        self.video = None
        self.frame_num = None

        self.is_playing = False
        self.jump_size = 10

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        layout = QVBoxLayout()
        self.image_viewer = ImageViewer()
        self.image_viewer.cropUpdated.connect(self.on_crop_updated)
        layout.addWidget(self.image_viewer)

        layout.addLayout(self._make_timeline_layout())
        layout.addLayout(self._make_controls_layout())

        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)

        # Build a timer to run every second
        self.timer = QTimer()
        self.timer.timeout.connect(self.play_callback)

    def on_crop_updated(self, box: Optional[Box]):
        if box is None:
            self.video.remove_crop(self.video.reader.current_frame)
        else:
            self.video.add_crop(self.video.reader.current_frame, box)
        self.frame_changed.emit(self.video.reader.current_frame)

    def _make_timeline_layout(self):
        layout = QHBoxLayout()
        # Frame labels needs a mono font to avoid resizing
        mono_font = QFontDatabase.systemFont(QFontDatabase.FixedFont)

        self.frame_num_label = QLabel('??/??')
        self.frame_num_label.setToolTip('Current frame/total frames')
        self.frame_num_label.setFont(mono_font)
        layout.addWidget(self.frame_num_label)

        self.slider = TickSlider(Qt.Horizontal)
        self.slider.setRange(0, 1)
        self.slider.setValue(0)
        self.slider.sliderMoved.connect(self.seek_absolute)
        layout.addWidget(self.slider)

        self.relative_frame_label = QLabel('Sync rel: --')
        self.relative_frame_label.setToolTip(
            'Current frame, relative to the sync frame')
        self.relative_frame_label.setFont(mono_font)
        layout.addWidget(self.relative_frame_label)
        return layout

    def _make_controls_layout(self):
        layout = QHBoxLayout()

        # Crop keyframe jumping
        prev_crop_kf_button = self.Button(text='Prev Crop')
        prev_crop_kf_button.setToolTip('Jump to previous crop keyframe (q)')
        prev_crop_kf_button.setShortcut(QKeySequence('q'))
        prev_crop_kf_button.setFixedSize(*CROP_JUMP_BTN_SIZE)
        prev_crop_kf_button.clicked.connect(self.seek_to_prev_crop_frame)
        layout.addWidget(prev_crop_kf_button)

        next_crop_kf_button = self.Button(text='Next Crop')
        next_crop_kf_button.setToolTip('Jump to next crop keyframe (e)')
        next_crop_kf_button.setShortcut(QKeySequence('e'))
        next_crop_kf_button.setFixedSize(*CROP_JUMP_BTN_SIZE)
        next_crop_kf_button.clicked.connect(self.seek_to_next_crop_frame)
        layout.addWidget(next_crop_kf_button)

        layout.addStretch()

        # Frame jumping
        self.big_prev_frame_button = self.Button()
        self.big_prev_frame_button.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_MediaSkipBackward
        ))
        self.big_prev_frame_button.setToolTip(
            f'Jump back by {self.jump_size} frames (Shift+A)')
        self.big_prev_frame_button.setShortcut(QKeySequence('shift+a'))
        self.big_prev_frame_button.setFixedSize(*PLAYBACK_BTN_SIZE)
        self.big_prev_frame_button.clicked.connect(
            lambda: self.seek_relative(-self.jump_size))
        layout.addWidget(self.big_prev_frame_button)

        prev_frame_button = self.Button()
        prev_frame_button.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_MediaSeekBackward
        ))
        prev_frame_button.setToolTip('Jump back by 1 frame (a)')
        prev_frame_button.setShortcut(QKeySequence('a'))
        prev_frame_button.setFixedSize(*PLAYBACK_BTN_SIZE)
        prev_frame_button.clicked.connect(self.prev)
        layout.addWidget(prev_frame_button)

        self.play_pause_button = self.Button()
        self.play_pause_button.setShortcut(QKeySequence('space'))
        self.play_pause_button.setFixedSize(*PLAYBACK_BTN_SIZE)
        self.started_or_stopped_playing(False)
        self.play_pause_button.clicked.connect(self.play_pause)
        layout.addWidget(self.play_pause_button)

        next_frame_button = self.Button()
        next_frame_button.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_MediaSeekForward
        ))
        next_frame_button.setToolTip('Jump forward by 1 frame (d)')
        next_frame_button.setShortcut(QKeySequence('d'))
        next_frame_button.setFixedSize(*PLAYBACK_BTN_SIZE)
        next_frame_button.clicked.connect(self.next)
        layout.addWidget(next_frame_button)

        self.big_next_frame_button = self.Button()
        self.big_next_frame_button.setIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_MediaSkipForward
        ))
        self.big_next_frame_button.setToolTip(
            f'Jump forward by {self.jump_size} frames (Shift+D)')
        self.big_next_frame_button.setShortcut(QKeySequence('shift+d'))
        self.big_next_frame_button.setFixedSize(*PLAYBACK_BTN_SIZE)
        self.big_next_frame_button.clicked.connect(
            lambda: self.seek_relative(self.jump_size))
        layout.addWidget(self.big_next_frame_button)

        layout.addStretch()

        jump_size_label = QLabel('Jump size:')
        jump_size_label.setToolTip('Number of frames to jump by')
        layout.addWidget(jump_size_label)
        jump_size_input = QSpinBox()
        jump_size_input.setRange(1, 1000)
        jump_size_input.setValue(self.jump_size)
        jump_size_input.setSingleStep(5)
        layout.addWidget(jump_size_input)
        jump_size_input.valueChanged.connect(self.set_jump_size)

        return layout

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.draw()

    @requires_video
    def play(self):
        self.video_started.emit()

    @requires_video
    def pause(self):
        self.video_paused.emit()

    @requires_video
    def play_pause(self):
        self.video_play_pause_toggle.emit()

    @requires_video
    def stop(self):
        self.video_stopped.emit()

    def set_playing(self, playing):
        self.is_playing = playing
        self.play_pause_button.update_is_playing()

    def play_callback(self):
        self.seek_relative(1, False)

    def set_jump_size(self, size: int):
        self.jump_size = size
        self.big_prev_frame_button.setToolTip(
            f'Jump back by {self.jump_size} frames (Shift+A)')
        self.big_next_frame_button.setToolTip(
            f'Jump forward by {self.jump_size} frames (Shift+D)')

    def slider_callback(self, value):
        if not self.is_playing:
            self.seek_absolute(value)

    @requires_video
    def seek_relative(self, frames, pause=True):
        self.video_seeked_relative.emit(frames)
        if pause:
            self.pause()

    @requires_video
    def seek_absolute(self, frame):
        self.video_seeked_absolute.emit(frame)
        self.pause()

    @requires_video
    def seek_to_next_crop_frame(self):
        frame = self.video.get_next_crop_frame()
        self.video_seeked_absolute.emit(frame)
        self.pause()

    @requires_video
    def seek_to_prev_crop_frame(self):
        frame = self.video.get_prev_crop_frame()
        self.video_seeked_absolute.emit(frame)
        self.pause()

    def started_or_stopped_playing(self, playing: bool):
        btn_shortcut = self.play_pause_button.shortcut()
        if playing:
            self.play_pause_button.setIcon(self.style().standardIcon(
                QStyle.StandardPixmap.SP_MediaPause
            ))
            self.play_pause_button.setToolTip('Pause (space)')
        else:
            self.play_pause_button.setIcon(self.style().standardIcon(
                QStyle.StandardPixmap.SP_MediaPlay
            ))
            self.play_pause_button.setToolTip('Play (space)')
        self.play_pause_button.setShortcut(btn_shortcut)

    def clear(self):
        self.video = None
        self.image_viewer.set_image(None)
        self.image_viewer.set_crop_box(None)
        self.frame_num = None
        self.frame_num_label.setText('??/??')
        self.slider.setValue(0)
        self.relative_frame_label.setText('Sync rel: --')

    def draw(self, video: Video = None, frame_num: int = None):
        self.frame_num = frame_num if frame_num is not None else self.frame_num
        prev_video = self.video
        self.video = video if video is not None else self.video

        if self.video is None:
            return

        relative_frame = self.video.abs_to_rel(self.frame_num)
        # Get the number of digits in the frame count
        n_dig = ceil(log10(len(self.video.reader)))
        fmt = f'{{:>{n_dig}d}}'
        self.frame_num_label.setText(
            f'{fmt.format(self.frame_num)}/{fmt.format(len(self.video.reader))}')
        if relative_frame is None:
            self.relative_frame_label.setText('Sync rel: --')
        else:
            self.relative_frame_label.setText(
                f'Sync rel: {fmt.format(relative_frame)}')

        self.slider.setValue(self.frame_num)
        self.slider.setRange(0, len(self.video.reader) - 1)

        frame = self.video.reader.grab(self.frame_num)

        height, width, _ = frame.shape
        bytesPerLine = 3 * width
        qImg = QImage(frame, width, height, bytesPerLine, QImage.Format_RGB888)
        pixmap = QPixmap(qImg)

        self.image_viewer.set_image(pixmap, reset=self.video != prev_video)
        cropbox, interpolated = self.video.get_crop(self.frame_num)
        self.image_viewer.set_crop_box(cropbox, interpolated=interpolated)

        frames = self.video.get_crop_frames()
        self.slider.set_ticks([f / len(self.video) for f in frames])

    @requires_video
    def prev(self):
        self.seek_relative(-1)

    @requires_video
    def next(self):
        self.seek_relative(1)
