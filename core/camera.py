from pygame.rect import Rect

from util.constants import Constants


class Camera:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.scale = 4
        self.rect = Rect(0, 0, Constants.CANVAS_SIZE, Constants.CANVAS_SIZE)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def scale_by(self, amount):
        self.scale += amount * self.scale
        if self.scale < 4:
            self.scale = 4
        if self.scale > 16:
            self.scale = 16
        # self.x -= amount * Constants.CANVAS_SIZE / 2
        # self.y -= amount * Constants.CANVAS_SIZE / 2

    def scale_to(self, scale):
        self.scale = scale

    def get_pixel_size(self):
        return self.scale

    def get_size(self):
        return self.scale * Constants.CANVAS_SIZE

    def get_rect(self):
        size = Constants.CANVAS_SIZE / self.scale
        self.rect.width = size
        self.rect.height = size
        return self.rect
