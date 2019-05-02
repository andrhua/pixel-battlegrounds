import pygame
import pygame.font

from util.constants import Constants as Consts


class Assets:
    font_regular = None
    font_logo = None
    font_small = None
    icon_photo = None
    icon_fullscreen = None

    def __init__(self):
        Assets.font_regular = pygame.font.Font('resources/font.otf', Consts.FONT_REGULAR)
        Assets.font_logo = pygame.font.Font('resources/font.otf', Consts.FONT_LOGO)
        Assets.font_small = pygame.font.Font('resources/font.otf', Consts.FONT_SMALL)
        Assets.icon_photo = pygame.image.load('resources/photo.png').convert_alpha()
        Assets.icon_fullscreen = pygame.image.load('resources/fullscreen.png').convert_alpha()
