import asyncio
import logging
import aio_timers
from functools import partial
from aiogram import Bot, Dispatcher, executor

import commands_processing
from pewpewbot.client import Client
from pewpewbot.command_patterns import ALL_COMMANDS
from pewpewbot.manager import Manager
from pewpewbot.settings import API_TOKEN
from pewpewbot.State import State


# Configure logging
logging.basicConfig(level=logging.INFO, filename='pewpew.log')

# Initialize bot and dispatcher
manager = Manager(State(), Client(), logging.getLogger(Manager.__name__))
dispatcher = Dispatcher(Bot(token=API_TOKEN))

for command in ALL_COMMANDS:
    if not command.enabled:
        continue
    if command.pattern is not None:
        kwargs = dict(regexp=command.pattern)
    else:
        kwargs = dict(commands=command.names)
    dispatcher.register_message_handler(partial(command.apply_and_get_awaitable, manager=manager), **kwargs)


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)
