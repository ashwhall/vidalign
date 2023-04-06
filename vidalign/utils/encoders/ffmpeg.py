import os
from typing import List
from vidalign.utils.clip import Clip
from vidalign.utils.encoders import Encoder
from vidalign.utils.video import Video


class FFmpeg(Encoder):
    def __init__(self):
        super().__init__(
            'FFmpeg',
            {
                'vcodec': Encoder.EncParam('-c:v', 'libx264', 'libx264', 'Video codec. Try `ffmpeg -codecs` for a list of available codecs.'),
                'acodec': Encoder.EncParam('-c:a', 'aac', 'aac', 'Audio codec. Try `ffmpeg -codecs` for a list of available codecs.'),
                'pix_fmt': Encoder.EncParam('-pix_fmt', 'yuv420p', 'yuv420p', 'Pixel format'),
                'crf': Encoder.EncParam('-crf', '18', '18', 'CRF. Lower values are better quality, but larger files.'),
                'scale': Encoder.EncParam('-s', None, None, 'Scale (WxH). E.g., 1280x720'),
                'extension': Encoder.EncParam('--', 'mp4', 'mp4', 'File extension')
            }
        )

    def output_path(self, video, clip, output_dir):
        path = self.get_clip_base_path(video, clip, output_dir)
        if ext := self.enc_params['extension'].value:
            base = os.path.splitext(path)[0]
            path = f'{base}.{ext}'
        return path

    def get_encode_command(self, video: Video, clip: Clip, output_dir: str):
        if video.crop is not None:
            raise NotImplementedError('FFmpeg does not support cropping.')

        cmd = []

        abs_start_frame = video.rel_to_abs(clip.start_frame)
        abs_end_frame = video.rel_to_abs(clip.end_frame)
        start_seconds = video.frames_to_seconds(abs_start_frame - .5)
        end_seconds = video.frames_to_seconds(abs_end_frame)

        duration = end_seconds - start_seconds

        cmd.append('ffmpeg')
        cmd.append('-hide_banner')
        cmd.append('-y')
        cmd.extend(('-i', video.path))

        if abs_start_frame > 0:
            cmd.extend(('-ss', video.seconds_to_timestamp(start_seconds)))
        if abs_end_frame < len(video):
            cmd.extend(('-t', video.seconds_to_timestamp(duration)))

        cmd.extend(self.enc_params['vcodec'].get_command_array())
        cmd.extend(self.enc_params['acodec'].get_command_array())
        cmd.extend(self.enc_params['pix_fmt'].get_command_array())
        cmd.extend(self.enc_params['crf'].get_command_array())
        cmd.extend(self.enc_params['scale'].get_command_array())

        cmd.append(self.output_path(video, clip, output_dir))

        return cmd
