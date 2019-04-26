import pygame
from pygame.rect import Rect
from pygame.surface import Surface

from resources.colors import Colors
from ui.styles import ButtonStyle
from util.constants import Constants
from util.settings import Settings


class Widget:
    def __init__(self, dimensions, dest):
        self.width = int(dimensions[0])
        self.height = int(dimensions[1])
        self.x = dest[0]
        self.y = dest[1]
        self.canvas = Surface([self.width, self.height]).convert_alpha()
        self.enabled = True
        self.hitbox = Rect(self.x, self.y, self.width, self.height)

    def draw(self, canvas):
        pass

    def hit(self, x, y):
        if self.enabled:
            flag = self.hitbox.collidepoint(x, y)
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


class ColorPicker(Widget):
    def __init__(self, bg_color):
        super().__init__((Settings.screen_width, Settings.screen_height / 10), (0, Settings.screen_height * 9 / 10))
        self.bg_color = bg_color
        self.buttons = []
        self.selected = -1
        style = ButtonStyle(None)
        for i in range(0, 19):
            style.bg_color = Colors.game[i]
            self.buttons.append(Button((Constants.color_width, Constants.color_width),
                                       ((i + 1) * Settings.screen_width / 20 - Constants.color_width / 2,
                                        Settings.screen_height / 20 - Constants.color_width / 2),
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


class SpriteImage(Widget):
    def __init__(self, dest):
        super().__init__((Constants.frame_width, 8 * Constants.frame_width), dest)
        self.image = pygame.image.load('resources/load.jpg')
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
                self.frame.__setattr__('x', self.i * Constants.frame_width)

    def draw(self, canvas):
        if self.enabled:
            canvas.blit(self.image, self.dest, self.frame)
