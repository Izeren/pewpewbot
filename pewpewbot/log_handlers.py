import logging
import os


class FileHandler(logging.FileHandler):
    def __init__(self, level):
        filepath = os.environ.get("LOGS_PATH")
        if not filepath:
            filepath = "/app/pew_{}.log".format(level)
        else:
            filepath += level + '.log'
        super().__init__(filepath)
