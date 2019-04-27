from util.settings import Settings


class Constants:
    game_field_width = 100
    game_field_height = 100
    scroll_amount = 0.1
    upscale_limit = 30
    downscale_limit = int(2.25 * game_field_width)
    text_regular_size = 50
    text_logo_size = 80
    text_small_size = 40
    line_width = 1
    cursor_on_time = 850
    cursor_off_time = 720
    color_width = 50
    pressed_color_width = 40
    frame_width = 64
    ratio = game_field_width / game_field_height
    canvas_width = Settings.screen_width
    canvas_height = int(canvas_width / ratio)
    CLICK_DEAD_ZONE = 0

