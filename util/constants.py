LOCAL_SAVE_LAST_LOGOUT_TIMESTAMP = 'last.logout'
LOCAL_SAVE_COOLDOWN_TIME = 'cooldown.time'
LOCAL_SAVE_EMAIL = 'email'
LOCAL_SAVE_PASSWORD = 'password'
DB_COLOR = 'color'
DB_TOKEN = 'idToken'
DB_PIXELS = 'pixels'


class Constants:
    COOLDOWN = 10 * 1000
    CANVAS_SIZE = 100
    ZOOM_STEP = 0.1
    UPSCALE_BOUND = 25
    DOWNSCALE_BOUND = 6
    FONT_REGULAR = 40
    FONT_LOGO = 60
    FONT_SMALL = 25
    LINE_WIDTH = 1
    CURSOR_ON_TIME = 850
    CURSOR_OFF_TIME = 720
    COLOR_BUTTON_SIZE = 20
    PRESSED_COLOR_WIDTH = 10
    FRAME_WIDTH = 64
    CLICK_DEAD_ZONE = 0
    SCREEN_WIDTH = 1280
    SCREEN_HEIGHT = 720
    COLOR_PICKER_HEIGHT = 0
    NOTIFICATION_TIMEOUT = 4 * 1000
    UI_BUTTON_SIZE = 25

    def __init__(self, display_info):
        # Constants.SCREEN_WIDTH = display_info.current_w
        # Constants.SCREEN_HEIGHT = display_info.current_h
        Constants.CLICK_DEAD_ZONE = display_info.current_w / 200
        Constants.COLOR_BUTTON_SIZE = Constants.SCREEN_HEIGHT * .06
        Constants.COLOR_PICKER_HEIGHT = Constants.SCREEN_HEIGHT * .1

