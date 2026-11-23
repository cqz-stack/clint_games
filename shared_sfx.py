"""Shared lightweight SFX for What If? games (procedural WAVs + macOS afplay)."""

from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

SOUNDS_DIR = Path(__file__).resolve().parent / "sounds"
_AFPLAY = "/usr/bin/afplay" if os.path.isfile("/usr/bin/afplay") else "afplay"


class GameSounds:
    """Play short effect WAVs without blocking the Tk loop."""

    def __init__(self, sounds_dir: Path | str | None = None) -> None:
        self.enabled = True
        self.sounds_dir = Path(sounds_dir) if sounds_dir else SOUNDS_DIR
        self._last_play: dict[str, float] = {}
        self._procs: list[subprocess.Popen] = []
        self._has_afplay = os.path.isfile("/usr/bin/afplay")

    def _reap(self) -> None:
        self._procs = [p for p in self._procs if p.poll() is None][-8:]

    def play(self, name: str, *, volume: float = 0.55, min_gap: float = 0.05) -> None:
        if not self.enabled or not self._has_afplay:
            return
        now = time.monotonic()
        if now - self._last_play.get(name, -99.0) < min_gap:
            return
        path = self.sounds_dir / f"{name}.wav"
        if not path.is_file():
            return
        self._last_play[name] = now
        self._reap()
        try:
            vol = max(0.05, min(1.0, volume))
            proc = subprocess.Popen(
                [_AFPLAY, "-v", f"{vol:.2f}", str(path)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            self._procs.append(proc)
        except OSError:
            self._has_afplay = False

    def stop_all(self) -> None:
        for p in self._procs:
            if p.poll() is None:
                try:
                    p.terminate()
                except OSError:
                    pass
        self._procs.clear()


SFX = GameSounds()
