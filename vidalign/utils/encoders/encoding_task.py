import subprocess
from typing import List
from dataclasses import dataclass

from vidalign.utils.video import Video
from vidalign.utils.clip import Clip
from vidalign.utils.encoders import Encoder


@dataclass
class EncodingTask:
    video: Video
    clip: Clip
    encoder: Encoder
    processing: bool = False
    _cancelled: bool = False
    stdout_lines: List[str] = None

    def get_encode_command(self, output_dir):
        return self.encoder.get_encode_command(self.video, self.clip, output_dir)

    def run_encode_job(self, output_dir):
        """Run the job and yield the entire stdout as a list of string lines with each update"""
        self.processing = True

        cmd = self.get_encode_command(output_dir)
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        self.stdout_lines = []
        string_buffer = ''
        for c in iter(lambda: proc.stdout.read(1), b''):
            char = c.decode('utf-8')
            string_buffer += char

            if self._cancelled:
                proc.kill()
                break
            
            if char == '\r':
                if self.stdout_lines:
                    self.stdout_lines.pop()
            if char in ('\n', '\r'):
                self.stdout_lines.append(string_buffer.strip())
                string_buffer = ''
                yield self.stdout_lines

        if string_buffer and not self._cancelled:
            self.stdout_lines.append(string_buffer.strip())
            yield self.stdout_lines

        self.processing = False
    
    def cancel_encode_job(self):
        self._cancelled = True
