import shelve
import sys

import pygame

from core.inputprocessor import InputProcessor
from resources.colors import Colors


class Screen(InputProcessor):
    LAST_EXIT = 'last_exit'

    def __init__(self, context):
        super().__init__()
        self.context = context
        self.surface = pygame.display.get_surface()
        self.widgets = {}
        self.init_ui()
        self.is_clicked = False

    def init_ui(self):
        pass

    def add_widget(self, name, widget):
        self.widgets[name] = widget

    def get_widget(self, name):
        return self.widgets[name]

    def process_input_event(self, e):
        if e.type == pygame.QUIT:
            self.exit()
        super().process_input_event(e)

    def update(self, delta):
        for w in self.widgets.values():
            w.update(delta)

    def draw(self):
        self.draw_background(self.surface)
        for w in self.widgets.values():
            w.draw(self.surface)
        pygame.display.flip()

    def draw_background(self, screen):
        self.surface.fill(Colors.WHITE)

    def save(self, key, value):
        self.context.data[key] = value

    def load(self, key):
        return self.context.data[key] if key in self.context.data else None

    def exit(self):
        self.context.data.close()
        pygame.display.quit()
        pygame.quit()
        sys.exit(1)


class Context:
    def __init__(self, game, firebase, auth):
        self.game = game
        self.firebase = firebase
        self.auth = auth
        self.user = None
        self.data = shelve.open('data/data')

    def get_local_user_token(self):
        return self.user['idToken']


class Target:
    def __init__(self):
        self.dest = (-1, -1)
        self.target_color = (0, 0, 0, 255)
        self.curr_color = (0, 0, 0)
        self.prev_dest = None
        self.prev_color = None
        self.different = False
        self.gone = False

    def commit(self, dest, target_color, curr_color):
        if self.dest[0] != dest[0] or self.dest[1] != dest[1]:
            self.prev_dest = self.dest
            self.prev_color = self.curr_color
            self.dest = dest
            self.target_color = target_color
            self.curr_color = curr_color
            self.different = True

    def __str__(self):
        return self.dest, self.target_color, self.curr_color
