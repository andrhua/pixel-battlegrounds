import pygame
from pygame.rect import Rect

from resources.colors import Colors
from ui.styles import Align, ButtonStyle
from ui.widget import Widget
from util.constants import Constants


class Button(Widget):
    def __init__(self, width, height, x, y, style):
        super().__init__(width, height, x, y)
        self.pressed_width, self.pressed_height = int(self.width * .8), int(self.height * .8)
        self.pressed_x, self.pressed_y = self.x + (self.width / 2 - self.pressed_width / 2), self.y + (
                self.height / 2 - self.pressed_height / 2)
        self.style = style
        self.pressed = False
        self.pressed_rect = Rect(0, 0, self.pressed_width, self.pressed_height)
        self.update_canvas()

    def update_canvas(self):
        pygame.draw.rect(self.canvas, self.style.background_color, Rect(0, 0, self.width, self.height))

    def draw(self, canvas):
        if self.pressed:
            canvas.blit(self.canvas, (self.pressed_width, self.pressed_height), self.pressed_rect)
        else:
            canvas.blit(self.canvas, (self.x, self.y))

    def on_hit(self, *args):
        self.pressed = not self.pressed


class TextButton(Button):
    def __init__(self, text, width, height, style):
        self.text = text
        text_width, text_height = style.font.size(text)
        super().__init__((text_width + 10, text_height + 2), width, height, style)
        self.update_dest(self.text)

    def update_dest(self, text):
        text_width, text_height = self.style.font.size(text)
        if self.style.align == Align.left:
            left = self.x
        elif self.style.align == Align.center:
            left = self.x + self.width / 2 - text_width / 2
        else:
            left = self.x + self.width - text_height
        self.x, self.y = left, self.y - self.height / 2

    def draw(self, canvas):
        canvas.blit(self.canvas, (self.x, self.y))

    def update_canvas(self):
        super().update_canvas()
        pygame.draw.rect(self.canvas, self.style.bg_color, Rect(1, 1, self.width - 2, self.height - 2))
        text_width, text_height = self.style.font.size(self.text)
        self.canvas.blit(self.style.font.render(self.text, True, self.style.text_color, self.style.bg_color),
                         (self.width / 2 - text_width / 2, self.height / 2 - text_height / 2))


class ColorPicker(Widget):
    def __init__(self, background_color):
        super().__init__(Constants.SCREEN_WIDTH, Constants.COLOR_PICKER_HEIGHT,
                         0, Constants.SCREEN_HEIGHT - Constants.COLOR_PICKER_HEIGHT)
        self.background_color = background_color
        self.buttons = []
        self.selected = -1
        style = ButtonStyle(None)
        for i, color in enumerate(Colors.GAME_COLORS):
            number_of_colors = len(Colors.GAME_COLORS)
            style.background_color = color
            self.buttons.append(Button(Constants.COLOR_BUTTON_SIZE, Constants.COLOR_BUTTON_SIZE,
                                       (i + 1) * Constants.SCREEN_WIDTH / (
                                               number_of_colors + 1) - Constants.COLOR_BUTTON_SIZE / 2,
                                       Constants.COLOR_PICKER_HEIGHT / 3 - Constants.COLOR_BUTTON_SIZE / 2,
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
        pygame.draw.rect(self.canvas, self.background_color, Rect(0, 0, self.width, self.height))
        for button in self.buttons:
            button.draw(self.canvas)
