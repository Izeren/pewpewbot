from pewpewbot.model_parsing_utils import parse_codes_up
from tests.mock_utils import mock_manager, KOLINE_DEFAULT_PARSED


def test_parse_codes_up():
    manager = mock_manager(koline=KOLINE_DEFAULT_PARSED)
    codes_left_to_up = parse_codes_up(manager.state.game_status.current_level.question)
    assert codes_left_to_up == 12
