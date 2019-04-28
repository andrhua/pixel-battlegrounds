import util.constants

from resources.colors import Colors
from ui.widget import Battleground
from util.constants import Constants


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
