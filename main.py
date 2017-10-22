import pygame
import sys
from random import randint

from pygame.rect import Rect

from settings import Settings


def run_game():
    pixel_size=4
    scroll_amount = 0.1
    upscale_limit = 40*pixel_size
    downscale_limit = 2000*pixel_size
    is_lmb_held = False
    settings = Settings()
    pygame.init()
    screen = pygame.display.set_mode((settings.screen_width, settings.screen_height))
    pygame.display.set_caption(settings.display_caption)
    screen.fill(settings.bg_color)

    canvas = pygame.Surface([settings.game_field_width*pixel_size, settings.game_field_height*pixel_size]).convert_alpha()
    canvas.fill((255, 255, 255))
    for i in range(0, settings.game_field_width):
        for j in range(0, settings.game_field_height):
            pygame.draw.rect(canvas, (randint(0, 255), randint(0, 255), randint(0, 255)), (i*pixel_size, j*pixel_size, pixel_size, pixel_size))
    camera = Rect(0, 0, settings.game_field_width*pixel_size, settings.game_field_height*pixel_size)

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type==pygame.MOUSEMOTION and is_lmb_held:
               pass
            if e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    is_lmb_held = False
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    coordinates = pygame.mouse.get_pos()
                    is_lmb_held = True

                if e.button == 4: #zoom in
                    offset_x = -camera.w * scroll_amount
                    offset_y = -camera.h * scroll_amount
                    if camera.w+offset_x <= upscale_limit:
                        offset_x = 0
                        offset_y = 0
                    camera.inflate_ip(offset_x, offset_y)

                elif e.button == 5: #zoom out
                    offset_x = camera.w * scroll_amount
                    offset_y = camera.h * scroll_amount
                    if camera.w+offset_x > downscale_limit:
                        offset_x = 0
                        offset_y = 0
                    camera.inflate_ip(offset_x, offset_y)

        if is_lmb_held:
            current_coordinates = pygame.mouse.get_pos()
            camera.move_ip((coordinates[0]-current_coordinates[0])*(camera.w/settings.screen_width), (coordinates[1]-current_coordinates[1])*(camera.w/settings.game_field_width))
            print((coordinates[0]-current_coordinates[0])*(camera.w/settings.screen_width), (coordinates[1]-current_coordinates[1])*(camera.w/settings.game_field_width))
            coordinates = current_coordinates

        camera_canvas = pygame.Surface((camera.w, camera.h))
        camera_canvas.blit(canvas, (0,0), camera)
        camera_canvas=pygame.transform.scale(camera_canvas, (settings.screen_width, settings.screen_height))
        screen.fill((255, 255, 255))
        screen.blit(camera_canvas, (0, 0))
        pygame.display.flip()


run_game()
