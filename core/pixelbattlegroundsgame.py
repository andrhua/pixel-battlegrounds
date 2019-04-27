import os

import pygame
import pyrebase

from core.game_screen import GameScreen
from core.login_screen import LoginScreen
from core.screens import Context
from resources.assets import Assets
from resources.colors import Colors
from util.constants import Constants


class PixelBattlegroundsGame:
    def __init__(self):
        config = {
            "apiKey": "AIzaSyCtCNdjjhu3YRmfABltpeJC2nq5OXTlgxc",
            "authDomain": "pixel-battlegrounds.firebaseapp.com",
            "databaseURL": "https://pixel-battlegrounds.firebaseio.com",
            "projectId": "pixel-battlegrounds",
            "storageBucket": "pixel-battlegrounds.appspot.com",
            "messagingSenderId": "704655328627"
        }
        self.firebase = pyrebase.initialize_app(config)
        self.auth = self.firebase.auth()

        path = 'data'
        if not os.path.exists(path):
            os.makedirs(path)

        pygame.init()
        pygame.key.set_repeat(400, 50)
        Assets()
        screen = pygame.display.set_mode()  # (Settings.screen_width, Settings.screen_height))
        Constants(pygame.display.Info())
        pygame.display.set_caption('Pixel Battlegrounds')
        screen.fill(Colors.messy_white)
        self.clock = pygame.time.Clock()
        self.context = Context(self, screen, self.firebase, self.auth)
        self.set_screen('login')

    def run(self):
        while 1:
            for e in pygame.event.get():
                self.screen.process_input_events(e)
            self.screen.update(self.clock.tick_busy_loop())
            self.screen.draw()

    def set_screen(self, screen_name):
        if screen_name == 'login':
            self.screen = LoginScreen(self.context)
        elif screen_name == 'game':
            self.screen = GameScreen(self.context)
