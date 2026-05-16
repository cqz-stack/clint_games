"""C-* scenarios."""

from game.combat import apply_damage, ball_hits_player, circles_overlap
from game.models import Ball, GameState
from game.player import Hitbox


def test_c01_one_damage():
    h, inv, dead = apply_damage(5, 0.0, 1, now=10.0)
    assert h == 4 and not dead


def test_c02_lethal():
    h, inv, dead = apply_damage(1, 0.0, 1, now=10.0)
    assert h == 0 and dead


def test_c03_invuln_blocks():
    h, inv, dead = apply_damage(5, 20.0, 1, now=10.0)
    assert h == 5 and inv == 20.0


def test_c04_after_invuln():
    h, inv, _ = apply_damage(5, 10.0, 1, now=11.0)
    assert h == 4


def test_c05_zero_damage():
    h, inv, dead = apply_damage(5, 0.0, 0, now=10.0)
    assert h == 5 and not dead


def test_c06_dead_stays_dead():
    h, inv, dead = apply_damage(0, 0.0, 1, now=10.0)
    assert h == 0 and dead


def test_overlap():
    hb = Hitbox(100, 100, 20)
    ball = Ball(110, 100, 0, 0, 15, "H", "#fff", 1)
    assert ball_hits_player(ball, hb)
    assert circles_overlap(0, 0, 10, 15, 0, 10)
