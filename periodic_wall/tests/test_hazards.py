"""H-* scenarios."""

import random

from game.data import LEVEL_1_TUNING, REFERENCE_HARD_TUNING
from game.hazards import hazard_radius, integrate_balls, spawn_tick
from game.models import Ball, GameState


def test_h01_spawns_with_seed():
    s = GameState.new_lab(800, 500, 42)
    rng = random.Random(42)
    for _ in range(100):
        s.spawn_accum = spawn_tick(s, 1 / 30, rng)
    assert len(s.balls) >= 1


def test_h02_deterministic_spawn():
    def run():
        s = GameState.new_lab(800, 500, 42)
        rng = random.Random(42)
        for _ in range(100):
            s.spawn_accum = spawn_tick(s, 1 / 30, rng)
        return [(b.sym, round(b.x, 2), round(b.y, 2)) for b in s.balls]

    assert run() == run()


def test_h03_period1_only():
    allowed = {"H", "He", "D", "T"}
    s = GameState.new_lab(800, 500, 99)
    rng = random.Random(99)
    for _ in range(200):
        s.spawn_accum = spawn_tick(s, 1 / 30, rng)
    assert all(b.sym in allowed for b in s.balls)


def test_h04_ball_falls():
    b = Ball(100, 50, 0, 5, 12, "H", "#fff", 1)
    s = GameState.new_lab(800, 500)
    s.balls = [b]
    integrate_balls(s, random.Random(0))
    assert s.balls[0].y > 50


def test_h05_cull_below_screen():
    b = Ball(100, 900, 0, 2, 12, "He", "#fff", 2)
    s = GameState.new_lab(800, 500)
    s.balls = [b]
    integrate_balls(s, random.Random(0))
    assert len(s.balls) == 0


def test_h06_cap():
    from game.data import HAZARD_LIST_HARD_CAP

    s = GameState.new_lab(800, 500)
    s.balls = [
        Ball(float(i), 100, 0, 1, 8, "H", "#fff", 1) for i in range(HAZARD_LIST_HARD_CAP + 50)
    ]
    integrate_balls(s, random.Random(0))
    assert len(s.balls) <= HAZARD_LIST_HARD_CAP


def test_h07_overlap_no_merge():
    s = GameState.new_lab(800, 500)
    s.balls = [
        Ball(200, 200, 0, 1, 20, "H", "#fff", 1),
        Ball(205, 202, 0, 1, 20, "H", "#fff", 1),
    ]
    integrate_balls(s, random.Random(0))
    assert len(s.balls) == 2


def test_h08_he_larger_than_h():
    r_h = hazard_radius(800, 500, 1)
    r_he = hazard_radius(800, 500, 2)
    assert r_he >= r_h


def test_h09_gentler_than_hard():
    assert LEVEL_1_TUNING.rain_density < REFERENCE_HARD_TUNING.rain_density
