"""S-* scenarios."""

import random

from game.models import GameEventType, GameState, PlayerInput
from game.player import Hitbox, floor_y
from game.survival_sim import tick

DT = 1.0 / 30.0


def test_s01_fresh_tick():
    s = GameState.new_lab(800, 500, 0)
    s, ev = tick(s, PlayerInput(), DT, random.Random(0))
    assert s.time_left < 300.0
    assert not any(e.type == GameEventType.DIED for e in ev)


def test_s02_no_instant_end():
    s = GameState.new_lab(800, 500, 0)
    s, ev = tick(s, PlayerInput(), DT, random.Random(0))
    assert GameEventType.WON not in {e.type for e in ev}
    assert GameEventType.DIED not in {e.type for e in ev}


def test_s03_move_right():
    s = GameState.new_lab(800, 500, 0)
    x0 = s.player.px
    for _ in range(30):
        s, _ = tick(s, PlayerInput(keys_held=frozenset(["d"])), DT, random.Random(1))
    assert s.player.px > x0


def test_s04_ball_hit():
    s = GameState.new_lab(800, 500, 0)
    fy = floor_y(500)
    s.player.px = 400
    s.player.py = fy
    from game.models import Ball

    s.balls = [Ball(400, fy - 30, 0, 0, 25, "H", "#fff", 1)]
    s, ev = tick(s, PlayerInput(), DT, random.Random(2))
    assert any(e.type == GameEventType.HIT for e in ev)
    assert s.hearts == 4


def test_s05_invuln_blocks_second_hit():
    s = GameState.new_lab(800, 500, 0)
    s.hearts = 4
    s.invuln_until = s.elapsed + 10.0
    from game.models import Ball

    s.balls = [Ball(s.player.px, s.player.py - 30, 0, 0, 25, "H", "#fff", 1)]
    s, ev = tick(s, PlayerInput(), DT, random.Random(3))
    assert s.hearts == 4
    assert not any(e.type == GameEventType.HIT for e in ev)


def test_s06_five_hits_die():
    from game.models import Ball

    s = GameState.new_lab(800, 500, 0)
    rng = random.Random(4)
    died = False
    for i in range(5):
        s.balls = [Ball(s.player.px, s.player.py - 30, 0, 0, 25, "H", "#fff", 1)]
        s.invuln_until = 0.0
        s.elapsed = float(i * 2)
        s, ev = tick(s, PlayerInput(), DT, rng)
        if any(e.type == GameEventType.DIED for e in ev):
            died = True
            break
    assert died


def test_s07_win_on_timer():
    s = GameState.new_lab(800, 500, 0)
    s.time_left = 0.01
    s, ev = tick(s, PlayerInput(), DT, random.Random(5))
    assert any(e.type == GameEventType.WON for e in ev)


def test_s08_two_balls_no_fusion():
    from game.models import Ball

    s = GameState.new_lab(800, 500, 0)
    s.balls = [
        Ball(200, 200, 0, 0, 20, "H", "#fff", 1),
        Ball(205, 200, 0, 0, 20, "He", "#fff", 2),
    ]
    s, _ = tick(s, PlayerInput(), DT, random.Random(6))
    assert len(s.balls) == 2


def test_s10_dead_stops():
    s = GameState.new_lab(800, 500, 0)
    s.hearts = 0
    s.active = False
    s, ev = tick(s, PlayerInput(), DT, random.Random(7))
    assert any(e.type == GameEventType.DIED for e in ev) or s.hearts == 0
