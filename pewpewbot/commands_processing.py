import re
from aiogram import types, Bot
from pewpewbot import utils
from pewpewbot.errors import ClientError
from pewpewbot.manager import Manager


async def dummy(message: types.Message, manager: Manager, **kwargs):
    await message.reply("Вы пытаетесь использовать команду {}, но у нее еще нет реализации"
                        .format(kwargs['command_name']))


async def help(message: types.Message, manager: Manager, **kwargs):
    await message.reply(utils.build_help())


async def send_ko(message: types.Message, manager: Manager, **kwargs):
    text = utils.trim_command_name(message, kwargs['command_name']).strip()
    await message.reply("Вы пытаетесь ввести код:" + text)


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
    if text.startswith('/'):
        text = text[1:]
    text = text.strip()
    # TODO: make all awaits in the end
    await message.reply("Пытаюсь пробить код: {}".format(text))
    try:
        code_verdict = await manager.http_client.post_code(text)
        if code_verdict.SUCCESS:
            await message.reply("Код принят")
        else:
            await message.reply("Неверный или повторно введенный код")
    except ClientError:
        await message.reply("Ошибка соединения с сервером")
    except Exception:
        await message.reply("Ошибка, бот не смог")


async def update_level(message: types.Message, manager: Manager, **kwargs):
    try:
        _process_next_level(await manager.http_client.status(), manager)
    except ClientError:
        await message.reply("Ошибка соединения с сервером")
    except Exception:
        await message.reply("Ошибка, бот не смог")


def _process_next_level(status, manager: Manager):
    manager.logger.info("New game status from site {} ".format(status))


def _update_current_level_info(game_status):
    pass


async def update_level_status(bot: Bot, manager: Manager, **kwargs):
    try:
        game_status = await manager.http_client.status()
        current_level_id = game_status.current_level.levelNumber
        if not manager.state.game_status:
            return _process_next_level(game_status, manager)
        if manager.state.game_status.current_level.levelNumber != current_level_id:
            utils.notify_all_channels(bot, manager, "Выдан новый уровень")
            await bot.send_message(manager.state.main_channel_id, "Выдан новый уровень")
            return _process_next_level(game_status, manager)
        else:
            return _update_current_level_info(game_status)
    except ClientError:
        await bot.send_message(manager.state.code_channel_id, "Ошибка при обновлении статуса уровня")
    except Exception:
        await bot.send_message(manager.state.code_channel_id, "Бот упал при обновлении статуса уровня")


async def process_unknown(message: types.Message, manager: Manager, **kwargs):
    await message.reply("Бот не смог распарсить команду: {}".format(message.text))
