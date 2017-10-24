class Constants:
    text_regular_size = 0
    pixel_size=0
    scroll_amount=0
    upscale_limit=0
    downscale_limit=0
    game_field_width=0
    game_field_height=0

    def __init__(self):
        Constants.pixel_size = 1
        Constants.scroll_amount = 0.1
        Constants.upscale_limit = 40 * self.pixel_size
        Constants.downscale_limit = 3000
        Constants.game_field_width = 10
        Constants.game_field_height = 5
        Constants.text_regular_size=50