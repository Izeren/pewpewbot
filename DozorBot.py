from aiogram import Bot

from State import State


class DozorBot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.state = State()
        self.http_client = None
