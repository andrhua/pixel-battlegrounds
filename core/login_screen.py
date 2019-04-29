from requests import HTTPError

import util.constants
from resources import i18n

from core.screen import Screen
from resources.assets import Assets
from resources.colors import Colors
from ui.styles import TextLabelStyle, Align, TextFormStyle
from ui.textlabel import TextLabel
from ui.widget import SpriteImage
from util.constants import Constants
from util.decorators import threaded


class LoginScreen(Screen):
    def __init__(self, context):
        super().__init__(context)
        self.login_anonymously()
        # self.active_form = None
        # self.forms = [self.get_widget('email_form'), self.get_widget('password_form')]
        # email, password = self.load(util.constants.LOCAL_SAVE_EMAIL), self.load(util.constants.LOCAL_SAVE_PASSWORD)
        # if email is not None:
        #     self.login(email, password)

    @threaded('login_anon')
    def login_anonymously(self):
        self.get_widget('loader').enabled = True
        self.context.user = self.context.auth.sign_in_anonymous()
        self.context.game.set_game_screen()

    @threaded('login_with_email_and_password')
    def login(self, email, password):
        def check_verification():
            token = self.context.get_local_user_token()
            info = self.context.auth.get_account_info(token)
            if info['users'][0]['emailVerified']:
                self.context.game.set_game_screen()
                self.save_credentials(email, password)
            else:
                self.context.auth.send_email_verification(token)
                self.update_login_feedback(i18n.VERIFICATION_SENT)

        self.get_widget('email_form').is_editable = False
        self.get_widget('password_form').is_editable = False
        self.get_widget('loader').enabled = True
        try:
            self.context.user = self.context.auth.sign_in_with_email_and_password(email, password)
            check_verification()
        except HTTPError as e:
            e = e.strerror
            if 'EMAIL_NOT_FOUND' in e:
                self.register(email, password)
            if 'INVALID_PASSWORD' in e:
                self.update_login_feedback(i18n.WRONG_PASSWORD)
            if 'INVALID_EMAIL' in e:
                self.update_login_feedback(i18n.WRONG_EMAIL)

    def register(self, email, password):
        try:
            self.context.user = self.context.auth.create_user_with_email_and_password(email, password)
        except HTTPError:
            self.update_login_feedback(i18n.WEAK_PASSWORD)
        else:
            self.context.auth.send_email_verification(self.context.get_local_user_token())
            self.update_login_feedback(i18n.VERIFICATION_SENT)
            self.save_credentials(email, password)

    def save_credentials(self, email, password):
        self.save(util.constants.LOCAL_SAVE_EMAIL, email)
        self.save(util.constants.LOCAL_SAVE_PASSWORD, password)

    def update_login_feedback(self, text):
        self.get_widget('login_feedback').set_text(text)
        self.get_widget('email_form').is_editable = True
        self.get_widget('password_form').is_editable = True
        self.get_widget('loader').enabled = False
        self.get_widget('login_feedback').enabled = True

    def init_ui(self):
        style_regular = TextLabelStyle(Assets.font_regular, Colors.BLACK, None, Align.center)
        style_logo = TextLabelStyle(Assets.font_logo, Colors.BLACK, None, Align.center)
        style_status = TextLabelStyle(Assets.font_small, Colors.GREY, None, Align.center)
        style_edit_text = TextFormStyle(Assets.font_regular, Colors.BLACK, Colors.GREY, Colors.WHITE, Align.center)
        self.add_widget('app_label', TextLabel(i18n.APP_NAME,
                                               Constants.SCREEN_WIDTH / 2, .5 * Constants.SCREEN_HEIGHT,
                                               style_logo))
        # self.add_widget('login', TextLabel('sign in / register',
        #                                    Constants.SCREEN_WIDTH / 2, .45 * Constants.SCREEN_HEIGHT,
        #                                    style_regular))
        # self.add_widget('email_form', TextForm(i18n.EMAIL_HINT,
        #                                        Constants.SCREEN_WIDTH / 2, .55 * Constants.SCREEN_HEIGHT,
        #                                        style_edit_text))
        # self.add_widget('password_form', TextForm(i18n.PASSWORD_HINT,
        #                                           Constants.SCREEN_WIDTH / 2, .65 * Constants.SCREEN_HEIGHT,
        #                                           style_edit_text, True))
        self.add_widget('loader', SpriteImage(
            Constants.SCREEN_WIDTH / 2 - Constants.FRAME_WIDTH / 2, .78 * Constants.SCREEN_HEIGHT))
        # self.add_widget('login_feedback', TextLabel('',
        #                                             Constants.SCREEN_WIDTH / 2, 9 * Constants.SCREEN_HEIGHT / 10,
        #                                             style_status))
        # self.get_widget('login_feedback').enabled = False

    def get_active_form(self):
        return self.get_widget(self.active_form)

    def switch_active_form(self):
        def other(label):
            return 'email_form' if label == 'password_form' else 'password_form'

        if self.active_form is not None:
            self.get_active_form().lose_focus()
            self.active_form = other(self.active_form)
            self.get_active_form().hit(self.get_active_form().x, self.get_active_form().y)

    def on_key_down(self, key, unicode):
        pass
        # if self.active_form is not None:
        #     form = self.get_active_form()
        #     if key == pygame.K_LEFT:
        #         form.move_cursor(-1)
        #     elif key == pygame.K_RIGHT:
        #         form.move_cursor(1)
        #     elif key == pygame.K_BACKSPACE:
        #         form.delete_symbol()
        #     elif key == pygame.K_TAB:
        #         self.switch_active_form()
        #     elif key == pygame.K_RETURN:
        #         if self.get_widget('password_form').get_text() == '':
        #             if self.active_form == 'email_form':
        #                 self.switch_active_form()
        #         else:
        #             self.get_widget('login_feedback').enabled = True
        #             email, password = self.get_widget('email_form'), self.get_widget('password_form')
        #             email.is_editable = False
        #             email.is_editable = False
        #             self.login(email.get_text(), password.get_text())
        #     else:
        #         form.append_text(unicode)

    def on_mouse_click(self):
        pass
        # x, y = pygame.mouse.get_pos()
        # for name, w in self.widgets.items():
        #     is_hit, widget = w.hit(x, y)
        #     if is_hit:
        #         self.active_form = name if widget == 'edit' else None
        #         return
