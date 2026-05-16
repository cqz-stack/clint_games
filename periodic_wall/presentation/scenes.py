"""Draw lists for v0 (testable without pixels)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any

from game.data import PERIOD_1_ELEMENTS
from game.models import Ball, GameState

BG = "#142033"
LAB_BG = "#0e1a2e"
FLOOR_TOP = "#d4a574"
FLOOR_BODY = "#8a5a30"
TITLE_FG = "#ffffff"
ACCENT = "#5fd3bb"
BRICK_FACE = "#c46a52"
BRICK_EDGE = "#8f3d2a"
MORTAR = "#2a2d3d"
STICK = "#ffffff"
HUD_FG = "#ffd866"

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


class PrimKind(Enum):
    RECT = auto()
    OVAL = auto()
    LINE = auto()
    TEXT = auto()
    ARC = auto()


@dataclass(frozen=True)
class DrawPrim:
    kind: PrimKind
    args: tuple[Any, ...]
    kwargs: dict[str, Any]


def paint_title_wall_scene(canvas, w: int, h: int) -> None:
    """Title art — direct Tk canvas calls (matches proven reference/periodic.py)."""
    if w < 10 or h < 10:
        return
    canvas.delete("scene")
    canvas.create_rectangle(0, 0, w, h, fill=BG, outline="", tags="scene")
    canvas.create_text(
        w / 2,
        h * 0.12,
        text="The Periodic Wall of Elements",
        fill=TITLE_FG,
        font=("Helvetica", 26, "bold"),
        tags="scene",
    )
    canvas.create_text(
        w / 2,
        h * 0.20,
        text="Version 0 — Level 1 only · dodge the element rain",
        fill="#8b90a0",
        font=("Helvetica", 13),
        tags="scene",
    )

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
    canvas.create_line(x_shoulder, y_body, x_hip, y_body, fill=STICK, width=3, tags="scene")
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


def build_title_draw_list(w: int, h: int) -> list[DrawPrim]:
    prims: list[DrawPrim] = [
        DrawPrim(PrimKind.RECT, (0, 0, w, h), {"fill": BG, "tag": "scene"}),
    ]
    margin_x = max(24, int(w * 0.04))
    row_y = int(h * 0.62)
    row_h = max(56, min(88, int(h * 0.14)))
    inner_w = w - 2 * margin_x
    n = len(PERIOD_4)
    gap = 3
    brick_w = (inner_w - gap * (n - 1)) / n
    for i, (z, sym) in enumerate(PERIOD_4):
        x0 = margin_x + i * (brick_w + gap)
        x1 = x0 + brick_w
        y0, y1 = row_y, row_y + row_h
        prims.append(
            DrawPrim(PrimKind.RECT, (x0, y0, x1, y1), {"fill": BRICK_EDGE, "tag": "brick"})
        )
        prims.append(
            DrawPrim(
                PrimKind.RECT,
                (x0 + 2, y0 + 2, x1 - 2, y1 - 2),
                {"fill": BRICK_FACE, "outline": MORTAR, "tag": "brick"},
            )
        )
        prims.append(
            DrawPrim(
                PrimKind.TEXT,
                ((x0 + x1) / 2, y0 + row_h * 0.68),
                {"text": sym, "fill": TITLE_FG, "tag": "brick"},
            )
        )
    brick_count = sum(1 for p in prims if p.kwargs.get("tag") == "brick")
    prims.append(
        DrawPrim(
            PrimKind.TEXT,
            (w / 2, h * 0.2),
            {"text": "The Periodic Wall of Elements", "tag": "title"},
        )
    )
    return prims


def _stickman_prims(px: float, py: float, duck: bool, walk_phase: int) -> list[DrawPrim]:
    import math

    prims: list[DrawPrim] = []
    phase = walk_phase * 0.25
    leg_s = 6.0 if (walk_phase % 2 == 0) else -6.0
    if duck:
        prims.append(
            DrawPrim(
                PrimKind.LINE,
                (px, py - 30, px, py - 8),
                {"fill": STICK, "width": 4, "tag": "stickman"},
            )
        )
        prims.append(
            DrawPrim(
                PrimKind.OVAL,
                (px - 13, py - 48, px + 13, py - 24),
                {"outline": STICK, "width": 3, "tag": "stickman"},
            )
        )
    else:
        prims.append(
            DrawPrim(
                PrimKind.LINE,
                (px, py - 54, px, py - 12),
                {"fill": STICK, "width": 4, "tag": "stickman"},
            )
        )
        prims.append(
            DrawPrim(
                PrimKind.OVAL,
                (px - 14, py - 72, px + 14, py - 44),
                {"outline": STICK, "width": 3, "tag": "stickman"},
            )
        )
        prims.append(
            DrawPrim(
                PrimKind.LINE,
                (px, py - 12, px - 16 + leg_s, py),
                {"fill": STICK, "width": 4, "tag": "stickman"},
            )
        )
        prims.append(
            DrawPrim(
                PrimKind.LINE,
                (px, py - 12, px + 16 - leg_s, py),
                {"fill": STICK, "width": 4, "tag": "stickman"},
            )
        )
        prims.append(
            DrawPrim(
                PrimKind.LINE,
                (px - 12, py - 40, px - 22, py - 28 + math.sin(phase) * 4),
                {"fill": STICK, "width": 4, "tag": "stickman"},
            )
        )
        prims.append(
            DrawPrim(
                PrimKind.LINE,
                (px + 12, py - 40, px + 22, py - 28 - math.sin(phase) * 4),
                {"fill": STICK, "width": 4, "tag": "stickman"},
            )
        )
    return prims


def _ball_prims(ball: Ball) -> list[DrawPrim]:
    x, y, r = ball.x, ball.y, ball.r
    return [
        DrawPrim(
            PrimKind.OVAL,
            (x - r, y - r, x + r, y + r),
            {"fill": ball.col, "outline": "#ffffff", "width": 2, "tag": "ball"},
        ),
        DrawPrim(
            PrimKind.TEXT,
            (x, y),
            {
                "text": ball.sym,
                "fill": "#0a1320",
                "font": ("Helvetica", max(10, int(r * 0.8)), "bold"),
                "tag": "ball",
            },
        ),
    ]


def build_lab_draw_list(state: GameState) -> list[DrawPrim]:
    w, h = int(state.room_w), int(state.room_h)
    prims: list[DrawPrim] = [
        DrawPrim(PrimKind.RECT, (0, 0, w, h), {"fill": LAB_BG, "tag": "room"}),
    ]
    prims.append(
        DrawPrim(
            PrimKind.RECT,
            (3, 3, w - 3, h - 3),
            {"outline": ACCENT, "width": 4, "tag": "border"},
        )
    )
    floor_y = h - 60
    prims.append(
        DrawPrim(
            PrimKind.RECT,
            (0, floor_y, w, h),
            {"fill": FLOOR_BODY, "tag": "floor"},
        )
    )
    prims.append(
        DrawPrim(
            PrimKind.LINE,
            (0, floor_y, w, floor_y),
            {"fill": FLOOR_TOP, "width": 4, "tag": "floor"},
        )
    )
    for ball in state.balls:
        prims.extend(_ball_prims(ball))
    prims.extend(
        _stickman_prims(
            state.player.px,
            state.player.py,
            False,
            state.player.walk_phase,
        )
    )
    m = int(state.time_left // 60)
    s = int(state.time_left % 60)
    prims.append(
        DrawPrim(
            PrimKind.TEXT,
            (w / 2, 32),
            {
                "text": f"LEVEL 1   ·   HP {state.hearts}/5   ·   {m}:{s:02d}",
                "fill": HUD_FG,
                "font": ("Helvetica", 22, "bold"),
                "tag": "hud",
            },
        )
    )
    prims.append(
        DrawPrim(
            PrimKind.TEXT,
            (w / 2, 62),
            {
                "text": "A/D or ← → to move · W or ↑ to jump · dodge the falling H, He, D, T",
                "fill": "#ffffff",
                "font": ("Helvetica", 13),
                "tag": "hud",
            },
        )
    )
    return prims


def build_end_draw_list(won: bool, w: int, h: int) -> list[DrawPrim]:
    msg = "You won!" if won else "You died"
    color = "#0f3d28" if won else "#4a1212"
    return [
        DrawPrim(PrimKind.RECT, (0, 0, w, h), {"fill": BG}),
        DrawPrim(PrimKind.RECT, (0, h // 2 - 43, w, h // 2 + 43), {"fill": color}),
        DrawPrim(PrimKind.TEXT, (w / 2, h // 2), {"text": msg, "tag": "banner"}),
    ]


def has_forbidden_v0_layers(prims: list[DrawPrim]) -> bool:
    forbidden = ("giant_ball", "fusion", "lava", "shockwave")
    for p in prims:
        tag = str(p.kwargs.get("tag", ""))
        if any(f in tag for f in forbidden):
            return True
    return False


def paint_to_canvas(canvas, prims: list[DrawPrim]) -> None:
    canvas.delete("all")
    for p in prims:
        kw = {k: v for k, v in p.kwargs.items() if k != "tag"}
        tag = p.kwargs.get("tag", "draw")
        if p.kind == PrimKind.RECT:
            canvas.create_rectangle(*p.args, **kw, tags=tag)
        elif p.kind == PrimKind.OVAL:
            canvas.create_oval(*p.args, **kw, tags=tag)
        elif p.kind == PrimKind.LINE:
            canvas.create_line(*p.args, **kw, tags=tag)
        elif p.kind == PrimKind.TEXT:
            if len(p.args) < 2:
                continue
            tx, ty = float(p.args[0]), float(p.args[1])
            kw.setdefault("fill", TITLE_FG)
            canvas.create_text(tx, ty, **kw, tags=tag)
        elif p.kind == PrimKind.ARC:
            canvas.create_arc(*p.args, **kw, tags=tag)
