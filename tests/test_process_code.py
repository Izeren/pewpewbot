from asyncio import Future

import pytest
from mock import call, Mock
from pytest_mock import MockerFixture

from tests.mock_utils import mock_message, mock_manager, DR_CODE, KOLINE_UP_1_CODE_LABEL_3, KOLINE_DEFAULT_PARSED, \
    mock_status, TM_DEFAULT, KOLINE_DEFAULT, LABEL_UP_DEFAULT, KO_DEFAULT
from pewpewbot.models import CodeResult, CodeVerdict, Status
from pewpewbot.commands_processing import process_code
from pewpewbot.views import try_send_code_view, code_update_view, code_verdict_view


# Given default
def mock_default(old_status: Status = None, new_status: Status = None):
    if not old_status:
        old_status = mock_status()
    message_mock = mock_message(DR_CODE)
    manager_mock = mock_manager(game_status=old_status)
    manager_mock.state.type_on = True
    code_verdict = CodeVerdict(55)
    future_status = Future()
    if not new_status:
        new_status = old_status
    future_status.set_result(new_status)
    manager_mock.http_client.post_code = Mock()
    manager_mock.http_client.status = Mock(return_value=future_status)
    verdict_message = code_verdict_view(code_verdict.value, DR_CODE)
    expected_caption = code_update_view(verdict_message, TM_DEFAULT, LABEL_UP_DEFAULT, KO_DEFAULT)
    return message_mock, manager_mock, code_verdict, expected_caption


@pytest.mark.asyncio
async def test_code_when_type_off(mocker: MockerFixture):
    # given
    message_mock, manager_mock, _, _ = mock_default()
    manager_mock.state.type_on = False
    get_code_mock = mocker.patch('pewpewbot.commands_processing.get_forced_code_text_from_message_or_reply',
                                 return_value=DR_CODE)

    # when
    await process_code(message_mock, manager_mock)

    # then
    message_mock.reply.assert_not_called()
    manager_mock.http_client.post_code.assert_not_called()
    get_code_mock.assert_not_called()


@pytest.mark.asyncio
async def test_code_with_unknown_verdict(mocker: MockerFixture):
    # given
    message_mock, manager_mock, _, _ = mock_default()
    code_result_test = CodeResult(100500, 'Unknown verdict')
    future_code_result = Future()
    future_code_result.set_result(code_result_test)
    manager_mock.http_client.post_code = mocker.Mock(return_value=future_code_result)

    # when
    await process_code(message_mock, manager_mock)

    # then
    manager_mock.http_client.post_code.assert_called_once_with(DR_CODE)
    message_mock.reply.assert_has_calls([
        call(try_send_code_view(DR_CODE), parse_mode='Markdown'),
        call(code_result_test.comment)])


@pytest.mark.asyncio
async def test_code_with_forced_verdict(mocker: MockerFixture):
    # given
    old_status = mock_status(KOLINE_DEFAULT, TM_DEFAULT, 1)
    new_status = mock_status(KOLINE_UP_1_CODE_LABEL_3, TM_DEFAULT, 1)
    message_mock, manager_mock, code_verdict, expected_caption = mock_default(old_status, new_status)
    notify_mock = mocker.patch('pewpewbot.utils.notify_all_channels')
    update_level_mock = mocker.patch('pewpewbot.commands_processing.update_level_status')
    send_ko_mock = mocker.patch('pewpewbot.commands_processing.send_ko')

    # when
    await process_code(message_mock, manager_mock, **{'forced_code_verdict': code_verdict})

    # then
    manager_mock.http_client.post_code.assert_not_called()
    notify_mock.assert_not_called()
    update_level_mock.assert_not_called()
    send_ko_mock.assert_called_once_with(
        message_mock,
        manager_mock,
        **{'forced_code_verdict': code_verdict, 'ko_caption': expected_caption}
    )
    message_mock.reply.assert_called_once_with(try_send_code_view(DR_CODE), parse_mode='Markdown')


@pytest.mark.asyncio
async def test_code_with_bad_verdict(mocker: MockerFixture):
    # given
    message_mock, manager_mock, _,  _ = mock_default()
    code_verdict = CodeVerdict(11)
    verdict_message = code_verdict_view(code_verdict.value, DR_CODE)
    notify_mock = mocker.patch('pewpewbot.utils.notify_all_channels')
    update_level_mock = mocker.patch('pewpewbot.commands_processing.update_level_status')
    send_ko_mock = mocker.patch('pewpewbot.commands_processing.send_ko')

    # when
    await process_code(message_mock, manager_mock, **{'forced_code_verdict': code_verdict})

    # then
    manager_mock.http_client.post_code.assert_not_called()
    notify_mock.assert_not_called()
    update_level_mock.assert_not_called()
    send_ko_mock.assert_not_called()
    message_mock.reply.assert_has_calls([
        call(try_send_code_view(DR_CODE), parse_mode='Markdown'),
        call(verdict_message, parse_mode='Markdown')
    ])


@pytest.mark.asyncio
async def test_code_with_last_code_on_level_verdict(mocker: MockerFixture):
    # given
    old_status = mock_status()
    new_status = mock_status(levelNumber=2)
    message_mock, manager_mock, _, _ = mock_default(old_status=old_status, new_status=new_status)
    code_verdict = CodeVerdict(9)
    verdict_message = code_verdict_view(code_verdict.value, DR_CODE)
    notify_mock = mocker.patch('pewpewbot.utils.notify_all_channels')
    update_level_mock = mocker.patch('pewpewbot.commands_processing.update_level_status')
    send_ko_mock = mocker.patch('pewpewbot.commands_processing.send_ko')

    # when
    await process_code(message_mock, manager_mock, **{'forced_code_verdict': code_verdict})

    # then
    manager_mock.http_client.post_code.assert_not_called()
    notify_mock.assert_called_once_with(manager_mock, verdict_message)
    update_level_mock.assert_called_once_with(manager_mock.bot, manager_mock, **{'forced_code_verdict': code_verdict})
    send_ko_mock.assert_not_called()
    message_mock.reply.assert_called_once_with(try_send_code_view(DR_CODE), parse_mode='Markdown')
