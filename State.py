import patterns
from utils import Modes


class State(object):
    def __init__(
            self,
            parse_on=False,
            type_on=False,
            maps_on=True,
            tip='',
            link='',
            other={},
            code_pattern = patterns.STANDARD_CODE_PATTERN
    ):
        self.code_pattern = code_pattern
        self.parse_on = parse_on
        self.type_on = type_on
        self.maps_on = maps_on
        self.other = other
        self.tip = tip
        self.link = link

    def set_parse(self, value):
        if value == Modes.ENABLED:
            self.parse_on = True
        elif value == Modes.DISABLED:
            self.parse_on = False

    def set_type(self, value):
        if value == Modes.ENABLED:
            self.type_on = True
        elif value == Modes.DISABLED:
            self.type_on = False

    def set_maps(self, value):
        if value == Modes.ENABLED:
            self.maps_on = True
        elif value == Modes.DISABLED:
            self.maps_on = False

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
