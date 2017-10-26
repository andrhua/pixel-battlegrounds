import shelve
from random import randint
import pygame
import sys
from pygame.rect import Rect
from assets import Assets
from colors import Colors
from ui import TextViewStyle, TextView, EditText, Align
from settings import Settings as Setts
from constants import Constants as Consts


class Context:
    def __init__(self, game, screen, firebase, auth):
        self.game=game
        self.screen = screen
        self.firebase = firebase
        self.auth = auth
        self.user = None


class Screen:
    def __init__(self, context):
        self.context = context
        self.widgets = []
        self.init_widgets()

    def init_widgets(self):
        pass

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            """else:
                for w in self.widgets:
                    if w.hit():
                        break"""

    def update(self, delta):
        self.process_events()

    def draw(self):
        self.draw_bg(self.context.screen)
        for w in self.widgets:
            w.draw(self.context.screen)
        pygame.display.flip()

    def draw_bg(self, screen):
        self.context.screen.fill(Colors.white)


class LoginScreen(Screen):
    def __init__(self, context):
        super().__init__(context)
        self.login()

    def login(self):
        credentials = self.load_credentials()
        email = credentials[0]
        password = credentials[1]
        if email is not None:
            self.context.user = self.context.auth.sign_in_with_email_and_password(email, password)
        else:
            email = input("Enter email: ")
            password = input("Enter password: ")
            try:
                self.user = self.context.auth.sign_in_with_email_and_password(email, password)
            except:
                self.context.user = self.context.auth.create_user_with_email_and_password(email, password)
            self.save_credentials(email, password)
            self.context.game.set_screen(1)
        print("Successfully logged in!")

    def save_credentials(self, email, password):
        file = shelve.open('player.data')
        file['email'] = email
        file['password'] = password
        file.close()

    def load_credentials(self):
        file = shelve.open('player.data')
        email = None
        password = None
        if 'email' in file:
            email = file['email']
            password = file['password']
        file.close()
        return email, password

    def init_widgets(self):
        style_regular = TextViewStyle(Assets.font_regular, Colors.black, Colors.white, Align.center)
        style_logo = TextViewStyle(Assets.font_logo, Colors.black, None, Align.center)
        style_edit_text = TextViewStyle(Assets.font_regular, Colors.grey, Colors.white)
        size = Assets.font_regular.size("Mail.ru's")
        self.widgets.append(TextView("Mail.ru's", (
            Setts.screen_width / 2 - size[0] / 2, .35 * Setts.screen_height - size[1] / 2), style_regular))
        size = Assets.font_logo.size("Battlegrounds")
        self.widgets.append(TextView("Battlegrounds",
                                     (Setts.screen_width / 2 - size[0] / 2, .45 * Setts.screen_height - size[1] / 2),
                                     style_logo))
        size = Assets.font_regular.size("email")
        self.widgets.append(EditText("email", (Setts.screen_width / 2 - size[0] / 2, .55 * Setts.screen_height),
                                     style_edit_text, (Setts.screen_width / 4, size[1] + 2)))
        size = Assets.font_regular.size("password")
        self.widgets.append(EditText("password", (Setts.screen_width / 2 - size[0] / 2, .65 * Setts.screen_height),
                                     style_edit_text, (Setts.screen_width / 4, size[1] + 2), True))


class GameScreen(Screen):
    def __init__(self, context):
        super().__init__(context)
        self.canvas = pygame.Surface(
            [Consts.game_field_width * Consts.pixel_size,
             Consts.game_field_height * Consts.pixel_size]).convert_alpha()
        self.canvas.fill((255, 255, 255))
        self.camera = Rect(0, 0, Consts.game_field_width * Consts.pixel_size,
                           Consts.game_field_height * Consts.pixel_size)
        self.is_lmb_held = False
        self.camera_x = 0
        self.camera_y = 0
        self.count = 0
        self.passed_time = 0
        self.load_game_field()

    def load_game_field(self):
        self.db = self.context.firebase.database()
        pixels = self.db.get(self.get_token()).val()
        for i in range(0, Consts.game_field_width):
            for j in range(0, Consts.game_field_height):
                colors = pixels[i][j]['color']
                self.canvas.set_at((i, j), colors)
        self.pixels_stream = self.db.stream(self.receive_pixel, self.get_token())

    def get_token(self):
        return self.context.user['idToken']

    def draw_bg(self, screen):
        camera_canvas = pygame.Surface((self.camera.w, self.camera.h))
        camera_canvas.blit(self.canvas, (0, 0), Rect(self.camera_x, self.camera_y, self.camera.w, self.camera.h))
        camera_canvas = pygame.transform.scale(camera_canvas, (Setts.screen_width, Setts.screen_height))
        screen.blit(camera_canvas, (0, 0))

    def receive_pixel(self, pixel):
        self.count += 1
        if self.count > 1:
            data = list(pixel['data'].keys())[0].split('/')
            dest = (int(data[0]), int(data[1]))
            self.canvas.set_at(dest, list(pixel['data'].values())[0]['color'])

    def conquer_pixel(self):
        x = int(self.coords[0] * (self.camera.w / Setts.screen_width) + self.camera.x)
        y = int(self.coords[1] * (self.camera.h / Setts.screen_height) + self.camera.y)
        colors = (randint(0, 255), randint(0, 255), randint(0, 255))
        self.send_pixel((x, y), colors)

    def send_pixel(self, dest, colors):
        self.db.update({
            str(dest[0]) + '/' + str(dest[1]) + '/': {
                "color": colors
            }
        }, self.get_token())

    def update_user_token(self, delta):
        self.passed_time += delta
        if self.passed_time > 55 * 60 * 1000:  # update token every 50 minutes
            self.context.auth.refresh(self.context.user['refreshToken'])
            self.passed_time = 0

    def update(self, delta):
        self.update_user_token(delta)
        super().update(delta)

    def inflate_camera(self, offset_x, offset_y):
        self.camera.inflate_ip(offset_x, offset_y)
        self.camera_x -= offset_x / 2
        self.camera_y -= offset_y / 2

    def process_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    self.is_lmb_held = True
                    self.coords = pygame.mouse.get_pos()
                if e.button == 4:  # zoom in
                    offset_x = -self.camera.w * Consts.scroll_amount
                    offset_y = -self.camera.h * Consts.scroll_amount
                    if self.camera.w + offset_x <= Consts.upscale_limit:
                        offset_x = 0
                        offset_y = 0
                    self.inflate_camera(offset_x, offset_y)
                elif e.button == 5:  # zoom out
                    offset_x = self.camera.w * Consts.scroll_amount
                    offset_y = self.camera.h * Consts.scroll_amount
                    if self.camera.w + offset_x > Consts.downscale_limit:
                        offset_x = 0
                        offset_y = 0
                    self.inflate_camera(offset_x, offset_y)
            if e.type == pygame.MOUSEBUTTONUP:
                if e.button == 1:
                    self.conquer_pixel()
                    self.is_lmb_held = False

        if self.is_lmb_held:
            curr_coords = pygame.mouse.get_pos()
            self.camera_x += (self.coords[0] - curr_coords[0]) * (self.camera.w / Setts.screen_width)
            self.camera_y += (self.coords[1] - curr_coords[1]) * (self.camera.h / Setts.screen_height)
            self.camera.__setattr__('x', self.camera_x)
            self.camera.__setattr__('y', self.camera_y)
            self.coords = curr_coords
