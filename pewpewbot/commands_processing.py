from ast import literal_eval
from dataclasses import asdict
import datetime
import logging
import os
import re
import decorator
import pathlib
import requests
from aiogram.types import InputFile
from marshmallow import EXCLUDE

from aiogram import types, Bot

from pewpewbot import model_parsing_utils
from pewpewbot.models import Status, CodeVerdict, StatusSchema, CodeResult
from pewpewbot import utils, code_utils, patterns, views
from pewpewbot.errors import AuthenticationError, ConnectionError, ValidationError
from pewpewbot.manager import Manager
from pewpewbot.views import try_send_code_view, code_update_view
from pewpewbot.utils import get_yandex_maps_formated_coords, pretty_format_message_with_coords

logger = logging.getLogger("bot")
logger.propagate = False


@decorator.decorator
async def safe_dzzzr_interaction(fn, bot: Bot, manager: Manager, **kwargs):
    try:
        return await fn(bot, manager, **kwargs)
    except AuthenticationError as e:
        logger.exception(e)
        if manager.state.debug_chat_id is not None:
            await bot.send_message(manager.state.debug_chat_id, "Ошибка аутентификации в движке дозора")
    except ConnectionError as e:
        logger.exception(e)
        if manager.state.debug_chat_id is not None:
            await bot.send_message(manager.state.debug_chat_id, "Ошибка подключения к движку дозора")
    except ValidationError as e:
        logger.exception(e)
        if manager.state.debug_chat_id is not None:
            await bot.send_message(manager.state.debug_chat_id, "Ошибка валидации ответа")
    except Exception as e:
        logger.exception(e)
        if manager.state.debug_chat_id is not None:
            await bot.send_message(manager.state.debug_chat_id, "Неожиданное исключение в боте")


async def dummy(message: types.Message, manager: Manager, **kwargs):
    await message.reply("Вы пытаетесь использовать команду {}, но у нее еще нет реализации"
                        .format(kwargs['command_name']))


@safe_dzzzr_interaction
async def img(message: types.Message, manager: Manager, **kwargs):
    screenshot_path = manager.screenshoter.file_name
    smart_path = pathlib.Path(screenshot_path)
    if not smart_path.is_file():
        await message.reply("URL не настроен или ещё не сделано ни одного скриншота")
        return
    mtime = smart_path.stat().st_mtime
    age_in_seconds = int(datetime.datetime.today().timestamp() - mtime)
    await message.reply_photo(InputFile(screenshot_path),
                              "Штабной док\n последнее обновление было {} секунд назад".format(age_in_seconds))


async def parse_coords_to_location(message: types.Message, manager: Manager, **kwargs):
    await message.reply("Вы пытаетесь использовать команду {}, но у нее еще нет реализации"
                        .format(kwargs['command_name']))


async def send_ko(message: types.Message, manager: Manager, **kwargs):
    ko_caption = kwargs['ko_caption'] if 'ko_caption' in kwargs else ''
    await manager.get_or_load_and_parse_koline()
    await message.reply(
        views.sector_list_ko_view(manager.state, ko_caption),
        parse_mode='Markdown')


async def process_link(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    if text:
        manager.state.link = text
        await message.reply("Установлена ссылка {}".format(text))
    else:
        link = manager.state.link
        if link:
            await message.reply("Ссылка: {}".format(link))
        else:
            await message.reply("Настройки ссылки не найдено")


@safe_dzzzr_interaction
async def process_tip(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    if text.startswith('clean'):
        manager.state.reset('tip')
        await message.reply("Запиненная подсказка сброшена")
    elif text:
        try:
            sector, tip = text.split(maxsplit=1)
            sector = sector.strip()
        except Exception as e:
            await message.reply("Неверный формат шаблона номера сектора '*' / 'all' / '' / 0-xx")
            raise Exception("Недостаточно данных для парсинга номера сектора и подсказки")
        if sector == '*' or sector == 'all' or sector == '':
            manager.state.set_tip_all_sectors(tip)
            await message.reply("Подсказка запинена на текущий уровень")
        else:
            try:
                sector_id = int(sector)
                if sector_id >= len(manager.state.koline.sectors):
                    await message.reply(f"Сектора под номером: {sector_id} не существует")
                    raise Exception("В качестве номера сектора может быть: '*' / 'all' / '' / int_sector_id")
                if not manager.state.tip:
                    manager.state.tip = [[]] * len(manager.state.koline.sectors)
                manager.state.set_tip_for_sector(tip, sector_id)
                await message.reply(f"Подсказка запинена для сектора: {sector_id}")
            except Exception as e:
                await message.reply("Возникла ошибка, не удалось запиить подсказку")
                raise e
    else:
        tip_text = manager.state.tip
        if tip_text:
            await message.reply("Запиненная подсказка: {}".format(tip_text))
        else:
            await message.reply("Нет запиненной подсказки")


async def process_pattern(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    # 'standar' is for stability to parse both standart and standard
    if 'standar' in text:
        manager.state.reset('code_pattern')
        await message.reply("Установлен стандартный шаблон кода")
    elif text:
        try:
            re.compile(text)
        except re.error:
            await message.reply("'{}' не является регулярным выражением. Шаблон кода не установлен".format(text))
        manager.state.code_pattern = text
        await message.reply("Шаблон кода установлен: {}".format(text))
    else:
        if manager.state.code_pattern:
            await message.reply("Шаблон кода: {}".format(manager.state.code_pattern))
        else:
            await message.reply("Шаблон кода: стандартный")


async def process_parse(message: types.Message, manager: Manager, **kwargs):
    await process_bool_setting(
        message=message,
        manager=manager,
        state_field='parse_on',
        desc="Парсинг",
        command_name=kwargs['command_name'])


async def process_maps(message: types.Message, manager: Manager, **kwargs):
    await process_bool_setting(
        message=message,
        manager=manager,
        state_field='maps_on',
        desc="Парсинг координат из чата",
        command_name=kwargs['command_name'])


async def process_type(message: types.Message, manager: Manager, **kwargs):
    await process_bool_setting(
        message=message,
        manager=manager,
        state_field='type_on',
        desc="Автоматический парсинг кодов",
        command_name=kwargs['command_name'])


async def process_bool_setting(message: types.Message, manager: Manager, state_field: str, desc: str,
                               command_name: str):
    """
    Updates bool settings from message in state.
    """
    text = utils.trim_command_name(message, command_name).strip()
    try:
        mode = utils.parse_bool(text)
        setattr(manager.state, state_field, mode)
        await message.reply(f"{desc} {utils.get_text_mode_status(mode)}")
    except ValueError:
        await message.reply("Неверный режим использования, используйте 'on' или 'off'")


async def get_bot_status(message: types.Message, manager: Manager, **kwargs):
    await message.reply(f'''Режим работы бота:
  \u2022 Парсинг движка {utils.get_text_mode_status(manager.state.parse_on)}
  \u2022 Автоматический ввод кодов {utils.get_text_mode_status(manager.state.type_on)}
  \u2022 Парсинг координат с локацией {utils.get_text_mode_status(manager.state.maps_on)}''')


async def task(message: types.Message, manager: Manager, **kwargs):
    if manager.state and manager.state.game_status and manager.state.game_status.current_level:
        await message.reply(utils.format_level_message(manager.state.game_status.current_level.question), 
            parse_mode='Markdown')


@safe_dzzzr_interaction
async def login(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    login, passwd = text.split(maxsplit=1)
    login = login.strip()
    passwd = passwd.strip()
    await manager.http_client.log_in(login, passwd)


def get_forced_code_text_from_message_or_reply(message: types.Message) -> str:
    text = utils.parse_message_text(message).lower().strip()
    if text.startswith('.') or text.startswith('/'):
        # Strip is here to remove space after /
        text = text[1:].strip()
        if 0 == len(text) and message.reply_to_message:
            parent = message.reply_to_message
            text = utils.parse_message_text(parent).lower().strip()
    return text


@safe_dzzzr_interaction
async def process_code(message: types.Message, manager: Manager, **kwargs):
    if not manager.state.type_on:
        return
    code = get_forced_code_text_from_message_or_reply(message)

    if manager.state.enhanced_code_report:
        await message.reply(try_send_code_view(code), parse_mode='Markdown')

    if 'forced_code_verdict' in kwargs:
        code_result = CodeResult(kwargs['forced_code_verdict'], '')
    else:
        code_result = await manager.http_client.post_code(code)

    if isinstance(code_result.verdict, int):
        return await message.reply(code_result.comment)
    verdict_value = code_result.verdict.value
    code_verdict_view_message = views.code_verdict_view(code_result.verdict.value, code)
    if verdict_value not in code_utils.GOOD_VERDICTS:
        return await message.reply(code_verdict_view_message, parse_mode='Markdown')
    else:
        if code_result.verdict.value == CodeVerdict.ACCEPTED_NEXT_LEVEL.value:
            await utils.notify_all_channels(manager, code_verdict_view_message)
            return await update_level_status(manager.bot, manager, **kwargs)
        code_updates = await _update_current_level_info_on_code(code_verdict_view_message, message, manager, **kwargs)
        kwargs['ko_caption'] = code_updates
        await send_ko(message, manager, **kwargs)


async def process_test_code(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    verdict, game_status_ref = text.split(maxsplit=1)
    code_verdict = CodeVerdict(int(verdict))
    game_status = get_forced_game_status_or_none(game_status_ref)
    if game_status is None:
        return await message.reply(f"Не удалось загрузить новый статус: {game_status_ref}")
    kwargs['forced_code_verdict'] = code_verdict
    kwargs['game_status'] = game_status
    message.text = 'dr1'
    await process_code(message, manager, **kwargs)


async def list_sectors(message: types.Message, manager: Manager, **kwargs):
    return await message.reply(views.get_sectors_list(manager.state.koline), parse_mode='Markdown')


def get_forced_game_status_or_none(status_ref: str):
    # TODO: fix unsafe calls and test
    if status_ref.startswith('{'):
        status_dict = status_ref
    elif '/' in status_ref:
        status_dict = requests.get(status_ref).text
    else:
        with open(f'test_game_states/{status_ref}') as f:
            status_dict = f.readline()
    try:
        return StatusSchema(partial=True, unknown=EXCLUDE).load(literal_eval(status_dict))
    except Exception as e:
        logger.error(f'Failed to parse forced status with ref: {status_ref}')
        return None


@safe_dzzzr_interaction
async def update_level(message: types.Message, manager: Manager, **kwargs):
    status_ref = utils.trim_command_name(message, kwargs['command_name'])
    if len(status_ref):
        game_status = get_forced_game_status_or_none(status_ref)
        if game_status is None:
            game_status = StatusSchema(partial=True, unknown=EXCLUDE).load({})
            await message.reply(f'Не удалось распарсить игровой статус: {status_ref}')
    else:
        game_status = await manager.http_client.status()
    await message.reply(str(game_status))
    await update_level_status(manager.bot, manager, **{'game_status': game_status})


async def process_next_level(status, manager: Manager, silent):
    manager.state.reset('code_pattern')
    manager.state.reset('tip')
    if silent:
        return
    await utils.notify_all_channels(manager, "Выдан новый уровень")
    if not status:
        await utils.notify_all_channels(manager, "Не удалось загрузить статус по игре")
        return
    if not status.current_level:
        await utils.notify_all_channels(manager, "Не удалось загрузить статус по уровню")
        return
    if status.current_level.question:
        await utils.notify_all_channels(manager, utils.format_level_message(status.current_level.question))
        schema_urls = utils.get_schema_urls(status.current_level.question)
        if len(schema_urls):
            for schema_url in schema_urls:
                try:
                    await utils.image_to_all_channels(manager, "Схема захода: \n", schema_url)
                except Exception as e:
                    await utils.notify_debug_chat(manager, f"Не удалось отправить картинку по адресу {schema_url}")
                    await utils.notify_debug_chat(manager, e)
        else:
            await utils.notify_all_channels(manager, "Схема захода: Не удалось распарсить")
    if status.current_level.locationComment:
        await utils.notify_all_channels(
            manager,
            utils.format_level_message(status.current_level.locationComment))


async def update_on_spoiler_solved(manager: Manager, new_status: Status) -> None:
    old_spoiler_status = manager.state.game_status.get_spoiler_or_none() if manager.state.game_status else None
    new_spoiler_status = new_status.get_spoiler_or_none() if new_status else None
    if old_spoiler_status and new_spoiler_status:
        if not old_spoiler_status.is_solved() and new_spoiler_status.is_solved():
            await utils.notify_all_channels(manager, "Спойлер ап:\n" +
                                            utils.clean_html_tags(new_spoiler_status.spoilerText))


async def _update_current_level_info(game_status: Status, manager: Manager, on_up: bool):
    if not on_up:
        await update_on_spoiler_solved(manager, game_status)
    manager.state.game_status = game_status
    if not game_status.current_level:
        logger.info("Level info is empty")
        return
    if not game_status.current_level.koline:
        logger.info("Level with empty koline")
        return
    try:
        manager.state.koline = model_parsing_utils.parse_koline_from_string(game_status.current_level.koline)
    except Exception as e:
        logger.error("Bad koline to parse: {}".format(game_status.current_level.koline))


async def _update_current_level_info_on_code(verdict: str, message: types.Message, manager: Manager, **kwargs):
    if 'game_status' in kwargs:
        new_status = kwargs['game_status']
    else:
        new_status = await manager.http_client.status()
    koline = manager.state.koline
    new_koline = model_parsing_utils.parse_koline_from_string(new_status.current_level.koline)

    if not koline:
        logger.error('Koline has not been initialized on level')
        manager.state.koline = new_koline
        manager.state.game_status = new_status
        return
    if len(koline.sectors) != len(new_koline.sectors):
        logger.error('Number of sectors has been changed, probably level has been upped')
        manager.state.koline = new_koline
        manager.state.game_status = new_status
        return
    codes_update = ''
    for old_sector, new_sector in zip(koline.sectors, new_koline.sectors):
        if len(old_sector.codes) != len(new_sector.codes):
            logger.error(f'Number of codes for sector: {new_sector.name} is broken')
            return
        for old_code, new_code in zip(old_sector.codes, new_sector.codes):
            if not old_code.taken and new_code.taken:
                codes_update += code_update_view(
                    verdict,
                    new_sector.name,
                    new_status.current_level.tm,
                    new_code.label,
                    new_code.ko
                )
    manager.state.koline = new_koline
    manager.state.game_status = new_status
    return codes_update


@safe_dzzzr_interaction
async def update_level_status(bot: Bot, manager: Manager, **kwargs):
    forced_update = 'game_status' in kwargs
    game_status = None
    if forced_update:
        game_status = kwargs['game_status']
    elif manager.state.parse_on:
        game_status = await manager.http_client.status()
    if not game_status or not game_status.current_level:
        return
    current_level_id = game_status.current_level.levelNumber
    # To avoid dummy messages to the chats on the bot or game startup
    is_fresh_start = not manager.state.game_status
    if is_fresh_start or manager.state.game_status.current_level.levelNumber != current_level_id:
        manager.logger.info(f'New game status from site {game_status}')
        await _update_current_level_info(game_status, manager, on_up=True)
        return await process_next_level(game_status, manager, silent=is_fresh_start)
    return await _update_current_level_info(game_status, manager, on_up=False)


async def try_process_coords(message: types.Message, manager: Manager, text: str):
    coords = re.findall(patterns.STANDARD_COORDS_PATTERN, text)
    if len(coords) > 2:
        await message.reply(
            pretty_format_message_with_coords(message.text),
            parse_mode='Markdown',
            disable_web_page_preview=True
        )


async def try_process_code(message: types.Message, manager: Manager, text: str):
    if re.fullmatch(patterns.CYRILLIC_DR_PATTERN, text):
        message.text = text.replace('д', 'd').replace('р', 'r')
    await process_code(message, manager)


async def process_unknown(message: types.Message, manager: Manager, **kwargs):
    text = utils.parse_message_text(message).lower()
    # check for '/ ' here is for processing messages with media content
    # as they are not yet supported for default commands
    if re.fullmatch(manager.state.code_pattern, text) or text.startswith('.') or text.startswith('/ '):
        await try_process_code(message, manager, text)
    elif manager.state.maps_on:
        await try_process_coords(message, manager, text)


async def process_get_chat_id(message: types.Message, manager: Manager, **kwargs):
    await message.reply("chat id: {}".format(message.chat.id))


async def pin_chat(message: types.Message, manager: Manager, **kwargs):
    if 'main' in utils.parse_message_text(message):
        setattr(manager.state, 'main_chat_id', str(message.chat.id))
        await message.reply("Установлен чат для организационной информации")
    elif 'code' in utils.parse_message_text(message):
        setattr(manager.state, 'code_chat_id', str(message.chat.id))
        await message.reply("Установлен чат для ввода кодов и штабных трансляций")
    elif 'debug' in utils.parse_message_text(message):
        setattr(manager.state, 'debug_chat_id', str(message.chat.id))
        await message.reply("Установлен чат для дебажных отчетов")
    else:
        await message.reply("Используйте один из допустимых аргументов: main, code, debug")


async def set_state_key_value(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    key, value = text.split()
    try:
        setattr(manager.state, key, value)
        await message.reply(f"Для переменной {key} установлено значение: {value}")
    except AttributeError:
        await message.reply(f"Переменной {key} не существует")
    except ValueError:
        await message.reply(f"{value} - недопустимое значение для переменной {key}")
    except TypeError:
        await message.reply(f"Не удалось присвоить значение переменной {key}")


async def get_all_params(message: types.Message, manager: Manager, **kwargs):
    values = asdict(manager.state)
    text = "\n".join(f"{key}: {value}" for key, value in values.items())
    await message.reply(f"Все заданные переменные:\n{text}")


async def get_version(message: types.Message, manager: Manager, **kwargs):
    msg = os.environ.get("VERSION", "Не задана")
    await message.reply(f"Версия бота: {msg}")


async def reset_to_default(message: types.Message, manager: Manager, **kwargs):
    key = utils.trim_command_name(message, kwargs['command_name']).strip()
    if len(key):
        try:
            manager.state.reset(key)
            await message.reply(f"Для переменной {key} установлено значение: {getattr(manager.state, key)}")
        except AttributeError:
            await message.reply(f"Переменной {key} не существует")
    else:
        manager.state.reset_all()
        await message.reply("Выполнен сброс к заводским настройкам")
