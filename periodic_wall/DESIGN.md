# Periodic Wall — Design (Version 0: One Level)

**Read this first:** We are designing the game **from the ground up**.  
`periodic.py` stays on disk **only as reference** — old ideas (fusion, giant ball, seven floors, lava, nuke) are **not** what we build next.

**Do not change the game code until this doc says so.** This file is the blueprint.

---

## 1. What we are building now (only this)

One playable slice:

| Piece | In v0? |
|-------|--------|
| Title screen | Yes |
| Pick **one** level (Level 1 only) | Yes |
| Lab: stick person on a flat floor | Yes |
| Balls fall from the sky | Yes |
| Move, jump, duck | Yes |
| 5 hearts, 5-minute timer | Yes |
| Win / lose, then play again | Yes |
| **Fusion** (balls merging) | **No — deleted from design** |
| **Giant ball** | **No — deleted from design** |
| **Shockwaves** | **No — deleted from design** |
| Levels 2, 3, 4, 5, 6, 7 | **No — later** |
| Lava, platforms, scrolling | **No — later** |
| Nuke cutscene | **No — later** |

**Level 1 only.** Period 1 elements only (H, He — and isotopes like D, T if we keep them in the pool).  
**Job:** dodge falling balls. That is the whole game for now.

---

## 2. The story in plain English

You see a **wall of element bricks** and a **stick person**.

You press **Play**, then **Level 1** (or just “Start” — only one choice).

You enter a **dark lab**. Colored balls with chemical symbols fall from above.

- **Move** left and right. **Jump**. **Duck** on the ground.
- A ball hits you → lose **1 heart** (you get a short moment where another hit does not count).
- **5 hearts** total. **0 hearts** → you lose.
- Survive **5 minutes** → you win.

No combos. No merging balls. No huge ball. No explosions from fusion.

---

## 3. Build order (ground up — one layer at a time)

Add layers **in this order**. Do not skip ahead.

```
Layer 0 — Window & screens
          Open app, title, one “Start Level 1” path, quit

Layer 1 — Empty lab
          Dark room, floor line, stick person standing still (no balls yet)

Layer 2 — Player movement
          Left/right, jump, gravity, land on floor, duck

Layer 3 — One falling ball (manual test)
          Spawn a single ball, it falls, goes off screen

Layer 4 — Ball rain (Level 1 pool only)
          Spawn many balls from period 1; light, slow rain

Layer 5 — Damage & hearts
          Touch ball → lose heart, invincibility blink, die at 0

Layer 6 — Timer & win
          Count down 5:00; win when it hits zero with hearts left

Layer 7 — End flow
          “You won!” / “You died!” → back to title or play again
```

**Fusion, giant ball, and shockwaves are not layers.** They are not on the roadmap until v0 is done and we deliberately start “Version 1” with more levels or mechanics.

---

## 4. Player flow (one level)

```
START
  → Title (wall + Play)
  → Level 1 only (one button, or Play goes straight into lab)
  → Lab
  → Win or lose
  → Title or “Play again”
```

No floor picker with seven numbers. At most: **Play** → **lab**.

---

## 5. The three boxes (modules)

Keep the code split in mind even while everything might still live in one file at first.

### Box A — Rules (brain)

**Job:** Given “what is the world?” and “what did the player press?”, compute the next moment.

**Handles:**

- Stick person position and velocity  
- List of falling balls (spawn, move, remove when off-screen)  
- Hearts and invincibility timer  
- Match timer  
- Win / lose  

**Does NOT handle:**

- Drawing  
- Mouse/keyboard from the OS (shell sends actions in)  
- Fusion, giant ball, shockwaves, lava, platforms  

**In (each frame):**

| Input | Meaning |
|-------|---------|
| `player_input` | Keys held, jump pressed this frame |
| `dt` | Time since last frame (~1/30 s) |
| `state` | Full game snapshot (see below) |

**Out (each frame):**

| Output | Meaning |
|--------|---------|
| `new_state` | Updated positions, balls, HP, time left |
| `events` | e.g. `HIT`, `DIED`, `WON` (empty list most frames) |

---

### Box B — Art (eyes)

**Job:** Draw what the rules say is true.

**In:** Read-only snapshot + screen size (width, height).

**Out:** Pictures on screen (or a list of “draw circle here” for tests).

**Draws for v0:**

- Title: brick wall + stick person on bricks  
- Lab: dark background, floor, stick person, falling balls (symbol + color)  
- HUD: timer, hearts (text is fine)  
- Win/lose message  

**Does not draw:** fusion effects, giant ball, lava, nuke.

---

### Box C — Shell (hands and ears)

**Job:** Window, keyboard, mouse, clock tick, switch screens.

**In:** OS events (key down, click, close window).

**Out:** Calls rules with `player_input`; tells art to paint; shows title vs lab.

**For v0:** One level means no need for a big “FLOORS 1–7” bar — one **Play** or **Start** is enough.

---

## 6. Game snapshot (what we save each frame)

Everything the rules box needs, in one bag:

```
level: 1                    # only value for v0
hearts: 5                   # 0 .. 5
invuln_until: time          # can't take damage until this time
time_left: seconds          # counts down from 300
player: { x, y, vy }        # feet on floor
balls: [ { x, y, vx, vy, r, symbol, color }, ... ]
room: { width, height }
rng_seed: number            # for tests: same seed → same rain
screen: TITLE | LAB | END   # which page
```

No `giant_ball`. No `shockwaves`. No `platforms`. No `lava`.

---

## 7. Level 1 content (data)

**Element pool (period 1 only):**

- Symbols: H, He (and D, T if we treat them as hydrogen — match reference `periodic.py` pool when we code).
- Each ball has a **color** and a **size** tied to atomic number (heavier → often bigger / faster fall).

**Difficulty (v0 — keep gentle):**

- Few balls per second  
- Slow fall  
- Cap max balls on screen so the computer stays fast  

Exact numbers can copy **row 1 tuning** from `periodic.py` as a starting point when implementing — but **without** any fusion code paths.

---

## 8. Inputs (player)

| You do | Rules hear |
|--------|------------|
| A / D or arrows | Move left / right |
| W or up | Jump |
| S or down | Duck on floor; fall faster in air |
| Play / Enter | Leave title → start Level 1 |
| Close window | Quit |

No keys `2`–`7` in v0 (no other levels).

---

## 9. Outputs (what you see)

| Screen | What’s on it |
|--------|----------------|
| Title | Wall, stick person, Play, Quit |
| Lab | Dark room, floor, you, falling balls, timer, HP |
| End | “You won!” or “You died!” |

You should **never** see: giant ball, fusion flash, vertical shock columns, lava, level 7 explosion.

---

## 10. Rules examples (no fusion)

### Example 1 — First frame of lab

- **In:** 5 hearts, 300 s left, player on floor, no balls  
- **Out:** Maybe 0 or 1 new ball; player unchanged; no events  

### Example 2 — Ball hits player

- **In:** 5 hearts, ball overlaps hit area  
- **Out:** 4 hearts, ball removed, `HIT` event, short invuln  

### Example 3 — Two balls overlap each other

- **In:** Two H balls in the same place  
- **Out:** **Nothing special** — both keep falling (we deleted fusion from the design)  

### Example 4 — Timer reaches 0, 1 heart left

- **Out:** `WON`, switch to end screen  

### Example 5 — Fifth hit (0 hearts)

- **Out:** `DIED`, switch to end screen  

---

## 11. Testing — yes, every box gets tests

**Short answer:** Yes. **Each box gets its own test file** (or more than one if the box is big). If a box has no tests, we do not trust it.

### Why tests matter here

- Boxes only talk through **inputs** and **outputs**. Tests check: “I gave X, I got Y.”
- We can run tests **without opening the game window** for all rules boxes.
- When we add Level 2 later, old tests must still pass — that proves we did not break v0.

### Rules for writing tests

| Rule | Meaning |
|------|---------|
| **Fixed luck** | Use a fixed `rng_seed` so ball spawns are the same every run |
| **No Tk in rules tests** | Do not create a window in `player`, `hazards`, `combat`, etc. |
| **Small steps** | Test one box at a time, then **integration** tests that wire boxes together |
| **Given / When / Then** | Each scenario says start state, action, expected result |
| **v0 only** | No fusion, no giant ball, level 1 only — tests should fail if those appear |

### Test file map (one file per box)

| Box | Test file | Needs window? |
|-----|-----------|----------------|
| `data` | `tests/test_data.py` | No |
| `models` | `tests/test_models.py` | No |
| `player` | `tests/test_player.py` | No |
| `hazards` | `tests/test_hazards.py` | No |
| `combat` | `tests/test_combat.py` | No |
| `survival_sim` | `tests/test_survival_sim.py` | No |
| `screen_flow` | `tests/test_screen_flow.py` | No |
| `presentation` | `tests/test_presentation.py` | No |
| `shell` | `tests/test_shell_smoke.py` | Yes (optional, few tests) |

**Integration:** `tests/test_v0_playthrough.py` — several boxes together (still no drawing if we use fake state).

---

## 12. Test scenarios by box

Use scenario IDs (e.g. `P-03`) in code comments so failures are easy to find.

---

### Box: `data` (recipe book)

| ID | Given | When | Then |
|----|-------|------|------|
| D-01 | Game constants loaded | Read max hearts | Value is `5` |
| D-02 | Game constants loaded | Read win time | Value is `300` seconds |
| D-03 | Level 1 pool | List all symbols | Only period-1 symbols (H, He, D, T — per our pool) |
| D-04 | Level 1 pool | Every symbol | Has a color and atomic number Z |
| D-05 | Level 1 tuning | Read spawn settings | Values are “gentle” (few balls, slow — match doc numbers) |
| D-06 | v0 scope | Search design flags | No fusion / giant-ball / lava constants required for v0 |

---

### Box: `models` (snapshots and events)

| ID | Given | When | Then |
|----|-------|------|------|
| M-01 | Empty template | Create new lab state | `level==1`, `hearts==5`, `time_left==300`, `screen==LAB` |
| M-02 | Lab state | Copy / serialize | Round-trip: same values after load |
| M-03 | Player input | Press jump once | `jump_pressed==True` for one frame only |
| M-04 | Event list | Add `HIT` | Events readable as type + optional data |
| M-05 | v0 state | Inspect snapshot | No fields named `giant_ball`, `shockwaves`, `lava` |

---

### Box: `player` (stick person movement)

| ID | Given | When | Then |
|----|-------|------|------|
| P-01 | On floor, no keys | Wait one frame | `x` unchanged, `vy==0` |
| P-02 | On floor | Hold right 10 frames | `x` increased; still on floor |
| P-03 | On floor | Hold left 10 frames | `x` decreased; not past left wall |
| P-04 | On floor | Press jump | `vy` negative (going up) |
| P-05 | In air | Press jump again | Still allowed (air jump — match reference) |
| P-06 | In air, no jump | Wait many frames | Comes back to floor; `vy==0` on land |
| P-07 | On floor | Hold duck | Hitbox smaller / head lower (ducking true) |
| P-08 | At right edge | Hold right | `x` does not go past right bound |
| P-09 | In air | Hold fast-fall key | Falls faster than gravity alone |
| P-10 | Ducking on floor | Release duck | Standing hitbox restored |

---

### Box: `hazards` (falling balls only — no fusion)

| ID | Given | When | Then |
|----|-------|------|------|
| H-01 | Empty ball list, seed `42` | Spawn tick × 100 | At least one ball spawned |
| H-02 | Same seed `42` | Spawn tick × 100 | Same symbols at same times as repeat run |
| H-03 | Many spawns | Check all symbols | Every symbol ∈ period-1 pool only |
| H-04 | Ball above screen | Move tick | `y` increases (falls down) |
| H-05 | Ball below screen bottom | Move tick | Ball removed from list |
| H-06 | Max balls on screen | Keep spawning | Count ≤ hard cap |
| H-07 | Two balls overlap | One move tick | **Still two balls** (no merge, no giant ball) |
| H-08 | Heavier symbol (He vs H) | Spawn both | He ball radius ≥ H ball radius (or faster fall — per our rule) |
| H-09 | Gentle tuning | Spawn rate | Fewer balls per second than reference “hard” row 5 |

---

### Box: `combat` (hearts and invincibility)

| ID | Given | When | Then |
|----|-------|------|------|
| C-01 | 5 hearts, not invuln | Take 1 damage | 4 hearts |
| C-02 | 1 heart, not invuln | Take 1 damage | 0 hearts, `is_dead==True` |
| C-03 | Just took damage | Take damage again immediately | Hearts unchanged (invuln) |
| C-04 | Invuln expired | Take 1 damage | Hearts decrease again |
| C-05 | 5 hearts | Take 0 damage | 5 hearts |
| C-06 | Dead (`hearts==0`) | Take damage | Still dead, no negative hearts |

---

### Box: `survival_sim` (one frame — wires player + hazards + combat + timer)

| ID | Given | When | Then |
|----|-------|------|------|
| S-01 | Fresh lab start | First tick | Valid state; timer slightly less than 300 |
| S-02 | Fresh lab | 1 tick, no input | No `DIED` / `WON` |
| S-03 | Holding right | 30 ticks | Player moved right |
| S-04 | Ball overlapping player, not invuln | 1 tick | `HIT` event, heart −1, ball gone |
| S-05 | 4 hearts, invuln active | Overlapping ball | No second heart lost |
| S-06 | Script: stand still, seed fixed | Simulate 5 hits spaced apart | `DIED` on 5th |
| S-07 | No hits | Simulate until `time_left<=0` | `WON` |
| S-08 | Two overlapping balls | 1 tick | Ball count unchanged by fusion; no giant object in state |
| S-09 | `time_left==0.01`, 1 heart | 1 tick | `WON` before or on that tick |
| S-10 | `hearts==0` | 1 tick | `DIED`; lab stopped |

---

### Box: `screen_flow` (which page we are on)

| ID | Given | When | Then |
|----|-------|------|------|
| F-01 | App start | — | Screen is `TITLE` |
| F-02 | Title | Command `PLAY` | Screen is `LAB`, level 1 |
| F-03 | Lab | Command `QUIT` or close | App exit / title (per our choice) |
| F-04 | Lab | Event `WON` | Screen is `END` (win) |
| F-05 | Lab | Event `DIED` | Screen is `END` (lose) |
| F-06 | End win | Command `PLAY_AGAIN` | Back to `LAB` with fresh hearts/timer |
| F-07 | Title | Command `PICK_LEVEL_2` | **Rejected** (v0 has no level 2) |
| F-08 | Any | Command `START_NUKE` | **Rejected** in v0 |

---

### Box: `presentation` (drawing — test without human eyes)

Prefer: art box returns a **draw list** (circles, rects, text). Tests compare the list.

| ID | Given | When | Then |
|----|-------|------|------|
| R-01 | Title screen, size 800×500 | Build draw list | Contains wall/bricks tag or brick count > 0 |
| R-02 | Lab state, 0 balls | Build draw list | Floor line + stick person present |
| R-03 | Lab state, 3 balls | Build draw list | 3 ball entries with matching symbols |
| R-04 | Lab state | Build draw list | Timer text includes minutes/seconds |
| R-05 | Lab state, 3 hearts | Build draw list | HP shows `3` or three heart glyphs |
| R-06 | End win | Build draw list | Win message string present |
| R-07 | v0 lab state | Build draw list | **No** giant-ball layer, fusion FX, or lava rects |
| R-08 | Same state, same size | Build draw list twice | Identical lists (deterministic art) |

---

### Box: `shell` (window — keep tests small)

| ID | Given | When | Then |
|----|-------|------|------|
| K-01 | App launched | Click Play (or automation) | Lab visible within N seconds |
| K-02 | Lab | Press Esc / close | Window closes without hang |
| K-03 | Title | Press Enter | Same as Play |

Run these manually or with a tiny smoke script — not hundreds of them.

---

## 13. Integration scenarios (several boxes at once)

| ID | Story | Steps | Then |
|----|-------|-------|------|
| I-01 | Perfect run | Start lab → simulate 300s no input → no collisions | `WON` |
| I-02 | Immediate death | Start lab → force 5 overlaps 1s apart | `DIED` |
| I-03 | Dodge run | Start lab → move right every frame, seed 42 | Alive at 60s; hearts may drop if unlucky |
| I-04 | Title journey | `TITLE` → `PLAY` → lab 10 ticks → forfeit | Back to title or end; no crash |
| I-05 | No fusion regression | Whole match seed 99 | Never `giant_ball` in state; ball count only changes by spawn/off-screen/hit |

---

## 14. Test order (when we write code)

Build tests **in the same order as layers** (section 3):

1. `data`, `models`  
2. `player`  
3. `hazards`  
4. `combat`  
5. `survival_sim`  
6. `screen_flow`  
7. `presentation`  
8. `shell` smoke  
9. Integration `I-*`  

A box is “done” when **all its scenarios pass** and it does not break older boxes.

---

## 15. Quick examples (kid-friendly)

**Player box:** “If I hold right, my stick person’s `x` goes up.”  
**Hazards box:** “Only H and He rain — never sodium.”  
**Combat box:** “Five ouches and I’m out.”  
**Survival box:** “Five minutes safe and I win.”  
**Art box:** “Draw list has a stick person and no giant ball.”  

---

## 16. What we removed (on purpose)

These existed in reference `periodic.py` but are **out of v0 design**:

| Removed | Why |
|---------|-----|
| Fusion | Too complex; learn dodge first |
| Giant ball | Comes from fusion; gone |
| Shockwaves | Comes from fusion; gone |
| Floors 2–7 | One level first |
| Lava / platforms | Later version |
| Nuke scene | Later version |

When v0 works and tests pass, we write a **new** section in this doc for “Version 1” (e.g. Level 2 + fusion, or Level 2 harder rain only — team choice).

---

## 17. Folder plan (when we rewrite code)

```
periodic_wall/
  DESIGN.md
  periodic.py            ← reference only
  game/
    data.py
    models.py
    player.py
    hazards.py
    combat.py
    survival_sim.py
    screen_flow.py
  presentation/
    scenes.py
  shell/
    tk_app.py
  tests/
    test_data.py
    test_models.py
    test_player.py
    test_hazards.py
    test_combat.py
    test_survival_sim.py
    test_screen_flow.py
    test_presentation.py
    test_shell_smoke.py
    test_v0_playthrough.py   ← integration I-*
```

No `fusion.py`. No `giant_ball.py`. No `lava_level.py` in v0.

---

## 18. Version roadmap (after v0 is done)

| Version | Add |
|---------|-----|
| **v0 (now)** | Level 1, dodge only, no fusion |
| v1 | Level 2 (new element pool, harder rain) — still no fusion unless we decide |
| v2 | Level 3 |
| v3+ | Fusion / giant ball **only if** we add them back to the design doc on purpose |
| later | Lava, more floors, nuke |

Each version: update **this doc first** → tests → code.

---

## 19. Glossary

| Word | Meaning in v0 |
|------|----------------|
| Level | Always 1 for now |
| Ball / hazard | Falling element orb |
| Hearts / HP | 5 hits until game over |
| Rules box | Logic without drawing |
| Reference code | Old `periodic.py` — look at numbers/art, do not copy fusion |

---

## 20. Run reference game (optional)

To see the **old** full game (not v0):

```bash
cd periodic_wall
python3 periodic.py
```

That build may still have fusion and many floors. **Our target is not that behavior** until the doc is updated for a new version.

---

*Design spec: Version 0 — one level, no fusion, no giant ball, built from the ground up. `periodic.py` is reference only.*
