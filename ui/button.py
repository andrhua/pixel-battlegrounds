import pygame
from pygame.rect import Rect

from resources.colors import Colors
from ui.styles import Align, ButtonStyle
from ui.widget import Widget
from util.constants import Constants


class Button(Widget):
    def __init__(self, width, height, x, y, style, run_on_hit, *args, **kwargs):
        super().__init__(width, height, x, y)
        self.pressed_width, self.pressed_height = int(self.width * .9), int(self.height * .9)
        self.pressed_x, self.pressed_y = self.x + (self.width / 2 - self.pressed_width / 2), self.y + (
                self.height / 2 - self.pressed_height / 2)
        self.style = style
        self.pressed = False
        self.pressed_rect = Rect(0, 0, self.pressed_width, self.pressed_height)
        self.run_on_hit = run_on_hit
        self.args = args
        self.kwargs = kwargs
        self.update_surface()

    def update_surface(self):
        pygame.draw.rect(self.surface, self.style.background_color, Rect(0, 0, self.width, self.height))

    def draw(self, surface):
        if self.enabled:
            surface.blit(self.surface, (
                self.x + (self.width / 2 - self.pressed_width / 2 if self.pressed else 0),
                self.y + (self.height / 2 - self.pressed_height / 2 if self.pressed else 0),
            ))

    def on_hit(self):
        self.pressed = not self.pressed
        self.surface = pygame.transform.scale(self.surface,
                               (self.pressed_width, self.pressed_height) if self.pressed else (self.width, self.height))
        self.run_on_hit(*self.args, **self.kwargs)


class TextButton(Button):
    def __init__(self, text, x, y, style, run_on_hit, *args, **kwargs):
        self.text = text
        self.text_x, self.text_y = 0, 0
        self.text_width, self.text_height = style.font.size(text)
        super().__init__(self.text_width + self.text_width / len(text) * 2,
                         self.text_height + self.text_height, x, y, style, run_on_hit, *args, **kwargs)
        self.update_text_position()

    def set_text(self, text):
        self.text = text
        old_width, old_height = self.width, self.height
        self.text_width, self.text_height = self.style.font.size(text)
        self.width, self.height = self.text_width * 1.75, self.text_height * 1.5
        self.update_rectangle_position(self.width - old_width, self.height - old_height)
        self.update_text_position()
        self.update_surface()

    def update_rectangle_position(self, dx, dy):
        if self.style.align == Align.left:
            pass
        elif self.style.align == Align.center:
            self.x -= dx / 2
            self.y -= dy / 2
        elif self.style.align == Align.right:
            self.x -= dx
            self.y -= dy

    def update_text_position(self):
        self.text_x = self.width / 2 - self.text_width / 2
        self.text_y = self.height / 2 - self.text_height / 2
        self.update_surface()

    def draw(self, surface):
        if self.enabled:
            surface.blit(self.surface, (self.x, self.y))

    def update_surface(self):
        super().update_surface()
        pygame.draw.rect(self.surface, self.style.background_color, Rect(1, 1, self.width - 2, self.height - 2))
        self.surface.blit(self.style.font.render(self.text, True, self.style.text_color, self.style.background_color),
                          (self.text_x, self.text_y))


class ImageButton(Button):
    def __init__(self, image, width, height, x, y, style, run_on_hit, *args, **kwargs):
        super().__init__(width, height, x, y, style, run_on_hit, *args, **kwargs)
        self.surface = pygame.transform.scale(image, (width, height))

    def on_hit(self):
        pass


class ColorPicker(Widget):
    def __init__(self, background_color):
        super().__init__(Constants.SCREEN_WIDTH, Constants.COLOR_PICKER_HEIGHT,
                         0, Constants.SCREEN_HEIGHT - Constants.COLOR_PICKER_HEIGHT)
        self.background_color = background_color
        self.selected_color = -1
        style = ButtonStyle(None)
        for i, color in enumerate(Colors.GAME_PALETTE):
            number_of_colors = len(Colors.GAME_PALETTE)
            style.background_color = color
            self.add_child(Button(Constants.COLOR_BUTTON_SIZE, Constants.COLOR_BUTTON_SIZE,
                                  (i + 1) * Constants.SCREEN_WIDTH / (number_of_colors + 1) - Constants.COLOR_BUTTON_SIZE / 2,
                                  Constants.COLOR_PICKER_HEIGHT / 2 - Constants.COLOR_BUTTON_SIZE / 2,
                                  style,
                                  self.activate_button, i))
        self.update_surface()

    def activate_button(self, i):
        if self.selected_color != -1:
            self.children[self.selected_color].pressed = False
        self.selected_color = i
        self.children[i].pressed = True
        self.update_surface()

    def draw(self, surface):
        if self.enabled:
            surface.blit(self.surface, (self.x, self.y))

    def update_surface(self, *args):
        self.surface.fill((0, 0, 0))
        self.surface.convert_alpha()
        pygame.draw.rect(self.surface, self.background_color, Rect(0, 0, self.width, self.height))
        for button in self.children:
            button.draw(self.surface)

    def reset_selection(self):
        self.children[self.selected_color].pressed = False
        self.selected_color = -1
        self.update_surface()

    def get_selection(self):
        return None if self.selected_color == -1 else Colors.GAME_PALETTE[self.selected_color]

    def hit(self, x, y):
        if self.enabled:
            for i, button in enumerate(self.children):
                if button.hit(x, y - self.y)[0] and button.pressed:
                    button.on_hit()
                    return True, 'palette'
            if self.hitbox.collidepoint(x, y):
                return True, 'palette'
        return False, 'palette'

    def __repr__(self):
        return 'palette'
