import re

from aiogram import types

from .DozorBot import DozorBot
from . import utils


async def dummy(message: types.Message, bot: DozorBot, **kwargs):
    await message.reply("Вы пытаетесь использовать команду {}, но у нее еще нет реализации"
                         .format(kwargs['command_name']))


async def help(message: types.Message, bot: DozorBot, **kwargs):
    await message.reply(utils.build_help())


async def send_ko(message : types.Message, bot: DozorBot, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    await message.reply("Вы пытаетесь ввести код:" + text)


async def process_link(message: types.Message, bot: DozorBot, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    if text:
        bot.state.set_link(text)
        await message.reply("Установлена ссылка {}".format(text))
    else:
        link = bot.state.get_link()
        if link:
            await message.reply("Ссылка: {}".format(link))
        else:
            await message.reply("Настройки ссылки не найдено")


async def process_tip(message: types.Message, bot: DozorBot, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    if text.startswith('clean'):
        bot.state.reset_tip()
        await message.reply("Запиненная подсказка сброшена")
    if text:
        bot.state.set_tip(text)
        await message.reply("Подсказка запинена на текущий уровень")
    else:
        tip_text = bot.state.get_tip()
        if tip_text:
            await message.reply("Запиненная подсказка: {}".format(tip_text))
        else:
            await message.reply("Нет запиненной подсказки")


async def process_pattern(message: types.Message, bot: DozorBot, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    # 'standar' is for stability to parse both standart and standard
    if 'standar' in text:
        bot.state.reset_pattern()
        await message.reply("Установлен стандартный шаблон кода")
    elif text:
        try:
            re.compile(text)
        except re.error:
            await message.reply("'{}' не является регулярным выражением. Шаблон кода не установлен".format(text))
        bot.state.set_pattern(text)
        await message.reply("Шаблон кода установлен: {}".format(text))
    else:
        if bot.state.code_pattern:
            await message.reply("Шаблон кода: {}".format(bot.state.code_pattern))
        else:
            await message.reply("Шаблон кода: стандартный")


async def process_parse(message: types.Message, bot: DozorBot, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    mode = utils.parse_new_mode(text)
    if mode is None:
        await message.reply("Неверный режим использования, используйте 'on' или 'off'")
    else:
        bot.state.set_parse(mode)
        await message.reply("Парсинг {}".format("включен" if mode else "выключен"))


async def process_maps(message: types.Message, bot: DozorBot, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    mode = utils.parse_new_mode(text)
    if mode is None:
        await message.reply("Неверный режим использования, используйте 'on' или 'off'")
    else:
        bot.state.set_maps(mode)
        await message.reply("Парсинг координат из чата {}".format("включен" if mode else "выключен"))


async def process_type(message: types.Message, bot: DozorBot, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    mode = utils.parse_new_mode(text)
    if mode is None:
        await message.reply("Неверный режим использования, используйте 'on' или 'off'")
    else:
        bot.state.set_type(mode)
        await message.reply("Автоматический парсинг кодов {}".format("включен" if mode else "выключен"))
