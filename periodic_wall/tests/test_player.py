"""P-* scenarios."""

from game.models import PlayerInput, PlayerState
from game.player import floor_y, step_player

DT = 1.0 / 60.0
W, H = 800.0, 500.0
FY = floor_y(H)


def test_p01_idle_on_floor():
    p = PlayerState(px=400, py=FY)
    np, _, _ = step_player(p, PlayerInput(), DT, W, H)
    assert abs(np.px - 400) < 0.01
    assert np.py == FY


def test_p02_move_right():
    p = PlayerState(px=400, py=FY)
    for _ in range(10):
        p, _, _ = step_player(p, PlayerInput(keys_held=frozenset(["Right"])), DT, W, H)
    assert p.px > 400


def test_p03_move_left():
    p = PlayerState(px=400, py=FY)
    for _ in range(10):
        p, _, _ = step_player(p, PlayerInput(keys_held=frozenset(["Left"])), DT, W, H)
    assert p.px < 400


def test_p04_jump():
    p = PlayerState(px=400, py=FY)
    p, _, _ = step_player(p, PlayerInput(jump_pressed=True), DT, W, H)
    assert p.vy < 0


def test_p05_air_jump():
    p = PlayerState(px=400, py=FY - 80, vy=-100)
    p, _, _ = step_player(p, PlayerInput(jump_pressed=True), DT, W, H)
    assert p.vy < 0


def test_p06_land_after_fall():
    p = PlayerState(px=400, py=FY - 100, vy=0)
    for _ in range(80):
        p, _, _ = step_player(p, PlayerInput(), DT, W, H)
    assert abs(p.py - FY) < 2
    assert p.vy == 0.0


def test_p07_duck_hitbox_smaller():
    p = PlayerState(px=400, py=FY)
    _, hb_stand, duck = step_player(p, PlayerInput(), DT, W, H)
    _, hb_duck, duck2 = step_player(
        p, PlayerInput(keys_held=frozenset(["s"])), DT, W, H
    )
    assert duck2
    assert hb_duck.r < hb_stand.r


def test_p08_right_wall():
    p = PlayerState(px=400, py=FY)
    for _ in range(200):
        p, _, _ = step_player(p, PlayerInput(keys_held=frozenset(["d"])), DT, W, H)
    assert p.px <= W - 28.0 + 0.01


def test_p09_fast_fall():
    p = PlayerState(px=400, py=FY - 120, vy=0)
    _, _, _ = step_player(p, PlayerInput(keys_held=frozenset(["s"])), DT, W, H)
    p_slow, _, _ = step_player(p, PlayerInput(), DT, W, H)
    p_fast, _, _ = step_player(
        PlayerState(px=400, py=FY - 120, vy=0),
        PlayerInput(keys_held=frozenset(["s"])),
        DT,
        W,
        H,
    )
    assert p_fast.vy > p_slow.vy
