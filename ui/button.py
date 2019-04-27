import pygame
from pygame.rect import Rect

from resources.colors import Colors
from ui.styles import Align, ButtonStyle
from ui.widget import Widget
from util.constants import Constants
from util.settings import Settings


class Button(Widget):
    def __init__(self, dimensions, dest, style):
        super().__init__(dimensions, dest)
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


class ColorPicker(Widget):
    def __init__(self, bg_color):
        super().__init__((Settings.screen_width, Settings.screen_height / 10), (0, Settings.screen_height * 9 / 10))
        self.bg_color = bg_color
        self.buttons = []
        self.selected = -1
        style = ButtonStyle(None)
        for i in range(0, 19):
            style.bg_color = Colors.game[i]
            self.buttons.append(Button((Constants.COLOR_BUTTON_WIDTH, Constants.COLOR_BUTTON_WIDTH),
                                       ((i + 1) * Settings.screen_width / 20 - Constants.COLOR_BUTTON_WIDTH / 2,
                                        Settings.screen_height / 20 - Constants.COLOR_BUTTON_WIDTH / 2),
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
