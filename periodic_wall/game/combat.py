"""Hearts and invulnerability."""

from __future__ import annotations

from game.data import DAMAGE_BALL_BUMP, HIT_INVULN_S
from game.models import Ball, GameEvent, GameEventType, GameState
from game.player import Hitbox


def apply_damage(
    hearts: int,
    invuln_until: float,
    amount: int,
    now: float,
) -> tuple[int, float, bool]:
    """Returns (new_hearts, new_invuln_until, is_dead)."""
    if amount <= 0 or now < invuln_until:
        return hearts, invuln_until, hearts <= 0
    hearts = max(0, hearts - amount)
    invuln_until = now + HIT_INVULN_S
    return hearts, invuln_until, hearts <= 0


def circles_overlap(
    ax: float, ay: float, ar: float, bx: float, by: float, br: float
) -> bool:
    dx = ax - bx
    dy = ay - by
    return dx * dx + dy * dy < (ar + br) ** 2


def ball_hits_player(ball: Ball, hb: Hitbox) -> bool:
    return circles_overlap(ball.x, ball.y, ball.r, hb.cx, hb.cy, hb.r)


def process_ball_collisions(
    state: GameState,
    hb: Hitbox,
    events: list[GameEvent],
) -> bool:
    """Remove hitting balls, apply damage. Returns True if player died."""
    i = 0
    while i < len(state.balls):
        ball = state.balls[i]
        if not ball_hits_player(ball, hb):
            i += 1
            continue
        if state.elapsed < state.invuln_until:
            i += 1
            continue
        state.balls.pop(i)
        hearts, invuln, dead = apply_damage(
            state.hearts,
            state.invuln_until,
            DAMAGE_BALL_BUMP,
            state.elapsed,
        )
        state.hearts = hearts
        state.invuln_until = invuln
        events.append(GameEvent(GameEventType.HIT))
        if dead:
            state.active = False
            events.append(GameEvent(GameEventType.DIED))
            return True
    return False
