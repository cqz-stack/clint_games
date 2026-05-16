"""v0 recipe book — level 1 only, no fusion."""

from __future__ import annotations

from dataclasses import dataclass

MAX_LEVEL = 1

PLAYER_MAX_HP = 5
SURVIVE_SECONDS = 300.0
FRAME_DT = 1.0 / 30.0

DAMAGE_BALL_BUMP = 1
HIT_INVULN_S = 0.52

GRAVITY_PX_S2 = 2200.0
JUMP_VELOCITY = -685.0
JUMP_VELOCITY_AIR = -625.0
FAST_FALL_BOOST = 1100.0
MOVE_SPEED = 6.2 * (FRAME_DT * 60.0)
PLAYER_PAD = 28.0

HAZARD_R_MIN_FRAC = 0.012
HAZARD_R_MAX_FRAC = 0.125
HAZARD_VY_BASE = 2.2
HAZARD_VY_PER_Z = 0.38
HAZARD_VY_LAYER = 0.42
HAZARD_RAIN_DENSITY_MULT = 5.0
HAZARD_SPAWN_EVERY_FLOOR = 0.008
HAZARD_LIST_HARD_CAP = 120

# Period 1 pool (H, He, D, T)
PERIOD_1_ELEMENTS: tuple[tuple[str, str], ...] = (
    ("H", "#7eb8ff"),
    ("He", "#b8c8ff"),
    ("D", "#66aaff"),
    ("T", "#88ccff"),
)

SYMBOL_Z: dict[str, int] = {
    "H": 1,
    "D": 1,
    "T": 1,
    "He": 2,
}

PERIOD_1_POOL: tuple[tuple[str, str, int], ...] = tuple(
    (sym, col, SYMBOL_Z[sym]) for sym, col in PERIOD_1_ELEMENTS
)

PERIOD_1_LABEL = "H–He"


@dataclass(frozen=True)
class LevelTuning:
    rain_density: float
    spawn_interval_mult: float
    burst_max: int
    layer_max: int
    vy_mult: float
    vx_mult: float


LEVEL_1_TUNING = LevelTuning(
    rain_density=0.10,
    spawn_interval_mult=5.5,
    burst_max=4,
    layer_max=0,
    vy_mult=0.32,
    vx_mult=0.30,
)

# Reference row 5 for H-09 comparison (hard mode — not used in v0 gameplay)
REFERENCE_HARD_TUNING = LevelTuning(
    rain_density=0.92,
    spawn_interval_mult=1.0,
    burst_max=88,
    layer_max=6,
    vy_mult=1.05,
    vx_mult=0.95,
)
