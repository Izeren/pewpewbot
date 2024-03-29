from asyncio import Future
from logging import Logger

from aiogram import types
from mock import Mock

from pewpewbot.model_parsing_utils import parse_koline_from_string
from pewpewbot.models import Status, LevelStatus, Spoiler, Koline
from pewpewbot.state import State
from pewpewbot.client import Client
from pewpewbot.manager import Manager

SECTOR_NAME_DEFAULT = 'основные коды'
SECTOR_NAME_BONUS = 'бонусные коды'
DR_CODE = 'dr1'
TM_DEFAULT = 42
# Label are counted from zero except the view
LABEL_UP_DEFAULT = 3
KO_DEFAULT = '1+'
UNUSUAL_CODE = 'test_code'
TEST_LEVEL_QUESTION = "<span>На локации вас ожидает 26 кодов. 13 верных, 13 штрафных (1 мин штрафа)." \
                      "Для прохождения нужно найти 12 верных кодов.</span></p>" \
                      "\r\n<p> </p>\r\n<p> </p>\r\n<p>МЕТКА НА УРОВНЕ:"
MAIN_SECTOR_DEFAULT = " основные коды: <span style='color:red'>1</span>, 2, 2, 1+, " \
                      "<span style='color:red'>1+</span>, " \
                      "<span style='color:red'>1+</span>, <span style='color:red'>1</span>, 1+, " \
                      "<span style='color:red'>1+</span>, <span style='color:red'>1</span>, 1+, " \
                      "<span style='color:red'>1+</span>, <span style='color:red'>1+</span><br>"
MAIN_SECTOR_UP_1_CODE_LABEL_3 = " основные коды: <span style='color:red'>1</span>, 2, 2, " \
                                "<span style='color:red'>1+</span>, <span style='color:red'>1+</span>, " \
                                "<span style='color:red'>1+</span>, <span style='color:red'>1</span>, 1+, " \
                                "<span style='color:red'>1+</span>, <span style='color:red'>1</span>, 1+, " \
                                "<span style='color:red'>1+</span>, <span style='color:red'>1+</span><br>"
BONUS_SECTOR_DEFAULT = " бонусные коды: <span style='color:red'>1</span>, 2<br>"
BONUS_SECTOR_UP_1_CODE_LABEL_1 = " бонусные коды: <span style='color:red'>1</span>, 2<br>"
KOLINE_DEFAULT = MAIN_SECTOR_DEFAULT
KOLINE_UP_1_CODE_LABEL_3 = MAIN_SECTOR_UP_1_CODE_LABEL_3
KOLINE_MULTISECTOR_DEFAULT = MAIN_SECTOR_DEFAULT + BONUS_SECTOR_DEFAULT
KOLINE_MULTISECTOR_BONUS_CODE_UP = MAIN_SECTOR_DEFAULT + BONUS_SECTOR_UP_1_CODE_LABEL_1
KOLINE_DEFAULT_PARSED = parse_koline_from_string(KOLINE_DEFAULT)
KOLINE_UP_1_CODE_LABEL_3_PARSED = parse_koline_from_string(KOLINE_UP_1_CODE_LABEL_3)


def mock_manager(koline: Koline = None, game_status: Status = None):
    client = Mock(Client)
    state = State()
    if game_status:
        state.koline = parse_koline_from_string(game_status.current_level.koline)
        state.game_status = game_status
    elif koline:
        state.koline = koline
        state.game_status = Status()
        state.game_status.current_level = LevelStatus()
        state.game_status.current_level.question = TEST_LEVEL_QUESTION
    logger_mock = Mock(Logger)
    return Manager(state, client, None, None, logger_mock)


def mock_manager_with_future_koline(str_koline=''):
    future_status = Future()
    koline = parse_koline_from_string(str_koline)
    status = Mock(Status)
    status.current_level = Mock(LevelStatus)
    status.current_level.koline = str_koline
    future_status.set_result(status)
    manager = mock_manager()
    manager.http_client.status = Mock(return_value=future_status)
    manager.state.game_status = status
    manager.state.koline = None
    return koline, manager


def mock_game_status(level_id, is_spoiler, is_solved):
    spoiler = Spoiler('Spoiler', '1' if is_solved else '0', 0, 1)
    spoiler.is_solved = Mock(return_value=is_solved)
    spoilers = [spoiler] if is_spoiler else []
    level_status = Mock(LevelStatus)
    level_status.spoilers = spoilers
    level_status.levelNumber = level_id
    game_status = Mock(Status)
    game_status.current_level = level_status
    game_status.get_spoiler_or_none = Mock(return_value=spoiler if is_spoiler else None)
    return game_status


def mock_message(text='mocked message'):
    message_mock = Mock(types.Message)
    message_mock.text = text
    return message_mock


def get_pin_message_to_mock_tip_for_manager_with_ko(koline: Koline = None, manager: Manager = None):
    if not manager:
        manager = mock_manager()
    if koline:
        manager.state.koline = koline
    else:
        manager.state.koline = KOLINE_DEFAULT_PARSED
    koline = manager.state.koline
    if 0 == len(koline.sectors):
        raise Exception("Mocking of tip for empty koline is not supported")
    tip_text = f'/tip all\n'
    all_tips = []
    for sector in koline.sectors:
        all_tips.append('\n'.join([f'tip: {code_id}' for code_id in range(len(sector.codes))]))
    message = mock_message(tip_text + '***'.join(all_tips))
    return message


def mock_status(koline: str = None, tm: int = None, levelNumber: int = None):
    """Mocks game status for testing purposes.

    :param koline: Koline in string representation
    :param tm: TM value
    :param levelNumber: Level number
    :return: Mocked game status object.

    Example:
    """
    status_mock = Mock(Status)
    status_mock.current_level.koline = koline if koline else KOLINE_DEFAULT
    status_mock.current_level.tm = tm if tm else TM_DEFAULT
    status_mock.current_level.levelNumber = levelNumber if levelNumber else 1
    return status_mock
