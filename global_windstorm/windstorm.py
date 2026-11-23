#!/usr/bin/env python3
"""Global Windstorm — dodge flying debris across 5 storm levels.

Run standalone:
    /opt/anaconda3/bin/python3.12 windstorm.py

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


BG = "#0e1520"
SKY = "#152033"
GROUND = "#2a3344"
ACCENT = "#3d9e8c"
TITLE_FG = "#e8eaf0"
MUTED = "#8b90a0"
STICK = "#e8eaf0"
DANGER_RED = "#ff3344"
WARN_RED = "#ff5566"
DEBRIS_FILL = "#c8d0dc"

FRAME_MS = 33
PLAYER_MAX_HP = 5
HIT_INVULN_S = 0.55
GRAVITY = 2400.0
JUMP_V = -620.0
MAX_JUMPS = 4  # quad jump
MOVE_SPEED = 340.0
DUCK_HEIGHT = 18.0
STAND_HEIGHT = 38.0
PLAYER_R = 14.0

# Level: (debris speed px/s, spawn every s, max on screen, survive seconds)
LEVEL_TUNING: tuple[tuple[float, float, int, float], ...] = (
    (280.0, 1.05, 4, 40.0),
    (360.0, 0.82, 6, 45.0),
    (460.0, 0.62, 9, 50.0),
    (580.0, 0.48, 12, 55.0),
    (720.0, 0.36, 16, 60.0),
)


@dataclass(frozen=True)
class LevelInfo:
    number: int
    speed: float
    spawn_every: float
    max_active: int
    survive_s: float


def level_info(n: int) -> LevelInfo:
    i = max(1, min(5, n)) - 1
    speed, every, cap, survive = LEVEL_TUNING[i]
    return LevelInfo(i + 1, speed, every, cap, survive)


class GlobalWindstormApp:
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
        self.root.title("Global Windstorm")
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
        self.big_btn = tkfont.Font(family="Helvetica", size=18, weight="bold")

        self._on_title = True
        self._playing = False
        self._after_id: str | None = None
        self._keys: set[str] = set()
        self._jump_queued = False
        self._jumps_left = MAX_JUMPS
        self._hp = PLAYER_MAX_HP
        self._invuln_until = 0.0
        self._level = 1
        self._debris: list[dict] = []
        self._warnings: list[dict] = []
        self._spawn_accum = 0.0
        self._level_start = 0.0
        self._px = 200.0
        self._py = 400.0
        self._vy = 0.0
        self._ducking = False
        self._cw = 900
        self._ch = 520
        self._wind_phase = 0.0

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
            activebackground="#4db8a4",
            relief=tk.FLAT,
            padx=16,
            pady=8,
            cursor="hand2",
            command=command,
        )

    def _build_title_screen(self) -> tk.Frame:
        frame = tk.Frame(self.container, bg=BG)
        header = tk.Frame(frame, bg=BG)
        header.pack(fill=tk.X, padx=24, pady=(24, 8))

        tk.Label(
            header,
            text="Global Windstorm",
            font=self.title_font,
            fg=TITLE_FG,
            bg=BG,
        ).pack(anchor=tk.W)
        tk.Label(
            header,
            text="Debris rockets through the gale. Duck, quad-jump, and don't get hit.",
            font=self.sub_font,
            fg=MUTED,
            bg=BG,
            wraplength=760,
            justify=tk.LEFT,
        ).pack(anchor=tk.W, pady=(8, 0))

        tk.Label(
            header,
            text="Levels 1–5 · each storm throws faster and more junk · red flash = incoming",
            font=self.sub_font,
            fg=WARN_RED,
            bg=BG,
        ).pack(anchor=tk.W, pady=(10, 0))

        levels = tk.Frame(frame, bg=BG)
        levels.pack(pady=(28, 12))
        tk.Label(
            levels,
            text="Pick a storm level",
            font=self.btn_font,
            fg=TITLE_FG,
            bg=BG,
        ).pack(pady=(0, 12))

        row = tk.Frame(levels, bg=BG)
        row.pack()
        for n in range(1, 6):
            info = level_info(n)
            tk.Button(
                row,
                text=str(n),
                font=self.big_btn,
                fg="#0d1117",
                bg="#3d4458" if n < 5 else "#8a3040",
                activeforeground="#0d1117",
                activebackground="#5a6a88",
                relief=tk.RAISED,
                bd=3,
                width=3,
                padx=10,
                pady=8,
                cursor="hand2",
                command=lambda v=n: self.start_level(v),
            ).pack(side=tk.LEFT, padx=8)
            # tiny speed hint under — skip for clean look

        hints = tk.Frame(frame, bg=BG)
        hints.pack(pady=(8, 0))
        for n in range(1, 6):
            info = level_info(n)
            tk.Label(
                hints,
                text=f"{n}: ×{info.speed/LEVEL_TUNING[0][0]:.1f} speed",
                font=("Helvetica", 10),
                fg=MUTED,
                bg=BG,
            ).pack(side=tk.LEFT, padx=10)

        btns = tk.Frame(frame, bg=BG)
        btns.pack(pady=(36, 12))
        self._styled_button(btns, "Play level 1", lambda: self.start_level(1)).pack(
            side=tk.LEFT, padx=8
        )
        leave = "Back to What If?" if self._on_back is not None else "Quit"
        self._styled_button(btns, leave, self._leave).pack(side=tk.LEFT, padx=8)

        art = tk.Canvas(frame, height=160, bg=SKY, highlightthickness=0, bd=0)
        art.pack(fill=tk.X, padx=24, pady=(20, 24))
        self._draw_title_art(art)
        return frame

    def _draw_title_art(self, c: tk.Canvas) -> None:
        w = max(400, int(c.winfo_reqwidth()) or 800)
        h = 160
        c.delete("all")
        c.create_rectangle(0, 0, 2000, h, fill=SKY, outline="")
        c.create_rectangle(0, h - 28, 2000, h, fill=GROUND, outline="")
        # wind lines
        for i in range(8):
            y = 20 + i * 14
            c.create_line(40 + i * 30, y, 220 + i * 50, y - 6, fill="#3a4a66", width=2)
        # red incoming markers
        for y in (40, 70, 100):
            c.create_polygon(18, y, 36, y - 10, 36, y + 10, fill=DANGER_RED, outline="")
        # flying junk
        c.create_oval(260, 36, 300, 70, fill=DEBRIS_FILL, outline=DANGER_RED, width=2)
        c.create_rectangle(400, 55, 455, 85, fill="#9aa8bc", outline=DANGER_RED, width=2)
        c.create_polygon(560, 48, 600, 70, 555, 92, fill="#b0bcc8", outline=DANGER_RED, width=2)
        # stick
        sx, sy = 720, h - 28
        c.create_oval(sx - 8, sy - 52, sx + 8, sy - 36, outline=STICK, width=2)
        c.create_line(sx, sy - 36, sx, sy - 12, fill=STICK, width=3)
        c.create_line(sx, sy - 28, sx - 14, sy - 18, fill=STICK, width=3)
        c.create_line(sx, sy - 28, sx + 14, sy - 18, fill=STICK, width=3)
        c.create_line(sx, sy - 12, sx - 10, sy, fill=STICK, width=3)
        c.create_line(sx, sy - 12, sx + 10, sy, fill=STICK, width=3)

    def _build_play_screen(self) -> tk.Frame:
        frame = tk.Frame(self.container, bg=BG)
        hud = tk.Frame(frame, bg=BG)
        hud.pack(fill=tk.X, padx=12, pady=8)

        self._time_lbl = tk.Label(hud, text="Survive: —", font=self.btn_font, fg=TITLE_FG, bg=BG)
        self._time_lbl.pack(side=tk.LEFT)
        self._hp_lbl = tk.Label(hud, text=f"HP: {PLAYER_MAX_HP}", font=self.btn_font, fg="#7ec8a0", bg=BG)
        self._hp_lbl.pack(side=tk.LEFT, padx=(18, 0))
        self._lvl_lbl = tk.Label(hud, text="Storm 1", font=self.btn_font, fg=WARN_RED, bg=BG)
        self._lvl_lbl.pack(side=tk.LEFT, padx=(18, 0))
        self._jump_lbl = tk.Label(hud, text=f"Jumps: {MAX_JUMPS}", font=self.btn_font, fg="#9ec8f0", bg=BG)
        self._jump_lbl.pack(side=tk.LEFT, padx=(18, 0))

        self._styled_button(hud, "Leave storm", self._forfeit).pack(side=tk.RIGHT)

        tk.Label(
            frame,
            text="A/D or ←/→ move · W/↑ jump (quad jump) · S duck · red markers = incoming debris",
            font=self.sub_font,
            fg=MUTED,
            bg=BG,
        ).pack(anchor=tk.W, padx=12)

        self.canvas = tk.Canvas(frame, bg=SKY, highlightthickness=0, bd=0, takefocus=True)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        def on_cfg(e: tk.Event) -> None:
            if e.widget is not self.canvas:
                return
            self._cw, self._ch = e.width, e.height

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
        if messagebox.askyesno("Leave storm", "Leave this windstorm?"):
            self.show_title_screen()

    # --- input -------------------------------------------------------------

    def _on_key_down(self, e: tk.Event) -> None:
        if not self._playing:
            if self._on_title and e.keysym in ("1", "2", "3", "4", "5"):
                self.start_level(int(e.keysym))
            return
        k = e.keysym
        if k in ("Left", "a", "A"):
            self._keys.add("left")
        elif k in ("Right", "d", "D"):
            self._keys.add("right")
        elif k in ("s", "S", "Down"):
            self._keys.add("duck")
        elif k in ("w", "W", "Up", "space"):
            self._jump_queued = True

    def _on_key_up(self, e: tk.Event) -> None:
        k = e.keysym
        if k in ("Left", "a", "A"):
            self._keys.discard("left")
        elif k in ("Right", "d", "D"):
            self._keys.discard("right")
        elif k in ("s", "S", "Down"):
            self._keys.discard("duck")

    # --- play --------------------------------------------------------------

    def start_level(self, n: int) -> None:
        self._stop_play()
        info = level_info(n)
        self._level = info.number
        self._on_title = False
        self._playing = True
        self._hp = PLAYER_MAX_HP
        self._invuln_until = 0.0
        self._debris.clear()
        self._warnings.clear()
        self._spawn_accum = 0.0
        self._level_start = time.monotonic()
        self._keys.clear()
        self._jump_queued = False
        self._jumps_left = MAX_JUMPS
        self._vy = 0.0
        self._ducking = False
        SFX.play("start", volume=0.5, min_gap=0.15)

        self._show_only(self.play_screen)
        self.root.update_idletasks()
        self._cw = max(400, int(self.canvas.winfo_width()))
        self._ch = max(300, int(self.canvas.winfo_height()))
        floor_y = self._floor_y()
        self._px = self._cw * 0.35
        self._py = floor_y

        self._hp_lbl.config(text=f"HP: {self._hp}")
        self._lvl_lbl.config(text=f"Storm {self._level}")
        self._jump_lbl.config(text=f"Jumps: {self._jumps_left}")
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
        return float(self._ch) - 36.0

    def _player_top(self) -> float:
        h = DUCK_HEIGHT if self._ducking else STAND_HEIGHT
        return self._py - h

    def _try_damage(self) -> bool:
        now = time.monotonic()
        if now < self._invuln_until:
            return False
        self._hp -= 1
        self._invuln_until = now + HIT_INVULN_S
        self._hp_lbl.config(text=f"HP: {max(0, self._hp)}")
        SFX.play("hit", volume=0.6, min_gap=0.1)
        return self._hp <= 0

    def _spawn_debris(self, info: LevelInfo) -> None:
        if len(self._debris) >= info.max_active:
            return
        floor = self._floor_y()
        from_left = random.random() < 0.5
        # Aim height: some high (jump over / don't duck), some low (must jump), some mid
        band = random.choice(("low", "mid", "high", "mid", "low"))
        if band == "low":
            cy = floor - random.uniform(10, 28)
        elif band == "high":
            cy = floor - random.uniform(110, 190)
        else:
            cy = floor - random.uniform(40, 95)

        r = random.uniform(12, 26)
        speed = info.speed * random.uniform(0.85, 1.15)
        if from_left:
            x = -r - 10
            vx = speed
            warn_x = 18.0
        else:
            x = self._cw + r + 10
            vx = -speed
            warn_x = float(self._cw) - 18.0

        # Slight vertical drift for chaos
        vy = random.uniform(-40, 40) * (0.4 + 0.15 * self._level)

        kind = random.choice(("oval", "box", "shard", "oval"))
        self._warnings.append(
            {
                "x": warn_x,
                "y": cy,
                "t0": time.monotonic(),
                "dur": 0.55,
                "from_left": from_left,
            }
        )
        SFX.play("warn", volume=0.28, min_gap=0.12)
        SFX.play("whoosh", volume=0.32, min_gap=0.08)
        self._debris.append(
            {
                "x": x,
                "y": cy,
                "vx": vx,
                "vy": vy,
                "r": r,
                "kind": kind,
                "born": time.monotonic(),
            }
        )

    def _tick(self) -> None:
        if not self._playing:
            return

        dt = FRAME_MS / 1000.0
        info = level_info(self._level)
        elapsed = time.monotonic() - self._level_start
        remaining = info.survive_s - elapsed
        if remaining <= 0:
            self._win_level()
            return

        m, s = int(remaining // 60), int(remaining % 60)
        self._time_lbl.config(text=f"Survive: {m}:{s:02d}")

        # spawn
        self._spawn_accum += dt
        while self._spawn_accum >= info.spawn_every:
            self._spawn_accum -= info.spawn_every
            self._spawn_debris(info)

        # movement
        speed = MOVE_SPEED * dt
        if "left" in self._keys:
            self._px -= speed
        if "right" in self._keys:
            self._px += speed
        pad = 28.0
        self._px = max(pad, min(self._cw - pad, self._px))

        floor = self._floor_y()
        on_ground = self._py >= floor - 1.5 and abs(self._vy) < 80

        if self._jump_queued:
            if on_ground:
                self._jumps_left = MAX_JUMPS
            if self._jumps_left > 0:
                self._vy = JUMP_V
                self._jumps_left -= 1
                self._jump_lbl.config(text=f"Jumps: {self._jumps_left}")
                SFX.play("jump", volume=0.38, min_gap=0.05)
            self._jump_queued = False

        if self._py < floor - 0.5:
            self._vy += GRAVITY * dt
        self._py += self._vy * dt
        if self._py >= floor:
            self._py = floor
            self._vy = 0.0
            self._jumps_left = MAX_JUMPS
            self._jump_lbl.config(text=f"Jumps: {self._jumps_left}")

        self._ducking = "duck" in self._keys and on_ground

        # integrate debris
        alive: list[dict] = []
        for d in self._debris:
            d["x"] = float(d["x"]) + float(d["vx"]) * dt
            d["y"] = float(d["y"]) + float(d["vy"]) * dt
            if -80 < float(d["x"]) < self._cw + 80:
                alive.append(d)
        self._debris = alive

        now = time.monotonic()
        self._warnings = [
            w for w in self._warnings if now - float(w["t0"]) < float(w["dur"])
        ]

        # collisions
        body_top = self._player_top()
        body_bot = self._py
        body_cx = self._px
        # thin hitbox when ducking
        half_w = 11.0 if self._ducking else 13.0
        if now >= self._invuln_until:
            hit_i = None
            for i, d in enumerate(self._debris):
                dx = abs(float(d["x"]) - body_cx)
                dy_closest = min(
                    abs(float(d["y"]) - body_top),
                    abs(float(d["y"]) - body_bot),
                    abs(float(d["y"]) - (body_top + body_bot) / 2),
                )
                # circle vs upright capsule approx
                if dx > float(d["r"]) + half_w:
                    continue
                if float(d["y"]) + float(d["r"]) < body_top:
                    continue
                if float(d["y"]) - float(d["r"]) > body_bot:
                    continue
                # closer check
                if dx * dx + dy_closest * dy_closest < (float(d["r"]) + half_w) ** 2 or (
                    body_top - float(d["r"]) <= float(d["y"]) <= body_bot + float(d["r"])
                    and dx < float(d["r"]) + half_w
                ):
                    hit_i = i
                    break
            if hit_i is not None:
                self._debris.pop(hit_i)
                if self._try_damage():
                    self._die()
                    return

        self._wind_phase += dt
        self._draw()
        self._schedule()

    def _win_level(self) -> None:
        self._stop_play()
        SFX.play("win", volume=0.55, min_gap=0.3)
        nxt = self._level + 1
        if nxt <= 5:
            again = messagebox.askyesno(
                "Storm cleared!",
                f"You rode out Storm {self._level}!\n\nAdvance to Storm {nxt}?",
            )
            if again:
                self.start_level(nxt)
            else:
                self.show_title_screen()
        else:
            messagebox.showinfo(
                "Global Windstorm cleared!",
                "All 5 storms beaten. The winds finally rest.",
            )
            self.show_title_screen()

    def _die(self) -> None:
        self._stop_play()
        SFX.play("die", volume=0.6, min_gap=0.3)
        messagebox.showinfo("Wiped out", "The windstorm got you. Try another run.")
        self.show_title_screen()

    # --- draw --------------------------------------------------------------

    def _draw(self) -> None:
        c = self.canvas
        c.delete("all")
        w, h = self._cw, self._ch
        floor = self._floor_y()

        c.create_rectangle(0, 0, w, h, fill=SKY, outline="")
        # wind streaks
        phase = self._wind_phase * 180
        for i in range(10):
            y = 30 + i * (h / 14)
            x0 = (phase + i * 70) % (w + 120) - 60
            c.create_line(x0, y, x0 + 90, y - 4, fill="#243044", width=2)

        c.create_rectangle(0, floor, w, h, fill=GROUND, outline="")
        c.create_line(0, floor, w, floor, fill="#3d4658", width=2)

        # red indicators for incoming throws
        now = time.monotonic()
        for warn in self._warnings:
            t = (now - float(warn["t0"])) / float(warn["dur"])
            pulse = 0.55 + 0.45 * abs(math.sin(now * 14))
            y = float(warn["y"])
            x = float(warn["x"])
            size = 14 + 6 * pulse
            if warn["from_left"]:
                c.create_polygon(
                    x,
                    y,
                    x + size,
                    y - size * 0.7,
                    x + size,
                    y + size * 0.7,
                    fill=DANGER_RED,
                    outline="#ffccd0",
                    width=1,
                )
            else:
                c.create_polygon(
                    x,
                    y,
                    x - size,
                    y - size * 0.7,
                    x - size,
                    y + size * 0.7,
                    fill=DANGER_RED,
                    outline="#ffccd0",
                    width=1,
                )
            # danger ring
            rr = 10 + 8 * (1 - t)
            c.create_oval(
                x - rr,
                y - rr,
                x + rr,
                y + rr,
                outline=WARN_RED,
                width=2,
            )

        # debris — always outlined in red so every thrown thing is marked
        for d in self._debris:
            x, y, r = float(d["x"]), float(d["y"]), float(d["r"])
            kind = str(d["kind"])
            if kind == "box":
                c.create_rectangle(
                    x - r,
                    y - r * 0.7,
                    x + r,
                    y + r * 0.7,
                    fill=DEBRIS_FILL,
                    outline=DANGER_RED,
                    width=3,
                )
            elif kind == "shard":
                c.create_polygon(
                    x,
                    y - r,
                    x + r,
                    y + r * 0.6,
                    x - r,
                    y + r * 0.6,
                    fill="#a8b4c4",
                    outline=DANGER_RED,
                    width=3,
                )
            else:
                c.create_oval(
                    x - r,
                    y - r,
                    x + r,
                    y + r,
                    fill=DEBRIS_FILL,
                    outline=DANGER_RED,
                    width=3,
                )
            # red tip indicator on leading edge
            lead = 1 if float(d["vx"]) > 0 else -1
            c.create_oval(
                x + lead * r - 4,
                y - 4,
                x + lead * r + 4,
                y + 4,
                fill=DANGER_RED,
                outline="",
            )

        # stickman
        self._draw_player(c)

        # blink when invulnerable
        if time.monotonic() < self._invuln_until and int(time.monotonic() * 10) % 2 == 0:
            c.create_text(
                self._px,
                self._player_top() - 16,
                text="!",
                fill=WARN_RED,
                font=("Helvetica", 16, "bold"),
            )

    def _draw_player(self, c: tk.Canvas) -> None:
        px, py = self._px, self._py
        duck = self._ducking
        if duck:
            # crouched
            c.create_oval(px - 8, py - 28, px + 8, py - 14, outline=STICK, width=2)
            c.create_line(px, py - 14, px, py - 4, fill=STICK, width=3)
            c.create_line(px, py - 10, px - 16, py - 6, fill=STICK, width=3)
            c.create_line(px, py - 10, px + 16, py - 6, fill=STICK, width=3)
            c.create_line(px, py - 4, px - 12, py, fill=STICK, width=3)
            c.create_line(px, py - 4, px + 12, py, fill=STICK, width=3)
        else:
            c.create_oval(px - 9, py - 52, px + 9, py - 34, outline=STICK, width=2)
            c.create_line(px, py - 34, px, py - 10, fill=STICK, width=3)
            c.create_line(px, py - 28, px - 16, py - 16, fill=STICK, width=3)
            c.create_line(px, py - 28, px + 16, py - 16, fill=STICK, width=3)
            c.create_line(px, py - 10, px - 12, py, fill=STICK, width=3)
            c.create_line(px, py - 10, px + 12, py, fill=STICK, width=3)


def main() -> None:
    GlobalWindstormApp().run()


if __name__ == "__main__":
    main()
