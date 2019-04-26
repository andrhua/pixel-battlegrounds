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
from util.settings import Settings


class LoginScreen(Screen):
    EMAIL = 'email'
    PASS = 'pass'
    VERIFICATION_SENT = "Verify your email via letter we've just sent and sign in."
    WRONG_PASS = "Incorrect password."
    WEAK_PASS = "Password must contain a minimum of 6 characters."
    WRONG_EMAIL = "Incorrect email."
    NOT_VERIFIED_EMAIL = "Please first verify your email. Check spam box if necessary."

    def __init__(self, context):
        super().__init__(context)
        self.edit_text_flag = False
        self.selected_edit_text = -1
        self.login_task = None
        email = self.load(self.EMAIL)
        if email is not None:
            self.context.last_exit = self.load(self.LAST_EXIT)
            self.login_task = AsyncTask(self.login, email, self.load(self.PASS))
            self.login_task.execute()

    def login(self, email, password):
        def handle_exception(e):
            print(e)
            if 'EMAIL_NOT_FOUND' in e:
                try:
                    self.context.user = self.context.auth.create_user_with_email_and_password(email, password)
                except HTTPError:
                    self.widgets[5].set_text(self.WEAK_PASS)
                else:
                    self.context.auth.send_email_verification(self.get_token())
                    self.widgets[5].set_text(self.VERIFICATION_SENT)
                    self.save(self.EMAIL, email)
                    self.save(self.PASS, password)
            if 'INVALID_PASSWORD' in e:
                self.widgets[5].set_text(self.WRONG_PASS)
            if 'INVALID_EMAIL' in e:
                self.widgets[5].set_text(self.WRONG_EMAIL)
            if 'EMAIL_NOT_VERIFIED' in e:
                self.context.auth.send_email_verification(self.get_token())
                self.widgets[5].set_text(self.NOT_VERIFIED_EMAIL)
            self.widgets[2].is_editable = True
            self.widgets[3].is_editable = True
            self.widgets[3].set_empty()
            self.widgets[4].enabled = False
            self.widgets[5].enabled = True

        def check_verification():
            info = self.context.auth.get_account_info(self.get_token())
            if info['users'][0]['emailVerified']:
                #self.initttt()
                self.context.game.set_screen('game')
            else:
                handle_exception('EMAIL_NOT_VERIFIED')

        self.widgets[2].is_editable = False
        self.widgets[3].is_editable = False
        self.widgets[4].enabled = True
        try:
            self.context.user = self.context.auth.sign_in_with_email_and_password(email, password)
        except HTTPError as e:
            handle_exception(e.strerror)
        else:
            check_verification()

    def initttt(self):
        def zzza():
            return {'color': [255, 255, 255]}
        strs = {}
        for i in range(0, 800000):
            print(i)
            strs[str(i)] = zzza()
        self.context.firebase.database().child('pixels').set(strs, self.get_token())

    def init_widgets(self):
        style_regular = TextLabelStyle(Assets.font_regular, Colors.black, None, Align.center)
        style_logo = TextLabelStyle(Assets.font_logo, Colors.black, None, Align.center)
        style_status = TextLabelStyle(Assets.font_small, Colors.grey, None, Align.center)
        style_edit_text = TextFormStyle(Assets.font_regular, Colors.black, Colors.grey, Colors.white, Align.center)
        size = Assets.font_regular.size("Mail.ru's")
        self.widgets.append(TextLabel("Mail.ru's", (
            Settings.screen_width / 2 - size[0] / 2, .30 * Settings.screen_height - size[1] / 2), style_regular))
        size = Assets.font_logo.size("Battlegrounds")
        self.widgets.append(TextLabel("Battlegrounds",
                                     (Settings.screen_width / 2 - size[0] / 2, .40 * Settings.screen_height - size[1] / 2),
                                     style_logo))
        size = Assets.font_regular.size("email")
        self.widgets.append(TextForm("email", (Settings.screen_width / 2 - size[0] / 2, .5 * Settings.screen_height),
                                     style_edit_text))
        size = Assets.font_regular.size("password")
        self.widgets.append(TextForm("password", (Settings.screen_width / 2 - size[0] / 2, .6 * Settings.screen_height),
                                     style_edit_text, True))
        self.widgets.append(SpriteImage((Settings.screen_width / 2 - Constants.frame_width / 2, .73 * Settings.screen_height)))
        self.widgets.append(TextLabel('',
                            (Settings.screen_width/2, 9*Settings.screen_height/10),
                            style_status))
        self.widgets[-1].enabled = False

    def switch_edit_texts(self):
        if self.selected_edit_text != -1:
            i = 2 if self.selected_edit_text == 3 else 3
            j = 3 if self.selected_edit_text == 3 else 2
            self.selected_edit_text = i
            self.widgets[j].lose_focus()
            self.widgets[i].hit(self.widgets[i].x, self.widgets[i].y)

    def process_events(self, e):
        if self.edit_text_flag:
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_LEFT:
                    self.widgets[self.selected_edit_text].move_cursor(-1)
                elif e.key == pygame.K_RIGHT:
                    self.widgets[self.selected_edit_text].move_cursor(1)
                elif e.key == pygame.K_BACKSPACE:
                    self.widgets[self.selected_edit_text].delete_symbol()
                elif e.key == pygame.K_TAB:
                    self.switch_edit_texts()
                elif e.key == pygame.K_RETURN:
                    if self.widgets[3].get_text() == '':
                        self.switch_edit_texts()
                    else:
                        self.widgets[4].enabled = True
                        self.widgets[2].is_editable = False
                        self.widgets[3].is_editable = False
                        self.login_task = AsyncTask(self.login, self.widgets[2].get_text(), self.widgets[3].get_text())
                        self.login_task.execute()
                else:
                    self.widgets[5].enabled = False
                    self.widgets[self.selected_edit_text].append_text(e.unicode)
        if e.type == pygame.QUIT:
            self.exit()
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            self.down_coords = pygame.mouse.get_pos()
        self.check_click(e)
        if self.is_clicked:
            pos = pygame.mouse.get_pos()
            i = 0
            for w in self.widgets:
                res = w.hit(pos[0], pos[1])
                if res[0]:
                    if res[1] == 'edit':
                        self.edit_text_flag = True
                        self.selected_edit_text = i
                        if self.selected_edit_text == 2:
                            self.widgets[3].lose_focus()
                    else:
                        self.unfocus_edit_text()
                    return
                i += 1
            self.unfocus_edit_text()

    def unfocus_edit_text(self):
        self.edit_text_flag = False
        self.selected_edit_text = -1
