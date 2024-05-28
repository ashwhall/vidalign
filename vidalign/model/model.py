from pathlib import Path
from threading import Thread
from typing import List

from PySide6 import QtCore

from vidalign.utils.clip import Clip
from vidalign.utils.encoders.encoder import Encoder
from vidalign.utils.encoders.encoding_task import EncodingTask
from vidalign.utils.encoders.ffmpeg import FFmpeg
from vidalign.utils.encoders.pyav import PyAV
from vidalign.utils.video import Video


class Model(QtCore.QObject):
    video_list_changed = QtCore.Signal(list)
    current_video_changed = QtCore.Signal(Video)
    current_frame_changed = QtCore.Signal(int)
    clip_list_changed = QtCore.Signal(list)
    current_clip_changed = QtCore.Signal(Clip)

    # Playback controls
    video_started = QtCore.Signal()
    video_paused = QtCore.Signal()
    video_stopped = QtCore.Signal()

    output_directory_changed = QtCore.Signal(str)

    encoder_dict_changed = QtCore.Signal(dict)
    current_encoder_changed = QtCore.Signal(Encoder)
    encoding_tasks_changed = QtCore.Signal(list)
    encoding_progress_changed = QtCore.Signal(object, list)

    def __init__(self):
        super(Model, self).__init__()
        self._videos: List[Video] = []
        self._clips: List[Clip] = []

        self._current_video: Video = None
        self._current_clip: Clip = None
        self._current_frame = 0
        self._video_playing = False

        self._output_directory: str = None

        self._video_playback_timer = QtCore.QTimer()
        self._video_playback_timer.timeout.connect(self._play_callback)

        self._encoders = [FFmpeg(), PyAV()]
        self._current_encoder = self._encoders[0]
        self._encoding_tasks: List[EncodingTask] = []
        self._encoding_percentage: float = None
        self._encoding_stdout: str = ''

    @property
    def output_directory(self):
        return self._output_directory

    @output_directory.setter
    def output_directory(self, value):
        self._output_directory = value
        self.output_directory_changed.emit(value)

    @property
    def encoders(self):
        return self._encoders

    @encoders.setter
    def encoders(self, encoders):
        self._encoders = encoders
        self.encoder_dict_changed.emit(encoders)

    @property
    def current_encoder(self):
        return self._current_encoder

    @current_encoder.setter
    def current_encoder(self, encoder: Encoder):
        if encoder not in self._encoders:
            raise ValueError(f'Encoder {encoder.name} not found')
        self._current_encoder = encoder
        self.current_encoder_changed.emit(encoder)

    @property
    def encoding_tasks(self):
        return self._encoding_tasks

    @encoding_tasks.setter
    def encoding_tasks(self, tasks):
        self._encoding_tasks = tasks
        self.encoding_tasks_changed.emit(tasks)

    def ready_to_encode(self):
        if not self.current_encoder:
            return False, 'No encoder selected'
        if not self.videos:
            return False, 'No videos imported'
        if not self.clips:
            return False, 'No clips created'
        if not self.output_directory:
            return False, 'No output directory selected'

        if any(task.processing for task in self.encoding_tasks):
            return False, 'Task(s) are already in progress'

        for video in self.videos:
            if not video.complete():
                return False, 'Video(s) not complete'

        for clip in self.clips:
            if not clip.complete():
                return False, 'Clip(s) not complete'

        try:
            self.make_encoding_tasks()
            for task in self.encoding_tasks:
                task.get_encode_command(self.output_directory)
        except Exception as e:
            return False, str(e)

        return True, None

    def make_encoding_tasks(self):
        tasks = []
        for clip in self.clips:
            for video in self.videos:
                tasks.append(EncodingTask(video, clip, self.current_encoder))
        self.encoding_tasks = tasks

    @property
    def videos(self):
        return self._videos

    @videos.setter
    def videos(self, value):
        self._videos = value
        self.video_list_changed.emit(self._videos)
        self.make_encoding_tasks()

    @property
    def current_video(self):
        return self._current_video

    @current_video.setter
    def current_video(self, value):
        if self._current_video is not None:
            current_frame_relative = self._current_video.abs_to_rel(
                self.current_frame)
            if value is not None and current_frame_relative is not None:
                if (current_frame_absolute := value.rel_to_abs(current_frame_relative)):
                    self.current_frame = current_frame_absolute

        self._current_video = value
        self.current_video_changed.emit(self._current_video)

    @property
    def current_frame(self):
        return self._current_frame

    @current_frame.setter
    def current_frame(self, value):
        if self._current_video is not None:
            self._current_frame = min(value, len(self._current_video) - 1)
        else:
            self._current_frame = 0

        self._current_frame = max(0, self._current_frame)
        self.current_frame_changed.emit(self._current_frame)

    def ensure_frame_in_bounds(self):
        self.current_frame = self._current_frame

    @property
    def clips(self):
        return self._clips

    @clips.setter
    def clips(self, value):
        self._clips = value
        self.clip_list_changed.emit(self._clips)
        self.make_encoding_tasks()

    @property
    def current_clip(self):
        return self._current_clip

    @current_clip.setter
    def current_clip(self, value):
        self._current_clip = value
        self.current_clip_changed.emit(self._current_clip)

    @property
    def video_playing(self):
        return self._video_playing

    def play_pause_video(self):
        if self.current_video is None:
            return
        if self.video_playing:
            self.pause_video()
        else:
            self.play_video()

    def play_video(self):
        if self.current_video is None:
            return
        if not self.video_playing:
            if self.current_frame >= (len(self.current_video) - 1):
                self.current_frame = 0
            self._video_playback_timer.start(
                1000 / self.current_video.reader.fps)
            self.video_started.emit()
        self._video_playing = True

    def pause_video(self):
        if self.current_video is None:
            return
        if self._video_playing:
            self._video_playback_timer.stop()
            self.video_paused.emit()
        self._video_playing = False

    def _play_callback(self):
        self.seek_relative(1, False)
        if self.current_frame >= (len(self.current_video) - 1):
            self.pause_video()

    def stop_video(self):
        self._video_playing = False
        self._video_playback_timer.stop()
        self.video_stopped.emit()
        self.current_frame = 0

    def seek_absolute(self, frame):
        self.current_frame = frame

    def abs_to_rel(self, frame):
        """Convert an absolute frame number to sync-frame-relative"""
        if self.current_video is None:
            return

        return self.current_video.abs_to_rel(frame)

    def rel_to_abs(self, frame):
        """Convert a sync-relative frame number to absolute"""
        if self.current_video is None:
            return

        return self.current_video.rel_to_abs(frame)

    def seek_absolute_frame_rel(self, frame):
        """Seek to an absolute frame, using sync-relative frames"""
        if self.current_video is None:
            return
        if new_frame := self.current_video.rel_to_abs(frame):
            self.current_frame = new_frame

        self.pause_video()

    def seek_relative(self, frames, pause=True):
        self.current_frame += frames
        if pause:
            self.pause_video()

    def set_current_video_sync_frame(self):
        if self.current_video is None:
            return

        self.current_video.sync_frame = self.current_frame
        self.current_video = self.current_video

    def remove_current_video(self):
        if self.current_video is None:
            return
        video = self.current_video

        video_idx = self.videos.index(video)
        new_selected_idx = min(video_idx, len(self.videos) - 2)
        if new_selected_idx >= 0:
            self.current_video = self.videos[new_selected_idx]
        else:
            self.current_video = None

        self.videos.remove(video)
        self.videos = self.videos

    def new_clip(self):
        max_unnamed_clip = 0
        for clip in self.clips:
            if clip.name.startswith('Clip '):
                max_unnamed_clip = max(
                    max_unnamed_clip, int(clip.name.split()[-1]))
        self.clips = [
            *self.clips, Clip(name=f'Clip {max_unnamed_clip + 1}', start_frame=self.abs_to_rel(self.current_frame))]

    def delete_clip(self, clip):
        if clip is None:
            return
        if clip == self.current_clip:
            clip_idx = self.clips.index(clip)
            new_selected_idx = min(clip_idx, len(self.clips) - 2)

            if new_selected_idx >= 0:
                self.current_clip = self.clips[new_selected_idx]
            else:
                self.current_clip = None

        self.clips = [c for c in self.clips if clip != c]

    def rename_clip(self, clip, name):
        if clip is None:
            return
        clip.name = name
        self.clips = self.clips

    def set_clip_start(self, clip):
        rel_frame = self.abs_to_rel(self.current_frame)
        if rel_frame is not None:
            clip.start_frame = rel_frame
        self.clips = self.clips

    def set_clip_end(self, clip):
        rel_frame = self.abs_to_rel(self.current_frame)
        if rel_frame is not None:
            clip.end_frame = rel_frame
        self.clips = self.clips

    def set_clip_duration(self, clip, duration: int):
        if clip.start_frame is None:
            return

        clip.end_frame = clip.start_frame + duration
        self.clips = self.clips

    def video_clip_dict(self):
        return {
            'videos': [v.to_dict() for v in self.videos],
            'clips': [c.to_dict() for c in self.clips],
            'output_directory': self.output_directory,
        }

    def reset_video_clip_config(self):
        self.videos = []
        self.clips = []
        self.current_clip = None
        self.current_video = None
        self.output_directory = None

    def encoders_dict(self):
        return {
            'encoders': {
                encoder.name: encoder.to_dict() for encoder in self.encoders
            }
        }

    def get_encode_commands(self):
        self.make_encoding_tasks()
        return [
            task.get_encode_command(self.output_directory) for task in self.encoding_tasks
        ]

    @property
    def encoding_percentage(self):
        return self._encoding_percentage

    @encoding_percentage.setter
    def encoding_percentage(self, value):
        self._encoding_percentage = value
        self.encoding_progress_changed.emit(value, self.encoding_stdout_lines)

    @property
    def encoding_stdout_lines(self):
        return self._encoding_stdout

    @encoding_stdout_lines.setter
    def encoding_stdout_lines(self, value):
        self._encoding_stdout = value
        self.encoding_progress_changed.emit(self.encoding_percentage, value)

    def start_encoding_tasks(self, skip_existing=False):
        """Start the encoding tasks in a separate thread"""
        self.make_encoding_tasks()

        def _run_async():
            self.encoding_percentage = 0
            self.encoding_stdout_lines = []
            cancelled = False

            if skip_existing:
                i = len(self.encoding_tasks) - 1
                while i >= 0:
                    task = self.encoding_tasks[i]
                    # Drop any tasks where the output already exists
                    if task.output_exists(self.output_directory):
                        self.encoding_tasks.pop(i)
                    i -= 1

            self.encoding_stdout_lines.append(
                '=== STARTING ENCODING TASKS ===')
            for i, task in enumerate(self.encoding_tasks):
                self.encoding_stdout_lines.append('')
                self.encoding_stdout_lines.append(
                    f'=== STARTING ENCODING TASK {i + 1}/{len(self.encoding_tasks)} ===')
                self.encoding_stdout_lines.append(
                    f'=== VIDEO: {task.video.name} ===')
                self.encoding_stdout_lines.append('')
                self.encoding_stdout_lines = self.encoding_stdout_lines

                # Hold onto the stdout lines prior to starting this task, so we can repeatedly
                # append the "updated" lines to the end of the list. Just a funny trick to handle
                # \r characters in the output
                pre_task_std_lines = self.encoding_stdout_lines
                for updated_std_lines in task.run_encode_job(self.output_directory):
                    self.encoding_stdout_lines = [
                        *pre_task_std_lines, *updated_std_lines]

                cancelled = cancelled or any(
                    [task.cancelled for task in self.encoding_tasks])
                if cancelled:
                    break

                self.encoding_percentage = (i + 1) / len(self.encoding_tasks)

            if cancelled:
                self.encoding_percentage = None
            else:
                self.encoding_percentage = 1

        thread = Thread(target=_run_async)
        thread.start()

    def cancel_encoding_tasks(self):
        for task in self.encoding_tasks:
            task.cancel_encode_job()
        self.encoding_stdout_lines = []
        self.encoding_percentage = None

    def finalise_encoding(self):
        self.encoding_percentage = None
        self.encoding_tasks = []
        self.encoding_stdout_lines = []

    def from_dict(self, data):
        if 'videos' in data:
            self.videos = [Video.from_dict(v) for v in data['videos']]
            self.current_video = None

        if 'clips' in data:
            self.clips = [Clip.from_dict(c) for c in data['clips']]
            self.current_clip = None

        if 'output_directory' in data:
            self.output_directory = data['output_directory']

        if 'encoders' in data:
            for key, data in data['encoders'].items():
                try:
                    idx = next(i for i, encoder in enumerate(
                        self.encoders) if encoder.name == key)
                    self.encoders[idx].update_from_dict(data)
                except IndexError:
                    print(f'WARNING: No encoder found with name {key}')
            self.encoders = self.encoders

    def set_current_video_alias(self, alias):
        if self.current_video is None:
            return

        self.current_video.alias = alias
        self.current_video = self.current_video
        self.videos = self.videos
