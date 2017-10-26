from enum import Enum
import pygame
import pyrebase
from assets import Assets
from constants import Constants as Consts
from screens import LoginScreen, Context, GameScreen
from settings import Settings as Setts


class Screens(Enum):
    Login = 0
    Game = 1


class Game:
    def __init__(self):
        pygame.init()
        Consts()
        Assets()
        Setts()
        self.init_pyrebase()
        screen = pygame.display.set_mode((Setts.screen_width, Setts.screen_height))
        pygame.display.set_caption(Setts.display_caption)
        screen.fill(Setts.bg_color)
        self.clock = pygame.time.Clock()
        self.context = Context(self, screen, self.firebase, self.auth)
        self.set_screen(Screens.Login)

    def init_pyrebase(self):
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

    def run(self):
        while 1:
            self.screen.update(self.clock.tick())
            self.screen.draw()

    def set_screen(self, screen_name):
        self.screen_name = screen_name
        if screen_name == Screens.Login:
            self.screen = LoginScreen(self.context)
        else:
            self.screen = GameScreen(self.context)
