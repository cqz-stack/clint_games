#!/usr/bin/env python3
"""Periodic Wall v0 — entry point.

The macOS system Python 3.9 ships with Tcl/Tk 8.5, which is deprecated and
fails to render Canvas content on modern macOS. We re-exec under a Python
with Tk >= 8.6 (anaconda3.12 is the proven one on this machine) so the game
window actually displays.
"""

from __future__ import annotations

import os
import sys


def _ensure_modern_tk() -> None:
    try:
        import tkinter
    except ImportError:
        return
    try:
        tk_version = float(tkinter.TkVersion)
    except Exception:
        return
    if tk_version >= 8.6:
        return

    if os.environ.get("PERIODIC_WALL_RELAUNCHED") == "1":
        sys.stderr.write(
            "ERROR: This Python's Tk is "
            f"{tk_version} (need >= 8.6). Please install Python 3.12 from "
            "python.org or anaconda3.\n"
        )
        return

    candidates = [
        "/opt/anaconda3/bin/python3.12",
        "/opt/anaconda3/bin/python3",
        "/opt/homebrew/bin/python3.12",
        "/usr/local/bin/python3.12",
    ]
    for cand in candidates:
        if not os.path.exists(cand):
            continue
        if cand == sys.executable:
            continue
        sys.stderr.write(
            f"Detected Tk {tk_version}; re-launching with {cand} for modern Tk 8.6+.\n"
        )
        env = dict(os.environ)
        env["PERIODIC_WALL_RELAUNCHED"] = "1"
        os.execve(cand, [cand, os.path.abspath(__file__), *sys.argv[1:]], env)


_ensure_modern_tk()

from shell.tk_app import run  # noqa: E402

if __name__ == "__main__":
    run()
