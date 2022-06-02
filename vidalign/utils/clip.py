class Clip:
    def __init__(self, name, start_frame=None, end_frame=None):
        self.name = name
        self._start_frame: int = start_frame
        self._end_frame: int = end_frame

    @property
    def start_frame(self):
        return self._start_frame

    @start_frame.setter
    def start_frame(self, value):
        if self.end_frame is not None:
            value = min(value, self.end_frame - 1)
        self._start_frame = value

    @property
    def end_frame(self):
        return self._end_frame

    @end_frame.setter
    def end_frame(self, value):
        if self.start_frame is not None:
            value = max(value, self.start_frame + 1)
        self._end_frame = value

    def complete(self):
        return self.name is not None and self.start_frame is not None and self.end_frame is not None

    def to_dict(self):
        return {
            'name': self.name,
            'start_frame': self.start_frame,
            'end_frame': self.end_frame,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            start_frame=data['start_frame'],
            end_frame=data['end_frame'],
        )