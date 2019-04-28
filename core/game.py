import util.constants
from resources.colors import Colors
from ui.widget import Battleground
from util.constants import Constants
from util.decorators import threaded
from random import randint, choice, random
from time import sleep


class Session:
    def __init__(self, game_screen, pixels_db, local_user_token):
        self.game_screen = game_screen
        self.pixels_db = pixels_db
        self.token = local_user_token
        # self.clear_background()
        self.battleground = Battleground(self.pixels_db.get(self.token).val())
        self.new_pixels_stream = pixels_db.stream(self.update_pixel, self.token)

    def clear_background(self):
        from random import choice
        pixels = {}
        for i in range(0, Constants.BATTLEGROUND_WIDTH * Constants.BATTLEGROUND_HEIGHT):
            pixels[str(i)] = {util.constants.DB_COLOR: choice(Colors.GAME_COLORS)}
        self.pixels_db.remove(self.token)
        self.pixels_db.set(self.token)

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
        self.cooldown_time = 0

    def set_cooldown(self, value):
        self.is_cooldown = value
        if value and self.cooldown_time <= 0:
            self.cooldown_time = Constants.COOLDOWN

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
            self.cooldown_time = max(cooldown_timer - (time.time() - last_logout_timestamp), 0)

    def set_cooldown(self, value):
        super().set_cooldown(value)
        self.session.game_screen.set_cooldown(value)

    def update(self, delta):
        if self.is_cooldown:
            self.cooldown_time -= delta
            if self.cooldown_time > 0:
                self.session.game_screen.update_cooldown_clock(self.cooldown_time)
            else:
                self.is_cooldown = False
                self.session.game_screen.set_cooldown(False)

    @threaded
    def conquer_pixel(self, x, y, new_color):
        super().conquer(x, y, new_color)
        self.session.conquer_pixel(x, y, new_color, self.get_token())

    def get_token(self):
        return self.user[util.constants.DB_TOKEN]


class Bot(Conqueror):
    def __init__(self, session):
        super().__init__()
        self.battleground = session.battleground

    def update(self, delta):
        if self.is_cooldown:
            self.cooldown_time -= delta
            if self.cooldown_time <= 0:
                self.is_cooldown = False
        else:
            self.conquer(0, 0, None)

    def conquer(self, x, y, new_color):
        super().conquer(x, y, new_color)
        self.battleground.set_pixel(
            randint(0, Constants.BATTLEGROUND_WIDTH - 1),
            randint(0, Constants.BATTLEGROUND_HEIGHT - 1),
            Colors.GAME_COLORS[0]# choice(Colors.GAME_COLORS)
        )
