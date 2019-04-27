import math
import shelve
import sys

import pygame

from resources.colors import Colors
from util.constants import Constants as Consts
from util.settings import Settings


class Screen:
    LAST_EXIT = 'last_exit'
    TOKEN = 'idToken'

    def __init__(self, context):
        self.context = context
        self.widgets = {}
        self.init_widgets()
        self.is_clicked = False
        self.down_coords = (0, 0)
        self.last_mouse_event = -1
        self.last_mouse_pos = (-1, -1)

    def init_widgets(self):
        pass

    def add_widget(self, name, widget):
        self.widgets[name] = widget

    def get_widget(self, name):
        return self.widgets[name]

    def process_input_events(self, e):
        pass

    def check_click(self, e):
        pos = pygame.mouse.get_pos()
        self.is_clicked = e.type == pygame.MOUSEBUTTONUP and \
                          e.button == 1 and math.fabs(self.down_coords[0] - pos[0]) <= Consts.CLICK_DEAD_ZONE and \
                          math.fabs(self.down_coords[1] - pos[1]) <= Consts.CLICK_DEAD_ZONE

    def update(self, delta):
        for w in self.widgets.values():
            w.update(delta)

    def draw(self):
        self.draw_background(self.context.screen)
        for w in self.widgets.values():
            w.draw(self.context.screen)
        pygame.display.flip()

    def draw_background(self, screen):
        self.context.screen.fill(Colors.white)

    def save(self, key, value):
        self.context.data[key] = value

    def load(self, key):
        return self.context.data[key] if key in self.context.data else None

    def get_token(self):
        return self.context.user[self.TOKEN]

    def exit(self):
        self.context.data.close()
        pygame.display.quit()
        pygame.quit()
        sys.exit(1)


class Context:
    def __init__(self, game, screen, firebase, auth):
        self.game = game
        self.screen = screen
        self.firebase = firebase
        self.auth = auth
        self.user = None
        self.data = shelve.open('data/data')


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
