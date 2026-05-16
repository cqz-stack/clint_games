"""Screen navigation — no drawing."""

from __future__ import annotations

from game.models import Command, GameEvent, GameEventType, GameState, Screen


class FlowState:
    __slots__ = ("screen", "game")

    def __init__(self, screen: Screen = Screen.TITLE, game: GameState | None = None):
        self.screen = screen
        self.game = game


def reduce_flow(
    flow: FlowState,
    command: Command | None = None,
    events: list[GameEvent] | None = None,
    *,
    room_w: float = 920.0,
    room_h: float = 580.0,
    rng_seed: int = 0,
) -> FlowState:
    events = events or []

    if command == Command.QUIT:
        return flow

    if command == Command.PICK_LEVEL_2 or command == Command.START_NUKE:
        return flow

    if command == Command.PLAY and flow.screen == Screen.TITLE:
        flow.screen = Screen.LAB
        flow.game = GameState.new_lab(room_w, room_h, rng_seed)
        return flow

    if command == Command.PLAY_AGAIN and flow.screen in (Screen.END_WIN, Screen.END_LOSE):
        flow.screen = Screen.LAB
        flow.game = GameState.new_lab(room_w, room_h, rng_seed)
        return flow

    if command == Command.FORFEIT and flow.screen == Screen.LAB:
        flow.screen = Screen.TITLE
        flow.game = None
        return flow

    for ev in events:
        if ev.type == GameEventType.WON and flow.screen == Screen.LAB:
            flow.screen = Screen.END_WIN
        elif ev.type == GameEventType.DIED and flow.screen == Screen.LAB:
            flow.screen = Screen.END_LOSE

    return flow
