import logging
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any, List, Union

from marshmallow import Schema, fields, post_load, missing

import patterns
from pewpewbot.errors import AuthenticationError


def _rename(data, **new_names):
    new_fields = {}
    for new_name, old_name in new_names.items():
        if old_name in data:
            new_fields[new_name] = data[old_name]
            del data[old_name]
    return {**data, **new_fields}


class EnumField(fields.Field):
    def __init__(self, enum, strict=True, *args, **kwargs):
        self.enum = enum
        self.strict = strict
        super(EnumField, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        if not self.strict and not isinstance(value, self.enum):
            return value
        return value.value

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        try:
            return self.enum(value)
        except ValueError:
            if not self.strict:
                return value
            self.fail(f'Enum {self.enum} has no such value', input=value)


class IntOrMissing(fields.Int):
    def deserialize(self, value, attr=None, data=None, **kwargs):
        if value == "":
            return missing
        return super().deserialize(value, attr, data, **kwargs)


class BonusLevelsField(fields.List):
    def __init__(self):
        super().__init__(fields.Nested(LevelStatusSchema()))

    def deserialize(self, value, attr=None, data=None, **kwargs):
        if value == [{}]:
            return []
        return super().deserialize(value, attr, data, **kwargs)


class StatusError(Enum):
    SUCCESS = 0
    NO_LEVEL = 15


class CodeVerdict(Enum):
    POSSIBLY_REPEAT = 0
    REPEAT = 7
    COMPOUND_ACCEPTED = 8
    ACCEPTED_NEXT_LEVEL = 9
    REJECTED = 11
    BONUS_REPEAT = 35
    BONUS_ACCEPTED = 36
    ACCEPTED = 55


@dataclass
class CodeResult:
    verdict: Union[CodeVerdict, int]
    comment: str


@dataclass
class Spoiler:
    spoilerText: str
    spoilerSolved: str
    spoilerPenalty: int
    spoilerNumber: int


@dataclass
class LevelStatus:
    isSabotage: bool = None
    levelNumber: int = None
    noMasterCode: bool = None
    isBonusLevel: bool = None
    bonusLevelTime: int = None
    hint1: str = None
    hint2: str = None
    hint3: str = None
    neededCodes: int = None
    codesFounded: int = None
    totalCodes: int = None
    bonusCodesTotal: int = None
    bonusCodesFounded: int = None
    skvoz: bool = None
    bonusCodesTimes: Any = None
    koline: str = None
    question: str = None
    locationComment: str = None
    spoilers: List[Spoiler] = None
    koinspoiler: bool = None
    timeOnLevel: str = None
    tm: int = None
    takeBreak: bool = None

    isLevelFinished: str = None
    locationLon: str = None
    locationLat: str = None
    locationRadius: str = None
    tryLimit: int = None
    tryLimitUsed: str = None
    bonusAfter: int = None

    @classmethod
    def from_api(cls, data) -> 'LevelStatus':
        return cls(**_rename(data))


@dataclass
class Status:
    game_id: str = None
    game_title: str = None
    game_greeting: str = None
    game_legend: str = None

    game_start_time: str = None
    hold_time: str = None
    break_time: str = None
    current_time: str = None

    current_level: LevelStatus = None
    bonus_levels: List[LevelStatus] = None

    last_organizational_message: str = None
    messages: List[str] = None
    error: StatusError = None
    error_text: str = None

    gameStartOnTime: str = None
    blockedError: str = None
    tryLimitError: str = None
    totallevels: int = None
    finished: bool = None
    gameStartOnDay: str = None
    teamName: str = None
    bonusSkvozLevels: str = None
    canControl: str = None
    countdown: str = None
    NextLevelSelector: str = None

    @classmethod
    def from_api(cls, data) -> 'Status':
        return cls(**_rename(
            data, game_id='gameId', game_title='gameName', game_greeting='greeting', game_legend='legend',
            game_start_time='gameStartTime', hold_time='holdTime', break_time='onBreak', current_time='currentTime',
            current_level='level', bonus_levels='bonusLevels', last_organizational_message='lastOrgMessage',
            error='errNo', error_text='errText'))


class SpoilerSchema(Schema):
    spoilerText = fields.Str()
    spoilerSolved = fields.Str()
    spoilerPenalty = fields.Int()
    spoilerNumber = fields.Int()

    @post_load
    def to_object(self, data, **kwargs):
        return Spoiler(**data)


class LevelStatusSchema(Schema):
    isSabotage = fields.Bool()
    levelNumber = IntOrMissing()
    noMasterCode = fields.Bool()
    isBonusLevel = fields.Bool()
    bonusLevelTime = IntOrMissing()
    hint1 = fields.Str()
    hint2 = fields.Str()
    hint3 = fields.Str()
    neededCodes = IntOrMissing()
    codesFounded = IntOrMissing()
    totalCodes = IntOrMissing(required=True)
    bonusCodesTotal = IntOrMissing(required=True)
    bonusCodesFounded = IntOrMissing(required=True)
    skvoz = fields.Bool(required=True)
    bonusCodesTimes = fields.Raw(required=True)
    koline = fields.Str(required=True)
    question = fields.Str(required=True)
    locationComment = fields.Str(required=True)
    spoilers = fields.List(fields.Nested(SpoilerSchema), required=True)
    koinspoiler = fields.Bool(required=True)
    timeOnLevel = fields.Str(required=True)
    tm = IntOrMissing(required=True)
    takeBreak = fields.Bool(required=True)

    isLevelFinished = fields.Str()
    locationLon = fields.Str()
    locationLat = fields.Str()
    locationRadius = fields.Str()
    tryLimit = fields.Int()
    tryLimitUsed = fields.Str()
    bonusAfter = fields.Int()

    @post_load
    def to_object(self, data, **kwargs) -> LevelStatus:
        return LevelStatus.from_api(data)


@dataclass
class ParsedCode:
    label: int
    ko: str
    taken: bool
    is_bonus: bool

    @staticmethod
    def from_string(label, raw_code, is_bonus=False):
        raw_code = raw_code.strip()
        taken = raw_code.startswith('r')
        if taken:
            ko = raw_code[1:]
        else:
            ko = raw_code
        return ParsedCode(label, ko, taken, is_bonus)


@dataclass
class Sector:
    name: str
    codes: List[ParsedCode]

    @staticmethod
    def from_string(raw_sector):
        raw_sector = raw_sector.strip()
        name, codes = raw_sector.rsplit(':', maxsplit=1)
        name = name.strip()
        codes = codes.strip()
        if len(name) == 0:
            name = "Сектор без названия"
        is_bonus = "бонус" in name.lower()
        return Sector(name=name, codes=list(ParsedCode.from_string(label, code, is_bonus)
                                            for label, code in enumerate(codes.split(','))))


@dataclass
class Koline:
    sectors: List[Sector]

    @staticmethod
    def from_string(koline: str):
        koline = koline.replace('null', 'N').strip()
        koline = koline.replace('<span style=\'color:red\'>', 'r')
        koline = koline.replace('</span>', '')
        return Koline(sectors=list(Sector.from_string(raw_sector) for raw_sector in koline.split('<br>') if raw_sector))


class StatusSchema(Schema):
    gameName = fields.Str(required=True)
    greeting = fields.Str(required=True)
    lastOrgMessage = fields.Str(required=True)
    gameId = fields.Str(required=True)
    gameStartTime = fields.Str()
    holdTime = fields.Str()
    onBreak = fields.Str()
    currentTime = fields.Str()
    legend = fields.Str()
    level = fields.Nested(LevelStatusSchema)
    bonusLevels = BonusLevelsField()
    messages = fields.List(fields.Str)
    errNo = EnumField(StatusError, strict=False, required=True)
    errText = fields.Str()

    gameStartOnTime = fields.Str()
    blockedError = fields.Str()
    tryLimitError = fields.Str()
    totallevels = fields.Int()
    finished = fields.Bool()
    gameStartOnDay = fields.Str()
    teamName = fields.Str()
    bonusSkvozLevels = fields.Str()
    canControl = fields.Str()
    countdown = fields.Str()
    NextLevelSelector = fields.Str()

    @post_load
    def to_object(self, data, **kwargs) -> Status:
        return Status.from_api(data)


class TokenSchema(Schema):
    error = fields.Str(required=True)
    code = IntOrMissing(required=True)
    userName = fields.Str()
    userToken = fields.Str()

    @post_load
    def extract_token(self, data, **kwargs) -> str:
        if data['code'] != 2:
            raise AuthenticationError(data)
        return data['userToken']


class CodeSchema(Schema):
    errNo = EnumField(CodeVerdict, strict=False, required=True)
    errText = fields.Str()

    @post_load
    def parse_error(self, data, **kwargs) -> CodeResult:
        return CodeResult(verdict=data['errNo'], comment=data['errText'])
