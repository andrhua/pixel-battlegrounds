import pygame


class Settings:
    display_caption=''
    screen_width=0
    screen_height=0
    bg_color=()
    def __init__(self):
        Settings.display_caption="Mail.ru's Battlegrounds"
        info=pygame.display.Info()
        Settings.screen_width=1280#info.current_w
        Settings.screen_height=720#info.current_h
        Settings.bg_color=(250, 250, 250)