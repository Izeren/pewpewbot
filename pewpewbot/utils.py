import asyncio
import logging
import re

import patterns
from State import CODE_CHAT_KEY, MAIN_CHAT_KEY, DEBUG_CHAT_KEY
from pewpewbot import command_patterns
from enum import Enum
from aiogram import types, Bot
from pewpewbot.TgCommand import TgCommand
from pewpewbot.manager import Manager

CLEAN_TAGS_RE = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

class Modes(Enum):
    ENABLED = "on"
    DISABLED = "off"

def build_pretty_level_question(question: str):
    raw_question = re.sub(CLEAN_TAGS_RE, '', question)
    coord_part_ids = [c.span() for c in re.finditer(patterns.STANDARD_COORDS_PATTERN, raw_question)]
    start = 0
    result = ""
    for index in range(len(coord_part_ids) // 2):
        c_start = coord_part_ids[2 * index][0]
        c_end = coord_part_ids[2 * index + 1][1]
        result += raw_question[start:c_start] + '`' + raw_question[c_start:c_end] + '`'
        start = c_end
    if start < len(raw_question):
        result += raw_question[start:]
    return result

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
        await manager.bot.send_message(manager.state.other[DEBUG_CHAT_KEY], message, parse_mode='Markdown')
    if CODE_CHAT_KEY in manager.state.other:
        await manager.bot.send_message(manager.state.other[CODE_CHAT_KEY], message, parse_mode='Markdown')
    if MAIN_CHAT_KEY in manager.state.other:
        await manager.bot.send_message(manager.state.other[MAIN_CHAT_KEY], message, parse_mode='Markdown')


async def notify_code_chat(bot: Bot, manager: Manager, message: types.message):
    if CODE_CHAT_KEY in manager.state.other:
        await bot.send_message(manager.state.other[CODE_CHAT_KEY], message, parse_mode='Markdown')


def get_text_mode_status(mode):
    return "включен" if mode else "выключен"


def get_all_active_commands():
    return list([command for name, command in vars(command_patterns).items()
                 if isinstance(command, TgCommand) and command.enabled])

# Util for performing periodic tasks. Accepts delay as constant
async def repeat_const_delay(delay: int, coro, *args, **kwargs):
    while True:
        await coro(*args, **kwargs)
        await asyncio.sleep(delay)

# Util for performing periodic tasks. Accepts a manager and key in manager.state.other so that delay can be changed in runtime
async def repeat_runtime_delay(manager: Manager, key: str, coro, *args, **kwargs):
    while True:
        try:
            await coro(*args, **kwargs)
        except Exception as exc:
            logging.error("Exception in task", exc_info=exc)
        try:
            await asyncio.sleep(int(manager.state.other[key]))
        except ValueError:
            logging.error(f"Key {key} is not found in manager.state.other or is not int. Using 30.")
            await asyncio.sleep(30)
        