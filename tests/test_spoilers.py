import pytest

from mock import call, Mock
from pytest_mock import MockerFixture


from pewpewbot.commands_processing import update_level_status
from pewpewbot.models import Koline
from tests.mock_utils import mock_manager, mock_game_status


def mock_koline_parser(mocker: MockerFixture):
    return mocker.patch('pewpewbot.model_parsing_utils.parse_koline_from_string', return_value=Mock(Koline))


def mock_channel_notifier(mocker: MockerFixture):
    return mocker.patch('pewpewbot.utils.notify_all_channels')


def mock_process_next_level(mocker: MockerFixture):
    return mocker.patch('pewpewbot.commands_processing.process_next_level')


@pytest.mark.asyncio
async def test_not_up_then_not_up(mocker: MockerFixture):
    # given
    game_status_l1_not_up = mock_game_status(1, True, False)
    manager_mock = mock_manager()
    manager_mock.state.game_status = game_status_l1_not_up
    parse_mock = mock_koline_parser(mocker)
    notify_mock = mock_channel_notifier(mocker)

    # when
    await update_level_status(manager_mock.bot, manager_mock, **{'game_status': game_status_l1_not_up})

    # then
    parse_mock.assert_called_once()
    game_status_l1_not_up.get_spoiler_or_none.assert_has_calls([call(), call()])
    game_status_l1_not_up.current_level.spoilers[0].is_solved.assert_has_calls([call(), call()])
    notify_mock.assert_not_called()


@pytest.mark.asyncio
async def test_not_up_then_up(mocker: MockerFixture):
    # given
    game_status_l1_not_up = mock_game_status(1, True, False)
    game_status_l1_up = mock_game_status(1, True, True)
    manager_mock = mock_manager()
    manager_mock.state.game_status = game_status_l1_not_up
    parse_mock = mock_koline_parser(mocker)
    notify_mock = mock_channel_notifier(mocker)

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


@pytest.mark.asyncio
async def test_up_then_not_up(mocker: MockerFixture):
    # given
    game_status_l1_up = mock_game_status(1, True, True)
    game_status_l1_not_up = mock_game_status(1, True, False)
    manager_mock = mock_manager()
    manager_mock.state.game_status = game_status_l1_up
    parse_mock = mock_koline_parser(mocker)
    notify_mock = mock_channel_notifier(mocker)

    # when
    await update_level_status(manager_mock.bot, manager_mock, **{'game_status': game_status_l1_not_up})

    # then
    game_status_l1_not_up.get_spoiler_or_none.assert_called_once_with()
    game_status_l1_up.get_spoiler_or_none.assert_called_once_with()
    game_status_l1_not_up.current_level.spoilers[0].is_solved.called_once_with()
    game_status_l1_up.current_level.spoilers[0].is_solved.called_once_with()
    parse_mock.assert_called_once()
    notify_mock.assert_not_called()


@pytest.mark.asyncio
async def test_not_up_then_no_spoiler(mocker: MockerFixture):
    # given
    game_status_l1_not_up = mock_game_status(1, True, False)
    game_status_l2_no_spoiler = mock_game_status(2, False, False)
    manager_mock = mock_manager()
    manager_mock.state.game_status = game_status_l1_not_up
    parse_mock = mock_koline_parser(mocker)
    next_level_mock = mock_process_next_level(mocker)

    # when
    await update_level_status(manager_mock.bot, manager_mock, **{'game_status': game_status_l2_no_spoiler})

    # then
    game_status_l1_not_up.get_spoiler_or_none.assert_not_called()
    game_status_l2_no_spoiler.get_spoiler_or_none.assert_not_called()
    game_status_l1_not_up.current_level.spoilers[0].is_solved.assert_not_called()
    parse_mock.assert_called_once()
    next_level_mock.assert_called_once_with(game_status_l2_no_spoiler, manager_mock, silent=False)


@pytest.mark.asyncio
async def test_up_then_no_spoiler(mocker: MockerFixture):
    # given
    game_status_l1_up = mock_game_status(1, True, True)
    game_status_l2_no_spoiler = mock_game_status(2, False, False)
    manager_mock = mock_manager()
    manager_mock.state.game_status = game_status_l1_up
    next_level_mock = mock_process_next_level(mocker)
    parse_mock = mock_koline_parser(mocker)

    # when
    await update_level_status(manager_mock.bot, manager_mock, **{'game_status': game_status_l2_no_spoiler})

    # then
    game_status_l1_up.get_spoiler_or_none.assert_not_called()
    game_status_l2_no_spoiler.get_spoiler_or_none.assert_not_called()
    game_status_l1_up.current_level.spoilers[0].is_solved.assert_not_called()
    parse_mock.assert_called_once()
    next_level_mock.assert_called_once_with(game_status_l2_no_spoiler, manager_mock, silent=False)
