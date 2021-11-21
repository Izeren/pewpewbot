import pytest

from pytest_mock import MockerFixture

from tests.mock_utils import mock_manager_with_future_koline


@pytest.mark.asyncio
async def test_get_or_load_and_parse_koline():
    # given
    koline, manager = mock_manager_with_future_koline()

    # when
    returned_koline = await manager.get_or_load_and_parse_koline()

    # then
    assert manager.state.koline == koline
    assert returned_koline == koline
    manager.http_client.status.assert_called_once_with()


@pytest.mark.asyncio
async def test_load_and_parse_koline():
    # given
    koline, manager = mock_manager_with_future_koline()

    # when
    returned_koline = await manager.load_and_parse_koline()

    # then
    assert manager.state.koline == koline
    assert returned_koline == koline
    manager.http_client.status.assert_called_once_with()


@pytest.mark.asyncio
async def test_get_or_load_and_parse_koline_not_empty():
    # given
    koline, manager = mock_manager_with_future_koline()
    manager.state.koline = koline

    # when
    await manager.get_or_load_and_parse_koline()

    # then
    assert manager.state.koline == koline
    manager.http_client.status.assert_not_called()
