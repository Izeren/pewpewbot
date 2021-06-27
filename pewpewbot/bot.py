import os
import asyncio
import logging
from pewpewbot.screenshot import Screenshoter
import commands_processing
from os import path
from functools import partial
from logging import config
from aiogram import Bot, Dispatcher, executor
from pewpewbot import utils
from pewpewbot.client import Client
from pewpewbot.manager import Manager
from pewpewbot.State import ENGINE_TIMEOUT_KEY, SCREENSHOT_TIMEOUT_KEY, State

# List of TgCommand which are enabled in command_patterns
ACTIVE_COMMANDS = utils.get_all_active_commands()

# Configure logging
config.fileConfig(path.join(path.dirname(path.abspath(__file__)), 'logging.ini'))
logger = logging.getLogger(__name__)
logger.propagate = False


def main():
    api_token = os.environ.get('API_TOKEN')
    login = os.environ.get('LOGIN')
    password = os.environ.get('PASSWORD')

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
    screenshoter = Screenshoter(loop=loop) # Can use separate loop here
    manager = Manager(state, Client(), screenshoter, bot, logging.getLogger(Manager.__name__))
    try:
        asyncio.ensure_future(manager.http_client.log_in(login, password), loop=loop)
    except Exception as e:
        logging.error("Failed to login")


    loop.create_task(utils.repeat_runtime_delay(manager, ENGINE_TIMEOUT_KEY, commands_processing.update_level_status, bot, manager))
    loop.create_task(utils.repeat_runtime_delay(manager, SCREENSHOT_TIMEOUT_KEY, screenshoter.update_screenshot, state))

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
