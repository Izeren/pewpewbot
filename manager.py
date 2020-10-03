from dataclasses import dataclass
from State import State
from client import Client


@dataclass
class Manager:
    state : State
    http_client : Client
