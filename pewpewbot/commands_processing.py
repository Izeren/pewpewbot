import datetime
import logging
import re
from aiogram import types, Bot

import code_utils
import views
from models import Status, Koline, CodeVerdict
from pewpewbot import utils
from pewpewbot.errors import ClientError
from pewpewbot.manager import Manager

logger = logging.getLogger(__name__)


async def dummy(message: types.Message, manager: Manager, **kwargs):
    await message.reply("Вы пытаетесь использовать команду {}, но у нее еще нет реализации"
                        .format(kwargs['command_name']))


async def help(message: types.Message, manager: Manager, **kwargs):
    await message.reply(utils.build_help())


async def send_ko(message: types.Message, manager: Manager, **kwargs):
    if not manager.state.koline:
        status = await manager.http_client.status()
        koline = Koline.from_string(status.current_level.koline)
    else:
        koline = manager.state.koline
    for sector in koline.sectors:
        if not manager.state.tip:
            await utils.notify_code_chat(manager.bot, manager, views.sector_default_ko_message(sector))
        else:
            await utils.notify_code_chat(manager.bot, manager, views.not_taken_with_tips(sector, manager.state.tip))


async def process_link(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    if text:
        manager.state.set_link(text)
        await message.reply("Установлена ссылка {}".format(text))
    else:
        link = manager.state.get_link()
        if link:
            await message.reply("Ссылка: {}".format(link))
        else:
            await message.reply("Настройки ссылки не найдено")


async def process_tip(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    if text.startswith('clean'):
        manager.state.reset_tip()
        await message.reply("Запиненная подсказка сброшена")
    if text:
        manager.state.set_tip(text)
        await message.reply("Подсказка запинена на текущий уровень")
    else:
        tip_text = manager.state.get_tip()
        if tip_text:
            await message.reply("Запиненная подсказка: {}".format(tip_text))
        else:
            await message.reply("Нет запиненной подсказки")


async def process_pattern(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    # 'standar' is for stability to parse managerh standart and standard
    if 'standar' in text:
        manager.state.reset_pattern()
        await message.reply("Установлен стандартный шаблон кода")
    elif text:
        try:
            re.compile(text)
        except re.error:
            await message.reply("'{}' не является регулярным выражением. Шаблон кода не установлен".format(text))
        manager.state.set_pattern(text)
        await message.reply("Шаблон кода установлен: {}".format(text))
    else:
        if manager.state.code_pattern:
            await message.reply("Шаблон кода: {}".format(manager.state.code_pattern))
        else:
            await message.reply("Шаблон кода: стандартный")


async def process_parse(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    mode = utils.parse_new_mode(text)
    if mode is None:
        await message.reply("Неверный режим использования, используйте 'on' или 'off'")
    else:
        manager.state.set_parse(mode)
        await message.reply("Парсинг {}".format("включен" if mode else "выключен"))


async def process_maps(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    mode = utils.parse_new_mode(text)
    if mode is None:
        await message.reply("Неверный режим использования, используйте 'on' или 'off'")
    else:
        manager.state.set_maps(mode)
        await message.reply("Парсинг координат из чата {}".format("включен" if mode else "выключен"))


async def process_type(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    mode = utils.parse_new_mode(text)
    if mode is None:
        await message.reply("Неверный режим использования, используйте 'on' или 'off'")
    else:
        manager.state.set_type(mode)
        await message.reply("Автоматический парсинг кодов {}".format(utils.get_text_mode_status(mode)))


async def get_bot_status(message: types.Message, manager: Manager, **kwargs):
    text = '''Режим работы бота:
--- Парсинг движка {}
--- Автоматический ввод кодов {}
--- Парсинг координат с локацией {}
'''
    formatted = text.format(
        utils.get_text_mode_status(manager.state.parse_on),
        utils.get_text_mode_status(manager.state.type_on),
        utils.get_text_mode_status(manager.state.maps_on)
    )
    await message.reply(formatted)


async def login(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    login, passwd = text.split(maxsplit=1)
    login = login.strip()
    passwd = passwd.strip()
    try:
        await manager.http_client.log_in(login, passwd)
    except ClientError:
        await message.reply("Ошибка соединения с сервером")
    except Exception as e:
        await message.reply("Ошибка, бот не смог")


async def process_code(message: types.Message, manager: Manager, **kwargs):
    text = message.text
    if text.startswith('.') or text.startswith('/'):
        text = text[1:]
    text = text.lower().strip()
    # TODO: make all awaits in the end
    await message.reply("Пытаюсь пробить код: {}".format(text))
    try:
        code_result = await manager.http_client.post_code(text)
        if isinstance(code_result.verdict, int):
            return await message.reply(code_result.comment)
        else:
            if code_result.verdict.value not in code_utils.GOOD_VERDICTS:
                return await message.reply(code_utils.CODE_VERDICT_TO_MESSAGE[code_result.verdict.value])
            else:
                if code_result.verdict.value == CodeVerdict.ACCEPTED_NEXT_LEVEL.value:
                    return await utils.notify_all_channels(manager, "Взят последний код на уровне")
                return await _update_current_level_info_on_code(
                    code_utils.CODE_VERDICT_TO_MESSAGE[code_result.verdict.value], message, manager)
    except ClientError:
        await message.reply("Ошибка соединения с сервером")
    except Exception:
        await message.reply("Ошибка, бот не смог")


async def update_level(message: types.Message, manager: Manager, **kwargs):
    try:
        status = await manager.http_client.status()
        await message.reply(status)
        await _process_next_level(status, manager)
    except ClientError:
        await message.reply("Ошибка соединения с сервером")
    except Exception:
        await message.reply("Ошибка, бот не смог")


async def _process_next_level(status, manager: Manager):
    await utils.notify_all_channels(manager, "Выдан новый уровень")
    manager.logger.info("New game status from site {} ".format(status))
    _update_current_level_info(status, manager)
    manager.state.reset_pattern()
    manager.state.reset_tip()


def _update_current_level_info(game_status: Status, manager: Manager):
    manager.state.game_status = game_status
    try:
        manager.state.koline = Koline.from_string(game_status.current_level.koline)
    except Exception as e:
        logger.error("Bad koline to parse: {}".format(game_status.current_level.koline))


async def _update_current_level_info_on_code(verdict: str, message: types.Message, manager: Manager):
    new_status = await manager.http_client.status()
    koline = manager.state.koline
    new_koline = Koline.from_string(new_status.current_level.koline)

    if not koline:
        logger.error("Koline has not been initialized on level")
        manager.state.koline = new_koline
        manager.state.game_status = new_status
        return
    if len(koline.sectors) != len(new_koline.sectors):
        logger.error("Number of sectors has been changed, probably level has been upped")
        return
    for old_sector, new_sector in zip(koline.sectors, new_koline.sectors):
        if len(old_sector.codes) != len(new_sector.codes):
            logger.error("Number of codes for sector: {} is broken".format(new_sector.name))
            return
        for old_code, new_code in zip(old_sector.codes, new_sector.codes):
            if not old_code.taken and new_code.taken:
                await message.reply(
                    "{} таймер: {}, метка: {}, ко: {}".format(
                        verdict,
                        datetime.timedelta(seconds=new_status.current_level.tm),
                        new_code.label,
                        new_code.ko
                    )
                )
    manager.state.koline = new_koline
    manager.state.game_status = new_status


async def update_level_status(bot: Bot, manager: Manager, **kwargs):
    try:
        game_status = await manager.http_client.status()
        current_level_id = game_status.current_level.levelNumber
        if not manager.state.game_status:
            return await _process_next_level(game_status, manager)
        if manager.state.game_status.current_level.levelNumber != current_level_id:
            return await _process_next_level(game_status, manager)
        else:
            return _update_current_level_info(game_status, manager)
    except ClientError:
        if 'chat_id' in manager.state.other:
            await bot.send_message(manager.state.other['chat_id'], "Ошибка при обновлении статуса уровня")
    except Exception:
        if 'chat_id' in manager.state.other:
            await bot.send_message(manager.state.other['chat_id'], "Бот упал при обновлении статуса уровня")


async def process_unknown(message: types.Message, manager: Manager, **kwargs):
    text = message.text.lower()
    if re.fullmatch(manager.state.get_pattern(), text) or text.startswith('.'):
        await process_code(message, manager)


async def process_get_chat_id(message: types.Message, manager: Manager, **kwargs):
    await message.reply("chat id: {}".format(message.chat.id))


async def set_state_key_value(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    key, value = text.split()
    manager.state.other[key] = value
    await message.reply("Для переменной {} установлено значение: {}".format(key, value))
