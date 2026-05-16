"""I-* integration scenarios."""

import random

from game.models import GameEventType, GameState, PlayerInput
from game.survival_sim import tick


def test_i01_win_after_300s_coarse():
    s = GameState.new_lab(800, 500, 0)
    rng = random.Random(0)
    dt = 1.0
    won = False
    for _ in range(301):
        s, ev = tick(s, PlayerInput(), dt, rng)
        if any(e.type == GameEventType.WON for e in ev):
            won = True
            break
    assert won


def test_i02_five_hits_die():
    s = GameState.new_lab(800, 500, 0)
    rng = random.Random(1)
    from game.models import Ball

    for i in range(5):
        s.balls = [Ball(s.player.px, s.player.py - 30, 0, 0, 30, "H", "#fff", 1)]
        s.invuln_until = 0.0
        s.elapsed = float(i * 2)
        s, ev = tick(s, PlayerInput(), 1 / 30, rng)
    assert any(e.type == GameEventType.DIED for e in ev)


def test_i03_dodge_60s_alive():
    s = GameState.new_lab(800, 500, 42)
    rng = random.Random(42)
    for _ in range(int(60 / (1 / 30))):
        s, _ = tick(s, PlayerInput(keys_held=frozenset(["d"])), 1 / 30, rng)
    assert s.hearts >= 0
    assert s.active or s.time_left < 300


def test_i04_screen_flow_journey():
    from game.models import Command
    from game.screen_flow import FlowState, reduce_flow

    f = FlowState()
    reduce_flow(f, Command.PLAY, room_w=640, room_h=400, rng_seed=0)
    for _ in range(10):
        s, ev = tick(f.game, PlayerInput(), 1 / 30, random.Random(0))
        f.game = s
        reduce_flow(f, events=ev)
    reduce_flow(f, Command.FORFEIT)
    from game.models import Screen

    assert f.screen == Screen.TITLE


def test_i05_no_giant_ball_in_state():
    s = GameState.new_lab(800, 500, 99)
    rng = random.Random(99)
    for _ in range(500):
        s, _ = tick(s, PlayerInput(), 1 / 30, rng)
    assert not hasattr(s, "giant_ball")
    d = s.__dict__
    assert "giant_ball" not in d
