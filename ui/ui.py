import pygame
from pygame.rect import Rect
from pygame.surface import Surface

from assets.colors import Colors
from ui.styles import Align, ButtonStyle
from util.constants import Constants as Consts
from util.settings import Settings as Setts


class Widget:
    def __init__(self, dimens, dest):
        self.width = int(dimens[0])
        self.height = int(dimens[1])
        self.x = dest[0]
        self.y = dest[1]
        self.canvas = Surface([self.width, self.height]).convert_alpha()
        self.enabled = True

    def draw(self, canvas):
        pass

    def hit(self, x, y):
        if self.enabled:
            flag = Rect(self.x, self.y, self.width, self.height).collidepoint(x, y)
            if flag:
                self.on_hit()
            return flag, 'widget'
        return False, 'widget'

    def update(self, delta):
        pass

    def update_canvas(self):
        pass

    def on_hit(self, *args):
        pass


class TextView(Widget):
    def __init__(self, text, dest, style, dimens=None):
        if dimens is None:
            size = style.font.size(text)
            super().__init__(size, dest)
        else:
            super().__init__(dimens, dest)
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
            size=self.style.font.size(self.text)
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


class EditText(TextView):
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
                True, self.style.text_color if self.is_editable else Colors.transparent_grey, self.style.bg_color)
            self.update_dest(self.editable_text if not self.is_protected else self.get_hidden_str())
        else:
            self.canvas = self.style.font.render(self.text, True, self.style.hint_color, self.style.bg_color)
            self.update_dest(self.text)
        if self.has_focus and self.is_visible:
            x = self.style.font.size(
                (self.editable_text if not self.is_protected else self.get_hidden_str())[:self.index])
            x = x[0] + (-1 if self.index > 0 else 1) * Consts.line_width
            pygame.draw.line(self.canvas, Colors.black, (x, 0), (x, self.height), Consts.line_width)
        pygame.draw.line(self.canvas, Colors.black, (0, self.height - 3 * Consts.line_width),
                         (self.canvas.get_width(), self.height - 3 * Consts.line_width),
                         Consts.line_width)

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
            if self.elapsed_time >= (Consts.cursor_on_time if self.is_visible else Consts.cursor_off_time):
                self.is_visible = not self.is_visible
                self.elapsed_time = 0
                self.update_canvas()

    def get_text(self):
        return self.editable_text.strip()


class Button(Widget):
    def __init__(self, dimens, dest, style):
        super().__init__(dimens, dest)
        self.pressed_dimens = (int(self.width*.8), int(self.height*.8))
        self.pressed_dest = (self.x+(self.width/2-self.pressed_dimens[0]/2),
                             self.y+(self.height/2-self.pressed_dimens[1]/2))
        self.style = style
        self.pressed = False
        self.pressed_rect = Rect(0, 0, self.pressed_dimens[0], self.pressed_dimens[1])
        self.update_canvas()

    def update_canvas(self):
        pygame.draw.rect(self.canvas, self.style.bg_color, Rect(0, 0, self.width, self.height))

    def draw(self, canvas):
        if self.pressed:
            canvas.blit(self.canvas, self.pressed_dest, self.pressed_rect)
        else:
            canvas.blit(self.canvas, (self.x, self.y))

    def on_hit(self, *args):
        self.pressed = not self.pressed


class TextButton(Button):
    def __init__(self, text, dest, style):
        self.text = text
        size = style.font.size(text)
        super().__init__((size[0] + 10, size[1] + 2), dest, style)
        self.update_dest(self.text)

    def update_dest(self, text):
        size = self.style.font.size(text)
        if self.style.align == Align.left:
            left = self.x
        elif self.style.align == Align.center:
            left = self.x + self.width / 2 - size[0] / 2
        else:
            left = self.x + self.width - size[0]
        self.dest = (left, self.y - self.height / 2)

    def draw(self, canvas):
        canvas.blit(self.canvas, self.dest)

    def update_canvas(self):
        super().update_canvas()
        pygame.draw.rect(self.canvas, self.style.bg_color, Rect(1, 1, self.width - 2, self.height - 2))
        size = self.style.font.size(self.text)
        self.canvas.blit(self.style.font.render(self.text, True, self.style.text_color, self.style.bg_color),
                         (self.width / 2 - size[0] / 2, self.height / 2 - size[1] / 2))


class Palette(Widget):
    def __init__(self, bg_color):
        super().__init__((Setts.screen_width, Setts.screen_height / 10), (0, Setts.screen_height * 9 / 10))
        self.bg_color = bg_color
        self.buttons = []
        self.selected = -1
        style = ButtonStyle(None)
        for i in range(0, 19):
            style.bg_color = Colors.game[i]
            self.buttons.append(Button((Consts.color_width, Consts.color_width),
                                       ((i + 1) * Setts.screen_width / 20 - Consts.color_width / 2,
                                        Setts.screen_height / 20 - Consts.color_width / 2),
                                       style))
        self.update_canvas()

    def draw(self, canvas):
        if self.enabled:
            canvas.blit(self.canvas, (self.x, self.y))

    def hit(self, x, y):
        if self.enabled:
            i = 0
            k = 21
            k_flag = False
            for button in self.buttons:
                if button.hit(x, y - self.y)[0] and button.pressed:
                    k = i
                    k_flag = True
                else:
                    button.pressed = False
                i += 1
            self.update_canvas()
            return k_flag, 'palette', k
        return False, 'palette', -1

    def update_canvas(self, *args):
        self.canvas.fill((0, 0, 0))
        self.canvas.convert_alpha()
        pygame.draw.rect(self.canvas, self.bg_color, Rect(0, 0, self.width, self.height))
        for button in self.buttons:
            button.draw(self.canvas)


class LoadingView(Widget):
    def __init__(self, dest):
        super().__init__((Consts.frame_width, 8 * Consts.frame_width), dest)
        self.image = pygame.image.load('assets/load.jpg')
        self.i = 0
        self.elapsed = 0
        self.limit = 125
        self.enabled = False
        self.frame = Rect(0, 0, self.width, self.height)
        self.dest = (self.x, self.y)

    def update(self, delta):
        if self.enabled:
            self.elapsed += delta
            if self.elapsed >= self.limit:
                self.elapsed %= self.limit
                self.i = (self.i + 1) % 9
                self.frame.__setattr__('x', self.i * Consts.frame_width)

    def draw(self, canvas):
        if self.enabled:
            canvas.blit(self.image, self.dest, self.frame)
