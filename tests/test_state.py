import pytest
from pewpewbot.State import State

def test_setters():
    state = State()
    
    # Test bool setters
    state.parse_on = True
    assert state.parse_on == True
    state.parse_on = "off"
    assert state.parse_on == False
    state.parse_on = "on"
    assert state.parse_on == True
    state.parse_on = "False"
    assert state.parse_on == False
    state.parse_on = 1
    assert state.parse_on == True
    state.parse_on = 0
    assert state.parse_on == False
    with pytest.raises(ValueError):
        state.parse_on = "kek"

    # Test wrong type
    with pytest.raises(ValueError):
        state.screenshot_url = 1