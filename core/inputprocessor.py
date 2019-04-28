import math

import pygame

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

    def on_mouse_drag(self, delta_x, delta_y):
        pass

    def check_click(self):
        x, y = pygame.mouse.get_pos()
        return math.fabs(self.last_down_position[0] - x) <= Constants.CLICK_DEAD_ZONE and \
               math.fabs(self.last_down_position[1] - y) <= Constants.CLICK_DEAD_ZONE
