# Legacy Periodic Wall (reference only)

This folder holds the **original monolith** before the v0 rewrite.

It includes fusion, giant ball, multiple floors, lava, and the nuke cutscene. **Not** the current game spec — see [../DESIGN.md](../DESIGN.md).

## Run the legacy game

```bash
cd reference
python3 periodic.py
```

On macOS, if Tk misbehaves: `/usr/bin/python3 periodic.py`

## Play the new v0 game

From the project root:

```bash
cd ..
python3 main.py
pytest
```
