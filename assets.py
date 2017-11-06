import pygame
import pygame.font
from constants import Constants as Consts


class Assets:
    font_regular = None
    font_logo = None
    font_small = None

    def __init__(self):
        Assets.font_regular = pygame.font.Font('wireone.ttf', Consts.text_regular_size)
        Assets.font_logo = pygame.font.Font('wireone.ttf', Consts.text_logo_size)
        Assets.font_small = pygame.font.Font('wireone.ttf', Consts.text_small_size)
