from models import Status, Koline
from pewpewbot import patterns

CODE_CHAT_KEY = 'code_chat_id'
MAIN_CHAT_KEY = 'main_chat_id'
DEBUG_CHAT_KEY = 'debug_chat_id'


class State(object):
    def __init__(
            self,
            parse_on=False,
            type_on=False,
            maps_on=True,
            tip='',
            link='',
            other={},
            code_pattern=patterns.STANDARD_CODE_PATTERN,
            game_status: Status = None,
            koline: Koline = None
    ):
        self.code_pattern = code_pattern
        self.parse_on = parse_on
        self.type_on = type_on
        self.maps_on = maps_on
        self.other = other
        self.tip = tip
        self.link = link
        self.game_status = game_status
        self.koline = koline

    def set_parse(self, mode):
        self.parse_on = mode

    def set_type(self, mode):
        self.type_on = mode

    def set_maps(self, mode):
        self.maps_on = mode

    def get_other(self, name):
        if name in self.other:
            return self.other[name]
        else:
            return "Значение не задано"

    def get_tip(self):
        return self.tip

    def set_tip(self, tip):
        self.tip = tip

    def reset_tip(self):
        self.tip = ''

    def get_link(self):
        return self.link

    def set_link(self, link):
        self.link = link

    def reset_link(self):
        self.link = ''

    def set_other(self, name, value):
        self.other[name] = value

    def set_pattern(self, pattern):
        self.code_pattern = pattern

    def reset_pattern(self):
        self.code_pattern = patterns.STANDARD_CODE_PATTERN

    def get_pattern(self):
        return self.code_pattern
