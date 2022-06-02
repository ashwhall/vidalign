from enum import Enum
from PySide6 import QtCore
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QLabel, QPushButton,
                               QHBoxLayout, QWidget, QSizePolicy)
from vidalign.constants import COLOURS


class StyledButton(QPushButton):
    class Style(Enum):
        DEFAULT = 'DEFAULT'
        POSITIVE = 'POSITIVE'
        NEGATIVE = 'NEGATIVE'
        PRIMARY = 'PRIMARY'

    def __init__(self, text, style=Style.DEFAULT):
        super().__init__(text)
        self.style = style
        if stylesheet := self.construct_stylesheet():
            self.setStyleSheet(stylesheet)
        self.setMinimumHeight(30)

    def construct_stylesheet(self):
        if self.style == StyledButton.Style.DEFAULT:
            bg = COLOURS['default']
            fg = COLOURS['black']
            border = COLOURS['default_dark']
        elif self.style == StyledButton.Style.POSITIVE:
            bg = COLOURS['positive']
            fg = COLOURS['white']
            border = COLOURS['positive_dark']
        elif self.style == StyledButton.Style.NEGATIVE:
            bg = COLOURS['negative']
            fg = COLOURS['white']
            border = COLOURS['negative_dark']
        elif self.style == StyledButton.Style.PRIMARY:
            bg = COLOURS['primary']
            fg = COLOURS['white']
            border = COLOURS['primary_dark']
        return f"""
            QPushButton {{
                background-color: {bg};
                color: {fg};
                border: 2px solid {border};
                border-radius: 5px;
            }}
            QPushButton:pressed {{
                background-color: {border};
            }}
        """
