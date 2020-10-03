from pewpewbot import command_patterns
from enum import Enum
from aiogram import types, Bot
from pewpewbot.TgCommand import TgCommand
from pewpewbot.manager import Manager


class Modes(Enum):
    ENABLED = "on"
    DISABLED = "off"


def build_help():
    return ''.join((value.help_text for name, value in vars(command_patterns).items()
                    if isinstance(value, TgCommand) and value.enabled))


def trim_command_name(message: types.Message, command_name):
    return message.text[len(command_name)+2:]


def parse_new_mode(mode):
    if mode == Modes.ENABLED.value:
        return True
    elif mode == Modes.DISABLED.value:
        return False
    else:
        return None


def notify_all_channels(bot: Bot, manager: Manager, message: types.message):
    if manager.state.main_channel_id:
        bot.send_message(manager.state.main_channel_id, message)
    if manager.state.code_channel_id:
        bot.send_message(manager.state.code_channel_id, message)
