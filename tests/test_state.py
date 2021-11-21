import pytest
from pewpewbot.state import State


def test_setters():
    state = State()
    
    # Test bool setters
    state.parse_on = True
    assert state.parse_on is True
    state.parse_on = "off"
    assert state.parse_on is False
    state.parse_on = "on"
    assert state.parse_on is True
    state.parse_on = "False"
    assert state.parse_on is False
    state.parse_on = 1
    assert state.parse_on is True
    state.parse_on = 0
    assert state.parse_on is False
    with pytest.raises(ValueError):
        state.parse_on = "kek"

    # Test wrong type
    with pytest.raises(ValueError):
        state.screenshot_url = 1