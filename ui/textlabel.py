import pygame
from pygame.rect import Rect

from resources.colors import Colors
from ui.styles import Align
from ui.widget import Widget
from util.constants import Constants


class TextLabel(Widget):
    def __init__(self, text, x, y, style, width=None, height=None):
        if width is None:
            width, height = style.font.size(text)
        super().__init__(width, height, x, y)
        self.text = text
        self.style = style
        self.update_position(text)
        self.update_surface()

    def draw(self, surface):
        if self.enabled:
            x, y = self.get_aligned_position(self.x, self.y, self.style, self.text)
            surface.blit(self.surface, (self.x - self.width / 2, self.y - self.height / 2))

    def update_surface(self):
        if self.style.background_color is not None:
            pygame.draw.rect(self.surface, self.style.background_color, Rect(0, 0, self.width, self.height))
            text_width, text_height = self.style.font.size(self.text)
            self.surface.blit(self.style.font.render(self.text, True, self.style.text_color, None),
                              (self.width / 2 - text_width / 2, self.height / 2 - text_height / 2))
        else:
            self.surface = self.style.font.render(self.text, True, self.style.text_color, None)

    def update_size(self):
        self.width, self.height = self.style.font.size(self.text)

    def set_text(self, text):
        self.text = text
        # self.update_size()
        self.update_position(text)
        self.update_surface()

    def get_aligned_position(self, x, y, style, text):
        text_width, text_height = style.font.size(text)
        if style.align == Align.left:
            left = x
        elif style.align == Align.center:
            left = x + self.width / 2 - text_width / 2
        else:
            left = x + self.width - text_width
        return left, y

    def update_position(self, text):
        pass
        # text_width, text_height = self.style.font.size(text)
        # if self.style.align == Align.left:
        #     left = self.x
        # elif self.style.align == Align.center:
        #     left = self.x + self.width / 2 - text_width / 2
        # else:
        #     left = self.x + self.width - text_width
        # self.x = left

    def set_text_color(self, text_color):
        self.style.text_color = text_color
        self.update_surface()

    def get_text(self):
        return self.text.strip()


class TextForm(TextLabel):
    def __init__(self, hint, x, y, style, is_protected=False):
        self.has_focus = False
        self.index = 0
        self.elapsed_time = 0
        self.is_protected = is_protected
        self.editable_text = ''
        self.is_editable = True
        self.is_visible = True
        super().__init__(hint, x, y, style)

    def get_hidden_str(self):
        return '*' * len(self.editable_text)

    def update_surface(self):
        if len(self.editable_text) > 0:
            self.surface = self.style.font.render(
                self.editable_text if not self.is_protected else self.get_hidden_str(),
                True, self.style.text_color if self.is_editable else Colors.SEMITRANSPARENT_GREY,
                self.style.background_color)
            self.update_position(self.editable_text)
        else:
            self.surface = self.style.font.render(self.text, True, self.style.hint_color, self.style.background_color)
            self.update_position(self.text)
        if self.has_focus and self.is_visible:
            x = self.style.font.size(self.editable_text[:self.index])[0]
            x = x + (-1 if self.index > 0 else 1) * Constants.LINE_WIDTH
            pygame.draw.line(self.surface, Colors.BLACK, (x, 0), (x, self.height), Constants.LINE_WIDTH)
        pygame.draw.line(self.surface, Colors.BLACK, (0, self.height - 3 * Constants.LINE_WIDTH),
                         (self.surface.get_width(), self.height - 3 * Constants.LINE_WIDTH),
                         Constants.LINE_WIDTH)

    def set_text(self, text):
        self.editable_text = text
        self.update_surface()

    def set_empty(self):
        self.set_text('')
        self.index = 0

    def move_cursor(self, amount):
        self.index += amount
        if self.index < 0:
            self.index = 0
        elif self.index > len(self.editable_text):
            self.index = len(self.editable_text)
        self.update_surface()

    def delete_symbol(self):
        if len(self.editable_text) > 0:
            self.editable_text = self.editable_text[:self.index - 1] + self.editable_text[self.index:]
            self.index -= 1
            self.update_surface()

    def hit(self, x, y):
        if self.enabled and self.is_editable:
            flag = Rect(self.x - self.width / 2, self.y - self.height / 2, self.width, self.height).collidepoint(x, y)
            if flag:
                self.on_hit()
            else:
                self.lose_focus()
            return flag, 'edit'
        return False, 'edit'

    def append_text(self, text):
        self.editable_text += text
        self.index += 1
        self.update_surface()

    def lose_focus(self):
        self.has_focus = False
        self.update_surface()

    def on_hit(self):
        self.has_focus = True
        self.is_visible = True
        self.update_surface()

    def update(self, delta):
        if self.has_focus:
            self.elapsed_time += delta
            if self.elapsed_time >= (Constants.CURSOR_ON_TIME if self.is_visible else Constants.CURSOR_OFF_TIME):
                self.is_visible = not self.is_visible
                self.elapsed_time = 0
                self.update_surface()

    def get_text(self):
        return self.editable_text.strip()
