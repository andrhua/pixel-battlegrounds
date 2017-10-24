import pygame
import pygame.freetype
from constants import Constants as Consts


class Assets:
    font_regular = None

    def __init__(self):
        Assets.font_regular = pygame.freetype.Font('wireone.ttf', Consts.text_regular_size)
