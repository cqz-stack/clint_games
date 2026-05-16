"""F-* scenarios."""

from game.models import Command, GameEvent, GameEventType, Screen
from game.screen_flow import FlowState, reduce_flow


def test_f01_start_title():
    f = FlowState()
    assert f.screen == Screen.TITLE


def test_f02_play_goes_lab():
    f = FlowState()
    reduce_flow(f, Command.PLAY, room_w=800, room_h=500, rng_seed=1)
    assert f.screen == Screen.LAB
    assert f.game is not None
    assert f.game.level == 1


def test_f03_forfeit_title():
    f = FlowState()
    reduce_flow(f, Command.PLAY, room_w=800, room_h=500)
    reduce_flow(f, Command.FORFEIT)
    assert f.screen == Screen.TITLE
    assert f.game is None


def test_f04_win_end():
    f = FlowState()
    reduce_flow(f, Command.PLAY, room_w=800, room_h=500)
    reduce_flow(f, events=[GameEvent(GameEventType.WON)])
    assert f.screen == Screen.END_WIN


def test_f05_die_end():
    f = FlowState()
    reduce_flow(f, Command.PLAY, room_w=800, room_h=500)
    reduce_flow(f, events=[GameEvent(GameEventType.DIED)])
    assert f.screen == Screen.END_LOSE


def test_f06_play_again():
    f = FlowState()
    reduce_flow(f, Command.PLAY, room_w=800, room_h=500, rng_seed=1)
    reduce_flow(f, events=[GameEvent(GameEventType.WON)])
    reduce_flow(f, Command.PLAY_AGAIN, room_w=800, room_h=500, rng_seed=2)
    assert f.screen == Screen.LAB
    assert f.game.hearts == 5


def test_f07_reject_level2():
    f = FlowState()
    reduce_flow(f, Command.PICK_LEVEL_2)
    assert f.screen == Screen.TITLE


def test_f08_reject_nuke():
    f = FlowState()
    reduce_flow(f, Command.START_NUKE)
    assert f.screen == Screen.TITLE
