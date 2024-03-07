import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List


class Encoder(ABC):

    @dataclass
    class EncParam:
        flag: str
        value: object
        default: object
        hint: str

        def get_command_array(self):
            if self.value:
                return [self.flag, self.value]
            return []

        def to_dict(self):
            return {
                'flag': self.flag,
                'value': self.value,
                'default': self.default,
                'hint': self.hint
            }

        @classmethod
        def from_dict(cls, data):
            return cls(
                data['flag'],
                data['value'],
                data['default'],
                data['hint']
            )

        def update_from_dict(self, data):
            self.value = data['value']

    def __init__(self, name, enc_params: Dict[str, EncParam]):
        self.name = name
        self.enc_params = enc_params

    def get_clip_base_path(self, video, clip, output_dir):
        """
        Get the unique base path for a clip.
        Constructed like {output_dir}/{clip_name}_{video_alias}
        """
        return os.path.join(output_dir, f'{clip.name.replace(" ", "_")}_{video.alias.replace(" ", "_")}')

    @abstractmethod
    def get_encode_command(self, video, clip, output_dir):
        pass

    @abstractmethod
    def output_path(self, video, clip, output_dir):
        pass

    def to_dict(self):
        return {
            'enc_params': {
                key: param.to_dict() for key, param in self.enc_params.items()
            }
        }

    @classmethod
    def from_dict(cls, data):
        enc = cls()
        enc.update_from_dict(data)

    def update_from_dict(self, data):
        for key, values in data['enc_params'].items():
            if key in self.enc_params:
                self.enc_params[key].update_from_dict(values)
            else:
                self.enc_params[key] = Encoder.EncParam.from_dict(values)

    def reset_params_to_default(self):
        for enc_param in self.enc_params.values():
            enc_param.value = enc_param.default

    def set_param(self, key, value):
        self.enc_params[key].value = value

    def reset_param_to_default(self, key):
        self.enc_params[key].value = self.enc_params[key].default
