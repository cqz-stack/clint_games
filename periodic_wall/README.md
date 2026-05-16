# The Periodic Wall of Elements (v0)

Version 0: **Level 1 only** — dodge period-1 element rain. No fusion, no giant ball.

See [DESIGN.md](DESIGN.md) for the spec and [periodic_wall_v0_implementation_966ea666.plan.md](periodic_wall_v0_implementation_966ea666.plan.md) for the engineering plan.

## Play v0

```bash
cd periodic_wall
python3 main.py
```

On macOS: `/usr/bin/python3 main.py`

## Run tests

```bash
pip install pytest   # once
pytest
```

## Legacy full game (reference)

The old monolith (7 floors, fusion, lava, nuke) lives in [reference/](reference/):

```bash
cd reference
python3 periodic.py
```
