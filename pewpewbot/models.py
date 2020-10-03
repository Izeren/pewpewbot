from dataclasses import dataclass
from enum import Enum
from typing import Any, List

from marshmallow import Schema, fields, post_load
from marshmallow_enum import EnumField

from pewpewbot.errors import AuthenticationError


def _rename(data, **new_names):
    new_fields = {}
    for new_name, old_name in new_names.items():
        if old_name in data:
            new_fields[new_name] = data[old_name]
            del data[old_name]
    return {**data, **new_fields}


class StatusError(Enum):
    SUCCESS = 1


class CodeVerdict(Enum):
    SUCCESS = 1
    FAILURE = 2


@dataclass
class LevelStatus:
    isSabotage: bool
    levelNumber: int
    noMasterCode: bool
    isBonusLevel: bool
    bonusLevelTime: int
    hint1: str
    hint2: str
    hint3: str
    neededCodes: int
    codesFounded: int
    totalCodes: int
    bonusCodesTotal: int
    bonusCodesFounded: int
    skvoz: bool
    bonusCodesTimes: Any
    koline: str
    question: str
    locationComment: str
    spoilers: List[str]
    koinspoiler: bool
    timeOnLevel: str
    tm: int
    takeBreak: bool

    @classmethod
    def from_api(cls, data) -> 'LevelStatus':
        return cls(**_rename(data))


@dataclass
class Status:
    game_id: str
    game_title: str
    game_greeting: str
    game_legend: str

    game_start_time: str
    hold_time: str
    break_time: str
    current_time: str

    current_level: LevelStatus
    bonus_levels: List[LevelStatus]

    last_organizational_message: str
    messages: List[str]
    error: StatusError
    error_text: str

    @classmethod
    def from_api(cls, data) -> 'Status':
        return cls(**_rename(
            data, game_id='gameId', game_title='gameName', game_greeting='greeting', game_legeng='legend',
            game_start_time='gameStartTime', hold_time='holdTime', break_time='onBreak', current_time='currentTime',
            current_level='level', bonus_levels='bonusLevels', last_organizational_message='lastOrgMessage',
            error='errNo', error_text='errText'))


class LevelStatusSchema(Schema):
    isSabotage = fields.Bool()
    levelNumber = fields.Int()
    noMasterCode = fields.Bool()
    isBonusLevel = fields.Bool()
    bonusLevelTime = fields.Int()
    hint1 = fields.Str()
    hint2 = fields.Str()
    hint3 = fields.Str()
    neededCodes = fields.Int()
    codesFounded = fields.Int()
    totalCodes = fields.Int(required=True)
    bonusCodesTotal = fields.Int(required=True)
    bonusCodesFounded = fields.Int(required=True)
    skvoz = fields.Bool(required=True)
    bonusCodesTimes = fields.Raw(required=True)
    koline = fields.Str(required=True)
    question = fields.Str(required=True)
    locationComment = fields.Str(required=True)
    spoilers = fields.List(fields.Str, required=True)
    koinspoiler = fields.Bool(required=True)
    timeOnLevel = fields.Str(required=True)
    tm = fields.Int(required=True)
    takeBreak = fields.Bool(required=True)

    @post_load
    def to_object(self, data) -> LevelStatus:
        return LevelStatus.from_api(data)


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
    bonusLevels = fields.List(fields.Nested(LevelStatusSchema))
    messages = fields.List(fields.Str)
    errNo = EnumField(StatusError, required=True, by_value=True)
    errText = fields.Str()

    @post_load
    def to_object(self, data) -> Status:
        return Status.from_api(data)


class TokenSchema(Schema):
    error = fields.Str(required=True)
    code = fields.Int(required=True)
    userName = fields.Str()

    userToken = fields.Str()
    @post_load
    def extract_token(self, data) -> str:
        if data['code'] != 2:
            raise AuthenticationError(data)
        return data['userToken']


class CodeSchema(Schema):
    err = EnumField(CodeVerdict, required=True, by_value=True)

    @post_load
    def parse_error(self, data) -> CodeVerdict:
        return data['err']
