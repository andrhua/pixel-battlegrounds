import time

import pygame
import util.constants
from pygame import Rect

from core.screen import Screen
from core.game import Session, Player, Bot
from resources.assets import Assets
from resources.colors import Colors
from ui.button import ColorPicker, TextButton
from ui.styles import TextLabelStyle, TextButtonStyle
from ui.textlabel import TextLabel
from util.constants import Constants


class GameScreen(Screen):
    def __init__(self, context):
        super().__init__(context)
        self.color_picker = self.get_widget('color_picker')
        self.camera = Rect(0, 0, Constants.BATTLEGROUND_WIDTH,
                           Constants.BATTLEGROUND_WIDTH * Constants.SCREEN_HEIGHT / Constants.SCREEN_WIDTH)
        self.is_cooldown = False
        self.camera_x = 0
        self.camera_y = 0
        self.count = 0
        self.passed_time = 0
        self.projection = None
        self.target = Target()
        self.session = Session(self, self.context.firebase.database().child('pixels'),
                               self.context.get_local_user_token())
        self.player = Player(self.context.user, self.session, self.load(util.constants.LOCAL_SAVE_COOLDOWN_TIME),
                             self.load(util.constants.LOCAL_SAVE_LAST_LOGOUT_TIMESTAMP))
        self.battleground = self.session.battleground.get_surface()
        if self.player.cooldown_time > 0:
            self.set_cooldown(True)
        self.bots = self.add_bots()

    def add_bots(self, num=50):
        bots = []
        for i in range(num):
            bots.append(Bot(self.session))
        return bots

    def init_ui(self):
        self.add_widget('color_picker', ColorPicker(Colors.SEMITRANSPARENT_BLACK))
        helper_label_width, helper_label_height = .055 * Constants.SCREEN_WIDTH, .045 * Constants.SCREEN_HEIGHT
        label_style = TextLabelStyle(Assets.font_regular, Colors.WHITE, Colors.SEMITRANSPARENT_BLACK)
        self.add_widget('location',
                        TextLabel('', Constants.SCREEN_WIDTH / 2, helper_label_height / 2,
                                  label_style,
                                  helper_label_width * 1.1, helper_label_height
                                  ))
        self.add_widget('exit',
                        TextButton('Exit', Constants.SCREEN_WIDTH, 0,
                                   TextButtonStyle(Assets.font_small, Colors.WHITE, Colors.WHITE, Colors.BLACK))
                        )
        self.add_widget('cooldown_clock',
                        TextLabel('', Constants.SCREEN_WIDTH / 2,
                                  Constants.SCREEN_HEIGHT - .6 * Constants.COLOR_PICKER_HEIGHT,
                                  label_style,
                                  helper_label_width, helper_label_height))

        self.get_widget('location').enabled = False
        self.get_widget('cooldown_clock').enabled = False
        # self.add_widget('round_clock',
        #                 TextLabel('00:00', Constants.SCREEN_WIDTH / 2, 0, text_view_style,
        #                           helper_label_width, helper_label_height))

    def update_user_token(self, delta):
        self.passed_time += delta
        if self.passed_time > 50 * 60 * 1000:  # update token every 50 minutes
            self.context.auth.refresh(self.context.user['refreshToken'])
            self.passed_time = 0

    def update_cooldown_clock(self, time_left):
        seconds = int((time_left / 1000) % 60)
        minutes = int((time_left / (1000 * 60)) % 60)
        self.get_widget('cooldown_clock').set_text(f'{minutes:02}:{seconds:02}')

    def update_pointer(self):
        x, y = pygame.mouse.get_pos()
        x = int(x * (self.camera.w / Constants.SCREEN_WIDTH) + self.camera.x)
        y = Constants.BATTLEGROUND_HEIGHT - int(y * (self.camera.h / Constants.SCREEN_HEIGHT) + self.camera.y) - 1
        self.get_widget('location').set_text(f'{x},{y}')

    def update(self, delta):
        self.update_user_token(delta)
        self.update_pointer()
        # self.update_round_clock()
        self.player.update(delta)
        for bot in self.bots:
            bot.update(delta)
        super().update(delta)

    def draw_background(self, screen):
        camera_surface = pygame.Surface((self.camera.w, self.camera.h))
        camera_surface.fill(Colors.ALMOST_WHITE)
        camera_surface.blit(self.battleground, (0, 0), Rect(self.camera.x, self.camera.y, self.camera.w, self.camera.h))
        camera_surface = pygame.transform.scale(camera_surface, (Constants.SCREEN_WIDTH, Constants.SCREEN_HEIGHT))
        screen.blit(camera_surface, (0, 0))

    def draw_projection(self):
        if self.color_picker.selected_color != -1:
            if self.target.different and self.target.prev_color is not None:
                self.target.different = False
                pygame.draw.rect(self.battleground, self.target.prev_color,
                                 Rect(self.target.prev_dest[0], self.target.prev_dest[1], 1, 1))
            pygame.draw.rect(self.battleground,
                             self.target.target_color if not self.target.gone else self.target.curr_color,
                             Rect(self.target.dest[0], self.target.dest[1], 1, 1))

    def draw(self):
        super().draw()
        self.draw_projection()

    def on_mouse_wheel_up(self):
        offset_x = -self.camera.w * Constants.ZOOM_STEP
        offset_y = -self.camera.h * Constants.ZOOM_STEP
        if self.camera.w + offset_x <= Constants.UPSCALE_BOUND:
            offset_x, offset_y = 0, 0
        self.scale_camera(offset_x, offset_y)

    def on_mouse_wheel_down(self):
        offset_x = self.camera.w * Constants.ZOOM_STEP
        offset_y = self.camera.h * Constants.ZOOM_STEP
        if self.camera.w + offset_x > Constants.DOWNSCALE_BOUND:
            offset_x, offset_y = 0, 0
        self.scale_camera(offset_x, offset_y)

    def on_mouse_click(self):
        x, y = pygame.mouse.get_pos()
        for w in self.widgets.values():
            hit_some_widget = w.hit(x, y)[0]
            if hit_some_widget:
                return
        if self.color_picker.selected_color != -1:
            x = int(self.last_down_position[0] * (self.camera.w / Constants.SCREEN_WIDTH) + self.camera.x)
            y = int(self.last_down_position[1] * (self.camera.h / Constants.SCREEN_HEIGHT) + self.camera.y)
            if 0 <= x < Constants.BATTLEGROUND_WIDTH and 0 <= y < Constants.BATTLEGROUND_HEIGHT:
                self.player.conquer_pixel(x, y, Colors.GAME_COLORS[self.color_picker.selected_color])
                self.set_cooldown(True)

    def on_mouse_drag(self, delta_x, delta_y):
        self.move_camera(delta_x, delta_y)

    def process_input_event(self, e):
        super().process_input_event(e)
        self.check_fill()

    def scale_camera(self, offset_x, offset_y):
        self.camera.inflate_ip(offset_x, offset_y)
        self.camera_x -= offset_x / 2
        self.camera_y -= offset_y / 2
        self.camera.__setattr__('x', self.camera_x)
        self.camera.__setattr__('y', self.camera_y)

    def check_fill(self):
        if self.color_picker.selected_color != -1:
            x, y = pygame.mouse.get_pos()
            if y <= Constants.SCREEN_HEIGHT - Constants.COLOR_PICKER_HEIGHT:
                self.target.gone = False
                x = int(x * (self.camera.w / Constants.SCREEN_WIDTH) + self.camera.x)
                y = int(y * (self.camera.h / Constants.SCREEN_HEIGHT) + self.camera.y)
                if 0 <= x < Constants.BATTLEGROUND_WIDTH and 0 <= y < Constants.BATTLEGROUND_HEIGHT:
                    self.target.commit((x, y), Colors.GAME_COLORS[self.color_picker.selected_color],
                                       self.session.battleground.get_at(x, y))
                else:
                    self.target.gone = True
            else:
                self.target.gone = True
        else:
            self.target.dest = (-1, -1)

    def move_camera(self, dx, dy):
        self.camera_x += dx * (self.camera.w / Constants.SCREEN_WIDTH)
        self.camera_y += dy * (self.camera.h / Constants.SCREEN_HEIGHT)
        self.camera.__setattr__('x', self.camera_x)
        self.camera.__setattr__('y', self.camera_y)

    def set_cooldown(self, value):
        if value:
            self.color_picker.reset_selection()
        self.get_widget('cooldown_clock').enabled = value
        self.color_picker.enabled = not value

    def exit(self):
        self.save(util.constants.LOCAL_SAVE_COOLDOWN_TIME, self.player.cooldown_time)
        self.save(util.constants.LOCAL_SAVE_LAST_LOGOUT_TIMESTAMP, time.time())
        super().exit()


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