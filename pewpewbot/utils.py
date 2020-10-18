from State import CODE_CHAT_KEY, MAIN_CHAT_KEY, DEBUG_CHAT_KEY
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


async def notify_all_channels(manager: Manager, message: types.message):
    if DEBUG_CHAT_KEY in manager.state.other:
        await manager.bot.send_message(manager.state.other[DEBUG_CHAT_KEY], message)
    if CODE_CHAT_KEY in manager.state.other:
        await manager.bot.send_message(manager.state.other[CODE_CHAT_KEY], message)
    if MAIN_CHAT_KEY in manager.state.other:
        await manager.bot.send_message(manager.state.other[MAIN_CHAT_KEY], message)


async def notify_code_chat(bot: Bot, manager: Manager, message: types.message):
    if CODE_CHAT_KEY in manager.state.other:
        await bot.send_message(manager.state.other[CODE_CHAT_KEY], message, parse_mode='Markdown')


def get_text_mode_status(mode):
    return "включен" if mode else "выключен"


def get_all_active_commands():
    return list([command for name, command in vars(command_patterns).items()
                 if isinstance(command, TgCommand) and command.enabled])
