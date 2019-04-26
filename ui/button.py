import pygame
from pygame.rect import Rect

from ui.styles import Align
from ui.widget import Widget


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