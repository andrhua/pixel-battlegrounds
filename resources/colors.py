from random import choice


def get_closest_game_palette_color_to(query_color):
    min_dist, closest = 255**2 * 3, Colors.GAME_PALETTE[0]
    for color in Colors.GAME_PALETTE:
        dist = sum(map(lambda a, b: (a - b)**2, color, query_color))
        if dist < min_dist:
            min_dist = dist
            closest = color
    return closest


def get_random_palette_color():
    return choice(Colors.GAME_PALETTE)


class Colors:
    BLACK = (0, 0, 0)
    WHITE = (254, 253, 255)
    GREY = (130, 130, 130)
    RED = (240, 10, 10)
    GAME_PALETTE = ((255, 255, 255), (195, 206, 226), (152, 150, 153), (69, 69, 69), (40, 38, 41), (116, 224, 50),
                    (35, 175, 70), (27, 185, 36), (255, 207, 71), (255, 170, 79), (253, 160, 57), (255, 208, 118),
                    (254, 41, 59), (247, 39, 39), (236, 85, 240), (188, 73, 192), (113, 164, 255), (78, 121, 213),
                    (51, 118, 233))
    SEMITRANSPARENT_BLACK = (0, 0, 0, 140)
    SEMITRANSPARENT_GREY = (128, 128, 128, 100)
    ALMOST_WHITE = (240, 240, 240)
