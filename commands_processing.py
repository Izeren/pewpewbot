import re

from aiogram import types

from client import ClientError
from manager import Manager
import utils
from models import CodeVerdict


def dummy(message : types.Message, bot : Manager, **kwargs):
    return message.reply("Вы пытаетесь использовать команду {}, но у нее еще нет реализации"
                         .format(kwargs['command_name']))

def send_ko(message : types.Message, bot : Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    return message.reply("Вы пытаетесь ввести код:" + text)


def process_link(message: types.Message, bot: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    if text:
        bot.state.set_link(text)
        return message.reply("Установлена ссылка {}".format(text))
    else:
        link = bot.state.get_link()
        if link:
            return message.reply("Ссылка: {}".format(link))
        else:
            return message.reply("Настройки ссылки не найдено")

def process_tip(message : types.Message, bot : Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    if text.startswith('clean'):
        bot.state.reset_tip()
        return message.reply("Запиненная подсказка сброшена")
    if text:
        bot.state.set_tip(text)
        return message.reply("Подсказка запинена на текущий уровень")
    else:
        tip_text = bot.state.get_tip()
        if tip_text:
            return message.reply("Запиненная подсказка: {}".format(tip_text))
        else:
            return message.reply("Нет запиненной подсказки")

def process_pattern(message: types.Message, bot: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    # 'standar' is for stability to parse both standart and standard
    if 'standar' in text:
        bot.state.reset_pattern()
        return message.reply("Установлен стандартный шаблон кода")
    elif text:
        try:
            re.compile(text)
        except re.error:
            return message.reply("'{}' не является регулярным выражением. Шаблон кода не установлен".format(text))
        bot.state.set_pattern(text)
        return message.reply("Шаблон кода установлен: {}".format(text))
    else:
        if bot.state.code_pattern:
            return message.reply("Шаблон кода: {}".format(bot.state.code_pattern))
        else:
            return message.reply("Шаблон кода: стандартный")

def process_parse(message: types.Message, bot: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    mode = utils.parse_new_mode(text)
    if mode is None:
        return message.reply("Неверный режим использования, используйте 'on' или 'off'")
    else:
        bot.state.set_parse(mode)
        return message.reply("Парсинг {}".format("включен" if mode else "выключен"))

def process_maps(message: types.Message, bot: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    mode = utils.parse_new_mode(text)
    if mode is None:
        return message.reply("Неверный режим использования, используйте 'on' или 'off'")
    else:
        bot.state.set_maps(mode)
        return message.reply("Парсинг координат из чата {}".format("включен" if mode else "выключен"))

def process_type(message: types.Message, bot: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    mode = utils.parse_new_mode(text)
    if mode is None:
        return message.reply("Неверный режим использования, используйте 'on' или 'off'")
    else:
        bot.state.set_type(mode)
        return message.reply("Автоматический парсинг кодов {}".format("включен" if mode else "выключен"))

async def process_code(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    # TODO: make all awaits in the end
    await message.reply("Пытаюсь пробить код: {}".format(text))
    try:
        code_verdict = await manager.http_client.post_code()
        if code_verdict.SUCCESS:
            await message.reply("Код принят")
        else:
            await message.reply("Неверный или повторно введенный код")
    except ClientError:
        await message.reply("Ошибка соединения с сервером")
    finally:
        await message.reply("Ошибка, бот не смог")
