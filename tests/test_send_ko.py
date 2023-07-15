from asyncio import Future

import pytest
from mock import Mock, call
from pytest_mock import MockerFixture

from pewpewbot.model_parsing_utils import parse_koline_from_string
from pewpewbot.commands_processing import send_ko, process_tip
from tests.mock_utils import mock_manager, get_pin_message_to_mock_tip_for_manager_with_ko, mock_message, \
    KOLINE_DEFAULT_PARSED, KOLINE_MULTISECTOR_BONUS_CODE_UP


@pytest.mark.asyncio
async def test_with_caption_no_tip(mocker: MockerFixture):
    # given
    message_mock = mock_message('/ko')
    manager_mock = mock_manager(KOLINE_DEFAULT_PARSED)
    full_view_mock = mocker.patch('pewpewbot.views.sector_default_ko_message', return_value='mocked_view')

    # when
    await send_ko(message_mock, manager_mock, **{'command_name': 'ko', 'ko_caption': 'mocked_caption\n'})

    # then
    full_view_mock.assert_called_once_with(manager_mock.state.koline.sectors[0])
    message_mock.reply.assert_called_once_with('mocked_caption\nmocked_view\n', parse_mode='Markdown')


@pytest.mark.asyncio
async def test_with_caption_with_tip(mocker: MockerFixture):
    # given
    message_mock = mock_message('/ko')
    manager_mock = mock_manager()
    pin_message_mock = get_pin_message_to_mock_tip_for_manager_with_ko(manager=manager_mock)
    future_koline = Future()
    future_koline.set_result(manager_mock.state.koline)
    manager_mock.get_or_load_and_parse_koline = Mock(return_value=future_koline)
    full_view_mock = mocker.patch('pewpewbot.views.sector_with_tips_ko_message', return_value='mocked_view')

    # when
    await process_tip(pin_message_mock, manager_mock, **{'command_name': 'tip'})
    await send_ko(message_mock, manager_mock, **{'command_name': 'ko', 'ko_caption': 'mocked_caption\n'})

    # then
    full_view_mock.assert_called_once_with(manager_mock.state.koline.sectors[0], manager_mock.state.tip[0])
    message_mock.reply.assert_called_once_with('mocked_caption\nmocked_view\n', parse_mode='Markdown')


@pytest.mark.asyncio
async def test_no_caption_no_tip(mocker: MockerFixture):
    # given
    message_mock = mock_message('/ko')
    manager_mock = mock_manager(KOLINE_DEFAULT_PARSED)
    full_view_mock = mocker.patch('pewpewbot.views.sector_default_ko_message', return_value='mocked_view')

    # when
    await send_ko(message_mock, manager_mock, **{'command_name': 'ko'})

    # then
    full_view_mock.assert_called_once_with(manager_mock.state.koline.sectors[0])
    message_mock.reply.assert_called_once_with('mocked_view\n', parse_mode='Markdown')


@pytest.mark.asyncio
async def test_no_caption_with_tip(mocker: MockerFixture):
    # given
    message_mock = mock_message('/ko')
    manager_mock = mock_manager()
    pin_message_mock = get_pin_message_to_mock_tip_for_manager_with_ko(manager=manager_mock)
    future_koline = Future()
    future_koline.set_result(manager_mock.state.koline)
    manager_mock.get_or_load_and_parse_koline = Mock(return_value=future_koline)
    full_view_mock = mocker.patch('pewpewbot.views.sector_with_tips_ko_message', return_value='mocked_view')

    # when
    await process_tip(pin_message_mock, manager_mock, **{'command_name': 'tip'})
    await send_ko(message_mock, manager_mock, **{'command_name': 'ko'})

    # then
    full_view_mock.assert_called_once_with(manager_mock.state.koline.sectors[0], manager_mock.state.tip[0])
    message_mock.reply.assert_called_once_with('mocked_view\n', parse_mode='Markdown')


@pytest.mark.asyncio
async def test_with_caption_with_tip_multi_sector(mocker: MockerFixture):
    # given
    message_mock = mock_message('/ko')
    manager_mock = mock_manager()
    pin_message_mock = get_pin_message_to_mock_tip_for_manager_with_ko(
        koline=parse_koline_from_string(KOLINE_MULTISECTOR_BONUS_CODE_UP),
        manager=manager_mock
    )
    future_koline = Future()
    future_koline.set_result(manager_mock.state.koline)
    manager_mock.get_or_load_and_parse_koline = Mock(return_value=future_koline)
    full_view_mock = mocker.patch('pewpewbot.views.sector_with_tips_ko_message', return_value='mocked_view')

    # when
    await process_tip(pin_message_mock, manager_mock, **{'command_name': 'tip'})
    await send_ko(message_mock, manager_mock, **{'command_name': 'ko', 'ko_caption': 'mocked_caption\n'})

    # then
    full_view_mock.has_calls([
        call(manager_mock.state.koline.sectors[0], manager_mock.state.tip[0]),
        call(manager_mock.state.koline.sectors[1], manager_mock.state.tip[1]),
    ])
    message_mock.reply.assert_called_once_with('mocked_caption\nmocked_view\nmocked_view\n', parse_mode='Markdown')


@pytest.mark.asyncio
async def test_no_caption_with_tip_multi_sector(mocker: MockerFixture):
    # given
    message_mock = mock_message('/ko')
    manager_mock = mock_manager()
    pin_message_mock = get_pin_message_to_mock_tip_for_manager_with_ko(
        koline=parse_koline_from_string(KOLINE_MULTISECTOR_BONUS_CODE_UP),
        manager=manager_mock
    )
    future_koline = Future()
    future_koline.set_result(manager_mock.state.koline)
    manager_mock.get_or_load_and_parse_koline = Mock(return_value=future_koline)
    full_view_mock = mocker.patch('pewpewbot.views.sector_with_tips_ko_message', return_value='mocked_view')

    # when
    await process_tip(pin_message_mock, manager_mock, **{'command_name': 'tip'})
    await send_ko(message_mock, manager_mock, **{'command_name': 'ko'})

    # then
    full_view_mock.has_calls([
        call(manager_mock.state.koline.sectors[0], manager_mock.state.tip[0]),
        call(manager_mock.state.koline.sectors[1], manager_mock.state.tip[1]),
    ])
    message_mock.reply.assert_called_once_with('mocked_view\nmocked_view\n', parse_mode='Markdown')


@pytest.mark.asyncio
async def test_with_caption_no_tip_multi_sector(mocker: MockerFixture):
    # given
    message_mock = mock_message('/ko')
    manager_mock = mock_manager(parse_koline_from_string(KOLINE_MULTISECTOR_BONUS_CODE_UP))
    future_koline = Future()
    future_koline.set_result(manager_mock.state.koline)
    manager_mock.get_or_load_and_parse_koline = Mock(return_value=future_koline)
    full_view_mock = mocker.patch('pewpewbot.views.sector_default_ko_message', return_value='mocked_view')

    # when
    await send_ko(message_mock, manager_mock, **{'command_name': 'ko', 'ko_caption': 'mocked_caption\n'})

    # then
    full_view_mock.has_calls([
        call(manager_mock.state.koline.sectors[0]),
        call(manager_mock.state.koline.sectors[1]),
    ])
    message_mock.reply.assert_called_once_with('mocked_caption\nmocked_view\nmocked_view\n', parse_mode='Markdown')


@pytest.mark.asyncio
async def test_no_caption_no_tip_multi_sector(mocker: MockerFixture):
    # given
    message_mock = mock_message('/ko')
    manager_mock = mock_manager(parse_koline_from_string(KOLINE_MULTISECTOR_BONUS_CODE_UP))
    future_koline = Future()
    future_koline.set_result(manager_mock.state.koline)
    manager_mock.get_or_load_and_parse_koline = Mock(return_value=future_koline)
    full_view_mock = mocker.patch('pewpewbot.views.sector_default_ko_message', return_value='mocked_view')

    # when
    await send_ko(message_mock, manager_mock, **{'command_name': 'ko'})

    # then
    full_view_mock.has_calls([
        call(manager_mock.state.koline.sectors[0]),
        call(manager_mock.state.koline.sectors[1]),
    ])
    message_mock.reply.assert_called_once_with('mocked_view\nmocked_view\n', parse_mode='Markdown')
