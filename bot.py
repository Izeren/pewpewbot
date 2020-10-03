import logging

from aiogram import Dispatcher, executor, types
from aiogram.dispatcher import filters

import command_patterns
import utils
from DozorBot import DozorBot
from settings import API_TOKEN

# Configure logging
logging.basicConfig(level=logging.INFO)


# Initialize bot and dispatcher
bot = DozorBot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    await message.reply(utils.build_help())

@dp.message_handler(filters.RegexpCommandsFilter(regexp_commands=[command_patterns.PARSE_COORDS_COMMAND.pattern]))
async def on_coords(message: types.Message):
    await command_patterns.PARSE_COORDS_COMMAND.apply_and_get_awaitable(message, bot)

@dp.message_handler(commands=[command_patterns.KO_COMMAND.name])
async def on_ko(message: types.Message):
    await command_patterns.KO_COMMAND.apply_and_get_awaitable(message, bot)

@dp.message_handler(commands=[command_patterns.IMG_COMMAND.name])
async def on_img(message: types.Message):
    await command_patterns.IMG_COMMAND.apply_and_get_awaitable(message, bot)

@dp.message_handler(commands=[command_patterns.LINK_COMMAND.name])
async def on_link(message: types.Message):
    await command_patterns.LINK_COMMAND.apply_and_get_awaitable(message, bot)

@dp.message_handler(commands=[command_patterns.TIP_COMMAND.name])
async def on_tip(message: types.Message):
    await command_patterns.TIP_COMMAND.apply_and_get_awaitable(message, bot)

@dp.message_handler(commands=[command_patterns.GET_CHAT_ID_COMMAND.name])
async def on_get_chat_id(message: types.Message):
    await command_patterns.GET_CHAT_ID_COMMAND.apply_and_get_awaitable(message, bot)

@dp.message_handler(commands=[command_patterns.PARSE_COMMAND.name])
async def on_parse(message: types.Message):
    await command_patterns.PARSE_COMMAND.apply_and_get_awaitable(message, bot)

@dp.message_handler(commands=[command_patterns.MAPS_COMMAND.name])
async def on_parse(message: types.Message):
    await command_patterns.MAPS_COMMAND.apply_and_get_awaitable(message, bot)

@dp.message_handler(commands=[command_patterns.PATTERN_COMMAND.name])
async def on_pattern(message: types.Message):
    await command_patterns.PATTERN_COMMAND.apply_and_get_awaitable(message, bot)

@dp.message_handler(commands=[command_patterns.PIN_COMMAND.name])
async def on_pin(message: types.Message):
    await command_patterns.PIN_COMMAND.apply_and_get_awaitable(message, bot)

@dp.message_handler(commands=[command_patterns.SLEEP_SECONDS_COMMAND.name])
async def echo(message: types.Message):
    await command_patterns.SLEEP_SECONDS_COMMAND.apply_and_get_awaitable(message, bot)

@dp.message_handler(commands=[command_patterns.STATUS_COMMAND.name])
async def echo(message: types.Message):
    await command_patterns.STATUS_COMMAND.apply_and_get_awaitable(message, bot)

@dp.message_handler(commands=[command_patterns.TEST_ERROR_COMMAND.name])
async def echo(message: types.Message):
    await command_patterns.TEST_ERROR_COMMAND.apply_and_get_awaitable(message, bot)

@dp.message_handler(commands=[command_patterns.TYPE_COMMAND.name])
async def echo(message: types.Message):
    await command_patterns.TYPE_COMMAND.apply_and_get_awaitable(message, bot)

@dp.message_handler(commands=[command_patterns.SET_COMMAND.name])
async def echo(message: types.Message):
    await command_patterns.SET_COMMAND.apply_and_get_awaitable(message, bot)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)