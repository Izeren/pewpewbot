import os
import asyncio
import logging
import pathlib
from pewpewbot.screenshot import Screenshoter
import commands_processing
from os import path
from functools import partial
from logging import config
from aiogram import Bot, Dispatcher, executor
from pewpewbot import utils
from pewpewbot.client import Client
from pewpewbot.manager import Manager
from pewpewbot.State import State

# List of TgCommand which are enabled in command_patterns
ACTIVE_COMMANDS = utils.get_all_active_commands()
DUMP_CONFIG_TIMEOUT = 30

# Configure logging
config.fileConfig(path.join(path.dirname(path.abspath(__file__)), 'logging.ini'))
logger = logging.getLogger(__name__)
logger.propagate = False


def main():
    api_token = os.environ.get('API_TOKEN')
    login = os.environ.get('LOGIN')
    password = os.environ.get('PASSWORD')
    state_file_path = pathlib.Path(os.environ.get('STATE_FILE_PATH', './state.json'))

    if not api_token:
        logger.error("Empty API_TOKEN for telegram bot, please provide")
        return
    if not login or not password:
        logger.warning("There is no LOGIN or PASSWORD, please use auth command for authorization")
    # Create loop will be used in bot
    loop = asyncio.get_event_loop()

    # Initialize bot and manager
    bot = Bot(token=api_token, loop=loop)
    state = State()
    if state_file_path.is_file():
        try:
            state.load_params(state_file_path)
        except Exception as exc:
            logger.warn("Failed to load params", exc_info=exc)
    screenshoter = Screenshoter(loop=loop) # Can use separate loop here
    manager = Manager(state, Client(), screenshoter, bot, logging.getLogger(Manager.__name__))
    try:
        asyncio.ensure_future(manager.http_client.log_in(login, password), loop=loop)
    except Exception as e:
        logging.error("Failed to login")


    loop.create_task(utils.repeat_runtime_delay(manager, 'engine_timeout', commands_processing.update_level_status, bot, manager))
    loop.create_task(utils.repeat_runtime_delay(manager, 'screenshot_timeout', screenshoter.update_screenshot, state))
    loop.create_task(utils.repeat_const_delay(DUMP_CONFIG_TIMEOUT, state.dump_params, state_file_path))


    # Create dispatcher
    dispatcher = Dispatcher(bot)

    # Register commands in dispatcher
    for command in ACTIVE_COMMANDS:
        if command.pattern is not None:
            kwargs = dict(regexp=command.pattern)
        else:
            kwargs = dict(commands=command.names)
        dispatcher.register_message_handler(partial(command.apply_and_get_awaitable, manager=manager), **kwargs)
    dispatcher.register_message_handler(partial(commands_processing.process_unknown, manager=manager), **{})

    # Start polling
    executor.start_polling(dispatcher, skip_updates=True)


if __name__ == '__main__':
    main()
