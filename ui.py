from enum import Enum

import pygame
from pygame.rect import Rect
from pygame.surface import Surface
from assets import Assets
from colors import Colors


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


class TextRectException:
    def __init__(self, message=None):
        self.message = message

    def __str__(self):
        return self.message


class Widget:
    def __init__(self, width, height):
        self.width = int(width)
        self.height = int(height)
        self.canvas = Surface([self.width, self.height]).convert_alpha()
        self.enabled = True

    def draw(self, canvas):
        pass

    def hit(self, x, y):
        if self.enabled:
            flag = Rect(0, 0, self.width, self.height).collidepoint(x, y)
            if flag:
                self.on_hit()
            return flag
        return False

    def on_hit(self):
        pass


class TextView(Widget):
    def __init__(self, text, dest, style, dimens=None):
        if dimens is None:
            size = style.font.size(text)
            super().__init__(size[0], size[1])
        else:
            super().__init__(dimens[0], dimens[1])
        self.text = text
        self.style = style
        self.update_dest(dest)
        self.update_canvas()

    def draw(self, canvas):
        canvas.blit(self.canvas, self.dest)

    def update_canvas(self):
        self.canvas = self.style.font.render(self.text, True, self.style.text_color, self.style.bg_color)

    def update_size(self):
        size = self.style.font.size(self.text)
        self.width = size[0]
        self.height = size[1]

    def set_text(self, text):
        self.text = text
        self.update_canvas()

    def update_dest(self, dest):
        left = 0
        size = self.style.font.size(self.text)
        if self.style.align == Align.left:
            left = dest[0]
        elif self.style.align == Align.center:
            left = dest[0] + self.width / 2 - size[0] / 2
        else:
            left = dest[0] + self.width - size[0]
        self.dest = (left, dest[1] - self.height / 2)

    def set_text_color(self, text_color):
        self.style.text_color = text_color
        self.update_canvas()


class EditText(TextView):
    def __init__(self, hint, dest, style, dimens, is_protected=False):
        super().__init__(hint, dest, style, dimens)
        self.is_protected = is_protected

    def update_canvas(self):
        super().update_canvas()
        pygame.draw.line(self.canvas, Colors.black, (0, self.height - 1), (self.canvas.get_width(), self.height - 1), 2)

    def append_text(self, text):
        self.set_text(text + self.text)
