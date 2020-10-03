from dataclasses import dataclass
from logging import Logger

from pewpewbot.State import State
from pewpewbot.client import Client


@dataclass
class Manager:
    state: State
    http_client: Client
    logger: Logger
