from datetime import datetime
import json
import logging
from pathlib import Path
from pewpewbot.models import Status, Koline
from dataclasses import MISSING, asdict, dataclass, field
from pewpewbot import patterns


@dataclass
class State:
    parse_on: bool = False
    type_on: bool = False
    maps_on: bool = True
    tip: list = field(default_factory=list)  # Should be list[list[str]]
    link: str = "http://classic.dzzzr.ru/moscow/go/"
    code_chat_id: str = field(default=None)
    main_chat_id: str = field(default=None)
    debug_chat_id: str = field(default=None)
    engine_timeout: int = 30
    screenshot_url: str = field(default=None)
    screenshot_timeout: int = 5
    screenshot_height: int = 1000
    screenshot_width: int = 1000
    code_pattern: str = patterns.STANDARD_CODE_PATTERN
    game_status: Status = field(default=None)
    koline: Koline = field(default=None)

    async def dump_params(
            self, file_path: Path, ignore_fields: list = ["game_status", "koline"]
    ):
        params_dict = asdict(self)
        for key in ignore_fields:
            params_dict.pop(key, None)
        with open(file_path, "w") as f:
            json.dump(params_dict, f)
        logging.info(f"Parameters dumped to {file_path}")

    def load_params(self, file_path: Path):
        with open(file_path, "r") as f:
            params = json.load(f)
        for param in params:
            try:
                setattr(self, param, params[param])
            except AttributeError:
                pass
        logging.info(f"Parameters loaded from {file_path}")

    def reset(self, field_name):
        """
        Resets field to default value.
        For example, state.reset("parse_on") is equialent to state.parse_on = False
        """
        if field_name not in self.__dataclass_fields__:
            raise ValueError(f"Field {field_name} does not exist in State")
        field = self.__dataclass_fields__[field_name]
        if field.default is MISSING and field.default_factory is MISSING:
            raise ValueError(f"Default value for field {field_name} is not set")
        if field.default is MISSING:
            setattr(self, field_name, field.default_factory())
        else:
            setattr(self, field_name, field.default)

    def reset_all(self):
        """
        Resets all fields to default values.
        """
        for field_name in self.__dataclass_fields__:
            self.reset(field_name)

    def set_tip_all_sectors(self, tip):
        sector_tips = [sector_tip.strip() for sector_tip in tip.split("***")]
        self.tip = []
        for sector_tip in sector_tips:
            self.tip.append(
                [
                    tip
                    for tip in [raw_tip.strip() for raw_tip in sector_tip.split("\n")]
                    if len(tip)
                ]
            )

    def set_tip_for_sector(self, sector_tip, sector_id):
        self.tip[sector_id] = [tip for tip in [raw_tip.strip() for raw_tip in sector_tip.split("\n")] if len(tip)]

    def __setattr__(self, name, value):
        if name not in self.__dataclass_fields__:
            raise AttributeError(f"Attribute {name} does not exist in State")
        field = self.__dataclass_fields__[name]
        field_type = field.type
        if isinstance(value, field_type) or value is None:  # if value type matches field
            super().__setattr__(name, value)
        elif field_type is int and isinstance(value, str):  # casts str to int
            super().__setattr__(name, int(value))

    def get_tm_or_none(self):
        tm = None
        if self.game_status and self.game_status.current_level:
            tm = self.game_status.current_level.tm
        return tm

    def get_engine_timeout(self):
        tm = self.get_tm_or_none()
        if tm and tm < self.engine_timeout:
            return tm
        else:
            return self.engine_timeout

    def get_screenshot_timeout(self):
        return self.screenshot_timeout
