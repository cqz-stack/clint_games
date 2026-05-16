"""R-* scenarios."""

from game.models import Ball, GameState
from presentation.scenes import (
    build_end_draw_list,
    build_lab_draw_list,
    build_title_draw_list,
    has_forbidden_v0_layers,
)


def test_r01_title_has_bricks():
    prims = build_title_draw_list(800, 500)
    bricks = [p for p in prims if p.kwargs.get("tag") == "brick"]
    assert len(bricks) > 0


def test_r02_lab_floor_and_stickman():
    s = GameState.new_lab(800, 500)
    prims = build_lab_draw_list(s)
    assert any(p.kwargs.get("tag") == "floor" for p in prims)
    assert any(p.kwargs.get("tag") == "stickman" for p in prims)


def test_r03_three_balls():
    s = GameState.new_lab(800, 500)
    s.balls = [
        Ball(10, 20, 0, 1, 12, "H", "#fff", 1),
        Ball(30, 40, 0, 1, 12, "He", "#fff", 2),
        Ball(50, 60, 0, 1, 12, "D", "#fff", 1),
    ]
    prims = build_lab_draw_list(s)
    balls = [p for p in prims if p.kwargs.get("tag") == "ball"]
    assert len(balls) >= 6


def test_r04_timer_hud():
    s = GameState.new_lab(800, 500)
    s.time_left = 125.0
    prims = build_lab_draw_list(s)
    hud = [p for p in prims if p.kwargs.get("tag") == "hud"]
    texts = [str(p.kwargs.get("text", "")) for p in hud]
    assert any("2:05" in t for t in texts)


def test_r05_hp_in_hud():
    s = GameState.new_lab(800, 500)
    s.hearts = 3
    prims = build_lab_draw_list(s)
    texts = [str(p.kwargs.get("text", "")) for p in prims]
    assert any("HP 3" in t for t in texts)


def test_r06_end_win():
    prims = build_end_draw_list(True, 800, 500)
    texts = [str(p.kwargs.get("text", "")) for p in prims]
    assert any("You won" in t for t in texts)


def test_r07_no_forbidden_layers():
    s = GameState.new_lab(800, 500)
    prims = build_lab_draw_list(s)
    assert not has_forbidden_v0_layers(prims)


def test_r08_deterministic():
    s = GameState.new_lab(800, 500)
    a = build_lab_draw_list(s)
    b = build_lab_draw_list(s)
    assert len(a) == len(b)
