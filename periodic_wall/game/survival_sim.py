"""One lab frame — wires player, hazards, combat, timer."""

from __future__ import annotations

import random

from game.combat import process_ball_collisions
from game.hazards import step_hazards
from game.models import GameEvent, GameEventType, GameState, PlayerInput
from game.player import step_player


def tick(
    state: GameState,
    inp: PlayerInput,
    dt: float,
    rng: random.Random | None = None,
) -> tuple[GameState, list[GameEvent]]:
    events: list[GameEvent] = []
    if not state.active:
        return state, events

    if rng is None:
        rng = random.Random(state.rng_seed + int(state.elapsed * 1000))

    state.elapsed += dt
    state.time_left -= dt

    if state.time_left <= 0:
        state.time_left = 0.0
        if state.hearts > 0:
            state.active = False
            events.append(GameEvent(GameEventType.WON))
        return state, events

    if state.hearts <= 0:
        state.active = False
        events.append(GameEvent(GameEventType.DIED))
        return state, events

    step_hazards(state, dt, rng)
    state.player, hb, _duck = step_player(
        state.player,
        inp,
        dt,
        state.room_w,
        state.room_h,
    )

    if process_ball_collisions(state, hb, events):
        return state, events

    return state, events
