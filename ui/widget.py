import pygame
from pygame.rect import Rect
from pygame.surface import Surface

from util.constants import Constants


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


class SpriteImage(Widget):
    def __init__(self, dest):
        super().__init__((Constants.FRAME_WIDTH, 8 * Constants.FRAME_WIDTH), dest)
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
                self.frame.__setattr__('x', self.i * Constants.FRAME_WIDTH)

    def draw(self, canvas):
        if self.enabled:
            canvas.blit(self.image, self.dest, self.frame)
