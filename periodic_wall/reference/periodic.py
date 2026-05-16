"""
The Periodic Wall of Elements — title screen and game shell.
Run: python periodic.py
"""

from __future__ import annotations

import math
import random
import time
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from tkinter import font as tkfont
from tkinter import messagebox


# --- Hook: set this when you know where Quit should go (URL, subprocess, etc.)
def handle_quit(root: tk.Tk) -> None:
    root.destroy()


BG = "#161822"
ACCENT = "#3d9e8c"
TITLE_FG = "#e8eaf0"
BTN_FG = "#0d1117"

# Fourth period (row) of the standard periodic table: K → Kr
PERIOD_4 = [
    (19, "K"),
    (20, "Ca"),
    (21, "Sc"),
    (22, "Ti"),
    (23, "V"),
    (24, "Cr"),
    (25, "Mn"),
    (26, "Fe"),
    (27, "Co"),
    (28, "Ni"),
    (29, "Cu"),
    (30, "Zn"),
    (31, "Ga"),
    (32, "Ge"),
    (33, "As"),
    (34, "Se"),
    (35, "Br"),
    (36, "Kr"),
]

BRICK_FACE = "#b85a42"
BRICK_EDGE = "#8f3d2a"
MORTAR = "#3d3548"
STICK = "#e8eaf0"

# Play screen — building & windows
BUILDING = "#4d556e"
BUILDING_TRIM = "#2f3548"
WINDOW_DARK = "#141a2c"
WINDOW_GLOW = "#252e45"
FACE_WINDOW_INDEX = 2  # third of five windows (0-based)
ROW_BTN_IDLE = "#3d4458"

# Survival: hazards use symbols from the first N periods (player's chosen row count)
PERIOD_HAZARDS: list[list[tuple[str, str]]] = [
    [
        ("H", "#7eb8ff"),
        ("He", "#b8c8ff"),
        ("D", "#66aaff"),
        ("T", "#88ccff"),
    ],
    [
        ("Li", "#cc99aa"),
        ("Be", "#c8d8c8"),
        ("B", "#d4a574"),
        ("C", "#8899aa"),
        ("N", "#5599dd"),
        ("O", "#66aacc"),
        ("F", "#55dd88"),
        ("Ne", "#99ccff"),
    ],
    [
        ("Na", "#c9b882"),
        ("Mg", "#dde0e8"),
        ("Al", "#b8c0c8"),
        ("Si", "#a8a898"),
        ("P", "#ffaa44"),
        ("S", "#ccb833"),
        ("Cl", "#66cc77"),
        ("Ar", "#99bbdd"),
    ],
    [
        ("K", "#d4a574"),
        ("Ca", "#e8e0d8"),
        ("Sc", "#c8c4d8"),
        ("Ti", "#a8a8b8"),
        ("V", "#8899aa"),
        ("Cr", "#8a9aaa"),
        ("Mn", "#9a8a88"),
        ("Fe", "#c08050"),
        ("Co", "#6688aa"),
        ("Ni", "#88a090"),
        ("Cu", "#b87333"),
        ("Zn", "#889988"),
        ("Ga", "#b8a898"),
        ("Ge", "#908880"),
        ("As", "#aa8866"),
        ("Se", "#bbaa44"),
        ("Br", "#5a8060"),
        ("Kr", "#8899bb"),
    ],
    [
        ("Rb", "#cc8899"),
        ("Sr", "#c8c8d0"),
        ("Y", "#a8a8c0"),
        ("Zr", "#9090a0"),
        ("Nb", "#8888a0"),
        ("Mo", "#778899"),
        ("Tc", "#6688aa"),
        ("Ru", "#667788"),
        ("Rh", "#708090"),
        ("Pd", "#8899aa"),
        ("Ag", "#c0c0d8"),
        ("Cd", "#a8b0b8"),
        ("In", "#b0a898"),
        ("Sn", "#a0a0a0"),
        ("Sb", "#908878"),
        ("Te", "#887760"),
        ("I", "#7b4fa3"),
        ("Xe", "#8899bb"),
    ],
    [
        ("Cs", "#dd99aa"),
        ("Ba", "#d8d0c0"),
        ("La", "#a898c8"),
        ("Ce", "#c8b898"),
        ("Pr", "#b8a8a8"),
        ("Nd", "#a89898"),
        ("Pm", "#988888"),
        ("Sm", "#908078"),
        ("Eu", "#8878a8"),
        ("Gd", "#788898"),
        ("Tb", "#708088"),
        ("Dy", "#687878"),
        ("Ho", "#607068"),
        ("Er", "#586058"),
        ("Tm", "#505050"),
        ("Yb", "#686060"),
        ("Lu", "#787070"),
        ("Hf", "#606878"),
        ("Ta", "#585868"),
        ("W", "#505058"),
        ("Re", "#484850"),
        ("Os", "#404048"),
        ("Ir", "#383840"),
        ("Pt", "#d0d0e0"),
        ("Au", "#ffd700"),
        ("Hg", "#b8b8c8"),
        ("Tl", "#a89888"),
        ("Pb", "#708090"),
        ("Bi", "#686878"),
        ("Po", "#585860"),
        ("At", "#484858"),
        ("Rn", "#a8e8ff"),
    ],
    [
        ("Fr", "#ee8899"),
        ("Ra", "#e8d8c8"),
        ("Ac", "#b8a8c8"),
        ("Th", "#a89888"),
        ("Pa", "#988878"),
        ("U", "#668844"),
        ("Np", "#557033"),
        ("Pu", "#445522"),
        ("Am", "#554433"),
        ("Cm", "#443322"),
    ],
]

# Atomic numbers for hazard size / fall speed (isotopes map to parent element)
SYMBOL_Z: dict[str, int] = {
    "H": 1,
    "D": 1,
    "T": 1,
    "He": 2,
    "Li": 3,
    "Be": 4,
    "B": 5,
    "C": 6,
    "N": 7,
    "O": 8,
    "F": 9,
    "Ne": 10,
    "Na": 11,
    "Mg": 12,
    "Al": 13,
    "Si": 14,
    "P": 15,
    "S": 16,
    "Cl": 17,
    "Ar": 18,
    "K": 19,
    "Ca": 20,
    "Sc": 21,
    "Ti": 22,
    "V": 23,
    "Cr": 24,
    "Mn": 25,
    "Fe": 26,
    "Co": 27,
    "Ni": 28,
    "Cu": 29,
    "Zn": 30,
    "Ga": 31,
    "Ge": 32,
    "As": 33,
    "Se": 34,
    "Br": 35,
    "Kr": 36,
    "Rb": 37,
    "Sr": 38,
    "Y": 39,
    "Zr": 40,
    "Nb": 41,
    "Mo": 42,
    "Tc": 43,
    "Ru": 44,
    "Rh": 45,
    "Pd": 46,
    "Ag": 47,
    "Cd": 48,
    "In": 49,
    "Sn": 50,
    "Sb": 51,
    "Te": 52,
    "I": 53,
    "Xe": 54,
    "Cs": 55,
    "Ba": 56,
    "La": 57,
    "Ce": 58,
    "Pr": 59,
    "Nd": 60,
    "Pm": 61,
    "Sm": 62,
    "Eu": 63,
    "Gd": 64,
    "Tb": 65,
    "Dy": 66,
    "Ho": 67,
    "Er": 68,
    "Tm": 69,
    "Yb": 70,
    "Lu": 71,
    "Hf": 72,
    "Ta": 73,
    "W": 74,
    "Re": 75,
    "Os": 76,
    "Ir": 77,
    "Pt": 78,
    "Au": 79,
    "Hg": 80,
    "Tl": 81,
    "Pb": 82,
    "Bi": 83,
    "Po": 84,
    "At": 85,
    "Rn": 86,
    "Fr": 87,
    "Ra": 88,
    "Ac": 89,
    "Th": 90,
    "Pa": 91,
    "U": 92,
    "Np": 93,
    "Pu": 94,
    "Am": 95,
    "Cm": 96,
}


def _build_period_rain_pools() -> list[list[tuple[str, str, int]]]:
    return [
        [(sym, col, SYMBOL_Z.get(sym, 1)) for sym, col in period]
        for period in PERIOD_HAZARDS
    ]


PERIOD_RAIN_POOLS = _build_period_rain_pools()

PERIOD_LABELS = ("H–He", "Li–Ne", "Na–Ar", "K–Kr", "Rb–Xe", "Cs–Rn", "Fr–Cm")

# Simplified build: only three playable floors (periods 1–3). More floors = later layers.
MAX_FLOOR = 3
ACTIVE_PERIOD_LABELS = PERIOD_LABELS[:MAX_FLOOR]


@dataclass(frozen=True)
class RowTuning:
    """Per-floor rain difficulty (floors 1–3 in this build)."""

    rain_density: float
    spawn_interval_mult: float
    burst_max: int
    layer_max: int
    vy_mult: float
    vx_mult: float
    z_scale: float
    lava_rise_mult: float = 1.0


@dataclass(frozen=True)
class FloorRules:
    """Which rule layers are on for this floor (see DESIGN.md)."""

    fusion: bool
    giant_ball: bool
    shockwaves: bool


# Index 0 = floor 1 … index 2 = floor 3
ROW_TUNINGS: tuple[RowTuning, ...] = (
    RowTuning(0.10, 5.5, 4, 0, 0.32, 0.30, 0.45),  # 1 — dodge only, very easy
    RowTuning(0.22, 3.6, 10, 1, 0.48, 0.42, 0.58),  # 2 — fusion on
    RowTuning(0.40, 2.4, 24, 2, 0.65, 0.58, 0.72),  # 3 — fusion + busier rain
)

FLOOR_RULES: tuple[FloorRules, ...] = (
    FloorRules(fusion=False, giant_ball=False, shockwaves=False),  # layer A
    FloorRules(fusion=True, giant_ball=True, shockwaves=True),  # layer B
    FloorRules(fusion=True, giant_ball=True, shockwaves=True),  # layer B + harder rain
)

SURVIVE_SECONDS = 300.0
SURVIVAL_FRAME_MS = 33

PLAYER_MAX_HP = 5
# Two hazards fuse when centers are this close relative to touching distance
HAZARD_FUSE_DIST_FRAC = 0.9
# Mixed fusion: outer ring reaches ⅓ of min(w,h) from center (full third of screen)
SHOCKWAVE_RADIUS_FRAC_MIXED = 1.0 / 3.0
SHOCKWAVE_DURATION_S = 0.48
# When fusion is above & aligned with the stickman, widen the two vertical columns
SHOCKWAVE_SPLIT_ALIGN_FRAC = 0.12
# Same-type fusion: damage check at contact (radius = this × min side)
SHOCKWAVE_DAMAGE_FRAC_SAME = 1.0 / 6.0
DAMAGE_HAZARD_BUMP = 1
DAMAGE_SHOCKWAVE_MIXED = 1
DAMAGE_SHOCKWAVE_SAME = 2
HIT_INVULN_S = 0.52

# Heaviest raindrops: radius so diameter ≈ ¼ of the shorter canvas side
HAZARD_R_MIN_FRAC = 0.012
HAZARD_R_MAX_FRAC = 0.125
# Fall speed scales with Z (1 = light … 20 = heavy)
HAZARD_VY_BASE = 2.2
HAZARD_VY_PER_Z = 0.38
HAZARD_VY_LAYER = 0.42
# Element rain density (user-tunable); 5 ≈ five times the original fall rate
HAZARD_RAIN_DENSITY_MULT = 5.0
HAZARD_SPAWN_EVERY_FLOOR = 0.008
HAZARD_SPAWN_BURST_MAX = 150
FUSION_RESOLVE_MAX_OUTER = 48
HAZARD_LIST_HARD_CAP = 900

# Giant fused ball (same-symbol): diameter = this × min(w,h); spawns at fusion, falls, damages on overlap
GIANT_BALL_DIAMETER_FRAC = 2.0 / 3.0
GIANT_BALL_DURATION_S = 5.8
GIANT_BALL_GRAVITY_PX_S2 = 2150.0
GIANT_BALL_INITIAL_VY = 140.0
DAMAGE_GIANT_BALL_CONTACT = 1

# Mixed vertical shock: two fixed-width columns; waves travel along Y (no horizontal growth)
VERT_SHOCK_STRIP_HALF_FRAC = 0.10
VERT_SHOCK_TRAVEL_SPEED = 400.0
VERT_SHOCK_PAIR_SEP_FRAC = 0.36
VERT_SHOCK_PAIR_SEP_WIDE_FRAC = 0.54
VERT_SHOCK_DAMAGE_R_FRAC = 0.46

# Stickman physics (canvas coords: y increases downward)
GRAVITY_PX_S2 = 2200.0
JUMP_VELOCITY = -685.0  # jump while on floor / platform
JUMP_VELOCITY_AIR = -625.0  # every mid-air jump (unlimited)
FAST_FALL_BOOST = 1100.0

LAVA_RISE_BASE_PX_S = 55.0
LAVA_RISE_RAMP_PER_MIN = 22.0
LAVA_PLATFORM_THICK = 12
# Endless climb: vertical gap & horizontal reach (tuned for multi-jump)
LAVA_PLATFORM_DY_MIN = 68.0
LAVA_PLATFORM_DY_MAX = 102.0
LAVA_PLATFORM_REACH_X = 175.0
LAVA_SCROLL_TRIGGER_Y = 118.0
LAVA_SCROLL_CHUNK = 210.0
LAVA_PLATFORMS_PER_SCROLL = 5
# Row 6: scroll down when feet are within this many px of the canvas bottom
LAVA_SCROLL_DOWN_MARGIN = 110.0
LAVA_PLATFORMS_PER_SCROLL_DOWN = 4
LAVA_DROP_IGNORE_S = 0.38

NUKE_CUTSCENE_SECONDS = 6.5
NUKE_FRAME_MS = 40


def draw_wall_scene(canvas: tk.Canvas, w: int, h: int) -> None:
    """Background: period-4 brick row and a stick figure lying on the center bricks."""
    canvas.delete("scene")
    canvas.create_rectangle(0, 0, w, h, fill=BG, outline="", tags="scene")

    margin_x = max(24, w * 0.04)
    row_y = h * 0.62
    row_h = max(56, min(88, h * 0.14))
    inner_w = w - 2 * margin_x
    n = len(PERIOD_4)
    gap = 3
    brick_w = (inner_w - gap * (n - 1)) / n

    for i, (z, sym) in enumerate(PERIOD_4):
        x0 = margin_x + i * (brick_w + gap)
        x1 = x0 + brick_w
        y0, y1 = row_y, row_y + row_h
        canvas.create_rectangle(x0, y0, x1, y1, fill=BRICK_EDGE, outline="", tags="scene")
        inset = 2
        canvas.create_rectangle(
            x0 + inset,
            y0 + inset,
            x1 - inset,
            y1 - inset,
            fill=BRICK_FACE,
            outline=MORTAR,
            width=2,
            tags="scene",
        )
        fz = max(9, int(brick_w * 0.22))
        fs = max(11, int(brick_w * 0.28))
        canvas.create_text(
            (x0 + x1) / 2,
            y0 + row_h * 0.38,
            text=str(z),
            fill="#d4a574",
            font=("Helvetica", fz),
            tags="scene",
        )
        canvas.create_text(
            (x0 + x1) / 2,
            y0 + row_h * 0.68,
            text=sym,
            fill=TITLE_FG,
            font=("Helvetica", fs, "bold"),
            tags="scene",
        )

    # Stick figure lying on top of the middle bricks (side view, head to the right)
    mid_i = n // 2
    span = 4
    i0 = max(0, mid_i - span // 2)
    i1 = min(n - 1, i0 + span - 1)
    bx0 = margin_x + i0 * (brick_w + gap)
    bx1 = margin_x + (i1 + 1) * brick_w + i1 * gap
    cx = (bx0 + bx1) / 2
    top = row_y

    scale = min(1.0, brick_w * 4 / 220)
    r_head = int(14 * scale)
    body_len = int(85 * scale)
    limb = int(38 * scale)

    # Resting line (body axis), slightly above brick tops
    y_body = top - r_head - int(6 * scale)
    x_head = cx + body_len * 0.35
    y_head = y_body

    canvas.create_oval(
        x_head - r_head,
        y_head - r_head,
        x_head + r_head,
        y_head + r_head,
        outline=STICK,
        width=3,
        tags="scene",
    )
    x_shoulder = x_head - r_head - int(4 * scale)
    x_hip = x_shoulder - body_len
    canvas.create_line(
        x_shoulder, y_body, x_hip, y_body, fill=STICK, width=3, tags="scene"
    )
    # Upper arm (resting on bricks)
    canvas.create_line(
        x_shoulder,
        y_body,
        x_shoulder - int(20 * scale),
        y_body + int(12 * scale),
        fill=STICK,
        width=3,
        tags="scene",
    )
    canvas.create_line(
        x_shoulder - int(5 * scale),
        y_body,
        x_shoulder - int(28 * scale),
        y_body + int(8 * scale),
        fill=STICK,
        width=3,
        tags="scene",
    )
    # Legs (bent, feet on bricks)
    canvas.create_line(
        x_hip,
        y_body,
        x_hip - int(18 * scale),
        y_body + int(22 * scale),
        fill=STICK,
        width=3,
        tags="scene",
    )
    canvas.create_line(
        x_hip + int(10 * scale),
        y_body,
        x_hip - int(8 * scale),
        y_body + int(26 * scale),
        fill=STICK,
        width=3,
        tags="scene",
    )


def draw_building_scene(canvas: tk.Canvas, w: int, h: int) -> None:
    """Night scene: building with five windows; stick figure head (outline only) in one window."""
    canvas.delete("scene")
    canvas.create_rectangle(0, 0, w, h, fill=BG, outline="", tags="scene")

    margin = max(32, int(w * 0.06))
    bw = w - 2 * margin
    bh = max(180, min(int(h * 0.5), int(h * 0.55)))
    bx0 = margin
    by1 = int(h - margin * 0.5)
    by0 = by1 - bh
    mid_x = w // 2

    # Roof
    peak_h = int(bh * 0.12)
    canvas.create_polygon(
        bx0 - 8,
        by0,
        mid_x,
        by0 - peak_h,
        bx0 + bw + 8,
        by0,
        fill=BUILDING_TRIM,
        outline="#1e2230",
        width=2,
        tags="scene",
    )
    canvas.create_rectangle(
        bx0, by0, bx0 + bw, by1, fill=BUILDING, outline=BUILDING_TRIM, width=3, tags="scene"
    )

    nwin = 5
    pad = bw * 0.07
    win_band = bw - 2 * pad
    gap = max(6, win_band * 0.035)
    each_w = (win_band - (nwin - 1) * gap) / nwin
    wh = bh * 0.38
    wy = by0 + bh * 0.2

    for i in range(nwin):
        wx0 = bx0 + pad + i * (each_w + gap)
        wx1 = wx0 + each_w
        is_face = i == FACE_WINDOW_INDEX
        inner_fill = WINDOW_GLOW if is_face else WINDOW_DARK
        canvas.create_rectangle(
            wx0, wy, wx1, wy + wh, fill="#0d1018", outline=BUILDING_TRIM, width=2, tags="scene"
        )
        inset = 4
        canvas.create_rectangle(
            wx0 + inset,
            wy + inset,
            wx1 - inset,
            wy + wh - inset,
            fill=inner_fill,
            outline="",
            tags="scene",
        )
        # Sill
        sill_h = 6
        canvas.create_rectangle(
            wx0 - 2,
            wy + wh,
            wx1 + 2,
            wy + wh + sill_h,
            fill=BUILDING_TRIM,
            outline="",
            tags="scene",
        )

        if is_face:
            cx = (wx0 + wx1) / 2
            cy = wy + inset + (wh - 2 * inset) * 0.48
            r = min(each_w, wh) * 0.28
            # Head only (no face features)
            canvas.create_oval(
                cx - r,
                cy - r,
                cx + r,
                cy + r,
                outline=STICK,
                width=3,
                tags="scene",
            )

    # Door (centered under windows)
    door_w = each_w * 1.1
    door_x0 = mid_x - door_w / 2
    door_y0 = wy + wh + sill_h + int(bh * 0.08)
    canvas.create_rectangle(
        door_x0,
        door_y0,
        door_x0 + door_w,
        by1 - 8,
        fill=WINDOW_DARK,
        outline=BUILDING_TRIM,
        width=2,
        tags="scene",
    )


def draw_nuke_explosion(
    canvas: tk.Canvas,
    w: int,
    h: int,
    t: float,
) -> None:
    """Overlay nuclear blast on top of existing scene. t in [0, 1] over cutscene."""
    mid_x = w * 0.5
    base_y = h * 0.72
    # Initial flash
    if t < 0.12:
        flash_a = 1.0 - t / 0.12
        c = "#ffffff" if t < 0.04 else "#fff4c8"
        canvas.create_rectangle(
            0,
            0,
            w,
            h,
            fill=c,
            outline="",
            tags="nukefx",
        )
        if flash_a > 0.3:
            canvas.create_oval(
                -w * 0.2,
                -h * 0.2,
                w * 1.2,
                h * 1.2,
                fill="#ffffee",
                outline="",
                tags="nukefx",
            )

    shake = math.sin(t * 95) * (14 * max(0.0, 1.0 - t * 1.2))
    ox, oy = shake, shake * 0.4

    # Expanding fireball / thermal bloom
    bloom = min(1.0, max(0.0, (t - 0.02) / 0.35))
    r0 = min(w, h) * (0.08 + bloom * 0.55)
    for i, col in enumerate(("#ffff88", "#ffaa33", "#ff4422", "#cc1100")):
        ri = r0 * (1.0 - i * 0.18)
        canvas.create_oval(
            mid_x - ri + ox,
            base_y - ri * 0.55 + oy,
            mid_x + ri + ox,
            base_y + ri * 0.85 + oy,
            fill=col,
            outline="",
            tags="nukefx",
        )

    # Mushroom stem
    if t > 0.08:
        stem_w = 18 + t * 40
        stem_h = min(h * 0.55, (t - 0.08) * h * 0.9)
        canvas.create_rectangle(
            mid_x - stem_w / 2 + ox,
            base_y - stem_h + oy,
            mid_x + stem_w / 2 + ox,
            base_y + h * 0.08 + oy,
            fill="#553322",
            outline="#221100",
            width=2,
            tags="nukefx",
        )

    # Mushroom cap
    if t > 0.15:
        cap_w = min(w * 0.85, (t - 0.15) * w * 1.1)
        cap_h = cap_w * 0.35
        cap_y = base_y - min(h * 0.5, (t - 0.15) * h * 0.95) + oy
        canvas.create_arc(
            mid_x - cap_w / 2 + ox,
            cap_y - cap_h,
            mid_x + cap_w / 2 + ox,
            cap_y + cap_h * 2,
            start=0,
            extent=180,
            style=tk.CHORD,
            fill="#8b4513",
            outline="#4a2510",
            width=3,
            tags="nukefx",
        )
        canvas.create_arc(
            mid_x - cap_w / 2 * 0.92 + ox,
            cap_y - cap_h * 0.9,
            mid_x + cap_w / 2 * 0.92 + ox,
            cap_y + cap_h * 1.8,
            start=0,
            extent=180,
            style=tk.CHORD,
            fill="#aa5533",
            outline="",
            tags="nukefx",
        )

    # Dark smoke ring
    if t > 0.2:
        sr = min(w, h) * (0.2 + t * 0.4)
        canvas.create_oval(
            mid_x - sr + ox,
            base_y - sr * 0.4 + oy,
            mid_x + sr + ox,
            base_y + sr * 0.65 + oy,
            fill="",
            outline="#2a2a2a",
            width=6,
            tags="nukefx",
        )

    # Title text late
    if t > 0.45:
        canvas.create_text(
            mid_x + ox,
            h * 0.18 + oy,
            text="CRITICAL REACTION",
            fill="#ffeedd",
            font=("Helvetica", max(18, int(w * 0.038)), "bold"),
            tags="nukefx",
        )


class PeriodicWallApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("The Periodic Wall of Elements")
        self.root.geometry("920x580")
        self.root.minsize(640, 420)
        self.root.configure(bg=BG)

        self.title_font = tkfont.Font(family="Helvetica", size=28, weight="bold")
        self.sub_font = tkfont.Font(family="Helvetica", size=13)
        self.btn_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.row_btn_font = tkfont.Font(family="Helvetica", size=16, weight="bold")

        self._title_active = True
        self._on_play_screen = False
        self._period_rows: int | None = None

        self._survival_after_id: str | None = None
        self._survival_active = False
        self._survival_keys: set[str] = set()
        self._survival_hazards: list[dict] = []
        self._survival_shockwaves: list[dict] = []
        self._survival_giant_ball: dict | None = None
        self._survival_player_hp = PLAYER_MAX_HP
        self._survival_invuln_until = 0.0
        self._survival_spawn_accum = 0.0
        self._survival_rows = 1
        self._survival_start = 0.0
        self._survival_px = 400.0
        self._survival_py = 400.0
        self._survival_cw = 920
        self._survival_ch = 580
        self._walk_phase = 0
        self._survival_vy = 0.0
        self._jump_queued = False
        self._survival_platforms: list[dict[str, float]] = []
        self._lava_surface_y: float | None = None
        self._lava_drop_ignore_deadline = 0.0
        self._lava_drop_ignore_y = -1e9

        self._nuke_after_id: str | None = None
        self._nuke_start = 0.0
        self._nuke_cw = 920
        self._nuke_ch = 580

        self._banner_after_id: str | None = None
        self._banner_frame: tk.Frame | None = None

        self.container = tk.Frame(self.root, bg=BG)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.title_screen = self._build_title_screen()
        self.play_screen = self._build_play_screen()
        self.survival_screen = self._build_survival_screen()
        self.nuke_screen = self._build_nuke_screen()

        # Stack screens; pack_forget() leaves ghost click targets on macOS Tk.
        for scr in (
            self.title_screen,
            self.play_screen,
            self.survival_screen,
            self.nuke_screen,
        ):
            scr.place(x=0, y=0, relwidth=1, relheight=1)

        # Floor picker on root (not inside screens) so nothing can cover the buttons.
        self._play_bar = self._build_play_bar()

        self.root.bind("<Return>", self._on_enter_key)
        self.root.bind("<KP_Enter>", self._on_enter_key)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close_window)
        self.root.bind_all("<KeyPress>", self._on_root_key_down)
        self.root.bind_all("<KeyRelease>", self._on_root_key_up)

        self.show_title_screen()

    def _on_close_window(self) -> None:
        self._cancel_banner_anim()
        self._stop_survival()
        self._stop_nuke()
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def _cancel_banner_anim(self) -> None:
        if self._banner_after_id is not None:
            try:
                self.root.after_cancel(self._banner_after_id)
            except (tk.TclError, ValueError):
                pass
            self._banner_after_id = None
        if self._banner_frame is not None:
            try:
                self._banner_frame.destroy()
            except tk.TclError:
                pass
            self._banner_frame = None

    def _show_end_banner(self, message: str, bg: str, on_done: Callable[[], None]) -> None:
        """Horizontal bar slides through the middle, then runs on_done (e.g. return to play)."""
        self._cancel_banner_anim()
        bar = tk.Frame(self.container, bg=bg, height=86)
        self._banner_frame = bar
        tk.Label(
            bar,
            text=message,
            font=self.title_font,
            fg=TITLE_FG,
            bg=bg,
        ).pack(expand=True, pady=14)
        nsteps = 24

        def step(phase: str, i: int) -> None:
            if self._banner_frame is None:
                return
            if phase == "in":
                if i > nsteps:
                    self._banner_after_id = self.root.after(900, lambda: step("out", 0))
                    return
                r = -1.12 + (i / nsteps) * 1.12
                bar.place(relx=r, rely=0.5, relwidth=1.0, height=86, anchor=tk.W)
                bar.lift()
                self._banner_after_id = self.root.after(14, lambda: step("in", i + 1))
            else:
                if i > nsteps:
                    self._cancel_banner_anim()
                    on_done()
                    return
                r = (i / nsteps) * 1.12
                bar.place(relx=r, rely=0.5, relwidth=1.0, height=86, anchor=tk.W)
                bar.lift()
                self._banner_after_id = self.root.after(14, lambda: step("out", i + 1))

        step("in", 0)

    def _styled_button(self, parent: tk.Misc, text: str, command) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            font=self.btn_font,
            fg=BTN_FG,
            bg=ACCENT,
            activeforeground=BTN_FG,
            activebackground="#2d8577",
            relief=tk.FLAT,
            padx=28,
            pady=12,
            cursor="hand2",
            command=command,
        )

    def _on_enter_key(self, event: tk.Event) -> None:
        if self._title_active:
            self.show_play_screen()

    def _survival_key_down(self, e: tk.Event) -> None:
        k = e.keysym
        if k in ("Left", "Right"):
            self._survival_keys.add(k)
        elif k in ("a", "A"):
            self._survival_keys.add("a")
        elif k in ("d", "D"):
            self._survival_keys.add("d")
        elif k in ("w", "W", "Up"):
            self._jump_queued = True
        elif k in ("s", "S"):
            self._survival_keys.add("s")
        elif k == "Down":
            self._survival_keys.add("down")

    def _survival_key_up(self, e: tk.Event) -> None:
        k = e.keysym
        if k in ("Left", "Right"):
            self._survival_keys.discard(k)
        elif k in ("a", "A"):
            self._survival_keys.discard("a")
        elif k in ("d", "D"):
            self._survival_keys.discard("d")
        elif k in ("s", "S"):
            self._survival_keys.discard("s")
        elif k == "Down":
            self._survival_keys.discard("down")

    def _on_root_key_down(self, e: tk.Event) -> None:
        if self._survival_active:
            self._survival_key_down(e)
            return
        if self._on_play_screen and e.keysym in (
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
        ):
            self._pick_row(int(e.keysym))

    def _on_root_key_up(self, e: tk.Event) -> None:
        if self._survival_active:
            self._survival_key_up(e)

    def _stop_survival(self) -> None:
        self._survival_active = False
        self._survival_keys.clear()
        if self._survival_after_id is not None:
            try:
                self.root.after_cancel(self._survival_after_id)
            except (tk.TclError, ValueError):
                pass
            self._survival_after_id = None
        self._survival_hazards.clear()
        self._survival_shockwaves.clear()
        self._survival_giant_ball = None
        self._survival_platforms.clear()
        self._lava_surface_y = None
        self._lava_drop_ignore_deadline = 0.0
        self._lava_drop_ignore_y = -1e9
        self._survival_player_hp = PLAYER_MAX_HP
        self._survival_invuln_until = 0.0

    def _pick_rain_spawn_x(self, w: float, h: float, margin: float) -> float:
        return random.uniform(margin, max(margin + 1, w - margin))

    @staticmethod
    def _row_tuning(row: int) -> RowTuning:
        return ROW_TUNINGS[max(1, min(6, row)) - 1]

    @staticmethod
    def _game_z_for_row(row: int, atomic_z: int) -> int:
        pool = PERIOD_RAIN_POOLS[max(1, min(7, row)) - 1]
        zs = [z for _, _, z in pool]
        lo, hi = min(zs), max(zs)
        tuning = PeriodicWallApp._row_tuning(row)
        if hi <= lo:
            gz = 10
        else:
            t = (atomic_z - lo) / (hi - lo)
            gz = 1 + int(round(t * 19))
        return max(1, min(20, int(1 + (gz - 1) * tuning.z_scale)))

    @staticmethod
    def _period_element_label(row: int) -> str:
        r = max(1, min(MAX_FLOOR, row))
        return ACTIVE_PERIOD_LABELS[r - 1]

    def _integrate_survival_giant_ball(
        self,
        w: float,
        h: float,
        dt: float,
        floor_y: float,
        lava_surface_y: float | None,
    ) -> None:
        """Falling fused orb: gravity, platforms (row 6), floor, lava; time limit."""
        g = self._survival_giant_ball
        if g is None:
            return
        now = time.monotonic()
        if now >= float(g["t_end"]):
            self._survival_giant_ball = None
            return

        cy = float(g["cy"])
        vy = float(g["vy"])
        cx = float(g["cx"])
        r = float(g["r"])

        vy += GIANT_BALL_GRAVITY_PX_S2 * dt
        old_cy = cy
        cy += vy * dt
        cx = max(r + 8.0, min(float(w) - r - 8.0, cx))

        if lava_surface_y is not None:
            for p in self._survival_platforms:
                py_p = float(p["y"])
                if float(lava_surface_y) <= py_p + 8:
                    continue
                x1, x2 = float(p["x1"]), float(p["x2"])
                if (
                    vy >= 0
                    and x1 - r * 0.3 <= cx <= x2 + r * 0.3
                    and old_cy + r <= py_p + 12
                    and cy + r >= py_p - 2
                ):
                    cy = py_p - r
                    vy = 0.0
                    break

        if lava_surface_y is not None and cy + r >= float(lava_surface_y) - 5:
            self._survival_giant_ball = None
            return

        if cy + r >= floor_y:
            cy = floor_y - r
            vy = 0.0

        if cy - r > float(h) + 280:
            self._survival_giant_ball = None
            return

        g["cx"] = cx
        g["cy"] = cy
        g["vy"] = vy

    def _try_giant_ball_contact_damage(self, tcx: float, tcy: float, tr: float) -> bool:
        """Crush damage while overlapping the falling orb. True if player died."""
        g = self._survival_giant_ball
        if g is None:
            return False
        cx, cy, r = float(g["cx"]), float(g["cy"]), float(g["r"])
        dx = tcx - cx
        dy = tcy - cy
        if dx * dx + dy * dy >= (r + tr) ** 2:
            return False
        if self._try_player_damage(DAMAGE_GIANT_BALL_CONTACT):
            self._survival_die()
            return True
        return False

    def _hazard_radius_for_z(self, w: float, h: float, z: int) -> float:
        m = min(float(w), float(h))
        t = (max(1, min(20, z)) - 1) / 19.0
        r_lo = m * HAZARD_R_MIN_FRAC
        r_hi = m * HAZARD_R_MAX_FRAC
        return r_lo + t * (r_hi - r_lo)

    def _hazard_vy_for_z(self, z: int, layer: int) -> float:
        t = (max(1, min(20, z)) - 1) / 19.0
        return (
            HAZARD_VY_BASE + t * 19.0 * HAZARD_VY_PER_Z + float(layer) * HAZARD_VY_LAYER
        )

    def _draw_survival_giant_ball(self, c: tk.Canvas, w: float, h: float) -> None:
        if self._survival_giant_ball is None:
            return
        g = self._survival_giant_ball
        cx = float(g["cx"])
        cy = float(g["cy"])
        r = float(g["r"])
        col = str(g["col"])
        sym = str(g["sym"])
        c.create_oval(
            cx - r,
            cy - r,
            cx + r,
            cy + r,
            fill=col,
            outline="#fff8e8",
            width=6,
            tags="dyn",
        )
        c.create_text(
            cx,
            cy,
            text=sym,
            fill="#0d1117",
            font=("Helvetica", max(22, int(r * 0.14)), "bold"),
            tags="dyn",
        )

    def _stop_nuke(self) -> None:
        if self._nuke_after_id is not None:
            try:
                self.root.after_cancel(self._nuke_after_id)
            except (tk.TclError, ValueError):
                pass
            self._nuke_after_id = None

    def _pick_row(self, n: int) -> None:
        """Floor button / key: start survival (wrapped so errors show in a dialog)."""
        if n < 1 or n > MAX_FLOOR:
            return
        if hasattr(self, "_floor_status_lbl"):
            self._floor_status_lbl.config(text=f"Starting floor {n}…")
            self.root.update_idletasks()
        try:
            self._start_survival_from_row(n)
        except Exception as exc:
            if hasattr(self, "_floor_status_lbl"):
                self._floor_status_lbl.config(text="")
            messagebox.showerror("Could not start floor", str(exc))

    def _ensure_survival_canvas_size(self) -> None:
        self.root.update_idletasks()
        w = int(self._survival_canvas.winfo_width())
        h = int(self._survival_canvas.winfo_height())
        if w <= 2 or h <= 2:
            w = max(640, int(self.root.winfo_width()) - 24)
            h = max(360, int(self.root.winfo_height()) - 130)
            w, h = max(400, w), max(300, h)
            self._survival_canvas.config(width=w, height=h)
            self.root.update_idletasks()
        self._survival_cw = max(400, w)
        self._survival_ch = max(300, h)

    def _schedule_survival_tick(self) -> None:
        if self._survival_active:
            self._survival_after_id = self.root.after(
                SURVIVAL_FRAME_MS, self._survival_tick
            )

    def _start_survival_from_row(self, n: int) -> None:
        self._stop_survival()
        self._stop_nuke()
        self._period_rows = n
        if n < 1 or n > MAX_FLOOR:
            return

        self._survival_rows = n
        self._survival_start = time.monotonic()
        self._survival_spawn_accum = 0.0
        self._survival_shockwaves.clear()
        self._survival_giant_ball = None
        self._survival_player_hp = PLAYER_MAX_HP
        self._survival_invuln_until = 0.0
        self._walk_phase = 0
        self._survival_active = True
        if hasattr(self, "_survival_hp_lbl"):
            self._survival_hp_lbl.config(text=f"HP: {PLAYER_MAX_HP}")
        if hasattr(self, "_survival_time_lbl") and n <= 6:
            diff = ("easy", "light", "medium", "tough", "hard", "lava")[
                n - 1
            ]
            self._survival_time_lbl.config(
                text=(
                    f"Survive: 5:00 · Period {n} ({self._period_element_label(n)}) · {diff}"
                )
            )

        self._on_play_screen = False
        self._hide_play_bar()
        self._show_only(self.survival_screen)
        self._ensure_survival_canvas_size()

        cw = max(float(self._survival_cw), 400.0)
        ch = max(float(self._survival_ch), 300.0)
        floor_y = float(ch - 40)
        self._survival_px = cw / 2
        self._survival_py = floor_y
        self._survival_vy = 0.0
        self._jump_queued = False
        if n == 6:
            self._init_lava_level(cw, ch, floor_y)
        else:
            self._survival_platforms.clear()
            self._lava_surface_y = None

        self._draw_survival_room()
        self._survival_canvas.focus_set()
        self.root.focus_force()
        c = self._survival_canvas
        c.delete("dyn")
        self._draw_stickman(c, self._survival_px, self._survival_py, False)
        self.root.update_idletasks()
        self._schedule_survival_tick()

    def _init_lava_level(self, cw: float, ch: float, floor_y: float) -> None:
        """Row 6: reachable platform chain from the floor; lava rises; world scrolls upward."""
        self._survival_platforms.clear()
        self._lava_drop_ignore_deadline = 0.0
        self._lava_drop_ignore_y = -1e9
        self._lava_surface_y = float(ch) + 55.0
        margin = 44.0
        prev_cx = cw / 2
        y = floor_y - random.uniform(74, 96)
        min_first_batch = 88.0
        while y > min_first_batch:
            pw = random.uniform(120, min(235, cw - 2 * margin))
            dx = random.uniform(-LAVA_PLATFORM_REACH_X, LAVA_PLATFORM_REACH_X)
            cx = max(margin + pw / 2, min(cw - margin - pw / 2, prev_cx + dx))
            x1 = cx - pw / 2
            x2 = cx + pw / 2
            self._survival_platforms.append(
                {"x1": x1, "x2": x2, "y": y, "thick": float(LAVA_PLATFORM_THICK)}
            )
            prev_cx = cx
            y -= random.uniform(LAVA_PLATFORM_DY_MIN, LAVA_PLATFORM_DY_MAX)
        self._extend_lava_platforms_upward(cw, max_layers=LAVA_PLATFORMS_PER_SCROLL * 2)

    def _extend_lava_platforms_upward(self, cw: float, max_layers: int) -> None:
        """Add platforms above the current top, always within jump reach of a parent."""
        if not self._survival_platforms or max_layers <= 0:
            return
        margin = 44.0
        layers = 0
        while layers < max_layers:
            top_p = min(self._survival_platforms, key=lambda p: float(p["y"]))
            min_y = float(top_p["y"])
            if min_y < 62:
                break
            prev_cx = (float(top_p["x1"]) + float(top_p["x2"])) / 2
            dy = random.uniform(LAVA_PLATFORM_DY_MIN, LAVA_PLATFORM_DY_MAX)
            y_new = min_y - dy
            if y_new < 38:
                break
            dx = random.uniform(-LAVA_PLATFORM_REACH_X, LAVA_PLATFORM_REACH_X)
            pw = random.uniform(115, min(240, cw - 2 * margin))
            cx = prev_cx + dx
            cx = max(margin + pw / 2, min(cw - margin - pw / 2, cx))
            x1 = cx - pw / 2
            x1 = max(margin, min(x1, cw - margin - pw))
            x2 = x1 + pw
            self._survival_platforms.append(
                {"x1": x1, "x2": x2, "y": y_new, "thick": float(LAVA_PLATFORM_THICK)}
            )
            if random.random() < 0.28:
                pw2 = random.uniform(100, min(200, cw - 2 * margin))
                cx2 = prev_cx - dx * 0.4 + random.uniform(-90, 90)
                cx2 = max(margin + pw2 / 2, min(cw - margin - pw2 / 2, cx2))
                x1b = cx2 - pw2 / 2
                x1b = max(margin, min(x1b, cw - margin - pw2))
                self._survival_platforms.append(
                    {
                        "x1": x1b,
                        "x2": x1b + pw2,
                        "y": y_new + random.uniform(-4, 4),
                        "thick": float(LAVA_PLATFORM_THICK),
                    }
                )
            prev_cx = cx
            layers += 1

    def _extend_lava_platforms_downward(
        self, cw: float, floor_y: float, max_layers: int
    ) -> None:
        """Add platforms below the current lowest tier, toward the floor (for descending)."""
        if max_layers <= 0:
            return
        margin = 44.0
        target_top = floor_y - 14.0
        if self._survival_platforms:
            bot = max(self._survival_platforms, key=lambda p: float(p["y"]))
            prev_cx = (float(bot["x1"]) + float(bot["x2"])) / 2
            y = float(bot["y"])
        else:
            prev_cx = cw / 2
            y = floor_y - random.uniform(74, 96)
        layers = 0
        while layers < max_layers and y < target_top - 40:
            dy = random.uniform(LAVA_PLATFORM_DY_MIN, LAVA_PLATFORM_DY_MAX)
            y_new = y + dy
            if y_new >= target_top:
                break
            dx = random.uniform(-LAVA_PLATFORM_REACH_X, LAVA_PLATFORM_REACH_X)
            pw = random.uniform(115, min(240, cw - 2 * margin))
            cx = prev_cx + dx
            cx = max(margin + pw / 2, min(cw - margin - pw / 2, cx))
            x1 = cx - pw / 2
            x1 = max(margin, min(x1, cw - margin - pw))
            x2 = x1 + pw
            self._survival_platforms.append(
                {"x1": x1, "x2": x2, "y": y_new, "thick": float(LAVA_PLATFORM_THICK)}
            )
            prev_cx = cx
            y = y_new
            layers += 1

    def _scroll_lava_world(self, w: float, h: float, shift: float) -> None:
        """Shift player, lava, and platforms (positive = camera follows climb; negative = descend)."""
        self._survival_py += shift
        if self._lava_surface_y is not None:
            self._lava_surface_y += shift
        for p in self._survival_platforms:
            p["y"] = float(p["y"]) + shift
        self._survival_platforms = [
            p for p in self._survival_platforms if -140 < float(p["y"]) < h + 100
        ]
        for hz in self._survival_hazards:
            hz["y"] = float(hz["y"]) + shift
        for sw in self._survival_shockwaves:
            sw["cy"] = float(sw["cy"]) + shift
        gb = self._survival_giant_ball
        if gb is not None:
            gb["cy"] = float(gb["cy"]) + shift

    def _update_survival_hp_label(self) -> None:
        if hasattr(self, "_survival_hp_lbl"):
            self._survival_hp_lbl.config(text=f"HP: {max(0, self._survival_player_hp)}")

    def _try_player_damage(self, amount: int) -> bool:
        """Apply damage if not invulnerable. Returns True if the player dies (HP <= 0)."""
        now = time.monotonic()
        if amount <= 0 or now < self._survival_invuln_until:
            return False
        self._survival_player_hp -= amount
        self._survival_invuln_until = now + HIT_INVULN_S
        self._update_survival_hp_label()
        return self._survival_player_hp <= 0

    def _shockwave_hits_player(
        self, tcx: float, tcy: float, tr: float, cx: float, cy: float, r_blast: float
    ) -> bool:
        dx = tcx - cx
        dy = tcy - cy
        return dx * dx + dy * dy < (r_blast + tr) ** 2

    def _clamp_shockwave_cx(self, cx: float, r: float, w: float) -> float:
        pad = max(8.0, r * 0.08)
        return max(pad + r, min(float(w) - pad - r, cx))

    def _mixed_fusion_shockwave_split(
        self,
        w: float,
        h: float,
        tcx: float,
        tcy: float,
        tr: float,
        cx_f: float,
        cy_f: float,
        R: float,
    ) -> bool:
        """True if blast should split: fusion above player, aligned, and full circle would clip them."""
        m = min(float(w), float(h))
        if abs(cx_f - tcx) >= m * SHOCKWAVE_SPLIT_ALIGN_FRAC:
            return False
        if cy_f >= tcy - tr * 0.25:
            return False
        return self._shockwave_hits_player(tcx, tcy, tr, cx_f, cy_f, R)

    def _append_mixed_shockwaves(
        self,
        w: float,
        h: float,
        tcx: float,
        tcy: float,
        tr: float,
        cx_f: float,
        cy_f: float,
        R: float,
    ) -> bool:
        """Two fixed vertical shock columns; damage once if either hits. True if player died."""
        t0 = time.monotonic()
        col = "#88c8e8"
        split = self._mixed_fusion_shockwave_split(w, h, tcx, tcy, tr, cx_f, cy_f, R)
        sep = R * (
            VERT_SHOCK_PAIR_SEP_WIDE_FRAC if split else VERT_SHOCK_PAIR_SEP_FRAC
        )
        r_hit = R * VERT_SHOCK_DAMAGE_R_FRAC
        cx_l = self._clamp_shockwave_cx(cx_f - sep, r_hit, w)
        cx_r = self._clamp_shockwave_cx(cx_f + sep, r_hit, w)
        hit = False
        for cxl in (cx_l, cx_r):
            if self._shockwave_hits_player(tcx, tcy, tr, cxl, cy_f, r_hit):
                hit = True
                break
        if hit:
            if self._try_player_damage(DAMAGE_SHOCKWAVE_MIXED):
                self._survival_die()
                return True
        for cxl, wdir in ((cx_l, -1.0), (cx_r, 1.0)):
            self._survival_shockwaves.append(
                {
                    "cx": cxl,
                    "cy": cy_f,
                    "t0": t0,
                    "r_max": R,
                    "mega": False,
                    "style": "vert_wave",
                    "wave_dir": wdir,
                    "col": col,
                    "sym": "",
                }
            )
        return False

    def _resolve_hazard_fusions(
        self, w: float, h: float, tcx: float, tcy: float, tr: float
    ) -> bool:
        """Two hazards overlap → fuse. Mixed: two vertical shocks. Same: falling ⅔-screen ball + initial blast."""
        m = min(float(w), float(h))
        hz_list = self._survival_hazards
        changed = True
        outer = 0
        while changed and outer < FUSION_RESOLVE_MAX_OUTER:
            outer += 1
            changed = False
            for i in range(len(hz_list)):
                for j in range(i + 1, len(hz_list)):
                    a, b = hz_list[i], hz_list[j]
                    dist = math.hypot(a["x"] - b["x"], a["y"] - b["y"])
                    touch = float(a["r"]) + float(b["r"])
                    if dist > touch * HAZARD_FUSE_DIST_FRAC:
                        continue
                    cx_f = (float(a["x"]) + float(b["x"])) / 2
                    cy_f = (float(a["y"]) + float(b["y"])) / 2
                    same = str(a["sym"]) == str(b["sym"])
                    if same:
                        r_dmg = m * SHOCKWAVE_DAMAGE_FRAC_SAME
                        if self._shockwave_hits_player(
                            tcx, tcy, tr, cx_f, cy_f, r_dmg
                        ):
                            if self._try_player_damage(DAMAGE_SHOCKWAVE_SAME):
                                self._survival_die()
                                return True
                        hz_list.pop(j)
                        hz_list.pop(i)
                        r_ball = max(40.0, m * (GIANT_BALL_DIAMETER_FRAC / 2.0))
                        cx_i = max(r_ball + 10.0, min(float(w) - r_ball - 10.0, cx_f))
                        self._survival_giant_ball = {
                            "cx": cx_i,
                            "cy": cy_f,
                            "vy": GIANT_BALL_INITIAL_VY,
                            "r": r_ball,
                            "t_end": time.monotonic() + GIANT_BALL_DURATION_S,
                            "sym": str(a["sym"]),
                            "col": str(a["col"]),
                        }
                        changed = True
                        break
                    R = m * SHOCKWAVE_RADIUS_FRAC_MIXED
                    hz_list.pop(j)
                    hz_list.pop(i)
                    if self._append_mixed_shockwaves(w, h, tcx, tcy, tr, cx_f, cy_f, R):
                        return True
                    changed = True
                    break
                if changed:
                    break
        return False

    def _step_survival_shockwaves(self) -> None:
        now = time.monotonic()
        self._survival_shockwaves = [
            s
            for s in self._survival_shockwaves
            if now - float(s["t0"]) < SHOCKWAVE_DURATION_S
        ]

    def _draw_vertical_wave_shockwave(
        self,
        c: tk.Canvas,
        h: float,
        cx: float,
        r_max: float,
        col: str,
        elapsed: float,
        wave_dir: float,
    ) -> None:
        """One of two narrow vertical shocks: fixed width, ripples travel along Y (not widening)."""
        half_w = max(4.5, r_max * VERT_SHOCK_STRIP_HALF_FRAC)
        amp = max(3.5, half_w * 0.42)
        wavelength = 46.0
        k = 2 * math.pi / wavelength
        travel = elapsed * VERT_SHOCK_TRAVEL_SPEED * wave_dir
        y0, y1 = 0.0, float(h)
        step = 4.0

        pts_l: list[float] = []
        y = y0
        while y <= y1:
            wx = amp * math.sin(k * y - travel)
            pts_l.extend([cx - half_w + wx, y])
            y += step

        pts_r: list[float] = []
        y = y1
        while y >= y0:
            wx = amp * math.sin(k * y - travel + 1.15)
            pts_r.extend([cx + half_w - wx, y])
            y -= step

        poly = pts_l + pts_r
        if len(poly) >= 6:
            c.create_polygon(
                poly,
                fill=col,
                outline="#c8e8ff",
                width=2,
                tags="dyn",
            )

        for frac, spd in ((0.32, 1.25), (0.68, 0.85)):
            pl: list[float] = []
            yy = y0
            while yy <= y1:
                cx_line = cx - half_w + 2 * half_w * frac
                off = (
                    0.5
                    * amp
                    * math.sin(k * yy * 2.05 - travel * spd + frac * 5.0)
                )
                pl.extend([cx_line + off, yy])
                yy += 6.5
            if len(pl) >= 4:
                c.create_line(
                    pl,
                    fill="#f5fbff",
                    width=2,
                    smooth=True,
                    tags="dyn",
                )

    def _draw_survival_shockwaves(self, c: tk.Canvas, w: float, h: float) -> None:
        now = time.monotonic()
        for s in self._survival_shockwaves:
            t = (now - float(s["t0"])) / SHOCKWAVE_DURATION_S
            if t <= 0:
                continue
            cx, cy = float(s["cx"]), float(s["cy"])
            r_max = float(s["r_max"])
            mega = bool(s["mega"])
            style = str(s.get("style", "ring"))
            elapsed = now - float(s["t0"])

            if style == "vert_wave" and not mega:
                wave_dir = float(s.get("wave_dir", 1.0))
                self._draw_vertical_wave_shockwave(
                    c, h, cx, r_max, str(s["col"]), elapsed, wave_dir
                )
                continue

            ring = r_max * min(1.0, t * 1.22)
            outline = "#fff8e0" if mega else "#9ec8f0"
            width = 10 if mega else 4
            c.create_oval(
                cx - ring,
                cy - ring,
                cx + ring,
                cy + ring,
                outline=outline,
                width=width,
                tags="dyn",
            )
            core = ring * 0.12
            c.create_oval(
                cx - core,
                cy - core,
                cx + core,
                cy + core,
                fill=str(s["col"]),
                outline=outline,
                width=1,
                tags="dyn",
            )
            if mega and str(s["sym"]):
                c.create_text(
                    cx,
                    cy,
                    text=str(s["sym"]),
                    fill="#0d1117",
                    font=("Helvetica", max(16, int(r_max * 0.11)), "bold"),
                    tags="dyn",
                )

    def _hazard_contact_damage_tick(self, tcx: float, tcy: float, tr: float) -> bool:
        """Remove hazards that touch the player; deal bump damage. True = player died."""
        now = time.monotonic()
        i = 0
        while i < len(self._survival_hazards):
            hz = self._survival_hazards[i]
            dx = hz["x"] - tcx
            dy = hz["y"] - tcy
            if dx * dx + dy * dy < (hz["r"] + tr) ** 2:
                if now < self._survival_invuln_until:
                    i += 1
                    continue
                self._survival_hazards.pop(i)
                if self._try_player_damage(DAMAGE_HAZARD_BUMP):
                    self._survival_die()
                    return True
                continue
            i += 1
        return False

    def _spawn_survival_hazards_tick(self, w: float, h: float, dt: float, row: int) -> None:
        row = max(1, min(6, row))
        tuning = self._row_tuning(row)
        pool = PERIOD_RAIN_POOLS[row - 1]
        if not pool:
            return

        base_every = 0.30 * tuning.spawn_interval_mult
        spawn_every = max(
            HAZARD_SPAWN_EVERY_FLOOR,
            base_every / (HAZARD_RAIN_DENSITY_MULT * tuning.rain_density),
        )
        self._survival_spawn_accum += dt
        burst_cap = min(HAZARD_SPAWN_BURST_MAX, tuning.burst_max)
        spawns_left = min(
            burst_cap,
            max(1, int((6 + row * 2) * HAZARD_RAIN_DENSITY_MULT * tuning.rain_density)),
        )
        while self._survival_spawn_accum >= spawn_every and spawns_left > 0:
            spawns_left -= 1
            self._survival_spawn_accum -= spawn_every
            sym, col, atomic_z = random.choice(pool)
            game_z = self._game_z_for_row(row, atomic_z)
            margin = 32
            layer = random.randint(0, tuning.layer_max)
            y_spawn = -15.0 - layer * random.uniform(45, 95)
            r = self._hazard_radius_for_z(w, h, game_z)
            vy = self._hazard_vy_for_z(game_z, layer) * tuning.vy_mult
            x = self._pick_rain_spawn_x(w, h, margin)
            self._survival_hazards.append(
                {
                    "x": x,
                    "y": y_spawn,
                    "vx": random.uniform(-1.1, 1.1) * (0.6 + row * 0.08) * tuning.vx_mult,
                    "vy": vy,
                    "sym": sym,
                    "col": col,
                    "z": game_z,
                    "r": r,
                    "kind": random.choice(("gas", "gas", "pool", "shard")),
                }
            )

    def _integrate_survival_hazards(self, w: float, h: float) -> None:
        for hz in self._survival_hazards:
            hz["x"] += hz["vx"]
            hz["y"] += hz["vy"]
            hz["vx"] += random.uniform(-0.04, 0.04)
            if hz["x"] < hz["r"]:
                hz["x"] = hz["r"]
                hz["vx"] *= -0.5
            elif hz["x"] > w - hz["r"]:
                hz["x"] = w - hz["r"]
                hz["vx"] *= -0.5
        self._survival_hazards = [
            z for z in self._survival_hazards if -220 < z["y"] < h + 80
        ]
        if len(self._survival_hazards) > HAZARD_LIST_HARD_CAP:
            self._survival_hazards.sort(key=lambda z: float(z["y"]))
            self._survival_hazards = self._survival_hazards[-HAZARD_LIST_HARD_CAP:]

    def _draw_survival_hazards(self, c: tk.Canvas) -> None:
        for hz in self._survival_hazards:
            x, y, r = hz["x"], hz["y"], hz["r"]
            if hz["kind"] == "gas":
                c.create_oval(
                    x - r - 6,
                    y - r - 6,
                    x + r + 6,
                    y + r + 6,
                    fill="",
                    outline="#446644",
                    width=2,
                    tags="dyn",
                )
                c.create_oval(
                    x - r,
                    y - r,
                    x + r,
                    y + r,
                    fill=hz["col"],
                    outline="#2a5533",
                    width=2,
                    tags="dyn",
                )
            elif hz["kind"] == "shard":
                c.create_polygon(
                    x,
                    y - r,
                    x + r * 0.9,
                    y + r * 0.5,
                    x - r * 0.9,
                    y + r * 0.5,
                    fill=hz["col"],
                    outline="#332222",
                    width=2,
                    tags="dyn",
                )
            else:
                c.create_oval(
                    x - r,
                    y - r * 0.6,
                    x + r,
                    y + r * 0.6,
                    fill=hz["col"],
                    outline="#553322",
                    width=2,
                    tags="dyn",
                )
            sym_fill = "#0d1117" if hz["kind"] in ("gas", "shard") else "#1a1a1a"
            c.create_text(
                x,
                y,
                text=hz["sym"],
                fill=sym_fill,
                font=("Helvetica", max(9, int(r * 0.45)), "bold"),
                tags="dyn",
            )

    def _draw_stickman(self, c: tk.Canvas, px: float, py: float, duck: bool) -> None:
        phase = self._walk_phase * 0.25
        leg_s = 4.0 if (int(self._walk_phase) % 2 == 0) else -4.0
        if duck:
            c.create_line(px, py - 22, px, py - 6, fill=STICK, width=3, tags="dyn")
            c.create_oval(px - 9, py - 34, px + 9, py - 18, outline=STICK, width=3, tags="dyn")
            c.create_line(px, py - 6, px - 10, py, fill=STICK, width=3, tags="dyn")
            c.create_line(px, py - 6, px + 10, py, fill=STICK, width=3, tags="dyn")
            c.create_line(
                px - 6, py - 14, px - 14, py - 10, fill=STICK, width=3, tags="dyn"
            )
            c.create_line(
                px + 6, py - 14, px + 14, py - 10, fill=STICK, width=3, tags="dyn"
            )
        else:
            c.create_line(px, py - 38, px, py - 8, fill=STICK, width=3, tags="dyn")
            c.create_oval(px - 10, py - 50, px + 10, py - 30, outline=STICK, width=3, tags="dyn")
            c.create_line(
                px, py - 8, px - 12 + leg_s, py, fill=STICK, width=3, tags="dyn"
            )
            c.create_line(
                px, py - 8, px + 12 - leg_s, py, fill=STICK, width=3, tags="dyn"
            )
            c.create_line(
                px - 8,
                py - 28,
                px - 18,
                py - 18 + math.sin(phase) * 2,
                fill=STICK,
                width=3,
                tags="dyn",
            )
            c.create_line(
                px + 8,
                py - 28,
                px + 18,
                py - 18 - math.sin(phase) * 2,
                fill=STICK,
                width=3,
                tags="dyn",
            )

    def _play_nuke_cutscene(self) -> None:
        self._stop_survival()
        self._stop_nuke()
        self._title_active = False
        self._on_play_screen = False
        self._hide_play_bar()
        self._nuke_start = time.monotonic()
        self._show_only(self.nuke_screen)
        self._nuke_canvas.focus_set()
        self._nuke_tick()

    def _nuke_tick(self) -> None:
        c = self._nuke_canvas
        w, h = self._nuke_cw, self._nuke_ch
        if w <= 2 or h <= 2:
            self._nuke_after_id = self.root.after(NUKE_FRAME_MS, self._nuke_tick)
            return

        elapsed = time.monotonic() - self._nuke_start
        if elapsed >= NUKE_CUTSCENE_SECONDS:
            self._stop_nuke()
            messagebox.showinfo(
                "Total meltdown",
                "You picked row 7. The building didn't survive.",
            )
            self.show_play_screen()
            return

        t = min(1.0, elapsed / (NUKE_CUTSCENE_SECONDS * 0.92))
        c.delete("all")
        draw_building_scene(c, w, h)
        draw_nuke_explosion(c, w, h, t)

        self._nuke_after_id = self.root.after(NUKE_FRAME_MS, self._nuke_tick)

    def _survival_forfeit(self) -> None:
        if not self._survival_active:
            return
        if messagebox.askyesno("Leave", "Leave the building? Your run will end."):
            self._stop_survival()
            self.show_play_screen()

    def _survival_win(self) -> None:
        self._stop_survival()

        def go() -> None:
            self.show_play_screen()

        self._show_end_banner("You won!", "#0f3d28", go)

    def _survival_die(self) -> None:
        self._stop_survival()

        def go() -> None:
            self.show_play_screen()

        self._show_end_banner("You died", "#4a1212", go)

    def _draw_survival_room(self) -> None:
        c = self._survival_canvas
        c.delete("room")
        w, h = self._survival_cw, self._survival_ch
        if w <= 1 or h <= 1:
            return
        floor_y = h - 40
        c.create_rectangle(0, 0, w, h, fill="#12151f", outline="", tags="room")
        c.create_rectangle(0, floor_y, w, h, fill="#1e2433", outline="", tags="room")
        c.create_line(0, floor_y, w, floor_y, fill="#3d4458", width=2, tags="room")
        c.create_rectangle(0, 0, w, 36, fill="#0e1118", outline="", tags="room")
        row = self._survival_rows
        period = self._period_element_label(row)
        if row == 6:
            hint = (
                f"Period 6 only ({period}) · rising lava · very heavy rain · "
                "mixed → vertical shocks · same → falling ball · 5 HP"
            )
        elif row == 1:
            hint = (
                f"Period 1 only ({period}) · gentle rain · "
                "mixed → vertical shocks · same → falling ball · 5 HP"
            )
        elif row >= 5:
            hint = (
                f"Period {row} only ({period}) · intense rain · "
                "mixed → vertical shocks · same → falling ball · 5 HP"
            )
        else:
            hint = (
                f"Period {row} only ({period}) · "
                "mixed → vertical shocks · same → falling ball · 5 HP"
            )
        c.create_text(
            16,
            18,
            text=hint,
            anchor=tk.W,
            fill="#8b90a0",
            font=("Helvetica", 12),
            tags="room",
        )

    def _survival_tick_row6_lava(
        self,
        c: tk.Canvas,
        w: int,
        h: int,
        dt: float,
        elapsed: float,
        floor_y: float,
    ) -> None:
        """Row 6: rising lava, platforms, falling elements, fusions & shockwaves."""
        assert self._lava_surface_y is not None
        ls = self._lava_surface_y
        lava_mult = self._row_tuning(6).lava_rise_mult
        rise = (
            LAVA_RISE_BASE_PX_S + (elapsed / 60.0) * LAVA_RISE_RAMP_PER_MIN
        ) * lava_mult
        self._lava_surface_y = ls - rise * dt

        now = time.monotonic()
        self._spawn_survival_hazards_tick(w, h, dt, 6)
        self._integrate_survival_hazards(w, h)

        px = self._survival_px
        speed = 6.2 * (dt * 60)
        moving = False
        if "Left" in self._survival_keys or "a" in self._survival_keys:
            self._survival_px -= speed
            moving = True
        if "Right" in self._survival_keys or "d" in self._survival_keys:
            self._survival_px += speed
            moving = True
        if moving:
            self._walk_phase += 1

        pad = 28.0
        self._survival_px = max(pad, min(w - pad, self._survival_px))
        px = self._survival_px

        on_support_jump = False
        if self._lava_surface_y > floor_y + 12 and abs(self._survival_py - floor_y) < 8:
            on_support_jump = True
        for p in self._survival_platforms:
            if self._lava_surface_y <= p["y"] + 8:
                continue
            if (
                p["x1"] - 4 <= px <= p["x2"] + 4
                and abs(self._survival_py - float(p["y"])) < 8
            ):
                on_support_jump = True
                break

        if self._jump_queued:
            if on_support_jump:
                self._survival_vy = JUMP_VELOCITY
            else:
                self._survival_vy = JUMP_VELOCITY_AIR
            self._jump_queued = False

        if (
            "down" in self._survival_keys
            and abs(self._survival_vy) < 55
        ):
            for p in self._survival_platforms:
                if self._lava_surface_y <= p["y"] + 8:
                    continue
                if (
                    p["x1"] - 4 <= px <= p["x2"] + 4
                    and abs(self._survival_py - float(p["y"])) < 8
                ):
                    self._lava_drop_ignore_deadline = now + LAVA_DROP_IGNORE_S
                    self._lava_drop_ignore_y = float(p["y"])
                    self._survival_py = float(p["y"]) + 10
                    self._survival_vy = 280.0
                    break

        prev_py = self._survival_py
        self._survival_vy += GRAVITY_PX_S2 * dt
        in_air = True
        for p in self._survival_platforms:
            if (
                p["x1"] - 4 <= px <= p["x2"] + 4
                and abs(self._survival_py - p["y"]) < 6
                and abs(self._survival_vy) < 80
            ):
                in_air = False
                break
        if self._lava_surface_y > floor_y + 12 and abs(self._survival_py - floor_y) < 6:
            in_air = False
        if in_air and "s" in self._survival_keys:
            self._survival_vy += FAST_FALL_BOOST * dt

        self._survival_py += self._survival_vy * dt

        safe_floor = self._lava_surface_y > floor_y + 10
        landed = False
        if self._survival_vy >= 0:
            for p in sorted(
                self._survival_platforms, key=lambda z: float(z["y"]), reverse=True
            ):
                if self._lava_surface_y <= p["y"] + 8:
                    continue
                if now < self._lava_drop_ignore_deadline and abs(
                    float(p["y"]) - self._lava_drop_ignore_y
                ) < 1.5:
                    continue
                if (
                    p["x1"] - 4 <= px <= p["x2"] + 4
                    and prev_py <= float(p["y"]) + 1.0
                    and self._survival_py >= float(p["y"])
                ):
                    self._survival_py = float(p["y"])
                    self._survival_vy = 0.0
                    landed = True
                    break
            if not landed and safe_floor:
                if prev_py <= floor_y + 1.0 and self._survival_py >= floor_y:
                    self._survival_py = floor_y
                    self._survival_vy = 0.0
                    landed = True

        py = self._survival_py
        on_support = landed or (
            abs(py - floor_y) < 3 and safe_floor and self._survival_vy == 0
        )
        if not on_support:
            for p in self._survival_platforms:
                if (
                    self._lava_surface_y > p["y"] + 8
                    and p["x1"] - 4 <= px <= p["x2"] + 4
                    and abs(py - float(p["y"])) < 3
                    and self._survival_vy == 0
                ):
                    on_support = True
                    break

        duck = (
            "s" in self._survival_keys
            and on_support
            and abs(self._survival_vy) < 100.0
        )

        guard = 0
        while self._survival_py < LAVA_SCROLL_TRIGGER_Y and guard < 30:
            guard += 1
            self._scroll_lava_world(w, h, LAVA_SCROLL_CHUNK)
            self._extend_lava_platforms_upward(w, LAVA_PLATFORMS_PER_SCROLL)

        guard_d = 0
        scroll_down_py = float(h) - LAVA_SCROLL_DOWN_MARGIN
        while self._survival_py > scroll_down_py and guard_d < 30:
            guard_d += 1
            self._scroll_lava_world(w, h, -LAVA_SCROLL_CHUNK)
            self._extend_lava_platforms_downward(w, floor_y, LAVA_PLATFORMS_PER_SCROLL_DOWN)

        py = self._survival_py
        if duck:
            tcx, tcy, tr = px, py - 18.0, 14.0
        else:
            tcx, tcy, tr = px, py - 30.0, 22.0

        lava_line = self._lava_surface_y
        if py >= lava_line - 8:
            self._survival_die()
            return
        if tcy >= lava_line - 4:
            self._survival_die()
            return

        if self._resolve_hazard_fusions(w, h, tcx, tcy, tr):
            return
        if self._hazard_contact_damage_tick(tcx, tcy, tr):
            return
        if self._try_giant_ball_contact_damage(tcx, tcy, tr):
            return

        c.delete("dyn")
        for p in self._survival_platforms:
            if self._lava_surface_y <= p["y"] + 3:
                continue
            x1, x2, yp = float(p["x1"]), float(p["x2"]), float(p["y"])
            th = float(p.get("thick", LAVA_PLATFORM_THICK))
            c.create_rectangle(
                x1,
                yp - th,
                x2,
                yp,
                fill="#4a4038",
                outline="#2a2520",
                width=2,
                tags="dyn",
            )
            c.create_line(x1, yp, x2, yp, fill="#6a6055", width=2, tags="dyn")

        self._draw_survival_giant_ball(c, float(w), float(h))
        self._draw_survival_hazards(c)

        ly = max(0.0, min(float(h), lava_line))
        c.create_rectangle(0, ly, w, h, fill="#4a1508", outline="", tags="dyn")
        c.create_rectangle(0, ly, w, min(h, ly + 28), fill="#cc3300", outline="", tags="dyn")
        c.create_rectangle(0, ly, w, min(h, ly + 12), fill="#ff9933", outline="", tags="dyn")
        for bx in range(0, w, 55):
            bub = (bx + (int(elapsed * 40) % 55)) % w
            c.create_oval(
                bub,
                ly + 8,
                bub + 14,
                ly + 26,
                fill="#ffcc66",
                outline="",
                tags="dyn",
            )
        c.create_text(
            w // 2,
            ly - 18,
            text="Ra",
            fill="#ffee88",
            font=("Helvetica", 14, "bold"),
            tags="dyn",
        )

        self._draw_survival_shockwaves(c, float(w), float(h))

        self._draw_stickman(c, px, py, duck)

        self._schedule_survival_tick()

    def _survival_tick(self) -> None:
        if not self._survival_active:
            return

        c = self._survival_canvas
        w, h = self._survival_cw, self._survival_ch
        if w <= 2 or h <= 2:
            self._ensure_survival_canvas_size()
            w, h = self._survival_cw, self._survival_ch
            if w <= 2 or h <= 2:
                self._schedule_survival_tick()
                return

        dt = SURVIVAL_FRAME_MS / 1000.0
        elapsed = time.monotonic() - self._survival_start
        remaining = SURVIVE_SECONDS - elapsed

        if remaining <= 0:
            self._survival_win()
            return

        self._step_survival_shockwaves()
        floor_y_tick = float(h - 40)
        lava_gl = self._lava_surface_y if self._survival_rows == 6 else None
        self._integrate_survival_giant_ball(float(w), float(h), dt, floor_y_tick, lava_gl)

        m = int(remaining // 60)
        s = int(remaining % 60)
        rows = self._survival_rows

        if rows == 6 and self._lava_surface_y is not None:
            self._survival_time_lbl.config(
                text=f"Survive: {m}:{s:02d}  ·  lava + falling elements"
            )
            self._survival_tick_row6_lava(
                c, w, h, dt, elapsed, floor_y=float(h - 40)
            )
            return

        self._survival_time_lbl.config(text=f"Survive: {m}:{s:02d}")

        self._spawn_survival_hazards_tick(w, h, dt, rows)
        self._integrate_survival_hazards(w, h)

        floor_y = float(h - 40)
        speed = (5.5 + min(rows, 6) * 0.35) * (dt * 60)
        moving = False
        if "Left" in self._survival_keys or "a" in self._survival_keys:
            self._survival_px -= speed
            moving = True
        if "Right" in self._survival_keys or "d" in self._survival_keys:
            self._survival_px += speed
            moving = True
        if moving:
            self._walk_phase += 1

        pad = 28.0
        self._survival_px = max(pad, min(w - pad, self._survival_px))

        on_support_jump = (
            self._survival_py >= floor_y - 2.0 and abs(self._survival_vy) < 130.0
        )

        if self._jump_queued:
            if on_support_jump:
                self._survival_vy = JUMP_VELOCITY
            else:
                self._survival_vy = JUMP_VELOCITY_AIR
            self._jump_queued = False

        if self._survival_py < floor_y - 0.5:
            self._survival_vy += GRAVITY_PX_S2 * dt
            if "s" in self._survival_keys:
                self._survival_vy += FAST_FALL_BOOST * dt

        self._survival_py += self._survival_vy * dt
        if self._survival_py >= floor_y:
            self._survival_py = floor_y
            if self._survival_vy > 0.0:
                self._survival_vy = 0.0

        duck = (
            "s" in self._survival_keys
            and self._survival_py >= floor_y - 1.0
            and abs(self._survival_vy) < 120.0
        )
        if duck:
            tcx = self._survival_px
            tcy = self._survival_py - 18.0
            tr = 14.0
        else:
            tcx = self._survival_px
            tcy = self._survival_py - 30.0
            tr = 22.0

        if self._resolve_hazard_fusions(w, h, tcx, tcy, tr):
            return
        if self._hazard_contact_damage_tick(tcx, tcy, tr):
            return
        if self._try_giant_ball_contact_damage(tcx, tcy, tr):
            return

        c.delete("dyn")
        px, py = self._survival_px, self._survival_py
        self._draw_survival_giant_ball(c, float(w), float(h))
        self._draw_survival_hazards(c)
        self._draw_survival_shockwaves(c, float(w), float(h))
        self._draw_stickman(c, px, py, duck)

        self._schedule_survival_tick()

    def _build_title_screen(self) -> tk.Frame:
        frame = tk.Frame(self.container, bg=BG)

        header = tk.Frame(frame, bg=BG)
        header.pack(side=tk.TOP, fill=tk.X, padx=16, pady=(16, 10))

        tk.Label(
            header,
            text="The Periodic Wall of Elements",
            font=self.title_font,
            fg=TITLE_FG,
            bg=BG,
            wraplength=780,
            justify=tk.CENTER,
        ).pack(pady=(0, 8))

        tk.Label(
            header,
            text="Press Enter or click Play — then pick a floor (1–7).",
            font=self.sub_font,
            fg="#8b90a0",
            bg=BG,
        ).pack(pady=(0, 16))

        btns = tk.Frame(header, bg=BG)
        btns.pack()
        self._styled_button(btns, "Play", self.show_play_screen).pack(side=tk.LEFT, padx=10)
        self._styled_button(btns, "Quit", self._on_close_window).pack(side=tk.LEFT, padx=10)

        canvas = tk.Canvas(frame, highlightthickness=0, bd=0, bg=BG)
        canvas.pack(fill=tk.BOTH, expand=True)

        def on_title_configure(e: tk.Event) -> None:
            if e.widget is not canvas:
                return
            draw_wall_scene(canvas, e.width, e.height)

        canvas.bind("<Configure>", on_title_configure)

        return frame

    def _build_play_bar(self) -> tk.Frame:
        """Floor picker lives on the root window so hidden screens cannot block clicks."""
        bar = tk.Frame(self.root, bg="#1e2433", padx=12, pady=10)

        top_row = tk.Frame(bar, bg="#1e2433")
        top_row.pack(fill=tk.X)
        self._styled_button(top_row, "Back to title", self.show_title_screen).pack(
            side=tk.LEFT, padx=(0, 12)
        )

        tk.Label(
            bar,
            text="FLOORS — click a number or press 1–7 on the keyboard",
            font=self.btn_font,
            fg="#e8ecf4",
            bg="#1e2433",
        ).pack(pady=(6, 8))

        row_fr = tk.Frame(bar, bg="#1e2433")
        row_fr.pack()
        floor_font = tkfont.Font(family="Helvetica", size=24, weight="bold")
        for n in range(1, 8):
            tk.Button(
                row_fr,
                text=str(n),
                font=floor_font,
                fg=TITLE_FG,
                bg=ROW_BTN_IDLE,
                activeforeground=TITLE_FG,
                activebackground="#5a6a88",
                relief=tk.RAISED,
                bd=3,
                width=2,
                padx=16,
                pady=8,
                cursor="hand2",
                takefocus=False,
                command=lambda v=n: self._pick_row(v),
            ).pack(side=tk.LEFT, padx=6)

        self._floor_status_lbl = tk.Label(
            bar,
            text="",
            font=self.sub_font,
            fg="#7ec8a0",
            bg="#1e2433",
        )
        self._floor_status_lbl.pack(pady=(8, 0))

        tk.Label(
            bar,
            text="1=H–He  2=Li–Ne  3=Na–Ar  4=K–Kr  5=Rb–Xe  6=Cs–Rn  7=meltdown",
            font=self.sub_font,
            fg="#8b90a0",
            bg="#1e2433",
        ).pack(pady=(4, 0))

        return bar

    def _show_play_bar(self) -> None:
        self._play_bar.pack(side=tk.TOP, fill=tk.X, before=self.container)
        self._play_bar.lift()

    def _hide_play_bar(self) -> None:
        self._play_bar.pack_forget()

    def _build_play_screen(self) -> tk.Frame:
        """Wall art only — floor buttons are on self._play_bar (root window)."""
        frame = tk.Frame(self.container, bg=BG)

        self._rows_hint = tk.Label(
            frame,
            text="Each floor uses only that period's elements. Row 1 = very easy · Row 5 = hard · Row 6 = lava",
            font=self.sub_font,
            fg="#8b90a0",
            bg=BG,
            wraplength=760,
            justify=tk.CENTER,
        )
        self._rows_hint.pack(pady=(8, 4))

        self._play_canvas = tk.Canvas(
            frame, highlightthickness=0, bd=0, bg=BG, takefocus=False
        )
        self._play_canvas.pack(fill=tk.BOTH, expand=True)

        def on_play_configure(e: tk.Event) -> None:
            if e.widget is not self._play_canvas:
                return
            draw_wall_scene(self._play_canvas, e.width, e.height)

        self._play_canvas.bind("<Configure>", on_play_configure)

        def on_wall_click(_e: tk.Event) -> None:
            if hasattr(self, "_floor_status_lbl"):
                self._floor_status_lbl.config(
                    text="Use the FLOORS bar at the very top (1–7), not the bricks."
                )

        self._play_canvas.bind("<Button-1>", on_wall_click)

        return frame

    def _build_survival_screen(self) -> tk.Frame:
        frame = tk.Frame(self.container, bg=BG)

        hud = tk.Frame(frame, bg=BG)
        hud.pack(fill=tk.X, padx=10, pady=8)

        hud_top = tk.Frame(hud, bg=BG)
        hud_top.pack(fill=tk.X)
        self._styled_button(hud_top, "Leave building", self._survival_forfeit).pack(
            side=tk.RIGHT
        )

        self._survival_time_lbl = tk.Label(
            hud_top,
            text="Survive: 5:00",
            font=self.btn_font,
            bg=BG,
            fg=TITLE_FG,
        )
        self._survival_time_lbl.pack(side=tk.LEFT)

        self._survival_hp_lbl = tk.Label(
            hud_top,
            text=f"HP: {PLAYER_MAX_HP}",
            font=self.btn_font,
            bg=BG,
            fg="#7ec8a0",
        )
        self._survival_hp_lbl.pack(side=tk.LEFT, padx=(16, 0))

        tk.Label(
            hud,
            text="WASD move · W/↑ jump · S duck on ground",
            font=self.sub_font,
            bg=BG,
            fg="#8b90a0",
        ).pack(fill=tk.X, anchor=tk.W, pady=(6, 0))

        self._survival_canvas = tk.Canvas(
            frame, highlightthickness=0, bd=0, bg="#12151f", takefocus=True
        )
        self._survival_canvas.pack(fill=tk.BOTH, expand=True)

        def on_survival_configure(e: tk.Event) -> None:
            if e.widget is not self._survival_canvas:
                return
            self._survival_cw = e.width
            self._survival_ch = e.height
            if self._survival_active:
                self._draw_survival_room()

        self._survival_canvas.bind("<Configure>", on_survival_configure)
        self._survival_canvas.bind(
            "<Button-1>", lambda _e: self._survival_canvas.focus_set()
        )

        return frame

    def _build_nuke_screen(self) -> tk.Frame:
        frame = tk.Frame(self.container, bg=BG)
        self._nuke_canvas = tk.Canvas(
            frame, highlightthickness=0, bd=0, bg=BG
        )
        self._nuke_canvas.pack(fill=tk.BOTH, expand=True)

        def on_nuke_configure(e: tk.Event) -> None:
            if e.widget is not self._nuke_canvas:
                return
            self._nuke_cw = e.width
            self._nuke_ch = e.height

        self._nuke_canvas.bind("<Configure>", on_nuke_configure)
        return frame

    def _show_only(self, screen: tk.Frame) -> None:
        screen.tkraise()
        self.root.update_idletasks()

    def show_title_screen(self) -> None:
        self._cancel_banner_anim()
        self._stop_survival()
        self._stop_nuke()
        self._title_active = True
        self._on_play_screen = False
        self._hide_play_bar()
        self._show_only(self.title_screen)

    def show_play_screen(self) -> None:
        self._cancel_banner_anim()
        self._stop_survival()
        self._stop_nuke()
        self._title_active = False
        self._on_play_screen = True
        self._show_play_bar()
        self._show_only(self.play_screen)
        if hasattr(self, "_floor_status_lbl"):
            self._floor_status_lbl.config(text="")
        self.root.update_idletasks()
        pw = int(self._play_canvas.winfo_width())
        ph = int(self._play_canvas.winfo_height())
        if pw <= 2 or ph <= 2:
            pw = max(400, int(self.root.winfo_width()) - 24)
            ph = max(200, int(self.root.winfo_height()) - 260)
            self._play_canvas.config(width=pw, height=ph)
            self.root.update_idletasks()
        if pw > 2 and ph > 2:
            draw_wall_scene(self._play_canvas, pw, ph)
        self.root.focus_set()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    PeriodicWallApp().run()


if __name__ == "__main__":
    main()
