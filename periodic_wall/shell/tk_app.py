"""v0 Tk shell — single-canvas, single-toolbar architecture.

We avoid frame stacking entirely (macOS Tk doesn't reliably tkraise/place_forget
overlapping frames). The app holds ONE toolbar and ONE canvas; switching screens
clears those widgets and rebuilds them.
"""

from __future__ import annotations

import random
import tkinter as tk
from tkinter import font as tkfont

from game.data import FRAME_DT
from game.models import Command, GameState, PlayerInput, Screen
from game.screen_flow import FlowState, reduce_flow
from game.survival_sim import tick
from presentation.scenes import (
    build_end_draw_list,
    build_lab_draw_list,
    paint_title_wall_scene,
    paint_to_canvas,
)

BG_TOOLBAR = "#1b2538"
BG_TITLE = "#142033"
BG_LAB = "#0e1a2e"
ACCENT = "#5fd3bb"
TITLE_FG = "#ffffff"
BTN_BG = "#5fd3bb"
BTN_FG = "#0a1320"


class PeriodicWallApp:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("The Periodic Wall of Elements")
        self.root.geometry("960x600")
        self.root.minsize(700, 480)
        self.root.configure(bg=BG_TOOLBAR)

        self.title_font = tkfont.Font(family="Helvetica", size=22, weight="bold")
        self.btn_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.label_font = tkfont.Font(family="Helvetica", size=14, weight="bold")

        self.flow = FlowState()
        self._keys: set[str] = set()
        self._jump = False
        self._after_id: str | None = None
        self._rng = random.Random()
        self._lab_status_var = tk.StringVar(value="")
        self._lab_start_retries = 0

        self.toolbar = tk.Frame(self.root, bg=BG_TOOLBAR, padx=12, pady=8)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)

        self.canvas = tk.Canvas(
            self.root,
            highlightthickness=0,
            bd=0,
            bg=BG_TITLE,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.root.bind_all("<KeyPress>", self._on_key_down)
        self.root.bind_all("<KeyRelease>", self._on_key_up)
        self.root.protocol("WM_DELETE_WINDOW", self._quit)

        self._show_screen(Screen.TITLE)

    def _styled_button(self, parent: tk.Widget, text: str, command) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            font=self.btn_font,
            fg=BTN_FG,
            bg=BTN_BG,
            activeforeground=BTN_FG,
            activebackground="#3fb39a",
            relief=tk.FLAT,
            padx=22,
            pady=8,
            cursor="hand2",
            command=command,
        )

    def _clear_toolbar(self) -> None:
        for child in list(self.toolbar.winfo_children()):
            child.destroy()

    def _build_title_toolbar(self) -> None:
        tk.Label(
            self.toolbar,
            text="The Periodic Wall of Elements",
            font=self.title_font,
            fg=TITLE_FG,
            bg=BG_TOOLBAR,
        ).pack(side=tk.LEFT, padx=(0, 16))
        self._styled_button(self.toolbar, "Play Level 1", self._play).pack(side=tk.LEFT, padx=6)
        self._styled_button(self.toolbar, "Quit", self._quit).pack(side=tk.LEFT, padx=6)

    def _build_lab_toolbar(self) -> None:
        tk.Label(
            self.toolbar,
            text="LEVEL 1 — LAB",
            font=self.label_font,
            fg="#ffd866",
            bg=BG_TOOLBAR,
        ).pack(side=tk.LEFT, padx=(0, 12))
        tk.Label(
            self.toolbar,
            textvariable=self._lab_status_var,
            font=self.label_font,
            fg="#e8eaf0",
            bg=BG_TOOLBAR,
        ).pack(side=tk.LEFT, padx=4)
        self._styled_button(self.toolbar, "Leave", self._forfeit).pack(side=tk.RIGHT)

    def _build_end_toolbar(self, won: bool) -> None:
        msg = "You won!" if won else "You died"
        tk.Label(
            self.toolbar,
            text=msg,
            font=self.title_font,
            fg="#ffd866" if won else "#ff7a7a",
            bg=BG_TOOLBAR,
        ).pack(side=tk.LEFT, padx=(0, 16))
        self._styled_button(self.toolbar, "Play again", self._play_again).pack(side=tk.LEFT, padx=6)
        self._styled_button(self.toolbar, "Title", self._to_title).pack(side=tk.LEFT, padx=6)

    def _show_screen(self, screen: Screen) -> None:
        self.flow.screen = screen
        self._stop_lab_loop()
        self._clear_toolbar()
        self.canvas.delete("all")

        if screen == Screen.TITLE:
            self.canvas.configure(bg=BG_TITLE)
            self._build_title_toolbar()
            self.root.after_idle(self._paint_title)
        elif screen == Screen.LAB:
            self.canvas.configure(bg=BG_LAB)
            self._build_lab_toolbar()
            self._lab_start_retries = 0
            self._start_lab_loop()
        elif screen in (Screen.END_WIN, Screen.END_LOSE):
            self.canvas.configure(bg=BG_TITLE)
            won = screen == Screen.END_WIN
            self._build_end_toolbar(won)
            w = max(400, self.canvas.winfo_width())
            h = max(300, self.canvas.winfo_height())
            paint_to_canvas(self.canvas, build_end_draw_list(won, w, h))

    def _on_canvas_configure(self, _event=None) -> None:
        if self.flow.screen == Screen.TITLE:
            self._paint_title()
        elif self.flow.screen == Screen.LAB and self.flow.game is not None:
            self._paint_lab()

    def _paint_title(self) -> None:
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10 or h < 10:
            return
        paint_title_wall_scene(self.canvas, w, h)

    def _paint_lab(self) -> None:
        if self.flow.game is None:
            return
        paint_to_canvas(self.canvas, build_lab_draw_list(self.flow.game))

    def _play(self) -> None:
        w = max(640, self.canvas.winfo_width())
        h = max(420, self.canvas.winfo_height())
        self._rng = random.Random()
        reduce_flow(
            self.flow,
            Command.PLAY,
            room_w=w,
            room_h=h,
            rng_seed=self._rng.randint(0, 2**30),
        )
        self._show_screen(Screen.LAB)

    def _play_again(self) -> None:
        w = max(640, self.canvas.winfo_width())
        h = max(420, self.canvas.winfo_height())
        reduce_flow(
            self.flow,
            Command.PLAY_AGAIN,
            room_w=w,
            room_h=h,
            rng_seed=self._rng.randint(0, 2**30),
        )
        self._show_screen(Screen.LAB)

    def _forfeit(self) -> None:
        reduce_flow(self.flow, Command.FORFEIT)
        self._show_screen(Screen.TITLE)

    def _to_title(self) -> None:
        reduce_flow(self.flow, Command.FORFEIT)
        self._show_screen(Screen.TITLE)

    def _quit(self) -> None:
        self._stop_lab_loop()
        self.root.destroy()

    def _player_input(self) -> PlayerInput:
        return PlayerInput(keys_held=frozenset(self._keys), jump_pressed=self._jump)

    def _lab_tick(self) -> None:
        if self.flow.screen != Screen.LAB or self.flow.game is None:
            return
        inp = self._player_input()
        self._jump = False
        state, events = tick(self.flow.game, inp, FRAME_DT, self._rng)
        self.flow.game = state
        reduce_flow(self.flow, events=events)
        w = max(400, self.canvas.winfo_width())
        h = max(400, self.canvas.winfo_height())
        if w > 2 and h > 2:
            self.flow.game.room_w = float(w)
            self.flow.game.room_h = float(h)
        m = int(state.time_left // 60)
        s = int(state.time_left % 60)
        self._lab_status_var.set(
            f"HP {state.hearts}/5   ·   Time {m}:{s:02d}   ·   Balls {len(state.balls)}"
        )
        self._paint_lab()
        if self.flow.screen == Screen.LAB and state.active:
            self._after_id = self.root.after(int(FRAME_DT * 1000), self._lab_tick)
        elif self.flow.screen == Screen.END_WIN:
            self._show_screen(Screen.END_WIN)
        elif self.flow.screen == Screen.END_LOSE:
            self._show_screen(Screen.END_LOSE)

    def _start_lab_loop(self) -> None:
        self._stop_lab_loop()
        if self.flow.game is None:
            w = max(640, self.canvas.winfo_width())
            h = max(420, self.canvas.winfo_height())
            self.flow.game = GameState.new_lab(w, h, self._rng.randint(0, 2**30))
        self.canvas.focus_set()
        self.root.update_idletasks()
        if self.canvas.winfo_width() < 10 or self.canvas.winfo_height() < 10:
            self._lab_start_retries += 1
            if self._lab_start_retries < 40:
                self.root.after(20, self._start_lab_loop)
            return
        self._lab_start_retries = 0
        self._lab_tick()

    def _stop_lab_loop(self) -> None:
        if self._after_id is not None:
            try:
                self.root.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None

    def _on_key_down(self, e: tk.Event) -> None:
        k = e.keysym
        if k in ("Return", "KP_Enter") and self.flow.screen == Screen.TITLE:
            self._play()
            return
        self._keys.add(k)
        if k in ("w", "W", "Up"):
            self._jump = True

    def _on_key_up(self, e: tk.Event) -> None:
        self._keys.discard(e.keysym)

    def run(self) -> None:
        self.root.mainloop()


def run() -> None:
    PeriodicWallApp().run()
