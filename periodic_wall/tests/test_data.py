"""D-* scenarios."""

from game import data


def test_d01_max_hearts():
    assert data.PLAYER_MAX_HP == 5


def test_d02_win_time():
    assert data.SURVIVE_SECONDS == 300.0


def test_d03_period1_symbols_only():
    syms = {s for s, _, _ in data.PERIOD_1_POOL}
    assert syms <= {"H", "He", "D", "T"}


def test_d04_every_symbol_has_z():
    for sym, _, z in data.PERIOD_1_POOL:
        assert data.SYMBOL_Z[sym] == z


def test_d05_gentle_tuning():
    t = data.LEVEL_1_TUNING
    assert t.rain_density <= 0.15
    assert t.burst_max <= 8


def test_d06_v0_gentler_than_hard_reference():
    assert data.LEVEL_1_TUNING.rain_density < data.REFERENCE_HARD_TUNING.rain_density
