import datetime
import time

import pygame
import util.constants
import resources.i18n
from pygame import Rect

from core.camera import Camera
from core.screen import Screen
from core.game import Session, Player, Bot, ImageProject
from resources.assets import Assets
from resources.colors import Colors
from ui.button import ColorPicker, TextButton
from ui.styles import TextLabelStyle, TextButtonStyle, Align
from ui.textlabel import TextLabel, Notification
from util.constants import Constants


class GameScreen(Screen):
    def __init__(self, context):
        super().__init__(context)
        self.color_picker = self.get_widget('color_picker')
        self.camera = Camera()
        self.passed_time = 0
        self.projection = None
        self.session = Session(self, self.context.firebase.database(),
                               self.context.get_local_user_token())
        self.player = Player(self.context.user, self.session, self.load(util.constants.LOCAL_SAVE_COOLDOWN_TIME),
                             self.load(util.constants.LOCAL_SAVE_LAST_LOGOUT_TIMESTAMP))
        self.canvas = self.session.canvas.get_surface()
        if self.player.cooldown_timer > 0:
            self.set_cooldown(True)
        self.bots = self.add_bots()
        self.bots_flag = False

    def add_bots(self, num=50):
        bots = []
        for i in range(num):
            bots.append(Bot(self.session, None))
        return bots

    def init_ui(self):
        self.add_widget('color_picker', ColorPicker(Colors.SEMITRANSPARENT_BLACK))
        label_style = TextLabelStyle(Assets.font_small, Colors.WHITE, Colors.SEMITRANSPARENT_BLACK, Align.left)
        button_style = TextButtonStyle(Assets.font_small, Colors.WHITE, Colors.WHITE, Colors.BLACK)
        self.add_widget('exit',
                        TextButton('Exit', 0, 0,
                                   button_style,
                                   self.exit)
                        )
        self.add_widget('location',
                        TextLabel('aaa,bbb', 0, Constants.SCREEN_HEIGHT - Constants.COLOR_PICKER_HEIGHT - self.get_widget('exit').height,
                                  label_style,
                                  ))
        label_style.align = Align.center
        self.add_widget('cooldown_clock',
                        TextLabel('00:00', Constants.SCREEN_WIDTH / 2,
                                  Constants.SCREEN_HEIGHT - .6 * Constants.COLOR_PICKER_HEIGHT,
                                  label_style).center())
        self.get_widget('cooldown_clock').enabled = False
        self.add_widget('notification',
                        Notification(Constants.SCREEN_WIDTH / 2, self.get_widget('location').y, label_style).center())
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
        x, y = self.global_to_canvas(*pygame.mouse.get_pos())
        y = Constants.CANVAS_SIZE - y - 1
        self.get_widget('location').set_text(f'{x},{y}')

    def update(self, delta):
        self.update_user_token(delta)
        self.update_pointer()
        # self.update_round_clock()
        self.player.update(delta)
        if self.bots_flag:
            for bot in self.bots:
                if bot.project.completed:
                    self.bots_flag = False
                    break
                bot.update(delta)
        super().update(delta)

    def draw_background(self, screen):
        size = int(self.camera.get_size())
        canvas = pygame.transform.scale(self.canvas, (size, size))
        screen.fill(Colors.ALMOST_WHITE)
        screen.blit(canvas, (self.camera.x, self.camera.y))

    def get_pixel_size(self):
        return self.camera.scale

    def draw_projection(self):
        if self.color_picker.selected_color != -1:
            x, y = pygame.mouse.get_pos()
            size = self.camera.get_pixel_size()
            pygame.draw.rect(self.surface, self.color_picker.get_selection(), Rect(x - size / 2, y - size / 2, size, size))

    def draw(self):
        super().draw()
        self.draw_projection()

    def on_mouse_wheel_up(self):
        self.camera.scale_by(Constants.ZOOM_STEP)

    def on_mouse_wheel_down(self):
        self.camera.scale_by(-Constants.ZOOM_STEP)

    def on_mouse_click(self):
        x, y = pygame.mouse.get_pos()
        for w in self.widgets.values():
            hit_some_widget, name = w.hit(x, y)
            if hit_some_widget:
                return
        if self.color_picker.selected_color != -1:
            x, y = self.global_to_canvas(x, y)
            if 0 <= x < Constants.CANVAS_SIZE and 0 <= y < Constants.CANVAS_SIZE:
                self.player.conquer_pixel(x, y, Colors.GAME_PALETTE[self.color_picker.selected_color])
                self.set_cooldown(True)

    def on_mouse_drag(self, dx, dy):
        self.camera.move(-dx, -dy)

    def global_to_canvas(self, x, y):
        return int((x - self.camera.x) / self.camera.scale), int((y - self.camera.y) / self.camera.scale)

    def canvas_to_global(self, position):
        pass

    def set_cooldown(self, value):
        if value:
            self.color_picker.reset_selection()
        self.get_widget('cooldown_clock').enabled = value
        self.color_picker.enabled = not value

    def notify(self, message):
        self.get_widget('notification').notify(message)

    def exit(self):
        self.save(util.constants.LOCAL_SAVE_COOLDOWN_TIME, self.player.cooldown_timer)
        self.save(util.constants.LOCAL_SAVE_LAST_LOGOUT_TIMESTAMP, time.time())
        super().exit()

    def on_key_down(self, key, unicode):
        if key == pygame.K_LSHIFT:
            self.on_mouse_wheel_up()
        elif key == pygame.K_LCTRL:
            self.on_mouse_wheel_down()
        elif key == pygame.K_ESCAPE:
            self.exit()
        elif key == pygame.K_s:
            self.save_battleground_to_image()
        elif key == pygame.K_n:
            self.create_new_project()
        elif key == pygame.K_b:
            self.launch_bots()
        elif key == pygame.K_i:
            self.toggle_ui()
        elif key == pygame.K_a:
            self.session.set_local_canvas_to_global()

    def save_battleground_to_image(self):
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
        pygame.image.save(self.canvas, f'Saved battlegrounds/{timestamp}.png')
        self.notify(resources.i18n.CANVAS_SAVED)

    def create_new_project(self):
        project = ImageProject()
        for bot in self.bots:
            bot.project = project

    def launch_bots(self):
        self.bots_flag = not self.bots_flag
        # self.notify())

    def toggle_ui(self):
        for name, w in self.widgets.items():
            if name != 'cooldown_clock':
                w.enabled = not w.enabled
