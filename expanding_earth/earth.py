#!/usr/bin/env python3
"""Expanding Earth — race 5 screens to the finish before the world crushes you.

Run standalone:
    /opt/anaconda3/bin/python3.12 earth.py

Or open it from the What If? hub.
"""

from __future__ import annotations

import math
import random
import sys
import time
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from tkinter import font as tkfont
from tkinter import messagebox

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from shared_sfx import SFX  # noqa: E402


BG = "#141810"
SKY = "#1c2830"
GROUND = "#3a4a32"
DIRT = "#2a3424"
ACCENT = "#6a9e4c"
TITLE_FG = "#e8eaf0"
MUTED = "#8b90a0"
STICK = "#e8eaf0"
TRUNK = "#6b4423"
TRUNK_EDGE = "#3d2410"
ROCK = "#7a7e88"
ROCK_EDGE = "#3a3c44"
WAVE = "#3a8ecc"
WAVE_FOAM = "#c8e8ff"
GOAL = "#e8c84a"
WARN = "#ff6644"

FRAME_MS = 33
LIVES_MAX = 5
HIT_INVULN_S = 0.85
GRAVITY = 2300.0
JUMP_V = -640.0
SCREENS_PER_LEVEL = 6  # longer runs
MAX_LEVEL = 8

# Base move speed falls each level (player gets slower as Earth expands / ground heaves).
BASE_SPEED = 340.0
SPEED_DROP_PER_LEVEL = 28.0
# Wave crest must stay under a full jump so you can leap over it.
WAVE_HEIGHT_MAX = 62.0
JUMP_CLEAR_PX = 95.0  # approx peak jump height with current gravity


@dataclass(frozen=True)
class LevelInfo:
    number: int
    move_speed: float
    hazard_rate: float  # spawns per second scale
    hazard_fall: float  # fall/sweep speed mult


def level_info(n: int) -> LevelInfo:
    i = max(1, min(MAX_LEVEL, n))
    speed = max(110.0, BASE_SPEED - (i - 1) * SPEED_DROP_PER_LEVEL)
    # Much denser storms than v1 — early levels were trivial.
    rate = 1.35 + (i - 1) * 0.28
    fall = 1.05 + (i - 1) * 0.16
    return LevelInfo(i, speed, rate, fall)


class ExpandingEarthApp:
    def __init__(
        self,
        root: tk.Tk | None = None,
        *,
        host: tk.Misc | None = None,
        on_back: Callable[[], None] | None = None,
    ) -> None:
        self._owns_root = root is None
        self._on_back = on_back
        self.root = root if root is not None else tk.Tk()
        self._mount = host if host is not None else self.root
        self.root.title("Expanding Earth")
        if self._owns_root:
            self.root.geometry("920x580")
            self.root.minsize(640, 420)
        self.root.configure(bg=BG)
        try:
            self._mount.configure(bg=BG)  # type: ignore[union-attr]
        except tk.TclError:
            pass

        self.title_font = tkfont.Font(family="Helvetica", size=28, weight="bold")
        self.sub_font = tkfont.Font(family="Helvetica", size=13)
        self.btn_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.big_btn = tkfont.Font(family="Helvetica", size=16, weight="bold")

        self._on_title = True
        self._playing = False
        self._after_id: str | None = None
        self._keys: set[str] = set()
        self._jump_queued = False
        self._lives = LIVES_MAX
        self._invuln_until = 0.0
        self._level = 1
        self._hazards: list[dict] = []
        self._spawn_accum = 0.0
        self._px = 80.0
        self._py = 400.0
        self._vy = 0.0
        self._camera_x = 0.0
        self._cw = 900
        self._ch = 520
        self._world_w = 4500.0
        self._shake = 0.0
        self._run_start = 0.0

        self.container = tk.Frame(self._mount, bg=BG)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.title_screen = self._build_title_screen()
        self.play_screen = self._build_play_screen()
        for scr in (self.title_screen, self.play_screen):
            scr.place(x=0, y=0, relwidth=1, relheight=1)

        self.root.bind("<Return>", self._on_enter)
        self.root.bind("<KP_Enter>", self._on_enter)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_window)
        self.root.bind_all("<KeyPress>", self._on_key_down)
        self.root.bind_all("<KeyRelease>", self._on_key_up)

        self.show_title_screen()

    # --- lifecycle ---------------------------------------------------------

    def teardown(self) -> None:
        self._stop_play()
        SFX.stop_all()
        try:
            self.root.unbind("<Return>")
            self.root.unbind("<KP_Enter>")
        except tk.TclError:
            pass
        try:
            self.root.unbind_all("<KeyPress>")
            self.root.unbind_all("<KeyRelease>")
        except tk.TclError:
            pass
        try:
            self.container.destroy()
        except tk.TclError:
            pass

    def _leave(self) -> None:
        if self._on_back is not None:
            self.teardown()
            self._on_back()
            return
        self._on_close_window()

    def _on_close_window(self) -> None:
        if self._on_back is not None and not self._owns_root:
            self._leave()
            return
        self._stop_play()
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def run(self) -> None:
        self.root.mainloop()

    # --- UI ----------------------------------------------------------------

    def _styled_button(self, parent: tk.Misc, text: str, command: Callable[[], None]) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            font=self.btn_font,
            fg="#0d1117",
            bg=ACCENT,
            activeforeground="#0d1117",
            activebackground="#8bc46a",
            relief=tk.FLAT,
            padx=16,
            pady=8,
            cursor="hand2",
            command=command,
        )

    def _build_title_screen(self) -> tk.Frame:
        frame = tk.Frame(self.container, bg=BG)
        header = tk.Frame(frame, bg=BG)
        header.pack(fill=tk.X, padx=24, pady=(22, 6))

        tk.Label(
            header,
            text="Expanding Earth",
            font=self.title_font,
            fg=TITLE_FG,
            bg=BG,
        ).pack(anchor=tk.W)
        tk.Label(
            header,
            text=(
                f"The ground is swelling. Race {SCREENS_PER_LEVEL} screens to the beacon — "
                "jump over waves; don't get smooshed by trunks or rocks."
            ),
            font=self.sub_font,
            fg=MUTED,
            bg=BG,
            wraplength=780,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(8, 0))
        tk.Label(
            header,
            text="8 levels · each one makes you slower · 5 lives",
            font=self.sub_font,
            fg=WARN,
            bg=BG,
        ).pack(anchor=tk.W, pady=(8, 0))

        levels = tk.Frame(frame, bg=BG)
        levels.pack(pady=(22, 6))
        tk.Label(
            levels,
            text="Pick a level",
            font=self.btn_font,
            fg=TITLE_FG,
            bg=BG,
        ).pack(pady=(0, 10))

        row1 = tk.Frame(levels, bg=BG)
        row1.pack()
        row2 = tk.Frame(levels, bg=BG)
        row2.pack(pady=(8, 0))
        for n in range(1, 9):
            parent = row1 if n <= 4 else row2
            info = level_info(n)
            tk.Button(
                parent,
                text=str(n),
                font=self.big_btn,
                fg="#0d1117",
                bg="#4a5a40" if n < 7 else "#8a5030",
                activeforeground="#0d1117",
                activebackground="#6a7a58",
                relief=tk.RAISED,
                bd=3,
                width=3,
                padx=8,
                pady=6,
                cursor="hand2",
                command=lambda v=n: self.start_level(v),
            ).pack(side=tk.LEFT, padx=6)

        speed_row = tk.Frame(frame, bg=BG)
        speed_row.pack(pady=(10, 0))
        for n in (1, 4, 8):
            info = level_info(n)
            tk.Label(
                speed_row,
                text=f"Lv{n} speed {info.move_speed:.0f}",
                font=("Helvetica", 10),
                fg=MUTED,
                bg=BG,
            ).pack(side=tk.LEFT, padx=14)

        btns = tk.Frame(frame, bg=BG)
        btns.pack(pady=(28, 10))
        self._styled_button(btns, "Play level 1", lambda: self.start_level(1)).pack(
            side=tk.LEFT, padx=8
        )
        leave = "Back to What If?" if self._on_back is not None else "Quit"
        self._styled_button(btns, leave, self._leave).pack(side=tk.LEFT, padx=8)

        art = tk.Canvas(frame, height=150, bg=SKY, highlightthickness=0, bd=0)
        art.pack(fill=tk.X, padx=24, pady=(16, 20))
        self._draw_title_art(art)
        return frame

    def _draw_title_art(self, c: tk.Canvas) -> None:
        h = 150
        c.delete("all")
        c.create_rectangle(0, 0, 2000, h, fill=SKY, outline="")
        c.create_rectangle(0, h - 32, 2000, h, fill=GROUND, outline="")
        # cracked earth bumps
        for x0 in (40, 160, 300, 480, 640):
            c.create_arc(x0, h - 50, x0 + 90, h - 10, start=0, extent=180, fill=DIRT, outline="")
        # trunk
        c.create_rectangle(220, 20, 250, h - 32, fill=TRUNK, outline=TRUNK_EDGE, width=2)
        # rock
        c.create_oval(380, 40, 430, 85, fill=ROCK, outline=ROCK_EDGE, width=2)
        # wave
        c.create_polygon(
            520, h - 32, 560, 70, 620, 55, 680, 80, 720, h - 32, fill=WAVE, outline=WAVE_FOAM, width=2
        )
        # goal beacon
        c.create_rectangle(820, h - 90, 836, h - 32, fill="#556040", outline="")
        c.create_oval(808, 28, 848, 68, fill=GOAL, outline="#fff0a0", width=2)
        # stick
        sx, sy = 120, h - 32
        c.create_oval(sx - 8, sy - 50, sx + 8, sy - 34, outline=STICK, width=2)
        c.create_line(sx, sy - 34, sx, sy - 12, fill=STICK, width=3)
        c.create_line(sx, sy - 28, sx - 12, sy - 18, fill=STICK, width=3)
        c.create_line(sx, sy - 28, sx + 12, sy - 18, fill=STICK, width=3)
        c.create_line(sx, sy - 12, sx - 10, sy, fill=STICK, width=3)
        c.create_line(sx, sy - 12, sx + 10, sy, fill=STICK, width=3)

    def _build_play_screen(self) -> tk.Frame:
        frame = tk.Frame(self.container, bg=BG)
        hud = tk.Frame(frame, bg=BG)
        hud.pack(fill=tk.X, padx=12, pady=8)

        self._lives_lbl = tk.Label(
            hud, text=f"Lives: {LIVES_MAX}", font=self.btn_font, fg="#7ec8a0", bg=BG
        )
        self._lives_lbl.pack(side=tk.LEFT)
        self._lvl_lbl = tk.Label(hud, text="Level 1", font=self.btn_font, fg=GOAL, bg=BG)
        self._lvl_lbl.pack(side=tk.LEFT, padx=(16, 0))
        self._speed_lbl = tk.Label(hud, text="Speed: —", font=self.btn_font, fg=MUTED, bg=BG)
        self._speed_lbl.pack(side=tk.LEFT, padx=(16, 0))
        self._dist_lbl = tk.Label(hud, text="Progress: 0/5 screens", font=self.btn_font, fg=TITLE_FG, bg=BG)
        self._dist_lbl.pack(side=tk.LEFT, padx=(16, 0))

        self._styled_button(hud, "Leave run", self._forfeit).pack(side=tk.RIGHT)

        tk.Label(
            frame,
            text=f"A/D or ←/→ move · W/↑ jump over waves · gold beacon is {SCREENS_PER_LEVEL} screens ahead",
            font=self.sub_font,
            fg=MUTED,
            bg=BG,
        ).pack(anchor=tk.W, padx=12)

        self.canvas = tk.Canvas(frame, bg=SKY, highlightthickness=0, bd=0, takefocus=True)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        def on_cfg(e: tk.Event) -> None:
            if e.widget is not self.canvas:
                return
            self._cw, self._ch = max(1, e.width), max(1, e.height)
            self._world_w = float(self._cw) * SCREENS_PER_LEVEL

        self.canvas.bind("<Configure>", on_cfg)
        return frame

    def _show_only(self, screen: tk.Frame) -> None:
        screen.tkraise()
        self.root.update_idletasks()

    def show_title_screen(self) -> None:
        self._stop_play()
        self._on_title = True
        self._show_only(self.title_screen)

    def _on_enter(self, _e: tk.Event | None = None) -> None:
        if self._on_title:
            self.start_level(1)

    def _forfeit(self) -> None:
        if not self._playing:
            return
        if messagebox.askyesno("Leave run", "Abandon this Expanding Earth run?"):
            self.show_title_screen()

    # --- input -------------------------------------------------------------

    def _on_key_down(self, e: tk.Event) -> None:
        if not self._playing:
            if self._on_title and e.keysym in tuple(str(i) for i in range(1, 9)):
                self.start_level(int(e.keysym))
            return
        k = e.keysym
        if k in ("Left", "a", "A"):
            self._keys.add("left")
        elif k in ("Right", "d", "D"):
            self._keys.add("right")
        elif k in ("w", "W", "Up", "space"):
            self._jump_queued = True

    def _on_key_up(self, e: tk.Event) -> None:
        k = e.keysym
        if k in ("Left", "a", "A"):
            self._keys.discard("left")
        elif k in ("Right", "d", "D"):
            self._keys.discard("right")

    # --- play --------------------------------------------------------------

    def start_level(self, n: int) -> None:
        self._stop_play()
        info = level_info(n)
        self._level = info.number
        self._on_title = False
        self._playing = True
        self._lives = LIVES_MAX
        self._invuln_until = 0.0
        self._hazards.clear()
        self._spawn_accum = 0.0
        self._keys.clear()
        self._jump_queued = False
        self._vy = 0.0
        self._shake = 0.0
        self._run_start = time.monotonic()
        self._camera_x = 0.0

        self._show_only(self.play_screen)
        self.root.update_idletasks()
        self._cw = max(400, int(self.canvas.winfo_width()))
        self._ch = max(300, int(self.canvas.winfo_height()))
        self._world_w = float(self._cw) * SCREENS_PER_LEVEL
        floor = self._floor_y()
        self._px = 70.0
        self._py = floor

        self._lives_lbl.config(text=f"Lives: {self._lives}")
        self._lvl_lbl.config(text=f"Level {self._level}")
        self._speed_lbl.config(text=f"Speed: {info.move_speed:.0f}")
        self._dist_lbl.config(text=f"Progress: 0/{SCREENS_PER_LEVEL} screens")
        SFX.play("start", volume=0.5, min_gap=0.15)
        # Pre-load hazards so the run is busy immediately
        for _ in range(4 + self._level):
            self._spawn_hazard(info)
            self._spawn_hazard(info, near=True)
        self.canvas.focus_set()
        self._schedule()

    def _stop_play(self) -> None:
        self._playing = False
        self._keys.clear()
        if self._after_id is not None:
            try:
                self.root.after_cancel(self._after_id)
            except (tk.TclError, ValueError):
                pass
            self._after_id = None

    def _schedule(self) -> None:
        if self._playing:
            self._after_id = self.root.after(FRAME_MS, self._tick)

    def _floor_y(self) -> float:
        return float(self._ch) - 40.0

    def _goal_x(self) -> float:
        return self._world_w - 80.0

    def _try_hit(self) -> bool:
        now = time.monotonic()
        if now < self._invuln_until:
            return False
        self._lives -= 1
        self._invuln_until = now + HIT_INVULN_S
        self._shake = 12.0
        self._lives_lbl.config(text=f"Lives: {max(0, self._lives)}")
        SFX.play("crush", volume=0.55, min_gap=0.12)
        return self._lives <= 0

    def _spawn_hazard(self, info: LevelInfo, *, near: bool = False) -> None:
        # Spawn ahead of the player in the upcoming stretch of world.
        lo = self._cw * (0.2 if near else 0.25)
        hi = self._cw * (0.85 if near else 1.55)
        ahead = self._px + random.uniform(lo, hi)
        if ahead > self._goal_x() - 120:
            return
        kind = random.choices(
            ("trunk", "rock", "wave"),
            weights=(0.36, 0.36, 0.28),
            k=1,
        )[0]
        floor = self._floor_y()
        if kind == "trunk":
            w = random.uniform(36, 58)
            self._hazards.append(
                {
                    "kind": "trunk",
                    "x": ahead,
                    "y": -160.0,
                    "w": w,
                    "h": random.uniform(150, 230),
                    "vy": (480.0 + random.uniform(0, 200)) * info.hazard_fall,
                    "vx": 0.0,
                    "landed": False,
                }
            )
            SFX.play("whoosh", volume=0.22, min_gap=0.15)
        elif kind == "rock":
            r = random.uniform(20, 38)
            self._hazards.append(
                {
                    "kind": "rock",
                    "x": ahead + random.uniform(-50, 50),
                    "y": -80.0,
                    "r": r,
                    "vy": (440.0 + random.uniform(0, 240)) * info.hazard_fall,
                    "vx": random.uniform(-55, 55),
                }
            )
            SFX.play("rock", volume=0.25, min_gap=0.12)
        else:
            # Ground wave — crest stays below a full jump so you can leap over it.
            self._hazards.append(
                {
                    "kind": "wave",
                    "x": ahead - 40,
                    "y": floor,
                    "w": random.uniform(140, 220),
                    "h": random.uniform(42.0, WAVE_HEIGHT_MAX),
                    "vx": (260.0 + random.uniform(0, 110)) * info.hazard_fall
                    * random.choice((-1.0, 1.0)),
                    "life": 3.6,
                    "t0": time.monotonic(),
                }
            )
            SFX.play("wave", volume=0.3, min_gap=0.2)

    def _tick(self) -> None:
        if not self._playing:
            return

        dt = FRAME_MS / 1000.0
        info = level_info(self._level)
        floor = self._floor_y()

        # win check
        if self._px >= self._goal_x() - 20:
            self._win_level()
            return

        # spawn — denser + occasional double throws
        self._spawn_accum += dt * info.hazard_rate
        cap = 16 + self._level * 3
        while self._spawn_accum >= 1.0:
            self._spawn_accum -= 1.0
            if len(self._hazards) < cap:
                self._spawn_hazard(info)
                if random.random() < 0.35 + self._level * 0.04:
                    self._spawn_hazard(info, near=True)

        # move
        speed = info.move_speed * dt
        if "left" in self._keys:
            self._px -= speed
        if "right" in self._keys:
            self._px += speed
        self._px = max(40.0, min(self._world_w - 20.0, self._px))

        on_ground = self._py >= floor - 1.5 and abs(self._vy) < 90
        if self._jump_queued:
            if on_ground:
                self._vy = JUMP_V
                SFX.play("jump", volume=0.38, min_gap=0.06)
            self._jump_queued = False

        if self._py < floor - 0.5:
            self._vy += GRAVITY * dt
        self._py += self._vy * dt
        if self._py >= floor:
            self._py = floor
            self._vy = 0.0

        # camera follows player
        target_cam = self._px - self._cw * 0.35
        self._camera_x += (target_cam - self._camera_x) * min(1.0, 6.0 * dt)
        self._camera_x = max(0.0, min(self._world_w - self._cw, self._camera_x))

        screens_done = min(
            SCREENS_PER_LEVEL,
            int(self._px / max(1.0, self._cw)),
        )
        frac = min(1.0, self._px / max(1.0, self._goal_x()))
        self._dist_lbl.config(
            text=f"Progress: {screens_done}/{SCREENS_PER_LEVEL} screens ({int(frac*100)}%)"
        )

        # hazards
        now = time.monotonic()
        kept: list[dict] = []
        for hz in self._hazards:
            kind = str(hz["kind"])
            if kind == "trunk":
                if not hz.get("landed"):
                    hz["y"] = float(hz["y"]) + float(hz["vy"]) * dt
                    if float(hz["y"]) + float(hz["h"]) >= floor:
                        hz["y"] = floor - float(hz["h"])
                        hz["landed"] = True
                        hz["stick_until"] = now + 1.35
                        self._shake = max(self._shake, 10.0)
                        SFX.play("crush", volume=0.4, min_gap=0.18)
                else:
                    if now > float(hz.get("stick_until", 0)):
                        continue
                kept.append(hz)
            elif kind == "rock":
                hz["vy"] = float(hz["vy"]) + GRAVITY * 0.55 * dt
                hz["x"] = float(hz["x"]) + float(hz["vx"]) * dt
                hz["y"] = float(hz["y"]) + float(hz["vy"]) * dt
                if float(hz["y"]) - float(hz["r"]) > self._ch + 40:
                    continue
                if float(hz["y"]) + float(hz["r"]) >= floor:
                    hz["y"] = floor - float(hz["r"])
                    hz["vy"] *= -0.25
                    hz["vx"] *= 0.7
                    if abs(float(hz["vy"])) < 40:
                        hz["vy"] = 0.0
                        hz["rest_t"] = float(hz.get("rest_t", 0)) + dt
                        if float(hz["rest_t"]) > 1.6:
                            continue
                kept.append(hz)
            else:  # wave
                hz["x"] = float(hz["x"]) + float(hz["vx"]) * dt
                if now - float(hz["t0"]) > float(hz["life"]):
                    continue
                kept.append(hz)
        self._hazards = kept

        # collisions — smoosh zones
        if now >= self._invuln_until:
            hit = False
            px, py = self._px, self._py
            head = py - 48.0
            for hz in self._hazards:
                kind = str(hz["kind"])
                if kind == "trunk":
                    x0 = float(hz["x"]) - float(hz["w"]) * 0.5
                    x1 = float(hz["x"]) + float(hz["w"]) * 0.5
                    y0 = float(hz["y"])
                    y1 = float(hz["y"]) + float(hz["h"])
                    if x0 < px < x1 and y0 < py and y1 > head + 8:
                        # crushing if trunk overlapping body
                        hit = True
                        break
                elif kind == "rock":
                    dx = px - float(hz["x"])
                    dy = (py - 22) - float(hz["y"])
                    if dx * dx + dy * dy < (float(hz["r"]) + 14) ** 2:
                        hit = True
                        break
                else:
                    # Wave: only the water volume hits. Jump clear of the crest = safe.
                    x0 = float(hz["x"])
                    x1 = x0 + float(hz["w"])
                    crest = float(hz["y"]) - float(hz["h"])
                    feet = py
                    # Require feet still inside the wave (below crest). Clear jump = no hit.
                    if x0 - 6 < px < x1 + 6 and feet >= crest + 6 and feet <= float(hz["y"]) + 2:
                        hit = True
                        break
            if hit:
                if self._try_hit():
                    self._die()
                    return
                # knock player back a bit
                self._px = max(40.0, self._px - 55.0)
                self._vy = JUMP_V * 0.55

        self._shake = max(0.0, self._shake - 40.0 * dt)
        self._draw()
        self._schedule()

    def _win_level(self) -> None:
        self._stop_play()
        SFX.play("win", volume=0.55, min_gap=0.3)
        nxt = self._level + 1
        if nxt <= MAX_LEVEL:
            again = messagebox.askyesno(
                "Beacon reached!",
                f"You crossed Expanding Earth level {self._level}!\n\n"
                f"Next level is slower. Continue to level {nxt}?",
            )
            if again:
                self.start_level(nxt)
            else:
                self.show_title_screen()
        else:
            messagebox.showinfo(
                "Earth settled… for now",
                "All 8 levels cleared. You outran the expanding crust.",
            )
            self.show_title_screen()

    def _die(self) -> None:
        self._stop_play()
        SFX.play("die", volume=0.6, min_gap=0.3)
        messagebox.showinfo("Smooshed", "The Expanding Earth got you. Try again.")
        self.show_title_screen()

    # --- draw --------------------------------------------------------------

    def _wx(self, x: float) -> float:
        shake = random.uniform(-self._shake, self._shake) if self._shake > 0 else 0.0
        return x - self._camera_x + shake

    def _draw(self) -> None:
        c = self.canvas
        c.delete("all")
        w, h = self._cw, self._ch
        floor = self._floor_y()
        cam = self._camera_x

        c.create_rectangle(0, 0, w, h, fill=SKY, outline="")

        # parallax hills
        for i, col in enumerate(("#1a2830", "#203038", "#243840")):
            base = 90 + i * 40
            pts: list[float] = [0, h]
            x = -((cam * (0.15 + i * 0.08)) % 200)
            while x < w + 220:
                pts.extend([x, floor - base + math.sin(x * 0.01 + i) * 18])
                x += 40
            pts.extend([w + 20, h])
            c.create_polygon(pts, fill=col, outline="")

        # ground strip across visible world
        c.create_rectangle(0, floor, w, h, fill=GROUND, outline="")
        c.create_line(0, floor, w, floor, fill="#4a5e3e", width=2)
        # cracks / expansion marks
        gx = -((cam) % 90)
        while gx < w:
            c.create_line(gx, floor, gx + 18, floor + 16, fill=DIRT, width=2)
            gx += 90

        # screen markers (every screen boundary)
        for s in range(SCREENS_PER_LEVEL + 1):
            bx = s * self._cw
            sx = self._wx(bx)
            if -20 <= sx <= w + 20:
                c.create_line(sx, 0, sx, floor, fill="#2a3840", dash=(4, 6))
                if 0 < s < SCREENS_PER_LEVEL:
                    c.create_text(
                        sx + 8,
                        18,
                        text=f"screen {s}",
                        anchor=tk.W,
                        fill="#4a5860",
                        font=("Helvetica", 10),
                    )

        # goal beacon
        gx = self._wx(self._goal_x())
        if -40 <= gx <= w + 40:
            c.create_rectangle(gx - 8, floor - 70, gx + 8, floor, fill="#556040", outline="#334028")
            c.create_oval(gx - 22, floor - 110, gx + 22, floor - 66, fill=GOAL, outline="#fff4b0", width=3)
            c.create_text(gx, floor - 88, text="END", fill="#2a2208", font=("Helvetica", 11, "bold"))

        # hazards
        for hz in self._hazards:
            kind = str(hz["kind"])
            if kind == "trunk":
                x = self._wx(float(hz["x"]))
                y0 = float(hz["y"])
                ww, hh = float(hz["w"]), float(hz["h"])
                c.create_rectangle(
                    x - ww / 2,
                    y0,
                    x + ww / 2,
                    y0 + hh,
                    fill=TRUNK,
                    outline=TRUNK_EDGE,
                    width=3,
                )
                # rings
                for ry in (y0 + 20, y0 + hh * 0.5, y0 + hh - 24):
                    c.create_oval(x - 8, ry - 5, x + 8, ry + 5, outline="#8a6238")
            elif kind == "rock":
                x = self._wx(float(hz["x"]))
                y = float(hz["y"])
                r = float(hz["r"])
                c.create_oval(x - r, y - r, x + r, y + r, fill=ROCK, outline=ROCK_EDGE, width=3)
                c.create_arc(x - r * 0.6, y - r * 0.6, x + r * 0.2, y, start=40, extent=80, style=tk.ARC, outline="#b0b4bc", width=2)
            else:
                x0 = self._wx(float(hz["x"]))
                ww, hh = float(hz["w"]), float(hz["h"])
                y1 = float(hz["y"])
                c.create_polygon(
                    x0,
                    y1,
                    x0 + ww * 0.2,
                    y1 - hh,
                    x0 + ww * 0.55,
                    y1 - hh * 0.75,
                    x0 + ww * 0.85,
                    y1 - hh * 1.05,
                    x0 + ww,
                    y1,
                    fill=WAVE,
                    outline=WAVE_FOAM,
                    width=2,
                )
                c.create_line(x0 + 10, y1 - 8, x0 + ww - 10, y1 - 8, fill=WAVE_FOAM, width=2)

        # player
        self._draw_player(c)

        if time.monotonic() < self._invuln_until and int(time.monotonic() * 8) % 2 == 0:
            c.create_text(
                self._wx(self._px),
                self._py - 64,
                text="SMOOSH!",
                fill=WARN,
                font=("Helvetica", 12, "bold"),
            )

    def _draw_player(self, c: tk.Canvas) -> None:
        px = self._wx(self._px)
        py = self._py
        c.create_oval(px - 9, py - 50, px + 9, py - 32, outline=STICK, width=2)
        c.create_line(px, py - 32, px, py - 10, fill=STICK, width=3)
        c.create_line(px, py - 26, px - 14, py - 16, fill=STICK, width=3)
        c.create_line(px, py - 26, px + 14, py - 16, fill=STICK, width=3)
        c.create_line(px, py - 10, px - 11, py, fill=STICK, width=3)
        c.create_line(px, py - 10, px + 11, py, fill=STICK, width=3)


def main() -> None:
    ExpandingEarthApp().run()


if __name__ == "__main__":
    main()
