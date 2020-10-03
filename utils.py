from enum import Enum

from aiogram import types

import command_patterns
from TgCommand import TgCommand

class Modes(Enum):
    ENABLED = "on"
    DISABLED = "off"

def build_help():
    return ''.join((value.help_text for name, value in vars(command_patterns).items() if isinstance(value, TgCommand) and value.enabled))

def trim_command_name(message : types.Message, command_name):
    return message.text[len(command_name)+2:]

def parse_new_mode(mode):
    if mode == Modes.ENABLED.value:
        return True
    elif mode == Modes.DISABLED.value:
        return False
    else:
        return None
