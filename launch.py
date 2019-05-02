import os
import sys

import pygame
import pyrebase
import resources

from core.game_screen import GameScreen
from core.login_screen import LoginScreen
from core.screen import Context
from resources.assets import Assets
from resources.colors import Colors
from util.constants import Constants


class PixelBattlegroundsGame:
    def __init__(self):
        config = {
            "apiKey": "AIzaSyCtCNdjjhu3YRmfABltpeJC2nq5OXTlgxc",
            "authDomain": "pixel-battlegrounds.firebaseapp.com",
            "databaseURL": "https://pixel-battlegrounds.firebaseio.com",
            "storageBucket": "pixel-battlegrounds.appspot.com",
        }
        firebase = pyrebase.initialize_app(config)
        auth = firebase.auth()

        paths = ['data', 'Saved canvases']
        for path in paths:
            if not os.path.exists(path):
                os.makedirs(path)

        pygame.init()
        pygame.key.set_repeat(400, 50)
        screen = pygame.display.set_mode((Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))
        Assets()
        Constants(pygame.display.Info())
        pygame.display.set_caption(resources.i18n.APP_NAME)
        screen.fill(Colors.ALMOST_WHITE)
        self.context = Context(self, firebase, auth)
        self.stop = False
        self.set_login_screen()

    def run(self):
        clock = pygame.time.Clock()
        while not self.stop:
            for e in pygame.event.get():
                self.screen.process_input_event(e)
            self.screen.update(clock.tick_busy_loop())
            self.screen.draw()
            pygame.display.update()
        pygame.display.quit()
        pygame.quit()
        sys.exit()

    def quit(self):
        self.stop = True

    def set_login_screen(self):
        self.screen = LoginScreen(self.context)

    def set_game_screen(self):
        self.screen = GameScreen(self.context)


if __name__ == '__main__':
    game_instance = PixelBattlegroundsGame()
    game_instance.run()
