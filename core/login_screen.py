import pygame
from requests import HTTPError

from resources.assets import Assets
from resources.colors import Colors
from core.screens import Screen
from ui.styles import TextLabelStyle, Align, TextFormStyle
from ui.textlabel import TextLabel, TextForm
from ui.widget import SpriteImage
from util.async_task import AsyncTask
from util.constants import Constants


class LoginScreen(Screen):
    EMAIL = "email"
    PASS = "pass"
    VERIFICATION_SENT = "Verify your email via letter we've just sent and sign in."
    WRONG_PASS = "Incorrect password."
    WEAK_PASS = "Password must contain a minimum of 6 characters."
    WRONG_EMAIL = "Incorrect email."
    NOT_VERIFIED_EMAIL = "Please first verify your email. Check spam box if necessary."
    APP_NAME = "Pixel Battlegrounds"
    EMAIL_HINT = "email"
    PASSWORD_HINT = "password"

    def __init__(self, context):
        super().__init__(context)
        self.active_form = None
        self.login_task = None
        email, password = self.load(self.EMAIL), self.load(self.PASS)
        if email is not None:
            self.context.last_exit = self.load(self.LAST_EXIT)
            # self.get_widget('email_form').set_text = email
            # self.get_widget('password_form').set_text = password
            self.login_task = AsyncTask(self.login, email, password)
            self.login_task.execute()

    def login(self, email, password):
        def handle_exception(e):
            def update_login_feedback(text):
                self.get_widget('login_feedback').set_text(text)

            # print(e)
            if 'EMAIL_NOT_FOUND' in e:
                try:
                    self.context.user = self.context.auth.create_user_with_email_and_password(email, password)
                except HTTPError:
                    update_login_feedback(self.WEAK_PASS)
                else:
                    self.context.auth.send_email_verification(self.get_token())
                    update_login_feedback(self.VERIFICATION_SENT)
                    self.save(self.EMAIL, email)
                    self.save(self.PASS, password)
            if 'INVALID_PASSWORD' in e:
                update_login_feedback(self.WRONG_PASS)
            if 'INVALID_EMAIL' in e:
                update_login_feedback(self.WRONG_EMAIL)
            if 'EMAIL_NOT_VERIFIED' in e:
                self.context.auth.send_email_verification(self.get_token())
                update_login_feedback(self.NOT_VERIFIED_EMAIL)
            self.get_widget('email_form').is_editable = True
            self.get_widget('password_form').is_editable = True
            self.get_widget('loader').enabled = False
            self.get_widget('login_feedback').enabled = True

        def check_verification():
            info = self.context.auth.get_account_info(self.get_token())
            if info['users'][0]['emailVerified']:
                # self.init_battleground()
                self.context.game.set_screen('game')
            else:
                handle_exception('EMAIL_NOT_VERIFIED')

        self.get_widget('email_form').is_editable = False
        self.get_widget('password_form').is_editable = False
        self.get_widget('loader').enabled = True
        try:
            self.context.user = self.context.auth.sign_in_with_email_and_password(email, password)
        except HTTPError as e:
            handle_exception(e.strerror)
        else:
            check_verification()

    def init_battleground(self):
        def get_default_color():
            from random import choice
            return {'color': choice(Colors.GAME_COLORS)}

        pixels = {}
        for i in range(0, Constants.BATTLEGROUND_WIDTH * Constants.BATTLEGROUND_HEIGHT):
            pixels[str(i)] = get_default_color()
        self.context.firebase.database().child('pixels').remove(self.get_token())
        self.context.firebase.database().child('pixels').set(pixels, self.get_token())

    def init_widgets(self):
        style_regular = TextLabelStyle(Assets.font_regular, Colors.BLACK, None, Align.center)
        style_logo = TextLabelStyle(Assets.font_logo, Colors.BLACK, None, Align.center)
        style_status = TextLabelStyle(Assets.font_small, Colors.GREY, None, Align.center)
        style_edit_text = TextFormStyle(Assets.font_regular, Colors.BLACK, Colors.GREY, Colors.WHITE, Align.center)
        size = Assets.font_logo.size(LoginScreen.APP_NAME)
        self.add_widget('app_label', TextLabel(LoginScreen.APP_NAME,
                                               Constants.SCREEN_WIDTH / 2 - size[0] / 2,
                                               .25 * Constants.SCREEN_HEIGHT - size[1] / 2,
                                               style_logo))
        size = Assets.font_regular.size('sign in / register')
        self.add_widget('login', TextLabel('sign in / register',
                                           Constants.SCREEN_WIDTH / 2 - size[0] / 2,
                                           .45 * Constants.SCREEN_HEIGHT - size[1] / 2,
                                           style_regular))
        size = Assets.font_regular.size(LoginScreen.EMAIL_HINT)
        self.add_widget('email_form', TextForm(LoginScreen.EMAIL_HINT,

                                               Constants.SCREEN_WIDTH / 2 - size[0] / 2, .55 * Constants.SCREEN_HEIGHT,
                                               style_edit_text))
        size = Assets.font_regular.size(LoginScreen.PASSWORD_HINT)
        self.add_widget('password_form', TextForm(LoginScreen.PASSWORD_HINT,
                                                  Constants.SCREEN_WIDTH / 2 - size[0] / 2,
                                                  .65 * Constants.SCREEN_HEIGHT,
                                                  style_edit_text, True))
        self.add_widget('loader', SpriteImage(
            Constants.SCREEN_WIDTH / 2 - Constants.FRAME_WIDTH / 2, .78 * Constants.SCREEN_HEIGHT))
        self.add_widget('login_feedback', TextLabel('',
                                                    Constants.SCREEN_WIDTH / 2, 9 * Constants.SCREEN_HEIGHT / 10,
                                                    style_status))
        self.get_widget('login_feedback').enabled = False

    def get_active_form(self):
        return self.get_widget(self.active_form)

    def switch_active_form(self):
        def other(label):
            return 'email_form' if label == 'password_form' else 'password_form'

        if self.active_form is not None:
            self.get_active_form().lose_focus()
            self.active_form = other(self.active_form)
            self.get_active_form().hit(self.get_active_form().x, self.get_active_form().y)

    def process_input_events(self, e):
        if self.active_form is not None:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    self.get_active_form().move_cursor(-1)
                elif e.key == pygame.K_RIGHT:
                    self.get_active_form().move_cursor(1)
                elif e.key == pygame.K_BACKSPACE:
                    self.get_active_form().delete_symbol()
                elif e.key == pygame.K_TAB:
                    self.switch_active_form()
                elif e.key == pygame.K_RETURN:
                    if self.get_widget('password_form').get_text() == '':
                        if self.active_form == 'email_form':
                            self.switch_active_form()
                    else:
                        self.get_widget('login_feedback').enabled = True
                        email, password = self.get_widget('email_form'), self.get_widget('password_form')
                        email.is_editable = False
                        email.is_editable = False
                        self.login_task = AsyncTask(self.login, email.get_text(), password.get_text())
                        self.login_task.execute()
                else:
                    self.get_widget('login_feedback').enabled = False
                    self.get_widget(self.active_form).append_text(e.unicode)
        if e.type == pygame.QUIT:
            self.exit()
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self.down_coords = pygame.mouse.get_pos()
        self.check_click(e)
        if self.is_clicked:
            x, y = pygame.mouse.get_pos()
            for name, w in self.widgets.items():
                is_hit, widget = w.hit(x, y)
                if is_hit:
                    if widget == 'edit':
                        self.active_form = name
                        # if self.active_form == 2:
                        #     self.widgets[''].lose_focus()
                    else:
                        self.unfocus_form()
                    return
            self.unfocus_form()

    def unfocus_form(self):
        self.active_form = None
