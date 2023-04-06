from PySide6 import QtCore
from PySide6.QtWidgets import (QLabel, QHBoxLayout, QSlider,
                               QVBoxLayout, QWidget, QSizePolicy, QStyleOptionSlider)
from PySide6.QtGui import QImage, QPixmap, QKeySequence, QPainter


class TickSlider(QSlider):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ticks = set()

    def set_ticks(self, tick_values):
        self.ticks = set(tick_values)
        self.update()

    def paintEvent(self, event):
        """Paint the ticks on the slider"""
        painter = QPainter(self)
        painter.setPen(self.palette().color(self.foregroundRole()))
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        tick_length = 5
        available = self.style().subControlRect(self.style().CC_Slider, opt, self.style().SC_SliderGroove, self)
        available.adjust(0, 0, -tick_length, 0)
        handle_width = self.style().subControlRect(self.style().CC_Slider, opt,
                                                   self.style().SC_SliderHandle, self).width()
        available_width = available.width() - handle_width / 2
        for tick in self.ticks:
            pos = available.left() + handle_width / 2 + (tick * available_width)
            painter.drawLine(pos, available.bottom(), pos, available.bottom() + tick_length)

        super().paintEvent(event)
