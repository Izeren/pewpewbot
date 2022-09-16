import logging
import os


class FileHandler(logging.FileHandler):
    def __init__(self, level):
        filepath = os.environ.get("LOGS_PATH")
        if not filepath:
            filepath = "/logs/pew_{}.log".format(level)
        else:
            filepath += level + '.log'
        super().__init__(filepath, encoding='utf-8')
