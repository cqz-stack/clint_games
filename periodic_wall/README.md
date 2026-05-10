# The Periodic Wall of Elements

Desktop survival game (Python + Tkinter). Clone this repo and run locally.

## Launch (macOS)

From this folder:

```bash
./play
```

That always uses **Apple’s** Python (`/usr/bin/python3`), which ships with Tk.

Or explicitly:

```bash
/usr/bin/python3 periodic.py
```

### If `python3 periodic.py` does nothing or errors

Your shell may be using **Homebrew’s** `python3` (often **no** `_tkinter`). Check:

```bash
which python3
python3 -c "import tkinter"
```

If that fails, either use `./play`, or put Apple first only for this command:

```bash
/usr/bin/python3 periodic.py
```

Other fixes: Command Line Tools (`xcode-select --install`), or `./launch_game.sh` for diagnostics.
