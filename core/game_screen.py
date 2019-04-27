import threading
import time

import pygame

from pygame import Rect
from resources.assets import Assets
from resources.colors import Colors
from core.screens import Screen, Target
from ui.styles import TextLabelStyle
from ui.textlabel import TextLabel
from ui.button import ColorPicker
from util.constants import Constants
from util.settings import Settings


class GameScreen(Screen):
    PIXELS = 'pixels'
    SERVICE = 'service'
    COLOR = 'color'
    NEXT_DRAW = 'next_draw'

    def __init__(self, context):
        super().__init__(context)
        self.db = self.context.firebase.database()
        self.pixels_stream = self.db.child(self.PIXELS).stream(self.receive_pixel, self.get_token())
        self.canvas = pygame.Surface(
            [Constants.game_field_width, Constants.game_field_height]).convert_alpha()
        self.canvas.fill(Colors.messy_white)
        self.camera = Rect(0, 0, Constants.game_field_width, Constants.game_field_height)
        self.is_lmb_held = False
        self.is_cooldown = False
        self.camera_x = 0
        self.camera_y = 0
        self.count = 0
        self.passed_time = 0
        self.down_coords = (-1, -1)
        self.prev_coords = (-1, -1)
        nd = self.load(self.NEXT_DRAW)

        if nd is not None:
            self.next_draw = max(self.load(self.NEXT_DRAW) - (time.time() - self.load(self.LAST_EXIT)), 0)
        else:
            self.next_draw = 0
        if self.next_draw > 0:
            self.set_waiting_mode(0)
        self.end_of_round = int(self.db.child(self.SERVICE).child('time').get(self.get_token()).val())
        self.suggestion = None
        self.target = Target()
        self.pixels_queue = []
        self.send_thread = threading.Thread(target=self.send_pixel, daemon=True)
        self.send_thread.start()
        self.load_battlegrounds()

    def init_widgets(self):
        self.add_widget('color_picker', ColorPicker(Colors.transparent_black))
        text_view_style = TextLabelStyle(Assets.font_small, Colors.white, Colors.transparent_black)
        self.add_widget('round_clock',
                        TextLabel('20:18', (Settings.screen_width / 2, 0), text_view_style,
                                  (.05 * Settings.screen_width, .065 * Settings.screen_height)))
        self.add_widget('cooldown_clock',
                        TextLabel('20:24', (Settings.screen_width / 2, 9 * Settings.screen_height / 10),
                                  text_view_style,
                                  (.05 * Settings.screen_width, .065 * Settings.screen_height)))
        self.add_widget('location',
                        TextLabel('(22, 48)', (0, 0), text_view_style)
                        )
        self.get_widget('cooldown_clock').enabled = False
        self.color_picker = self.get_widget('color_picker')

    def update_user_token(self, delta):
        self.passed_time += delta
        if self.passed_time > 50 * 60 * 1000:  # update token every 50 minutes
            self.context.auth.refresh(self.context.user['refreshToken'])
            self.passed_time = 0

    def update_round_clock(self):
        t = self.end_of_round - time.time() * 1000
        seconds = int((t / 1000) % 60)
        minutes = int((t / (1000 * 60)) % 60)
        flag_1 = seconds < 10
        flag_2 = minutes < 10
        self.get_widget('round_clock').set_text(
            ('0' if flag_2 else '') + str(minutes) + ':' + ('0' if flag_1 else '') + str(seconds))

    def update_cooldown_clock(self):
        t = self.next_draw
        seconds = int((t / 1000) % 60)
        minutes = int((t / (1000 * 60)) % 60)
        flag_1 = seconds < 10
        flag_2 = minutes < 10
        self.get_widget('cooldown_clock').set_text(
            ('0' if flag_2 else '') + str(minutes) + ':' + ('0' if flag_1 else '') + str(seconds))

    def update_pointer(self):
        pos = pygame.mouse.get_pos()
        x = int(pos[0] * (self.camera.w / Settings.screen_width) + self.camera.x) + 1
        y = Constants.game_field_height - int(pos[1] * (self.camera.h / Settings.screen_height) + self.camera.y)
        self.get_widget('location').set_text(str('(') + str(x) + ', ' + str(y) + ')')

    def update(self, delta):
        if (delta > 1000 or delta < 0) and self.next_draw > 0:
            self.next_draw = 60 * 60 * 1000
        self.update_user_token(delta)
        self.update_pointer()
        self.update_round_clock()
        if self.is_cooldown:
            self.update_cooldown_clock()
            self.next_draw -= delta
            if self.next_draw <= 0:
                self.color_picker.enabled = True
                self.get_widget('cooldown_clock').enabled = False
                self.is_cooldown = False

        super().update(delta)

    def draw_background(self, screen):
        camera_canvas = pygame.Surface((self.camera.w, self.camera.h))
        camera_canvas.fill(Colors.messy_white)
        camera_canvas.blit(self.canvas, (0, 0), Rect(self.camera_x, self.camera_y, self.camera.w, self.camera.h))
        camera_canvas = pygame.transform.scale(camera_canvas, (Settings.screen_width, Settings.screen_width))
        screen.blit(camera_canvas, (0, 0))

    def draw_projection(self):
        if self.color_picker.selected != -1:
            if self.target.different and self.target.prev_color is not None:
                self.target.different = False
                pygame.draw.rect(self.canvas, self.target.prev_color,
                                 Rect(self.target.prev_dest[0], self.target.prev_dest[1], 1, 1))
            pygame.draw.rect(self.canvas,
                             self.target.target_color if not self.target.gone else self.target.curr_color,
                             Rect(self.target.dest[0], self.target.dest[1], 1, 1))

    def draw(self):
        super().draw()
        self.draw_projection()

    def process_input_events(self, e):
        if e.type == pygame.QUIT:
            self.exit()
        if e.type == pygame.MOUSEBUTTONDOWN:
            if e.button == 1:
                self.is_lmb_held = True
                self.down_coords = pygame.mouse.get_pos()
                self.prev_coords = self.down_coords
            if e.button == 4:  # zoom in
                offset_x = -self.camera.w * Constants.scroll_amount
                offset_y = -self.camera.h * Constants.scroll_amount
                if self.camera.w + offset_x <= Constants.upscale_limit:
                    offset_x = 0
                    offset_y = 0
                self.inflate_camera(offset_x, offset_y)
            if e.button == 5:  # zoom out
                offset_x = self.camera.w * Constants.scroll_amount
                offset_y = self.camera.h * Constants.scroll_amount
                if self.camera.w + offset_x > Constants.downscale_limit:
                    offset_x = 0
                    offset_y = 0
                self.inflate_camera(offset_x, offset_y)
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            self.is_lmb_held = False
        self.check_click(e)
        if self.is_clicked:
            pos = pygame.mouse.get_pos()
            flag = False
            for w in self.widgets.values():
                flag = w.hit(pos[0], pos[1])
                if flag[0]:
                    break
            if not flag[0] and self.color_picker.selected != -1:
                self.conquer_pixel()
            self.color_picker.selected = flag[2] if flag[0] and flag[1] == 'palette' else -1
        if self.is_lmb_held:
            self.move_field()
        self.check_fill()

    def inflate_camera(self, offset_x, offset_y):
        self.camera.inflate_ip(offset_x, offset_y)
        self.camera_x -= offset_x / 2
        self.camera_y -= offset_y / 2
        self.camera.__setattr__('x', self.camera_x)
        self.camera.__setattr__('y', self.camera_y)

    def check_fill(self):
        pos = pygame.mouse.get_pos()
        if self.color_picker.selected != -1:
            if pos[1] <= 9 * Settings.screen_height / 10:
                self.target.gone = False
                x = int(pos[0] * (self.camera.w / Settings.screen_width) + self.camera.x)
                y = int(pos[1] * (self.camera.h / Settings.screen_height) + self.camera.y)
                if 0 <= x < Constants.game_field_width and 0 <= y < Constants.game_field_height:
                    self.target.commit((x, y), Colors.game[self.color_picker.selected],
                                       self.canvas.get_at((x, y)))
                else:
                    self.target.gone = True
            else:
                self.target.gone = True
        else:
            self.target.dest = (-1, -1)

    def move_field(self):
        pos = pygame.mouse.get_pos()
        self.camera_x += (self.prev_coords[0] - pos[0]) * (self.camera.w / Settings.screen_width)
        self.camera_y += (self.prev_coords[1] - pos[1]) * (self.camera.h / Settings.screen_height)
        self.camera.__setattr__('x', self.camera_x)
        self.camera.__setattr__('y', self.camera_y)
        self.prev_coords = pos

    def set_waiting_mode(self, code):
        if code == 1:
            self.next_draw = 5 * 1000  # 0 * 90 * 1000
        self.color_picker.enabled = False
        self.get_widget('cooldown_clock').enabled = True
        self.is_cooldown = True

    def conquer_pixel(self):
        if self.prev_coords[1] <= 9 * Settings.screen_height / 10:
            x = int(self.prev_coords[0] * (self.camera.w / Settings.screen_width) + self.camera.x)
            y = int(self.prev_coords[1] * (self.camera.h / Settings.screen_height) + self.camera.y)
            if 0 <= x < Constants.game_field_width and 0 <= y < Constants.game_field_height:
                self.set_waiting_mode(1)
                colors = Colors.game[self.color_picker.selected]
                self.pixels_queue.append(((x, y), colors))

    def send_pixel(self):
        while 1:
            if self.pixels_queue.__len__() != 0:
                pixel = self.pixels_queue.pop(0)
                dest = pixel[0]
                colors = pixel[1]
                self.db.child(self.PIXELS).child(str(dest[0] + dest[1] * Constants.game_field_width)).update(
                    {
                        self.COLOR: colors
                    }, self.get_token())

    def receive_pixel(self, pixel):
        self.count += 1
        if self.count > 1:
            number = int(pixel['path'][1:])
            x = number % Constants.game_field_width
            y = int((number - x) / Constants.game_field_width)
            self.canvas.set_at((x, y), pixel['data'][self.COLOR])

    def load_battlegrounds(self):
        pixels = self.db.child(self.PIXELS).get(self.get_token()).val()
        for j in range(0, Constants.game_field_height):
            for i in range(0, Constants.game_field_width):
                self.canvas.set_at((i, j), pixels[i + Constants.game_field_width * j][self.COLOR])

    def exit(self):
        self.save(self.NEXT_DRAW, self.next_draw)
        self.save(self.LAST_EXIT, time.time())
        super().exit()
