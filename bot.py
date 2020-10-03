import logging
from functools import partial

from aiogram import Dispatcher, executor

from .command_patterns import ALL_COMMANDS
from .DozorBot import DozorBot
from .settings import API_TOKEN


# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = DozorBot(token=API_TOKEN)
dispatcher = Dispatcher(bot)


for command in ALL_COMMANDS:
    if not command.enabled:
        continue
    if command.pattern is not None:
        kwargs = dict(regexp=command.pattern)
    else:
        kwargs = dict(commands=command.names)
    dispatcher.register_message_handler(partial(command.apply_and_get_awaitable, bot=bot), **kwargs)


if __name__ == '__main__':
    executor.start_polling(dispatcher, skip_updates=True)
