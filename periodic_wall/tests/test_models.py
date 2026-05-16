"""M-* scenarios."""

import dataclasses

from game.models import Command, GameEvent, GameEventType, GameState, PlayerInput


def test_m01_new_lab():
    s = GameState.new_lab(800, 500, rng_seed=42)
    assert s.level == 1
    assert s.hearts == 5
    assert s.time_left == 300.0
    assert s.room_w == 800


def test_m02_copy_roundtrip():
    s = GameState.new_lab(640, 400, 7)
    s.hearts = 3
    from game.models import Ball

    s.balls.append(Ball(1, 2, 0, 3, 10, "H", "#fff", 1))
    c = s.copy()
    c.hearts = 1
    assert s.hearts == 3
    assert len(c.balls) == 1


def test_m03_jump_one_frame():
    inp = PlayerInput(jump_pressed=True)
    assert inp.jump_pressed is True


def test_m04_events():
    ev = GameEvent(GameEventType.HIT, {"amount": 1})
    assert ev.type == GameEventType.HIT


def test_m05_no_forbidden_fields():
    fields = {f.name for f in dataclasses.fields(GameState)}
    for bad in ("giant_ball", "shockwaves", "lava_surface_y"):
        assert bad not in fields
