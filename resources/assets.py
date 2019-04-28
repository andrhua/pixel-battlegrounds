import pygame
import pygame.font

from util.constants import Constants as Consts


class Assets:
    font_regular = None
    font_logo = None
    font_small = None

    def __init__(self):
        Assets.font_regular = pygame.font.Font('resources/font.otf', Consts.FONT_REGULAR)
        Assets.font_logo = pygame.font.Font('resources/font.otf', Consts.FONT_LOGO)
        Assets.font_small = pygame.font.Font('resources/font.otf', Consts.FONT_SMALL)
