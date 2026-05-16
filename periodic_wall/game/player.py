"""Stick person movement and hitbox — pure functions."""

from __future__ import annotations

import math
from dataclasses import dataclass

from game.data import (
    FAST_FALL_BOOST,
    GRAVITY_PX_S2,
    JUMP_VELOCITY,
    JUMP_VELOCITY_AIR,
    MOVE_SPEED,
    PLAYER_PAD,
)
from game.models import PlayerInput, PlayerState


@dataclass(frozen=True)
class Hitbox:
    cx: float
    cy: float
    r: float


def floor_y(room_h: float) -> float:
    return room_h - 40.0


def step_player(
    player: PlayerState,
    inp: PlayerInput,
    dt: float,
    room_w: float,
    room_h: float,
) -> tuple[PlayerState, Hitbox, bool]:
    """Returns updated player, hitbox, and whether player is ducking."""
    fy = floor_y(room_h)
    px, py, vy = player.px, player.py, player.vy
    walk_phase = player.walk_phase
    keys = {k.lower() for k in inp.keys_held}
    keys.update(inp.keys_held)

    moving = False
    if "left" in keys or "a" in keys:
        px -= MOVE_SPEED * (dt / (1.0 / 30.0))
        moving = True
    if "right" in keys or "d" in keys:
        px += MOVE_SPEED * (dt / (1.0 / 30.0))
        moving = True
    if moving:
        walk_phase += 1

    px = max(PLAYER_PAD, min(room_w - PLAYER_PAD, px))

    on_ground = py >= fy - 2.0 and abs(vy) < 130.0
    if inp.jump_pressed:
        vy = JUMP_VELOCITY if on_ground else JUMP_VELOCITY_AIR

    if py < fy - 0.5:
        vy += GRAVITY_PX_S2 * dt
        if "s" in keys or "down" in keys:
            vy += FAST_FALL_BOOST * dt

    py += vy * dt
    if py >= fy:
        py = fy
        if vy > 0.0:
            vy = 0.0

    duck = ("s" in keys or "down" in keys) and py >= fy - 1.0 and abs(vy) < 120.0
    if duck:
        hb = Hitbox(px, py - 18.0, 14.0)
    else:
        hb = Hitbox(px, py - 30.0, 22.0)

    new_player = PlayerState(px=px, py=py, vy=vy, walk_phase=walk_phase)
    return new_player, hb, duck
