"""Falling balls — spawn and move only (no fusion)."""

from __future__ import annotations

import random
from dataclasses import replace

from game.data import (
    HAZARD_LIST_HARD_CAP,
    HAZARD_R_MAX_FRAC,
    HAZARD_R_MIN_FRAC,
    HAZARD_RAIN_DENSITY_MULT,
    HAZARD_SPAWN_EVERY_FLOOR,
    HAZARD_VY_BASE,
    HAZARD_VY_LAYER,
    HAZARD_VY_PER_Z,
    LEVEL_1_TUNING,
    PERIOD_1_POOL,
)
from game.models import Ball, GameState


def hazard_radius(w: float, h: float, z: int) -> float:
    m = min(w, h)
    t = (max(1, min(20, z)) - 1) / 19.0
    r_lo = m * HAZARD_R_MIN_FRAC
    r_hi = m * HAZARD_R_MAX_FRAC
    return r_lo + t * (r_hi - r_lo)


def hazard_vy(z: int, layer: int, vy_mult: float) -> float:
    t = (max(1, min(20, z)) - 1) / 19.0
    base = HAZARD_VY_BASE + t * 19.0 * HAZARD_VY_PER_Z + float(layer) * HAZARD_VY_LAYER
    return base * vy_mult


def spawn_tick(state: GameState, dt: float, rng: random.Random) -> float:
    """Update spawn_accum on state; append new balls. Returns new spawn_accum."""
    tuning = LEVEL_1_TUNING
    row = 1
    base_every = 0.30 * tuning.spawn_interval_mult
    spawn_every = max(
        HAZARD_SPAWN_EVERY_FLOOR,
        base_every / (HAZARD_RAIN_DENSITY_MULT * tuning.rain_density),
    )
    accum = state.spawn_accum + dt
    burst_cap = tuning.burst_max
    spawns_left = min(
        burst_cap,
        max(1, int((6 + row * 2) * HAZARD_RAIN_DENSITY_MULT * tuning.rain_density)),
    )
    w, h = state.room_w, state.room_h
    while accum >= spawn_every and spawns_left > 0:
        spawns_left -= 1
        accum -= spawn_every
        sym, col, atomic_z = rng.choice(PERIOD_1_POOL)
        layer = rng.randint(0, tuning.layer_max)
        y_spawn = -15.0 - layer * rng.uniform(45, 95)
        r = hazard_radius(w, h, atomic_z)
        vy = hazard_vy(atomic_z, layer, tuning.vy_mult)
        margin = 32.0
        x = rng.uniform(margin, max(margin + 1, w - margin))
        state.balls.append(
            Ball(
                x=x,
                y=y_spawn,
                vx=rng.uniform(-1.1, 1.1) * 0.6 * tuning.vx_mult,
                vy=vy,
                sym=sym,
                col=col,
                z=atomic_z,
                r=r,
            )
        )
    return accum


def integrate_balls(state: GameState, rng: random.Random) -> None:
    w, h = state.room_w, state.room_h
    for ball in state.balls:
        ball.x += ball.vx
        ball.y += ball.vy
        ball.vx += rng.uniform(-0.04, 0.04)
        if ball.x < ball.r:
            ball.x = ball.r
            ball.vx *= -0.5
        elif ball.x > w - ball.r:
            ball.x = w - ball.r
            ball.vx *= -0.5
    state.balls = [b for b in state.balls if -220 < b.y < h + 80]
    if len(state.balls) > HAZARD_LIST_HARD_CAP:
        state.balls.sort(key=lambda b: b.y)
        state.balls = state.balls[-HAZARD_LIST_HARD_CAP:]


def step_hazards(state: GameState, dt: float, rng: random.Random) -> None:
    state.spawn_accum = spawn_tick(state, dt, rng)
    integrate_balls(state, rng)
