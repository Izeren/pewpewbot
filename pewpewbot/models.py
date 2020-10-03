from dataclasses import dataclass
from enum import Enum
from typing import Any, List

from marshmallow import Schema, fields, post_load, missing

from pewpewbot.errors import AuthenticationError


def _rename(data, **new_names):
    new_fields = {}
    for new_name, old_name in new_names.items():
        if old_name in data:
            new_fields[new_name] = data[old_name]
            del data[old_name]
    return {**data, **new_fields}


class EnumField(fields.Field):
    default_error_messages = {
        'by_name': 'Invalid enum member {input}',
        'by_value': 'Invalid enum value {input}',
        'must_be_string': 'Enum name must be string'
    }

    def __init__(self, enum, by_value=False, *args, **kwargs):
        self.enum = enum
        self.by_value = by_value
        super(EnumField, self).__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        elif self.by_value:
            return value.value
        else:
            return value.name

    def _deserialize(self, value, attr, data, **kwargs):
        if value is None:
            return None
        elif self.by_value:
            return self._deserialize_by_value(value)
        else:
            return self._deserialize_by_name(value)

    def _deserialize_by_value(self, value):
        try:
            return self.enum(value)
        except ValueError:
            self.fail('by_value', input=value)

    def _deserialize_by_name(self, value):
        if not isinstance(value, str):
            self.fail('must_be_string', input=value)
        try:
            return getattr(self.enum, value)
        except AttributeError:
            self.fail('by_name', input=value)


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


class CodeVerdict(Enum):
    SUCCESS = 1
    FAILURE = 2


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
    spoilers: List[str] = None
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
    spoilers = fields.List(fields.Str, required=True)
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
    errNo = EnumField(StatusError, required=True, by_value=True)
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
    err = EnumField(CodeVerdict, required=True, by_value=True)

    @post_load
    def parse_error(self, data, **kwargs) -> CodeVerdict:
        return data['err']
