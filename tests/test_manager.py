import pytest

from asyncio import Future
from pytest_mock import MockerFixture

from pewpewbot.State import State
from pewpewbot.models import Status, LevelStatus
from pewpewbot.client import Client
from pewpewbot.manager import Manager
from pewpewbot.model_parsing_utils import parse_koline_from_string


def mock_manager(mocker: MockerFixture):
    future_status = Future()
    koline = parse_koline_from_string('')
    status = mocker.MagicMock(Status)
    status.current_level = mocker.Mock(LevelStatus)
    status.current_level.koline = ''
    future_status.set_result(status)
    client = mocker.Mock(Client)
    client.status = mocker.Mock(return_value=future_status)
    state = State()
    state.game_status = status
    manager = Manager(state, client, None, None, None)
    manager.state.koline = None
    return koline, manager


@pytest.mark.asyncio
async def test_get_or_load_and_parse_koline(mocker: MockerFixture):
    # given
    koline, manager = mock_manager(mocker)

    # when
    returned_koline = await manager.get_or_load_and_parse_koline()

    # then
    assert manager.state.koline == koline
    assert returned_koline == koline
    manager.http_client.status.assert_called_once_with()


@pytest.mark.asyncio
async def test_load_and_parse_koline(mocker: MockerFixture):
    # given
    koline, manager = mock_manager(mocker)

    # when
    returned_koline = await manager.load_and_parse_koline()

    # then
    assert manager.state.koline == koline
    assert returned_koline == koline
    manager.http_client.status.assert_called_once_with()


@pytest.mark.asyncio
async def test_get_or_load_and_parse_koline_not_empty(mocker: MockerFixture):
    # given
    koline, manager = mock_manager(mocker)
    manager.state.koline = koline

    # when
    await manager.get_or_load_and_parse_koline()

    # then
    assert manager.state.koline == koline
    manager.http_client.status.assert_not_called()
