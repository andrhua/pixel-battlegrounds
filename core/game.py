from io import BytesIO
from random import shuffle

import requests
from PIL import Image

import util.constants
from resources.colors import get_random_palette_color, get_closest_game_palette_color_to
from ui.widget import Battleground
from util.constants import Constants
from util.decorators import threaded


class Session:
    def __init__(self, game_screen, pixels_db, local_user_token):
        self.game_screen = game_screen
        self.pixels_db = pixels_db
        self.token = local_user_token
        # self.clear_background(500, 500)
        self.battleground = Battleground(self.pixels_db.get(self.token).val())
        self.new_pixels_stream = pixels_db.stream(self.update_pixel, self.token)

    def clear_background(self, width=Constants.BATTLEGROUND_WIDTH, height=Constants.BATTLEGROUND_HEIGHT):
        pixels = {}
        for i in range(width * height):
            pixels[str(i)] = {util.constants.DB_COLOR: get_random_palette_color()}
        self.pixels_db.set(pixels, self.token)

    def conquer_pixel(self, x, y, new_color, token):
        self.pixels_db.child(str(x + y * Constants.BATTLEGROUND_WIDTH)).update({util.constants.DB_COLOR: new_color}, token)

    def update_pixel(self, pixel):
        number = int(pixel['path'][1:])
        x = number % Constants.BATTLEGROUND_WIDTH
        y = int((number - x) / Constants.BATTLEGROUND_WIDTH)
        self.battleground.set_pixel(x, y, pixel['data'][util.constants.DB_COLOR])


class Conqueror:
    def __init__(self):
        self.is_cooldown = False
        self.cooldown_timer = 0

    def set_cooldown(self, value):
        self.is_cooldown = value
        if value:
            self.cooldown_timer = Constants.COOLDOWN

    def update(self, delta):
        pass

    def conquer(self, x, y, new_color):
        self.set_cooldown(True)


class Player(Conqueror):
    def __init__(self, firebase_user, session, cooldown_timer, last_logout_timestamp):
        super().__init__()
        self.user = firebase_user
        self.session = session
        # restore cooldown from previous session if necessary
        if cooldown_timer is not None:
            import time
            self.cooldown_timer = max(cooldown_timer - (time.time() - last_logout_timestamp), 0)
            if self.cooldown_timer > 0:
                self.set_cooldown(True)

    def set_cooldown(self, value):
        super().set_cooldown(value)
        self.session.game_screen.set_cooldown(value)

    def update(self, delta):
        if self.is_cooldown:
            self.cooldown_timer -= delta
            if self.cooldown_timer > 0:
                self.session.game_screen.update_cooldown_clock(self.cooldown_timer + 1000)
            else:
                self.is_cooldown = False
                self.session.game_screen.set_cooldown(False)

    @threaded('conquer')
    def conquer_pixel(self, x, y, new_color):
        super().conquer(x, y, new_color)
        self.session.conquer_pixel(x, y, new_color, self.get_token())

    def get_token(self):
        return self.user[util.constants.DB_TOKEN]


class Bot(Conqueror):
    def __init__(self, session, image_project):
        super().__init__()
        self.battleground = session.battleground
        self.project = image_project

    def update(self, delta):
        if self.is_cooldown:
            self.cooldown_timer -= delta
            if self.cooldown_timer <= 0:
                self.is_cooldown = False
        else:
            self.conquer(0, 0, None)

    def set_cooldown(self, value):
        pass

    def conquer(self, x, y, new_color):
        super().conquer(x, y, new_color)
        i, color = self.project.get_random_pixel()
        if i >= 0:
            x, y = i % Constants.BATTLEGROUND_WIDTH, i // Constants.BATTLEGROUND_HEIGHT
            # self.battleground.set_pixel(
            #     randint(0, Constants.BATTLEGROUND_WIDTH - 1),
            #     randint(0, Constants.BATTLEGROUND_HEIGHT - 1),
            #     Colors.GAME_PALETTE[13]
            # )
            self.battleground.set_pixel(x, y, color)


class ImageProject:
    def __init__(self, picture_url='https://source.unsplash.com/random/500x500'):
        response = requests.get(picture_url)
        img = Image.open(BytesIO(response.content))
        # if img.width > Constants.SCREEN_WIDTH or img.height > Constants.SCREEN_HEIGHT:
        #     img.resize((500, 500), Image.LANCZOS)
        self.pixels = list(img.getdata())[:Constants.BATTLEGROUND_WIDTH * Constants.BATTLEGROUND_HEIGHT]
        self.indices = [i for i in range(len(self.pixels))]
        self.completed = False
        shuffle(self.indices)
        img.show()

    def get_random_pixel(self):
        if self.indices:
            i = self.indices.pop()
            return i, get_closest_game_palette_color_to(self.pixels[i])
        self.completed = True
        return -1, None


