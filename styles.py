from enum import Enum


class Align(Enum):
    left = 0
    center = 1
    right = 2


class TextViewStyle:
    def __init__(self, font, text_color, bg_color, align=Align.left):
        self.font = font
        self.text_color = text_color
        self.bg_color = bg_color
        self.align = align


class EditTextStyle(TextViewStyle):
    def __init__(self, font, text_color, hint_color, bg_color, align=Align.left):
        super().__init__(font, text_color, bg_color, align)
        self.hint_color = hint_color


class ButtonStyle:
    def __init__(self, bg_color):
        self.bg_color = bg_color


class TextButtonStyle(ButtonStyle):
    def __init__(self, font, text_color, border_color, bg_color=None, align=Align.center):
        super().__init__(bg_color)
        self.border_color=border_color
        self.align=align
        self.font = font
        self.text_color = text_color
