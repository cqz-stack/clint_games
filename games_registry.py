"""What If? game catalog — add a new GameEntry here when you upload a game."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GameEntry:
    """One playable title on the hub screen."""

    id: str
    title: str
    blurb: str
    # How to open it from the hub (see games_hub.LAUNCHERS).
    launch_key: str


# Append new games at the bottom. The hub shows every entry as a clickable button.
GAMES: tuple[GameEntry, ...] = (
    GameEntry(
        id="periodic_wall",
        title="The Periodic Wall of Elements",
        blurb="Dodge elemental rain, fuse hazards, grab power-ups, and survive the floors.",
        launch_key="periodic_wall",
    ),
    GameEntry(
        id="global_windstorm",
        title="Global Windstorm",
        blurb="Duck and quad-jump through 5 storms of flying debris — red markers warn every throw.",
        launch_key="global_windstorm",
    ),
    GameEntry(
        id="expanding_earth",
        title="Expanding Earth",
        blurb="5 lives, 8 levels (each slower) — race 5 screens while dodging trunks, waves, and rocks.",
        launch_key="expanding_earth",
    ),
    GameEntry(
        id="geometry_dash",
        title="Geometry Dash",
        blurb="Hard long auto-runner — spikes, jump pads, and orbs you must click or fall through.",
        launch_key="geometry_dash",
    ),
    GameEntry(
        id="battling_monsters",
        title="Battling Monsters",
        blurb="Survivor-style sandbox — gems, gold shop, 50 stages, giant bosses every 10.",
        launch_key="battling_monsters",
    ),
    GameEntry(
        id="raising_a_colony",
        title="Raising a Colony",
        blurb="200-day colony reign (5 min/day). Termite queens go immobile — workers carry them.",
        launch_key="raising_a_colony",
    ),
)
