from functools import partial
from pewpewbot.manager import Manager
from textwrap import dedent

from aiogram import types
from pewpewbot import commands_processing, utils
from typing import List


class TgCommand(object):
    def __init__(self, names, help_text, awaitable_action_method, enabled=False, pattern=None):
        if isinstance(names, str):
            names = [names]
        self.names = names
        self.pattern = pattern
        self.help_text = dedent(help_text)
        self.awaitable_action_method = awaitable_action_method
        self.enabled = enabled

    def apply_and_get_awaitable(self, message, manager, **kwargs):
        command_name = utils.parse_message_text(message).split(' ', maxsplit=1)[0].lstrip('/')
        # assert command_name in self.names, (command_name, self.names)
        kwargs['command_name'] = command_name
        return self.awaitable_action_method(message, manager, **kwargs)


class TgCommandManager:
    def __init__(self, commands: List[TgCommand] = None):
        if commands is None:
            self.commands = []
        else:
            self.commands = commands

    def add_commands(self, *args):
        self.commands.extend(
            command for command in args if isinstance(command, TgCommand)
        )

    def get_enabled_commands(self):
        return [command for command in self.commands if command.enabled]

    async def process_help(self, message: types.Message, manager: Manager, **kwargs):
        text = "".join(
            (command.help_text for command in self.commands if command.enabled)
        )
        await message.reply(text)

    def register_commands(self, dispatcher, manager):
        # Register commands in dispatcher
        for command in self.get_enabled_commands():
            if command.pattern is not None:
                kwargs = dict(regexp=command.pattern)
            else:
                kwargs = dict(commands=command.names)
            dispatcher.register_message_handler(
                partial(command.apply_and_get_awaitable, manager=manager), **kwargs
            )
        dispatcher.register_message_handler(
            partial(commands_processing.process_unknown, manager=manager),
            content_types=types.ContentType.all(), **{}
        )
