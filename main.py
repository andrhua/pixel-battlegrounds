import pygame
import sys
from random import randint
from pygame.rect import Rect
from constants import Constants
from settings import Settings


class Game:
    def __init__(self):
        pygame.init()

        self.setts = Settings()
        self.consts = Constants()

        self.screen = pygame.display.set_mode((self.setts.screen_width, self.setts.screen_height))
        pygame.display.set_caption(self.setts.display_caption)
        self.screen.fill(self.setts.bg_color)

        self.canvas = pygame.Surface(
            [self.consts.game_field_width * self.consts.pixel_size,
             self.consts.game_field_height * self.consts.pixel_size]).convert_alpha()
        self.canvas.fill((255, 255, 255))
        for i in range(0, self.consts.game_field_width):
            for j in range(0, self.consts.game_field_height):
                pygame.draw.rect(self.canvas, (randint(0, 255), randint(0, 255), randint(0, 255)),
                                 (i * self.consts.pixel_size, j * self.consts.pixel_size, self.consts.pixel_size,
                                  self.consts.pixel_size))
        self.camera = Rect(0, 0, self.consts.game_field_width * self.consts.pixel_size,
                           self.consts.game_field_height * self.consts.pixel_size)

        self.is_lmb_held = False
        self.camera_x=0
        self.camera_y=0

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    self.is_lmb_held = False
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.coords = pygame.mouse.get_pos()
                    self.is_lmb_held = True
                if e.button == 4:  # zoom in
                    offset_x = -self.camera.w * self.consts.scroll_amount
                    offset_y = -self.camera.h * self.consts.scroll_amount
                    if self.camera.w + offset_x <= self.consts.upscale_limit:
                        offset_x = 0
                        offset_y = 0
                    self.inflate(offset_x, offset_y)
                elif e.button == 5:  # zoom out
                    offset_x = self.camera.w * self.consts.scroll_amount
                    offset_y = self.camera.h * self.consts.scroll_amount
                    if self.camera.w + offset_x > self.consts.downscale_limit:
                        offset_x = 0
                        offset_y = 0
                    self.inflate(offset_x, offset_y)

        if self.is_lmb_held:
            curr_coords = pygame.mouse.get_pos()
            self.camera_x+=(self.coords[0] - curr_coords[0]) * (self.camera.w / self.setts.screen_width)
            self.camera_y+=(self.coords[1] - curr_coords[1]) * (self.camera.h / self.setts.screen_height)
            self.camera.__setattr__('x', self.camera_x)
            self.camera.__setattr__('y', self.camera_y)
            self.coords = curr_coords

    def inflate(self, offset_x, offset_y):
        self.camera.inflate_ip(offset_x, offset_y)
        self.camera_x-=offset_x/2
        self.camera_y-=offset_y/2

    def draw(self):
        camera_canvas = pygame.Surface((self.camera.w, self.camera.h))
        camera_canvas.blit(self.canvas, (0, 0), Rect(self.camera_x, self.camera_y, self.camera.w, self.camera.h))
        camera_canvas = pygame.transform.scale(camera_canvas, (self.setts.screen_width, self.setts.screen_height))
        self.screen.fill((255, 255, 255))
        self.screen.blit(camera_canvas, (0, 0))
        pygame.display.flip()

    def run(self):
        while 1:
            self.process_events()
            self.draw()


game = Game()
game.run()
