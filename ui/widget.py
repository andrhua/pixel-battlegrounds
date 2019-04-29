import util.constants
import pygame
from pygame.rect import Rect
from pygame.surface import Surface

from resources.colors import Colors
from util.constants import Constants


class Widget:
    def __init__(self, width, height, x, y):
        self.width = int(width)
        self.height = int(height)
        self.x = x
        self.y = y
        self.surface = Surface([self.width, self.height]).convert_alpha()
        self.enabled = True
        self.hitbox = Rect(self.x, self.y, self.width, self.height)
        self.children = []

    def add_child(self, widget):
        self.children.append(widget)

    def draw(self, surface):
        pass

    def hit(self, x, y):
        if self.enabled:
            for child in self.children:
                is_hit, name = child.hit(x, y)
                if is_hit:
                    return is_hit, name
            is_hit = self.hitbox.collidepoint(x, y)
            if is_hit:
                self.on_hit()
            return is_hit, self.__repr__()
        return False, self.__repr__()

    def update(self, delta):
        pass

    def update_surface(self):
        pass

    def on_hit(self, *args):
        pass

    def __repr__(self):
        return 'widget'


class SpriteImage(Widget):
    def __init__(self, x, y):
        super().__init__(Constants.FRAME_WIDTH, 8 * Constants.FRAME_WIDTH, x, y)
        self.image = pygame.image.load('resources/loader.jpg')
        self.i = 0
        self.elapsed = 0
        self.limit = 125
        self.enabled = False
        self.frame = Rect(0, 0, self.width, self.height)
        self.position = (self.x, self.y)

    def update(self, delta):
        if self.enabled:
            self.elapsed += delta
            if self.elapsed >= self.limit:
                self.elapsed %= self.limit
                self.i = (self.i + 1) % 9
                self.frame.__setattr__('x', self.i * Constants.FRAME_WIDTH)

    def draw(self, surface):
        if self.enabled:
            surface.blit(self.image, self.position, self.frame)


class Battleground:
    def __init__(self, pixels):
        self.surface = pygame.Surface([Constants.BATTLEGROUND_WIDTH, Constants.BATTLEGROUND_HEIGHT]).convert_alpha()
        self.surface.fill(Colors.ALMOST_WHITE)
        for y in range(0, Constants.BATTLEGROUND_HEIGHT):
            for x in range(0, Constants.BATTLEGROUND_WIDTH):
                self.set_pixel(x, y, pixels[x + Constants.BATTLEGROUND_WIDTH * y][util.constants.DB_COLOR])

    def get_surface(self):
        return self.surface

    def set_pixel(self, x, y, new_color):
        self.surface.set_at((x, y), new_color)

    def get_at(self, x, y):
        return self.surface.get_at((x, y))