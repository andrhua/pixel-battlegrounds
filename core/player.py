from util.decorators import threaded
import util.constants


class Player:
    def __init__(self, firebase_user, session, cooldown_timer, last_logout_timestamp):
        self.user = firebase_user
        self.session = session
        # restore cooldown from previous session if necessary
        if cooldown_timer is not None:
            import time
            self.cooldown_time = max(cooldown_timer - (time.time() - last_logout_timestamp), 0)
        else:
            self.cooldown_time = 0

    def set_cooldown(self, value):
        if value and self.cooldown_time <= 0:
            self.cooldown_time = 5 * 1000
        self.session.game_screen.set_cooldown(value)

    def update(self, delta):
        if self.cooldown_time > 0:
            self.cooldown_time -= delta
            self.session.game_screen.update_cooldown_clock(self.cooldown_time)

    @threaded
    def conquer_pixel(self, x, y, new_color):
        self.session.conquer_pixel(x, y, new_color, self.get_token())

    def get_token(self):
        return self.user[util.constants.DB_TOKEN]
