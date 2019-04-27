from enum import Enum


class Align(Enum):
    left = 0
    center = 1
    right = 2


class TextLabelStyle:
    def __init__(self, font, text_color, background_color=None, align=Align.left):
        self.font = font
        self.text_color = text_color
        self.background_color = background_color
        self.align = align


class TextFormStyle(TextLabelStyle):
    def __init__(self, font, text_color, hint_color, background_color, align=Align.left):
        super().__init__(font, text_color, background_color, align)
        self.hint_color = hint_color


class ButtonStyle:
    def __init__(self, background_color):
        self.background_color = background_color


class TextButtonStyle(ButtonStyle):
    def __init__(self, font, text_color, border_color, background_color=None, align=Align.center):
        super().__init__(background_color)
        self.border_color = border_color
        self.align = align
        self.font = font
        self.text_color = text_color
