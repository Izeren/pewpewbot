import asyncio
import logging
from functools import partial
from aiogram import Bot, Dispatcher, executor

import commands_processing
from pewpewbot.client import Client
from pewpewbot.command_patterns import ALL_COMMANDS
from pewpewbot.manager import Manager
from pewpewbot.settings import API_TOKEN
from pewpewbot.State import State

# Every 30 seconds bot will ping server
TIMEOUT = 30


def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, filename='pewpew.log')

    # Create loop will be used in bot
    loop = asyncio.get_event_loop()

    # Initialize bot and manager
    bot = Bot(token=API_TOKEN, loop=loop)
    manager = Manager(State(), Client(), logging.getLogger(Manager.__name__))
    try:
        from settings import LOGIN
        from settings import PASSWD
        asyncio.ensure_future(manager.http_client.log_in(LOGIN, PASSWD), loop=loop)
    except Exception as e:
        logging.getLogger(__name__).error("Failed to login")

    # Use hack for repeated coro every TIMEOUT seconds
    def repeat(coro, loop):
        asyncio.ensure_future(coro(bot, manager), loop=loop)
        loop.call_later(TIMEOUT, repeat, coro, loop)

    # Run timer call inside of loop
    loop.call_later(TIMEOUT, repeat, commands_processing.update_level_status, loop)

    # Create dispatcher
    dispatcher = Dispatcher(bot)

    # Register commands in dispatcher
    for command in ALL_COMMANDS:
        if not command.enabled:
            continue
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
