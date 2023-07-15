import pytest
from pewpewbot.state import State

MULTI_SECTOR_TIP = """
tip1 
tip2
***
tip3
"""

SINGLE_SECTOR_TIP = """
tip1
tip2
"""


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


# Test tip setter and clean on level up
def test_set_tip_all_sectors():
    state = State()
    state.set_tip_all_sectors(MULTI_SECTOR_TIP)
    assert state.tip == [['tip1', 'tip2'], ['tip3']]


def test_set_tip_single_sector():
    state = State()
    state.tip = [[]]
    state.set_tip_for_sector(SINGLE_SECTOR_TIP, 0)
    assert state.tip == [['tip1', 'tip2']]
