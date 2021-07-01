import asyncio
import logging
import re

import patterns
from pewpewbot import command_patterns
from enum import Enum
from aiogram import types, Bot
from pewpewbot.TgCommand import TgCommand
from pewpewbot.manager import Manager

CLEAN_TAGS_RE = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')

DZZZR_UPLOADED_FILES_LINK = 'http://classic.dzzzr.ru/'


class Modes(Enum):
    ENABLED = "on"
    DISABLED = "off"


def clean_html_tags(message):
    return re.sub(CLEAN_TAGS_RE, '', message)


def pretty_format_message_with_coords(message):
    coord_part_ids = [c.span() for c in re.finditer(patterns.STANDARD_COORDS_PATTERN, message)]
    start = 0
    result = ""
    for index in range(len(coord_part_ids) // 2):
        c_start = coord_part_ids[2 * index][0]
        c_end = coord_part_ids[2 * index + 1][1]
        result += message[start:c_start] + '`' + message[c_start:c_end] + '`'
        start = c_end
    if start < len(message):
        result += message[start:]
    return result


def format_level_message(question: str):
    return pretty_format_message_with_coords(clean_html_tags(question))


def trim_command_name(message: types.Message, command_name):
    return message.text[len(command_name) + 2:]


def parse_new_mode(mode):
    if mode == Modes.ENABLED.value:
        return True
    elif mode == Modes.DISABLED.value:
        return False
    else:
        return None


async def notify_all_channels(manager: Manager, message: types.message):
    if manager.state.debug_chat_id:
        await manager.bot.send_message(manager.state.debug_chat_id, message, parse_mode='Markdown')
    if manager.state.code_chat_id:
        await manager.bot.send_message(manager.state.code_chat_id, message, parse_mode='Markdown')
    if manager.state.main_chat_id:
        await manager.bot.send_message(manager.state.main_chat_id, message, parse_mode='Markdown')


async def image_to_all_channels(manager: Manager, message: types.message, link: str):
    if manager.state.debug_chat_id:
        await manager.bot.send_photo(manager.state.debug_chat_id, link, message, parse_mode='Markdown')
    if manager.state.code_chat_id:
        await manager.bot.send_photo(manager.state.code_chat_id, link, message, parse_mode='Markdown')
    if manager.state.main_chat_id:
        await manager.bot.send_photo(manager.state.main_chat_id, link, message, parse_mode='Markdown')


async def notify_code_chat(manager: Manager, message: types.message):
    if manager.state.code_chat_id is not None:
        await manager.bot.send_message(manager.state.code_chat_id, message, parse_mode='Markdown')


async def notify_debug_chat(manager: Manager, message: types.message):
    if manager.state.debug_chat_id is not None:
        await manager.bot.send_message(manager.state.debug_chat_id, message, parse_mode='Markdown')


def get_text_mode_status(mode):
    return "включен" if mode else "выключен"


# Util for performing periodic tasks. Accepts delay as constant
async def repeat_const_delay(delay: int, coro, *args, **kwargs):
    while True:
        try:
            await coro(*args, **kwargs)
        except Exception as exc:
            logging.error("Exception in task", exc_info=exc)
        await asyncio.sleep(delay)


# Util for performing periodic tasks. Accepts a manager and key in manager.state so that delay can be changed in runtime
async def repeat_runtime_delay(manager: Manager, key: str, coro, *args, **kwargs):
    while True:
        try:
            await coro(*args, **kwargs)
        except Exception as exc:
            logging.error("Exception in task", exc_info=exc)
        try:
            delay = getattr(manager.state, key)
            if not isinstance(delay, int):
                logging.error(f"manager.state.{key} is not int. Using 30.")
                delay = 30
            await asyncio.sleep(delay)
        except AttributeError:
            logging.error(f"Key {key} is not found in manager.state. Using 30.")
            await asyncio.sleep(30)


def get_schema_urls(level_message):
    links = re.findall(patterns.SCHEMA_LINK_PATTERN, level_message.lower())
    return tuple(DZZZR_UPLOADED_FILES_LINK + link for link in links)
