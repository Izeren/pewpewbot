import unittest

from unittest.mock import Mock, patch, call
from logging import Logger

from State import State
from client import Client
from pewpewbot.commands_processing import update_level_status
from manager import Manager
from models import Status, Spoiler, LevelStatus, Koline
from queue_bot import QueueBot
from screenshot import Screenshoter


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


screenshoter_mock = Mock(Screenshoter)
http_client_mock = Mock(Client)

bot_mock = Mock(QueueBot)
logger_mock = Mock(Logger)
state_mock = Mock(State)
manager_mock = Manager(state_mock, http_client_mock, screenshoter_mock, bot_mock, logger_mock)


class OnLevelSpoilerTests(unittest.IsolatedAsyncioTestCase):

    @patch('pewpewbot.model_parsing_utils.parse_koline_from_string', return_value=Mock(Koline))
    @patch('pewpewbot.utils.notify_all_channels')
    async def test_not_up_then_not_up(self, notify_mock, parse_mock):
        # given
        game_status_l1_not_up = mock_game_status(1, True, False)
        manager_mock.state.game_status = game_status_l1_not_up

        # when
        await update_level_status(manager_mock.bot, manager_mock, **{'game_status': game_status_l1_not_up})

        # then
        parse_mock.assert_called_once()
        game_status_l1_not_up.get_spoiler_or_none.assert_has_calls([call(), call()])
        game_status_l1_not_up.current_level.spoilers[0].is_solved.assert_has_calls([call(), call()])
        notify_mock.assert_not_called()

    # Order of patches has to be opposite to the order of mocks passed through the argument
    @patch('pewpewbot.model_parsing_utils.parse_koline_from_string', return_value=Mock(Koline))
    @patch('pewpewbot.utils.notify_all_channels')
    async def test_not_up_then_up(self, notify_mock, parse_mock):
        # given
        game_status_l1_not_up = mock_game_status(1, True, False)
        game_status_l1_up = mock_game_status(1, True, True)
        manager_mock.state.game_status = game_status_l1_not_up

        # when
        await update_level_status(manager_mock.bot, manager_mock, **{'game_status': game_status_l1_up})

        # then
        game_status_l1_not_up.get_spoiler_or_none.assert_called_once_with()
        game_status_l1_up.get_spoiler_or_none.assert_called_once_with()
        game_status_l1_not_up.current_level.spoilers[0].is_solved.called_once_with()
        game_status_l1_up.current_level.spoilers[0].is_solved.called_once_with()
        parse_mock.assert_called_once()
        notify_mock.assert_called_once_with(manager_mock, "Спойлер ап:\n" +
                                            game_status_l1_up.current_level.spoilers[0].spoilerText)

    @patch('pewpewbot.model_parsing_utils.parse_koline_from_string', return_value=Mock(Koline))
    @patch('pewpewbot.utils.notify_all_channels')
    async def test_up_then_not_up(self, notify_mock, parse_mock):
        # given
        game_status_l1_up = mock_game_status(1, True, True)
        game_status_l1_not_up = mock_game_status(1, True, False)
        manager_mock.state.game_status = game_status_l1_up

        # when
        await update_level_status(manager_mock.bot, manager_mock, **{'game_status': game_status_l1_not_up})

        # then
        game_status_l1_not_up.get_spoiler_or_none.assert_called_once_with()
        game_status_l1_up.get_spoiler_or_none.assert_called_once_with()
        game_status_l1_not_up.current_level.spoilers[0].is_solved.called_once_with()
        game_status_l1_up.current_level.spoilers[0].is_solved.called_once_with()
        parse_mock.assert_called_once()
        notify_mock.assert_not_called()


class OnLevelUpSpoilerTests(unittest.IsolatedAsyncioTestCase):

    @patch('pewpewbot.model_parsing_utils.parse_koline_from_string', return_value=Mock(Koline))
    @patch('pewpewbot.commands_processing.process_next_level')
    async def test_not_up_then_no_spoiler(self, next_level_mock, parse_mock):
        # given
        game_status_l1_not_up = mock_game_status(1, True, False)
        game_status_l2_no_spoiler = mock_game_status(2, False, False)
        manager_mock.state.game_status = game_status_l1_not_up

        # when
        await update_level_status(manager_mock.bot, manager_mock, **{'game_status': game_status_l2_no_spoiler})

        # then
        game_status_l1_not_up.get_spoiler_or_none.assert_not_called()
        game_status_l2_no_spoiler.get_spoiler_or_none.assert_not_called()
        game_status_l1_not_up.current_level.spoilers[0].is_solved.assert_not_called()
        parse_mock.assert_called_once()
        next_level_mock.assert_called_once_with(game_status_l2_no_spoiler, manager_mock, silent=False)

    @patch('pewpewbot.model_parsing_utils.parse_koline_from_string', return_value=Mock(Koline))
    @patch('pewpewbot.commands_processing.process_next_level')
    async def test_up_then_no_spoiler(self, next_level_mock, parse_mock):
        # given
        game_status_l1_up = mock_game_status(1, True, True)
        game_status_l2_no_spoiler = mock_game_status(2, False, False)
        manager_mock.state.game_status = game_status_l1_up

        # when
        await update_level_status(manager_mock.bot, manager_mock, **{'game_status': game_status_l2_no_spoiler})

        # then
        game_status_l1_up.get_spoiler_or_none.assert_not_called()
        game_status_l2_no_spoiler.get_spoiler_or_none.assert_not_called()
        game_status_l1_up.current_level.spoilers[0].is_solved.assert_not_called()
        parse_mock.assert_called_once()
        next_level_mock.assert_called_once_with(game_status_l2_no_spoiler, manager_mock, silent=False)


if __name__ == '__main__':
    unittest.main()
