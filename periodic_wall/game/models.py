"""Snapshots, inputs, and events for v0."""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import Enum, auto
from typing import Any


class Screen(Enum):
    TITLE = auto()
    LAB = auto()
    END_WIN = auto()
    END_LOSE = auto()


class GameEventType(Enum):
    HIT = auto()
    DIED = auto()
    WON = auto()


@dataclass(frozen=True)
class GameEvent:
    type: GameEventType
    data: dict[str, Any] = field(default_factory=dict)


@dataclass
class Ball:
    x: float
    y: float
    vx: float
    vy: float
    r: float
    sym: str
    col: str
    z: int


@dataclass
class PlayerState:
    px: float
    py: float
    vy: float = 0.0
    walk_phase: int = 0


@dataclass
class GameState:
    level: int = 1
    hearts: int = 5
    invuln_until: float = 0.0
    time_left: float = 300.0
    elapsed: float = 0.0
    player: PlayerState = field(default_factory=PlayerState)
    balls: list[Ball] = field(default_factory=list)
    room_w: float = 920.0
    room_h: float = 580.0
    rng_seed: int = 0
    spawn_accum: float = 0.0
    active: bool = True

    @staticmethod
    def new_lab(
        room_w: float = 920.0,
        room_h: float = 580.0,
        rng_seed: int = 0,
    ) -> GameState:
        from game.data import PLAYER_MAX_HP, SURVIVE_SECONDS

        floor_y = room_h - 40.0
        return GameState(
            level=1,
            hearts=PLAYER_MAX_HP,
            time_left=SURVIVE_SECONDS,
            player=PlayerState(px=room_w / 2, py=floor_y),
            room_w=room_w,
            room_h=room_h,
            rng_seed=rng_seed,
        )

    def copy(self) -> GameState:
        return replace(
            self,
            player=replace(self.player),
            balls=[replace(b) for b in self.balls],
        )


@dataclass
class PlayerInput:
    keys_held: frozenset[str] = frozenset()
    jump_pressed: bool = False


class Command(Enum):
    PLAY = auto()
    PLAY_AGAIN = auto()
    QUIT = auto()
    FORFEIT = auto()
    PICK_LEVEL_2 = auto()
    START_NUKE = auto()
