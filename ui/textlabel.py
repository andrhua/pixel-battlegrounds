import pygame
from pygame.rect import Rect

from resources.colors import Colors
from ui.styles import Align
from ui.widget import Widget
from util.constants import Constants


class TextLabel(Widget):
    def __init__(self, text, dest, style, dimensions=None):
        if dimensions is None:
            size = style.font.size(text)
            super().__init__(size, dest)
        else:
            super().__init__(dimensions, dest)
        self.text = text
        self.style = style
        self.update_dest(text)
        self.update_canvas()

    def draw(self, canvas):
        if self.enabled:
            canvas.blit(self.canvas, self.dest)

    def update_canvas(self):
        if self.style.bg_color is not None:
            pygame.draw.rect(self.canvas, self.style.bg_color, Rect(0, 0, self.width, self.height))
            size = self.style.font.size(self.text)
            self.canvas.blit(self.style.font.render(self.text, True, self.style.text_color, None),
                             (self.width/2-size[0]/2, self.height/2-size[1]/2))
        else:
            self.canvas = self.style.font.render(self.text, True, self.style.text_color, None)

    def update_size(self):
        size = self.style.font.size(self.text)
        self.width = size[0]
        self.height = size[1]

    def set_text(self, text):
        self.text = text
        self.update_dest(text)
        self.update_canvas()

    def update_dest(self, text):
        size = self.style.font.size(text)
        if self.style.align == Align.left:
            left = self.x
        elif self.style.align == Align.center:
            left = self.x + self.width / 2 - size[0] / 2
        else:
            left = self.x + self.width - size[0]
        self.dest = (left, self.y)

    def set_text_color(self, text_color):
        self.style.text_color = text_color
        self.update_canvas()

    def get_text(self):
        return self.text.strip()


class TextForm(TextLabel):
    def __init__(self, hint, dest, style, is_protected=False):
        self.has_focus = False
        self.index = 0
        self.elapsed_time = 0
        self.is_protected = is_protected
        self.editable_text = ''
        self.is_editable = True
        super().__init__(hint, dest, style)

    def get_hidden_str(self):
        return '*' * len(self.editable_text)

    def update_canvas(self):
        if len(self.editable_text) > 0:
            self.canvas = self.style.font.render(
                self.editable_text if not self.is_protected else self.get_hidden_str(),
                True, self.style.text_color if self.is_editable else Colors.SEMITRANSPARENT_GREY, self.style.bg_color)
            self.update_dest(self.editable_text if not self.is_protected else self.get_hidden_str())
        else:
            self.canvas = self.style.font.render(self.text, True, self.style.hint_color, self.style.bg_color)
            self.update_dest(self.text)
        if self.has_focus and self.is_visible:
            x = self.style.font.size(
                (self.editable_text if not self.is_protected else self.get_hidden_str())[:self.index])
            x = x[0] + (-1 if self.index > 0 else 1) * Constants.LINE_WIDTH
            pygame.draw.line(self.canvas, Colors.BLACK, (x, 0), (x, self.height), Constants.LINE_WIDTH)
        pygame.draw.line(self.canvas, Colors.BLACK, (0, self.height - 3 * Constants.LINE_WIDTH),
                         (self.canvas.get_width(), self.height - 3 * Constants.LINE_WIDTH),
                         Constants.LINE_WIDTH)

    def set_text(self, text):
        self.editable_text = text
        self.update_canvas()

    def set_empty(self):
        self.set_text('')
        self.index = 0

    def move_cursor(self, amount):
        self.index += amount
        if self.index < 0:
            self.index = 0
        elif self.index > len(self.editable_text):
            self.index = len(self.editable_text)
        self.update_canvas()

    def delete_symbol(self):
        if len(self.editable_text) > 0:
            self.editable_text = self.editable_text[:self.index - 1] + self.editable_text[self.index:]
            self.index -= 1
            self.update_canvas()

    def hit(self, x, y):
        if self.enabled and self.is_editable:
            flag = Rect(self.x, self.y, self.width, self.height).collidepoint(x, y)
            if flag:
                self.on_hit()
            else:
                self.lose_focus()
            return flag, 'edit'
        return False, 'edit'

    def append_text(self, text):
        self.editable_text += text
        self.index += 1
        self.update_canvas()

    def lose_focus(self):
        self.has_focus = False
        self.update_canvas()

    def on_hit(self):
        self.has_focus = True
        self.is_visible = True
        self.update_canvas()

    def update(self, delta):
        if self.has_focus:
            self.elapsed_time += delta
            if self.elapsed_time >= (Constants.CURSOR_ON_TIME if self.is_visible else Constants.CURSOR_OFF_TIME):
                self.is_visible = not self.is_visible
                self.elapsed_time = 0
                self.update_canvas()

    def get_text(self):
        return self.editable_text.strip()