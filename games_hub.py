#!/usr/bin/env python3
"""What If? — hub title screen listing every game.

Run from the repo root (needs modern Tk, same as Periodic Wall):

    /opt/anaconda3/bin/python3.12 games_hub.py

To add a game later:
  1. Append a GameEntry in games_registry.py
  2. Register a launcher function in LAUNCHERS below
"""

from __future__ import annotations

import os
import sys
import tkinter as tk
from collections.abc import Callable
from pathlib import Path
from tkinter import font as tkfont
from tkinter import messagebox

from games_registry import GAMES, GameEntry
from shared_sfx import SFX

ROOT = Path(__file__).resolve().parent

APP_NAME = "What If?"

HUB_BG = "#12141c"
HUB_PANEL = "#1a1e2a"
HUB_ACCENT = "#3d9e8c"
HUB_TITLE = "#e8eaf0"
HUB_MUTED = "#8b90a0"


def _ensure_modern_tk() -> None:
    """Re-exec under Anaconda/Homebrew Python if system Tk is too old (macOS)."""
    try:
        import tkinter as _tk
    except ImportError:
        return
    try:
        tk_version = float(_tk.TkVersion)
    except Exception:
        return
    if tk_version >= 8.6:
        return
    if os.environ.get("CLINT_GAMES_RELAUNCHED") == "1":
        return
    candidates = [
        "/opt/anaconda3/bin/python3.12",
        "/opt/anaconda3/bin/python3",
        "/opt/homebrew/bin/python3.12",
        "/usr/local/bin/python3.12",
    ]
    for cand in candidates:
        if not os.path.exists(cand) or cand == sys.executable:
            continue
        env = dict(os.environ)
        env["CLINT_GAMES_RELAUNCHED"] = "1"
        os.execve(cand, [cand, os.path.abspath(__file__), *sys.argv[1:]], env)


_ensure_modern_tk()


def _back_to_hub(hub: "GamesHub") -> Callable[[], None]:
    def back() -> None:
        hub._game_app = None
        hub.root.title(APP_NAME)
        hub.show_hub()

    return back


def _launch_periodic_wall(hub: "GamesHub") -> None:
    """Open Periodic Wall's own title screen inside this window."""
    periodic_dir = str(ROOT / "periodic_wall")
    if periodic_dir not in sys.path:
        sys.path.insert(0, periodic_dir)
    import periodic  # noqa: WPS433  — local game package

    hub.hide_hub()
    hub.root.title("The Periodic Wall of Elements")
    hub._game_app = periodic.PeriodicWallApp(
        root=hub.root,
        host=hub.game_host,
        on_back=_back_to_hub(hub),
    )


def _launch_global_windstorm(hub: "GamesHub") -> None:
    """Open Global Windstorm's title screen inside this window."""
    wind_dir = str(ROOT / "global_windstorm")
    if wind_dir not in sys.path:
        sys.path.insert(0, wind_dir)
    import windstorm  # noqa: WPS433  — local game package

    hub.hide_hub()
    hub.root.title("Global Windstorm")
    hub._game_app = windstorm.GlobalWindstormApp(
        root=hub.root,
        host=hub.game_host,
        on_back=_back_to_hub(hub),
    )


def _launch_expanding_earth(hub: "GamesHub") -> None:
    """Open Expanding Earth's title screen inside this window."""
    earth_dir = str(ROOT / "expanding_earth")
    if earth_dir not in sys.path:
        sys.path.insert(0, earth_dir)
    import earth  # noqa: WPS433  — local game package

    hub.hide_hub()
    hub.root.title("Expanding Earth")
    hub._game_app = earth.ExpandingEarthApp(
        root=hub.root,
        host=hub.game_host,
        on_back=_back_to_hub(hub),
    )


def _launch_geometry_dash(hub: "GamesHub") -> None:
    """Open Geometry Dash inside this window."""
    dash_dir = str(ROOT / "geometry_dash")
    if dash_dir not in sys.path:
        sys.path.insert(0, dash_dir)
    import dash  # noqa: WPS433  — local game package

    hub.hide_hub()
    hub.root.title("Geometry Dash")
    hub._game_app = dash.GeometryDashApp(
        root=hub.root,
        host=hub.game_host,
        on_back=_back_to_hub(hub),
    )


def _launch_battling_monsters(hub: "GamesHub") -> None:
    """Open Battling Monsters inside this window."""
    mon_dir = str(ROOT / "battling_monsters")
    if mon_dir not in sys.path:
        sys.path.insert(0, mon_dir)
    import monsters  # noqa: WPS433  — local game package

    hub.hide_hub()
    hub.root.title("Battling Monsters")
    hub._game_app = monsters.BattlingMonstersApp(
        root=hub.root,
        host=hub.game_host,
        on_back=_back_to_hub(hub),
    )


def _launch_raising_a_colony(hub: "GamesHub") -> None:
    """Open Raising a Colony inside this window."""
    col_dir = str(ROOT / "raising_a_colony")
    if col_dir not in sys.path:
        sys.path.insert(0, col_dir)
    import colony  # noqa: WPS433  — local game package

    hub.hide_hub()
    hub.root.title("Raising a Colony")
    hub._game_app = colony.RaisingColonyApp(
        root=hub.root,
        host=hub.game_host,
        on_back=_back_to_hub(hub),
    )


# Map GameEntry.launch_key → opener. Add new games here.
LAUNCHERS: dict[str, Callable[["GamesHub"], None]] = {
    "periodic_wall": _launch_periodic_wall,
    "global_windstorm": _launch_global_windstorm,
    "expanding_earth": _launch_expanding_earth,
    "geometry_dash": _launch_geometry_dash,
    "battling_monsters": _launch_battling_monsters,
    "raising_a_colony": _launch_raising_a_colony,
}


class GamesHub:
    """Top-level title screen: pick a game, then enter that game's title screen."""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title(APP_NAME)
        self.root.geometry("920x580")
        self.root.minsize(640, 420)
        self.root.configure(bg=HUB_BG)

        self.title_font = tkfont.Font(family="Helvetica", size=32, weight="bold")
        self.sub_font = tkfont.Font(family="Helvetica", size=13)
        self.btn_font = tkfont.Font(family="Helvetica", size=15, weight="bold")
        self.card_font = tkfont.Font(family="Helvetica", size=16, weight="bold")
        self.blurb_font = tkfont.Font(family="Helvetica", size=12)

        self._game_app = None
        self._hub_canvas: tk.Canvas | None = None
        self._hub_cards_window: int | None = None
        self._hub_cards: tk.Frame | None = None
        self._refresh_after_ids: list[str] = []

        # Separate layers: hub UI vs game mount (never pack+place the same parent).
        self.hub_frame = self._build_hub()
        self.game_host = tk.Frame(self.root, bg=HUB_BG)

        self.hub_frame.place(x=0, y=0, relwidth=1, relheight=1)

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def _build_hub(self) -> tk.Frame:
        frame = tk.Frame(self.root, bg=HUB_BG)

        header = tk.Frame(frame, bg=HUB_BG)
        header.pack(fill=tk.X, padx=28, pady=(28, 8))

        tk.Label(
            header,
            text=APP_NAME,
            font=self.title_font,
            fg=HUB_TITLE,
            bg=HUB_BG,
        ).pack(anchor=tk.W)

        tk.Label(
            header,
            text="Pick a game. New titles you add will show up here.",
            font=self.sub_font,
            fg=HUB_MUTED,
            bg=HUB_BG,
        ).pack(anchor=tk.W, pady=(6, 0))

        list_wrap = tk.Frame(frame, bg=HUB_BG)
        list_wrap.pack(fill=tk.BOTH, expand=True, padx=28, pady=(18, 12))

        canvas = tk.Canvas(list_wrap, bg=HUB_BG, highlightthickness=0, bd=0)
        scroll = tk.Scrollbar(list_wrap, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scroll.set)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        cards = tk.Frame(canvas, bg=HUB_BG)
        window_id = canvas.create_window((0, 0), window=cards, anchor=tk.NW)
        self._hub_canvas = canvas
        self._hub_cards_window = window_id
        self._hub_cards = cards

        def _sync_scroll(_event: tk.Event | None = None) -> None:
            self._sync_hub_scroll_width()

        cards.bind("<Configure>", _sync_scroll)
        canvas.bind("<Configure>", _sync_scroll)

        if not GAMES:
            tk.Label(
                cards,
                text="No games registered yet. Add one in games_registry.py.",
                font=self.sub_font,
                fg=HUB_MUTED,
                bg=HUB_BG,
            ).pack(pady=40)
        else:
            for game in GAMES:
                self._add_game_card(cards, game)

        footer = tk.Frame(frame, bg=HUB_BG)
        footer.pack(fill=tk.X, padx=28, pady=(4, 22))
        tk.Button(
            footer,
            text="Quit",
            font=self.btn_font,
            fg="#0d1117",
            bg=HUB_ACCENT,
            activeforeground="#0d1117",
            activebackground="#4db8a4",
            relief=tk.FLAT,
            padx=22,
            pady=8,
            cursor="hand2",
            command=self._on_close,
        ).pack(side=tk.RIGHT)

        return frame

    def _add_game_card(self, parent: tk.Frame, game: GameEntry) -> None:
        card = tk.Frame(parent, bg=HUB_PANEL, padx=18, pady=16)
        card.pack(fill=tk.X, pady=8)

        left = tk.Frame(card, bg=HUB_PANEL)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tk.Label(
            left,
            text=game.title,
            font=self.card_font,
            fg=HUB_TITLE,
            bg=HUB_PANEL,
            anchor=tk.W,
            justify=tk.LEFT,
            wraplength=560,
        ).pack(anchor=tk.W)

        tk.Label(
            left,
            text=game.blurb,
            font=self.blurb_font,
            fg=HUB_MUTED,
            bg=HUB_PANEL,
            anchor=tk.W,
            justify=tk.LEFT,
            wraplength=560,
        ).pack(anchor=tk.W, pady=(6, 0))

        play_btn = tk.Button(
            card,
            text="Play",
            font=self.btn_font,
            fg="#0d1117",
            bg=HUB_ACCENT,
            activeforeground="#0d1117",
            activebackground="#4db8a4",
            relief=tk.FLAT,
            padx=18,
            pady=10,
            cursor="hand2",
            command=lambda g=game: self._open_game(g),
        )
        play_btn.pack(side=tk.RIGHT, padx=(12, 0))

        for widget in (card, left, *left.winfo_children()):
            widget.bind("<Button-1>", lambda _e, g=game: self._open_game(g))
            widget.configure(cursor="hand2")

    def _open_game(self, game: GameEntry) -> None:
        if self._game_app is not None:
            return
        launcher = LAUNCHERS.get(game.launch_key)
        if launcher is None:
            messagebox.showinfo(
                "Coming soon",
                f'"{game.title}" is listed, but no launcher is wired yet.\n'
                f'Add LAUNCHERS["{game.launch_key}"] in games_hub.py.',
            )
            return
        SFX.play("ui", volume=0.4, min_gap=0.05)
        try:
            launcher(self)
        except Exception as exc:
            messagebox.showerror("Could not open game", str(exc))
            self._game_app = None
            self.show_hub()

    def hide_hub(self) -> None:
        """Cover the hub with the game host (hub stays mapped in the background)."""
        self._cancel_pending_refreshes()
        # Keep hub_frame placed so it retains a real fullscreen size on macOS Tk.
        self.game_host.place(x=0, y=0, relwidth=1, relheight=1)
        self.game_host.lift()
        self.root.update_idletasks()

    def show_hub(self) -> None:
        """Return to the game list and force canvases to relayout (fullscreen-safe)."""
        self._cancel_pending_refreshes()
        for child in list(self.game_host.winfo_children()):
            try:
                child.destroy()
            except tk.TclError:
                pass
        self.game_host.place_forget()

        self.hub_frame.place(x=0, y=0, relwidth=1, relheight=1)
        self.hub_frame.lift()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.root.title(APP_NAME)

        # Immediate + delayed passes — fullscreen layout settles asynchronously.
        self._refresh_hub_layout()
        for delay in (16, 50, 120, 250):
            aid = self.root.after(delay, self._refresh_hub_layout)
            self._refresh_after_ids.append(aid)

    def _cancel_pending_refreshes(self) -> None:
        for aid in self._refresh_after_ids:
            try:
                self.root.after_cancel(aid)
            except (tk.TclError, ValueError):
                pass
        self._refresh_after_ids.clear()

    def _sync_hub_scroll_width(self) -> None:
        if self._hub_canvas is None or self._hub_cards_window is None:
            return
        try:
            self.root.update_idletasks()
            cw = int(self._hub_canvas.winfo_width())
            ch = int(self._hub_canvas.winfo_height())
            if cw <= 1:
                # Fallback while Tk still reports a collapsed canvas in fullscreen.
                cw = max(200, int(self.root.winfo_width()) - 80)
            if ch <= 1:
                ch = max(120, int(self.root.winfo_height()) - 180)
                self._hub_canvas.configure(width=cw, height=ch)
            self._hub_canvas.itemconfigure(self._hub_cards_window, width=max(1, cw))
            bbox = self._hub_canvas.bbox("all")
            if bbox is not None:
                self._hub_canvas.configure(scrollregion=bbox)
        except tk.TclError:
            pass

    def _refresh_hub_layout(self) -> None:
        """Force hub widgets to get real sizes after a game (esp. macOS fullscreen)."""
        if self._game_app is not None:
            return
        try:
            if not self.hub_frame.winfo_ismapped():
                self.hub_frame.place(x=0, y=0, relwidth=1, relheight=1)
            self.hub_frame.lift()
            self.root.update_idletasks()

            rw = max(1, int(self.root.winfo_width()))
            rh = max(1, int(self.root.winfo_height()))
            # Explicit sizes help place() children after an overlay is removed.
            self.hub_frame.configure(width=rw, height=rh)

            if self._hub_cards is not None:
                wrap = max(240, rw - 120)
                for child in self._hub_cards.winfo_children():
                    for lbl in child.winfo_children():
                        if isinstance(lbl, tk.Frame):
                            for nested in lbl.winfo_children():
                                if isinstance(nested, tk.Label):
                                    nested.configure(wraplength=wrap)

            self._sync_hub_scroll_width()
            self.hub_frame.update_idletasks()
            if self._hub_canvas is not None:
                try:
                    self._hub_canvas.event_generate("<Configure>")
                except tk.TclError:
                    pass
            self.root.update_idletasks()
        except tk.TclError:
            pass

    def _on_close(self) -> None:
        self._cancel_pending_refreshes()
        SFX.stop_all()
        if self._game_app is not None:
            try:
                self._game_app.teardown()
            except Exception:
                pass
            self._game_app = None
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    GamesHub().run()


if __name__ == "__main__":
    main()
