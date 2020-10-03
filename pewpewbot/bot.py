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

# Every 10 seconds bot will ping server
TIMEOUT = 30


def main():
    # Configure logging
    logging.basicConfig(level=logging.INFO, filename='pewpew.log')

    # Create loop will be used in bot
    loop = asyncio.get_event_loop()

    # Initialize bot and manager
    bot = Bot(token=API_TOKEN, loop=loop)
    manager = Manager(State(), Client(), logging.getLogger(Manager.__name__))

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

    # Start polling
    executor.start_polling(dispatcher, skip_updates=True)


if __name__ == '__main__':
    main()

#
# DELAY = 7200
#
# bot = Bot(token='BOT TOKEN HERE')
# dp = Dispatcher(bot)
#
# @dp.message_handler(commands=['start', 'help'])
# async def send_welcome(message: types.Message):
#     await message.reply("Hi!\nI'm EchoBot!\nPowered by aiogram.")
#
#
# async def update_price():
#     ...
#
#
# def repeat(coro, loop):
#     asyncio.ensure_future(coro(), loop=loop)
#     loop.call_later(DELAY, repeat, coro, loop)
#
#
# if __name__ == '__main__':
#     loop = asyncio.get_event_loop()
#     loop.call_later(DELAY, repeat, update_price, loop)
#     executor.start_polling(dp, loop=loop)
