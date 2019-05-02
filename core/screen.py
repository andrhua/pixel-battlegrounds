import math
import shelve
import sys

import pygame

from resources.colors import Colors
from util.constants import Constants


class InputProcessor:
    def __init__(self):
        self.last_down_position = (-1, -1)
        self.is_lmb_held = False

    def process_input_event(self, e):
        if e.type == pygame.KEYDOWN:
            self.on_key_down(e.key, e.unicode)
        elif e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
                self.on_left_mouse_button_down()
            elif e.button == 4:
                self.on_mouse_wheel_up()
            elif e.button == 5:
                self.on_mouse_wheel_down()
        elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.on_left_mouse_button_up()
        if self.is_lmb_held:
            x, y = pygame.mouse.get_pos()
            self.on_mouse_drag(self.last_down_position[0] - x, self.last_down_position[1] - y)
            self.last_down_position = (x, y)

    def on_key_down(self, key, unicode):
        pass

    def on_left_mouse_button_down(self):
        self.is_lmb_held = True
        self.last_down_position = pygame.mouse.get_pos()

    def on_mouse_wheel_up(self):
        pass

    def on_mouse_wheel_down(self):
        pass

    def on_left_mouse_button_up(self,):
        self.is_lmb_held = False
        if self.check_click():
            self.on_mouse_click()

    def on_mouse_click(self):
        pass

    def on_mouse_drag(self, dx, dy):
        pass

    def check_click(self):
        x, y = pygame.mouse.get_pos()
        return math.fabs(self.last_down_position[0] - x) <= Constants.CLICK_DEAD_ZONE and \
               math.fabs(self.last_down_position[1] - y) <= Constants.CLICK_DEAD_ZONE


class Context:
    def __init__(self, game, firebase, auth):
        self.game = game
        self.firebase = firebase
        self.auth = auth
        self.user = None
        self.data = shelve.open('data/data')

    def get_local_user_token(self):
        return self.user['idToken']


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

    def draw_background(self, screen):
        self.surface.fill(Colors.WHITE)

    def save(self, key, value):
        self.context.data[key] = value

    def load(self, key):
        return self.context.data[key] if key in self.context.data else None

    def exit(self):
        self.context.data.close()
        self.context.game.quit()
