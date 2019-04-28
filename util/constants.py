class Constants:
    BATTLEGROUND_WIDTH = 100
    BATTLEGROUND_HEIGHT = 100
    SCROLL_STEP = 0.1
    UPSCALE_BOUND = 30
    DOWNSCALE_BOUND = int(2.25 * BATTLEGROUND_WIDTH)
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
    SCREEN_WIDTH = 0
    SCREEN_HEIGHT = 0
    COLOR_PICKER_HEIGHT = 0

    def __init__(self, display_info):
        Constants.SCREEN_WIDTH = display_info.current_w
        Constants.SCREEN_HEIGHT = display_info.current_h
        Constants.CLICK_DEAD_ZONE = display_info.current_w / 200
        Constants.COLOR_BUTTON_SIZE = Constants.SCREEN_HEIGHT * .06
        Constants.COLOR_PICKER_HEIGHT = Constants.SCREEN_HEIGHT * .15

