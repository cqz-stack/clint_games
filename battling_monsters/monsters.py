#!/usr/bin/env python3
"""Battling Monsters — Survivor.io-style: infinite sandbox, gems, level-ups, bosses.

Run standalone:
    /opt/anaconda3/bin/python3.12 monsters.py

Or open it from the What If? hub.
"""

from __future__ import annotations

import json
import math
import random
import sys
import traceback
import tkinter as tk
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from tkinter import font as tkfont
from tkinter import messagebox

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))
from shared_sfx import SFX  # noqa: E402

PROGRESS_PATH = Path(__file__).resolve().parent / "progress.json"

BG = "#14181c"
FLOOR = "#2d4a28"
FLOOR2 = "#254022"
ACCENT = "#c4e06a"
TITLE_FG = "#e8eaf0"
MUTED = "#8b90a0"
PLAYER_COL = "#6ec8ff"
SKIN = "#f0c8a0"
HP_FG = "#7cff6b"
HP_BG = "#2a3038"
HURT = "#ff5566"
BOSS_COL = "#ff4466"
MINI_COL = "#ffaa44"
CARD_BG = "#222830"
CARD_EDGE = "#4a5560"
SHOP_BG = "#1a222c"
GEM_GREEN = "#5dcf5a"
GEM_BLUE = "#4aa8ff"
GEM_GOLD = "#ffd24a"
CRATE_COL = "#8a6238"
CRATE_EDGE = "#c49a5a"
WAND_COL = "#e8d080"
GOLD_COL = "#ffd24a"

FRAME_MS = 16
CAMPAIGN_LEVELS = 50
BOSSES_PER_LEVEL = 3
# Regular stages: mid-run bosses at these player levels
BOSS_AT_PLAYER_LV = (10, 25, 40)
# Giant boss stages (every 10)
GIANT_STAGES = (10, 20, 30, 40, 50)
# Regular boss HP/damage scale: +10% per campaign stage (0.1 each level)
BOSS_SCALE_PER_LEVEL = 0.10

PLAYER_R = 16.0
BASE_SPEED = 420.0
BASE_HP = 14
PICKUP_BASE = 55.0
XP_PER_LEVEL = 5
HIT_INVULN = 0.95
OOC_REGEN_S = 5.0
KILL_DROP_FIRST = 5
KILL_DROP_EVERY = 50
MAX_SPEED_MULT = 1.8

SPAWN_BASE = 0.14  # much harder — constant pressure
CRATE_SPAWN_EVERY = 4.5
IDLE_GEM_EVERY = 3.0
IDLE_GEM_COUNT = 5

# Lobby shop (permanent upgrades). cost = base + step * owned
SHOP_ITEMS: dict[str, dict] = {
    "hp": {"name": "Max HP", "desc": "+2 max HP", "max": 12, "base": 40, "step": 25},
    "dmg": {"name": "Damage", "desc": "+10% damage", "max": 12, "base": 50, "step": 30},
    "spd": {"name": "Speed", "desc": "+6% move speed", "max": 8, "base": 45, "step": 28},
    "magnet": {"name": "Magnet", "desc": "+20% gem range", "max": 8, "base": 35, "step": 22},
    "goldfind": {"name": "Gold Find", "desc": "+25% crate gold", "max": 8, "base": 40, "step": 30},
    "orbit": {"name": "Start Orbit", "desc": "Begin runs with Orbit Blades", "max": 1, "base": 180, "step": 0},
    "aura": {"name": "Start Aura", "desc": "Begin runs with Burn Aura", "max": 1, "base": 180, "step": 0},
    # Hotbar unlocks (buy with gold — skeles free; termite earned by beating Termite Queen)
    "unlock_rockets": {"name": "Unlock Rockets", "desc": "Hotbar: Rocket Rain", "max": 1, "base": 120, "step": 0},
    "unlock_acid": {"name": "Unlock Acid", "desc": "Hotbar: Acid Bomb", "max": 1, "base": 140, "step": 0},
    "unlock_whirl": {"name": "Unlock Whirl", "desc": "Hotbar: Whirlwind", "max": 1, "base": 150, "step": 0},
    "unlock_meteor": {"name": "Unlock Meteors", "desc": "Hotbar: Meteor Shower", "max": 1, "base": 200, "step": 0},
}

# Hotbar skills — skeles start unlocked; others shop / termite via Stage 30
HOTBAR: tuple[dict, ...] = (
    {"id": "rockets", "name": "Rocket Rain", "key": "1", "cd": 9.0, "color": "#ff7744", "unlock": "unlock_rockets"},
    {"id": "acid", "name": "Acid Bomb", "key": "2", "cd": 8.0, "color": "#88ff44", "unlock": "unlock_acid"},
    {"id": "skeles", "name": "Summon Skeles", "key": "3", "cd": 14.0, "color": "#dde0e8", "unlock": "unlock_skeles"},
    {"id": "whirl", "name": "Whirlwind", "key": "4", "cd": 7.0, "color": "#88ccff", "unlock": "unlock_whirl"},
    {"id": "meteor", "name": "Meteor Shower", "key": "5", "cd": 12.0, "color": "#ff9944", "unlock": "unlock_meteor"},
    {"id": "termite", "name": "Termite Summon", "key": "6", "cd": 11.0, "color": "#c8a060", "unlock": "unlock_termite"},
)

# Every giant boss uses the full ability roster (immobile ones skip leap/charge in AI)
GIANT_FULL_KIT: tuple[str, ...] = (
    "summon",
    "slam",
    "volley",
    "charge",
    "nova",
    "beam",
    "rain",
    "swirl",
    "leap",
    "poison",
)
GIANT_HP_MULT = 5.0

GIANT_BOSSES: dict[int, dict] = {
    10: {
        "id": "queen_witch",
        "name": "Queen Witch",
        "body": "#6a2a8a",
        "accent": "#e0a0ff",
        "kit": GIANT_FULL_KIT,
        "hp": 420,
        "r": 48,
        "speed": 95,
        "immobile": False,
    },
    20: {
        "id": "king_zombie",
        "name": "King Zombie",
        "body": "#4a6a40",
        "accent": "#b0d0a0",
        "kit": GIANT_FULL_KIT,
        "hp": 560,
        "r": 52,
        "speed": 80,
        "immobile": False,
    },
    30: {
        "id": "termite_queen",
        "name": "Termite Queen",
        "body": "#8a7030",
        "accent": "#e0c070",
        "kit": GIANT_FULL_KIT,
        "hp": 700,
        "r": 56,
        "speed": 0,
        "immobile": True,
        "summon_every": 0.5,
    },
    40: {
        "id": "the_one",
        "name": "The One Zombie",
        "body": "#1a1a1a",
        "accent": "#ff3040",
        "kit": GIANT_FULL_KIT,
        "hp": 900,
        "r": 50,
        "speed": 120,
        "immobile": False,
    },
    50: {
        "id": "generator",
        "name": "The Generator",
        "body": "#406080",
        "accent": "#88e0ff",
        "kit": GIANT_FULL_KIT,
        "hp": 1100,
        "r": 58,
        "speed": 0,
        "immobile": True,
        "summon_every": 0.55,
        "lightning": True,
    },
}


def _default_progress() -> dict:
    return {
        "unlocked": 1,
        "gold": 0,
        "shop": {k: 0 for k in SHOP_ITEMS},
        "skills": {"unlock_termite": 0},  # earned by beating Termite Queen
    }


def _load_progress() -> dict:
    base = _default_progress()
    if PROGRESS_PATH.exists():
        try:
            data = json.loads(PROGRESS_PATH.read_text())
            base["unlocked"] = max(1, min(CAMPAIGN_LEVELS, int(data.get("unlocked", 1))))
            base["gold"] = max(0, int(data.get("gold", 0)))
            shop = data.get("shop", {})
            for k in SHOP_ITEMS:
                base["shop"][k] = max(0, min(SHOP_ITEMS[k]["max"], int(shop.get(k, 0))))
            skills = data.get("skills", {})
            base["skills"]["unlock_termite"] = 1 if int(skills.get("unlock_termite", 0)) else 0
        except Exception:
            pass
    return base


def _save_progress(progress: dict) -> None:
    try:
        PROGRESS_PATH.write_text(
            json.dumps(
                {
                    "unlocked": progress.get("unlocked", 1),
                    "gold": progress.get("gold", 0),
                    "shop": progress.get("shop", {}),
                    "skills": progress.get("skills", {}),
                }
            )
        )
    except OSError:
        pass


def _skill_unlocked(progress: dict, unlock_key: str) -> bool:
    if unlock_key == "unlock_skeles":
        return True  # starter hotbar ability
    if unlock_key == "unlock_termite":
        return int(progress.get("skills", {}).get("unlock_termite", 0)) >= 1
    return int(progress.get("shop", {}).get(unlock_key, 0)) >= 1


def _shop_cost(item_id: str, owned: int) -> int:
    d = SHOP_ITEMS[item_id]
    return int(d["base"] + d["step"] * owned)


WEAPON_DEFS: dict[str, dict] = {
    "orbit": {"name": "Orbit Blades", "desc": "Big spinning blades — high damage.", "max": 5},
    "bolt": {"name": "Magic Bolt", "desc": "Auto-fires at nearest foe.", "max": 5},
    "aura": {"name": "Burn Aura", "desc": "Damages monsters near you.", "max": 5},
    "wave": {"name": "Shock Wave", "desc": "Huge damaging pulse ring.", "max": 5},
    "meteor": {"name": "Meteor", "desc": "Drops rocks on random foes.", "max": 5},
}

AMP_DEFS: dict[str, dict] = {
    "dmg": {"name": "Power Amp", "desc": "+20% weapon damage."},
    "spd": {"name": "Swift Boots", "desc": "+6% move speed (capped)."},
    "asap": {"name": "Rapid Amp", "desc": "+15% attack speed."},
    "magnet": {"name": "Gem Magnet", "desc": "+30% gem pickup range."},
    "vital": {"name": "Vital Core", "desc": "+2 max HP and heal 2."},
}

# Zombie roster — kind, hp, speed, r, body, accent, attack, weight
MOB_KINDS = (
    ("zombie", 4.0, 88.0, 14.0, "#5a7a52", "#a8c0a0", "melee", 28),
    ("zdog", 2.5, 170.0, 11.0, "#6a6a48", "#c0b880", "dash", 16),
    ("spider_r", 3.2, 135.0, 12.0, "#a02828", "#ff7070", "spin", 12),
    ("spider_b", 3.6, 125.0, 12.0, "#2838a0", "#7090ff", "shoot", 12),
    ("worker", 6.5, 72.0, 16.0, "#c9a038", "#ffe08a", "melee", 18),
)

# Miniboss picks
MINI_BOSSES = (
    ("lead_worker", "Lead Zombie Worker", 55.0, 85.0, 26.0, "#d4b040", "#fff0a0", "melee"),
    ("spike_spider", "Spiky Zombie Spider", 48.0, 140.0, 24.0, "#802060", "#ff80d0", "spin"),
)

# Per campaign stage (1–10): three unique bosses. Each kit = summon + 2 specials.
# (id, name, body, accent, (ability, ability, ability))
STAGE_BOSSES: dict[int, tuple[tuple[str, str, str, str, tuple[str, str, str]], ...]] = {
    1: (
        ("slime", "Slime Lord", "#3a8a3a", "#b0ffb0", ("summon", "slam", "nova")),
        ("toad", "Bog Toad", "#4a6a2a", "#d0e080", ("summon", "volley", "poison")),
        ("root", "Root Hulk", "#5a4030", "#c0a080", ("summon", "charge", "rain")),
    ),
    2: (
        ("ash", "Ash Fiend", "#a04020", "#ffc090", ("summon", "nova", "beam")),
        ("ember", "Ember Witch", "#902020", "#ff8080", ("summon", "volley", "rain")),
        ("cinder", "Cinder Knight", "#6a3030", "#e0a090", ("summon", "charge", "slam")),
    ),
    3: (
        ("frost", "Frost Queen", "#5080c0", "#d0e8ff", ("summon", "volley", "nova")),
        ("yeti", "Yeti Chief", "#7090a0", "#e8f0ff", ("summon", "slam", "leap")),
        ("ice", "Ice Warden", "#4060a0", "#a0c0ff", ("summon", "beam", "swirl")),
    ),
    4: (
        ("sand", "Sand Pharaoh", "#c0a040", "#ffe0a0", ("summon", "rain", "beam")),
        ("scarab", "Scarab King", "#806020", "#e0c060", ("summon", "swirl", "charge")),
        ("mirage", "Mirage Mage", "#a08050", "#fff0c0", ("summon", "volley", "leap")),
    ),
    5: (
        ("storm", "Storm Titan", "#4050a0", "#a0b0ff", ("summon", "beam", "nova")),
        ("gale", "Gale Archer", "#6080b0", "#c0d8ff", ("summon", "volley", "rain")),
        ("thunder", "Thunder Ogre", "#303870", "#8090e0", ("summon", "slam", "swirl")),
    ),
    6: (
        ("vine", "Vine Hydra", "#2a6a40", "#80e0a0", ("summon", "poison", "slam")),
        ("bloom", "Bloom Witch", "#408060", "#a0ffc0", ("summon", "volley", "nova")),
        ("thorn", "Thorn Beast", "#306030", "#70c070", ("summon", "charge", "rain")),
    ),
    7: (
        ("bone", "Bone Lord", "#c8c0b0", "#fff8e0", ("summon", "swirl", "beam")),
        ("grave", "Grave Knight", "#8a8070", "#d0c8b0", ("summon", "charge", "slam")),
        ("wraith", "Wraith Queen", "#706890", "#d0c0ff", ("summon", "volley", "leap")),
    ),
    8: (
        ("magma", "Magma Baron", "#c03010", "#ff9040", ("summon", "nova", "rain")),
        ("lava", "Lava Witch", "#a02020", "#ff6060", ("summon", "volley", "beam")),
        ("basalt", "Basalt Golem", "#503028", "#c08060", ("summon", "slam", "charge")),
    ),
    9: (
        ("void", "Void Herald", "#301848", "#a060e0", ("summon", "swirl", "beam")),
        ("rift", "Rift Stalker", "#201030", "#8050c0", ("summon", "leap", "volley")),
        ("abyss", "Abyss Knight", "#181028", "#6040a0", ("summon", "charge", "nova")),
    ),
    10: (
        ("chaos", "Chaos Emperor", "#801030", "#ff4060", ("summon", "nova", "swirl")),
        ("doom", "Doom Sorcerer", "#601040", "#e040a0", ("summon", "rain", "beam")),
        ("final", "Final Colossus", "#401020", "#c02040", ("summon", "slam", "leap")),
    ),
}


@dataclass
class Monster:
    x: float
    y: float
    hp: float
    max_hp: float
    speed: float
    r: float
    kind: str
    body: str
    accent: str
    attack: str
    rank: str  # "mob" | "mini" | "boss"
    boss_i: int = 0
    name: str = ""
    kit: tuple[str, ...] = ()
    kit_i: int = 0
    hurt_t: float = 0.0
    atk_cd: float = 0.0
    state_t: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    facing: float = 0.0
    dead: bool = False
    immobile: bool = False
    summon_every: float = 0.0
    lightning: bool = False
    giant: bool = False


@dataclass
class Gem:
    x: float
    y: float
    value: int  # 1 / 5 / 10
    color: str
    r: float = 6.0


@dataclass
class PowerDrop:
    """bomb = clear screen, ham = +10 HP."""
    x: float
    y: float
    kind: str  # "bomb" | "ham"
    r: float = 12.0


@dataclass
class Crate:
    x: float
    y: float
    hp: float
    max_hp: float
    r: float = 16.0


@dataclass
class Coin:
    x: float
    y: float
    value: int
    r: float = 7.0


@dataclass
class Bullet:
    x: float
    y: float
    vx: float
    vy: float
    dmg: float
    life: float
    r: float = 5.0
    color: str = "#a0e0ff"
    hostile: bool = False  # True = hurts player


@dataclass
class RingFX:
    x: float
    y: float
    r: float
    max_r: float
    life: float
    color: str


@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: float
    color: str
    r: float = 3.0


@dataclass
class AcidPool:
    x: float
    y: float
    r: float
    life: float
    dps: float


@dataclass
class FallingMeteor:
    """Falls from the sky onto (x,y), then explodes."""
    x: float
    y: float
    height: float  # pixels above impact (screen offset)
    delay: float  # wait before dropping
    boom_r: float = 0.0
    boom_life: float = 0.0
    state: str = "fall"  # fall | boom | done
    dmg: float = 5.0


@dataclass
class PlayerLoadout:
    weapons: dict[str, int] = field(default_factory=lambda: {"bolt": 1})
    amps: dict[str, int] = field(default_factory=dict)
    shop_dmg: int = 0
    shop_spd: int = 0
    shop_magnet: int = 0
    shop_goldfind: int = 0
    shop_hp: int = 0

    def dmg_mult(self) -> float:
        return 1.0 + 0.20 * self.amps.get("dmg", 0) + 0.10 * self.shop_dmg

    def speed_mult(self) -> float:
        return min(MAX_SPEED_MULT, 1.0 + 0.08 * self.amps.get("spd", 0) + 0.06 * self.shop_spd)

    def asap_mult(self) -> float:
        return 1.0 + 0.15 * self.amps.get("asap", 0)

    def magnet_mult(self) -> float:
        return 1.0 + 0.30 * self.amps.get("magnet", 0) + 0.20 * self.shop_magnet

    def gold_mult(self) -> float:
        return 1.0 + 0.25 * self.shop_goldfind

    def bonus_hp(self) -> int:
        return 2 * self.amps.get("vital", 0) + 2 * self.shop_hp


class BattlingMonstersApp:
    def __init__(
        self,
        root: tk.Tk | None = None,
        *,
        host: tk.Misc | None = None,
        on_back: Callable[[], None] | None = None,
    ) -> None:
        self._owns_root = root is None
        self._on_back = on_back
        self.root = root if root is not None else tk.Tk()
        self._mount = host if host is not None else self.root
        self.root.title("Battling Monsters")
        if self._owns_root:
            self.root.geometry("960x600")
            self.root.minsize(720, 450)
        self.root.configure(bg=BG)
        try:
            self._mount.configure(bg=BG)  # type: ignore[union-attr]
        except tk.TclError:
            pass

        self.title_font = tkfont.Font(family="Helvetica", size=28, weight="bold")
        self.sub_font = tkfont.Font(family="Helvetica", size=13)
        self.btn_font = tkfont.Font(family="Helvetica", size=14, weight="bold")
        self.card_font = tkfont.Font(family="Helvetica", size=13, weight="bold")
        self.small_font = tkfont.Font(family="Helvetica", size=11)

        self._progress = _load_progress()
        self._on_title = True
        self._playing = False
        self._paused_levelup = False
        self._after_id: str | None = None
        self._keys: set[str] = set()
        self._cw = 900
        self._ch = 540
        self._cam_x = 0.0
        self._cam_y = 0.0

        self._campaign = 1
        self._px = 0.0
        self._py = 0.0
        self._facing = 0.0
        self._hp = float(BASE_HP)
        self._max_hp = float(BASE_HP)
        self._invuln = 0.0
        self._xp = 0
        self._plvl = 1
        self._xp_need = XP_PER_LEVEL
        self._loadout = PlayerLoadout()
        self._monsters: list[Monster] = []
        self._gems: list[Gem] = []
        self._drops: list[PowerDrop] = []
        self._crates: list[Crate] = []
        self._coins: list[Coin] = []
        self._bullets: list[Bullet] = []
        self._rings: list[RingFX] = []
        self._particles: list[Particle] = []
        self._acids: list[AcidPool] = []
        self._meteors: list[FallingMeteor] = []
        self._spawn_t = 0.0
        self._crate_t = 0.0
        self._gem_idle_t = 0.0
        self._mini_t = 25.0
        self._run_t = 0.0
        self._bosses_spawned = 0
        self._bosses_killed = 0
        self._kills = 0
        self._run_gold = 0
        self._ooc_t = 0.0
        self._orbit_angle = 0.0
        self._bolt_cd = self._aura_cd = self._wave_cd = self._meteor_cd = 0.0
        self._hot_cd: dict[str, float] = {h["id"]: 0.0 for h in HOTBAR}
        self._whirl_t = 0.0
        self._whirl_x = 0.0
        self._whirl_y = 0.0
        self._aim_skill: str | None = None
        self._aim_wx = 0.0
        self._aim_wy = 0.0
        self._hotbar_geom: list[tuple[str, float, float, float, float]] = []
        self._levelup_choices: list[tuple[str, str]] = []
        self._level_btns: list[tk.Button] = []
        self._shop_btns: dict[str, tk.Button] = {}
        self._gold_lbl: tk.Label | None = None
        self._pending_end: str | None = None  # "win" | "die"
        self._active_boss: Monster | None = None
        self._hit_this_frame = False
        self._bombing = False
        self._pending_termite_msg = False

        self.container = tk.Frame(self._mount, bg=BG)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.title_screen = self._build_title()
        self.play_screen = self._build_play()
        for scr in (self.title_screen, self.play_screen):
            scr.place(x=0, y=0, relwidth=1, relheight=1)

        self.root.bind("<Return>", self._on_enter)
        self.root.protocol("WM_DELETE_WINDOW", self._on_close_window)
        self.root.bind_all("<KeyPress>", self._on_key_down)
        self.root.bind_all("<KeyRelease>", self._on_key_up)
        self.show_title()

    def teardown(self) -> None:
        self._stop()
        SFX.stop_all()
        for seq in ("<Return>",):
            try:
                self.root.unbind(seq)
            except tk.TclError:
                pass
        try:
            self.root.unbind_all("<KeyPress>")
            self.root.unbind_all("<KeyRelease>")
        except tk.TclError:
            pass
        try:
            self.container.destroy()
        except tk.TclError:
            pass

    def _leave(self) -> None:
        if self._on_back is not None:
            self.teardown()
            self._on_back()
            return
        self._on_close_window()

    def _on_close_window(self) -> None:
        if self._on_back is not None and not self._owns_root:
            self._leave()
            return
        self._stop()
        try:
            self.root.destroy()
        except tk.TclError:
            pass

    def run(self) -> None:
        self.root.mainloop()

    def _btn(self, parent: tk.Misc, text: str, cmd: Callable[[], None], *, bg: str | None = None) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            font=self.btn_font,
            fg="#0d1117",
            bg=bg or ACCENT,
            activeforeground="#0d1117",
            activebackground="#d8f090",
            relief=tk.FLAT,
            padx=14,
            pady=7,
            cursor="hand2",
            command=cmd,
        )

    def _build_title(self) -> tk.Frame:
        frame = tk.Frame(self.container, bg=BG)
        # Main lobby
        main = tk.Frame(frame, bg=BG)
        main.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(16, 6), pady=10)
        box = tk.Frame(main, bg=BG)
        box.pack(fill=tk.BOTH, expand=True)
        tk.Label(box, text="Battling Monsters", font=self.title_font, fg=TITLE_FG, bg=BG).pack()
        tk.Label(
            box,
            text="Survivor.io sandbox · break crates for gold · shop in the lobby · much harder foes",
            font=self.sub_font,
            fg=MUTED,
            bg=BG,
            wraplength=640,
            justify=tk.CENTER,
        ).pack(pady=(4, 2))
        tk.Label(
            box,
            text="WASD move · auto wand attacks · 3 bosses per stage",
            font=self.sub_font,
            fg=ACCENT,
            bg=BG,
        ).pack(pady=(0, 6))

        tk.Label(box, text="Campaign (50 levels · giant bosses every 10)", font=self.btn_font, fg=TITLE_FG, bg=BG).pack(
            pady=(2, 4)
        )
        grid_wrap = tk.Frame(box, bg=BG)
        grid_wrap.pack(fill=tk.BOTH, expand=True, pady=(0, 4))
        # Tall viewport so many levels show at once; width tracks the lobby panel
        canvas = tk.Canvas(grid_wrap, bg=BG, highlightthickness=0, width=720, height=560)
        scroll = tk.Scrollbar(grid_wrap, orient=tk.VERTICAL, command=canvas.yview)
        grid = tk.Frame(canvas, bg=BG)
        win_id = canvas.create_window((0, 0), window=grid, anchor=tk.NW)

        def _sync_scroll(_e: tk.Event | None = None) -> None:
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _sync_width(e: tk.Event) -> None:
            # Stretch the button grid to the visible canvas width so no columns clip
            canvas.itemconfigure(win_id, width=max(1, int(e.width)))
            _sync_scroll()

        grid.bind("<Configure>", _sync_scroll)
        canvas.bind("<Configure>", _sync_width)
        canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)

        def _wheel(e: tk.Event) -> None:
            canvas.yview_scroll(int(-1 * (e.delta / 120)), "units")

        canvas.bind("<Enter>", lambda _e: canvas.bind_all("<MouseWheel>", _wheel))
        canvas.bind("<Leave>", lambda _e: canvas.unbind_all("<MouseWheel>"))

        self._level_btns.clear()
        cols = 5  # 5 across → Lv 1–10 fully visible in first two rows
        for i in range(1, CAMPAIGN_LEVELS + 1):
            label = f"Lv {i}"
            if i in GIANT_STAGES:
                label = f"☠{i}"
            b = tk.Button(
                grid,
                text=label,
                font=self.small_font,
                fg="#0d1117",
                bg=ACCENT,
                activeforeground="#0d1117",
                activebackground="#d8f090",
                relief=tk.FLAT,
                padx=10,
                pady=8,
                cursor="hand2",
                command=lambda n=i: self.start_run(n),
            )
            b.grid(row=(i - 1) // cols, column=(i - 1) % cols, padx=3, pady=3, sticky="nsew")
            self._level_btns.append(b)
        for c in range(cols):
            grid.columnconfigure(c, weight=1, uniform="lv")

        row = tk.Frame(box, bg=BG)
        row.pack(pady=(8, 0))
        leave = "Back to What If?" if self._on_back is not None else "Quit"
        self._btn(row, leave, self._leave).pack()

        # Side shop (slightly narrower so the level rack gets more room)
        shop = tk.Frame(frame, bg=SHOP_BG, width=240, highlightbackground=CARD_EDGE, highlightthickness=1)
        shop.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 12), pady=12)
        shop.pack_propagate(False)
        tk.Label(shop, text="GOLD SHOP", font=self.btn_font, fg=GOLD_COL, bg=SHOP_BG).pack(pady=(12, 4))
        self._gold_lbl = tk.Label(shop, text="Gold: 0", font=self.sub_font, fg=TITLE_FG, bg=SHOP_BG)
        self._gold_lbl.pack(pady=(0, 8))
        tk.Label(
            shop,
            text="Break crates in-run for gold.\nUpgrades are permanent.",
            font=self.small_font,
            fg=MUTED,
            bg=SHOP_BG,
            justify=tk.CENTER,
        ).pack(pady=(0, 8))

        self._shop_btns.clear()
        list_fr = tk.Frame(shop, bg=SHOP_BG)
        list_fr.pack(fill=tk.BOTH, expand=True, padx=10)
        for iid, idef in SHOP_ITEMS.items():
            row_f = tk.Frame(list_fr, bg=SHOP_BG)
            row_f.pack(fill=tk.X, pady=3)
            tk.Label(row_f, text=idef["name"], font=self.small_font, fg=TITLE_FG, bg=SHOP_BG, anchor=tk.W).pack(
                anchor=tk.W
            )
            tk.Label(row_f, text=idef["desc"], font=self.small_font, fg=MUTED, bg=SHOP_BG, anchor=tk.W).pack(
                anchor=tk.W
            )
            b = self._btn(row_f, "Buy", lambda i=iid: self._buy_shop(i), bg=GOLD_COL)
            b.pack(anchor=tk.W, pady=(2, 4))
            self._shop_btns[iid] = b
        return frame

    def _refresh_level_buttons(self) -> None:
        unlocked = self._progress["unlocked"]
        for i, b in enumerate(self._level_btns, start=1):
            giant = i in GIANT_STAGES
            if i <= unlocked:
                b.config(state=tk.NORMAL, bg=BOSS_COL if giant else ACCENT, text=f"☠{i}" if giant else f"Lv {i}")
            else:
                b.config(state=tk.DISABLED, bg="#555", text=f"{'☠' if giant else 'Lv '}{i} 🔒")
        self._refresh_shop()

    def _refresh_shop(self) -> None:
        if self._gold_lbl is not None:
            self._gold_lbl.config(text=f"Gold: {self._progress.get('gold', 0)}")
        shop = self._progress.get("shop", {})
        for iid, btn in self._shop_btns.items():
            owned = int(shop.get(iid, 0))
            mx = SHOP_ITEMS[iid]["max"]
            if owned >= mx:
                btn.config(state=tk.DISABLED, text="MAX", bg="#555")
            else:
                cost = _shop_cost(iid, owned)
                btn.config(state=tk.NORMAL, text=f"Buy {cost}g  ({owned}/{mx})", bg=GOLD_COL)

    def _buy_shop(self, item_id: str) -> None:
        shop = self._progress.setdefault("shop", {k: 0 for k in SHOP_ITEMS})
        owned = int(shop.get(item_id, 0))
        if owned >= SHOP_ITEMS[item_id]["max"]:
            return
        cost = _shop_cost(item_id, owned)
        if self._progress.get("gold", 0) < cost:
            messagebox.showinfo("Shop", "Not enough gold — break more crates!")
            return
        self._progress["gold"] -= cost
        shop[item_id] = owned + 1
        _save_progress(self._progress)
        SFX.play("ui", volume=0.45, min_gap=0.05)
        self._refresh_shop()

    def _build_play(self) -> tk.Frame:
        frame = tk.Frame(self.container, bg=BG)
        hud = tk.Frame(frame, bg=BG)
        hud.pack(fill=tk.X, padx=10, pady=6)
        self._hud_lbl = tk.Label(hud, text="", font=self.btn_font, fg=TITLE_FG, bg=BG, justify=tk.LEFT)
        self._hud_lbl.pack(side=tk.LEFT)
        self._btn(hud, "Quit run", self._forfeit).pack(side=tk.RIGHT)

        self.canvas = tk.Canvas(frame, bg=BG, highlightthickness=0, bd=0, takefocus=True)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self._on_cfg)
        self.canvas.bind("<Motion>", self._on_mouse_move)
        self.canvas.bind("<Button-1>", self._on_mouse_click)

        self._lu_frame = tk.Frame(self.canvas, bg=CARD_BG, highlightbackground=ACCENT, highlightthickness=2)
        tk.Label(self._lu_frame, text="LEVEL UP! Pick one", font=self.btn_font, fg=ACCENT, bg=CARD_BG).pack(
            pady=(12, 8)
        )
        self._lu_cards = tk.Frame(self._lu_frame, bg=CARD_BG)
        self._lu_cards.pack(padx=12, pady=(0, 12))
        return frame

    def _on_cfg(self, e: tk.Event) -> None:
        if e.widget is self.canvas:
            self._cw, self._ch = max(1, e.width), max(1, e.height)

    def _show(self, screen: tk.Frame) -> None:
        screen.tkraise()
        self.root.update_idletasks()

    def show_title(self) -> None:
        self._stop()
        self._hide_levelup()
        self._on_title = True
        self._progress = _load_progress()
        self._refresh_level_buttons()
        self._show(self.title_screen)

    def _bank_run_gold(self) -> None:
        if self._run_gold > 0:
            self._progress["gold"] = int(self._progress.get("gold", 0)) + self._run_gold
            _save_progress(self._progress)
            self._run_gold = 0

    def _on_enter(self, _e: tk.Event | None = None) -> None:
        if self._on_title:
            self.start_run(min(self._progress["unlocked"], CAMPAIGN_LEVELS))

    def _forfeit(self) -> None:
        self._bank_run_gold()
        self.show_title()

    def _stop(self) -> None:
        self._playing = False
        self._paused_levelup = False
        if self._after_id is not None:
            try:
                self.root.after_cancel(self._after_id)
            except tk.TclError:
                pass
            self._after_id = None

    def _on_key_down(self, e: tk.Event) -> None:
        key = (e.keysym or "").lower()
        self._keys.add(key)
        if not self._playing or self._paused_levelup:
            return
        if key == "escape":
            if self._aim_skill is not None:
                self._aim_skill = None
                return
            self._forfeit()
            return
        for h in HOTBAR:
            if key == h["key"]:
                self._select_hotbar(h["id"])
                break

    def _on_mouse_move(self, e: tk.Event) -> None:
        if not self._playing or self._aim_skill is None:
            return
        self._aim_wx = e.x + self._cam_x
        self._aim_wy = e.y + self._cam_y

    def _on_mouse_click(self, e: tk.Event) -> None:
        if not self._playing or self._paused_levelup:
            return
        # Hotbar slot click?
        for sid, x0, y0, x1, y1 in self._hotbar_geom:
            if x0 <= e.x <= x1 and y0 <= e.y <= y1:
                self._select_hotbar(sid)
                return
        if self._aim_skill is not None:
            self._aim_wx = e.x + self._cam_x
            self._aim_wy = e.y + self._cam_y
            self._confirm_aim()

    def _hotbar_is_unlocked(self, skill_id: str) -> bool:
        meta = next((h for h in HOTBAR if h["id"] == skill_id), None)
        if meta is None:
            return False
        return _skill_unlocked(self._progress, meta["unlock"])

    def _select_hotbar(self, skill_id: str) -> None:
        if self._pending_end:
            return
        if not self._hotbar_is_unlocked(skill_id):
            msg = (
                "Beat the Termite Queen (Stage 30) to unlock Termite Summon!"
                if skill_id == "termite"
                else "Buy this ability in the Gold Shop first!"
            )
            messagebox.showinfo("Locked", msg)
            return
        if self._hot_cd.get(skill_id, 0) > 0:
            return
        if self._aim_skill == skill_id:
            self._aim_skill = None
            return
        self._aim_skill = skill_id
        self._aim_wx = self._px + math.cos(self._facing) * 120
        self._aim_wy = self._py + math.sin(self._facing) * 120
        SFX.play("ui", volume=0.25, min_gap=0.05)

    def _confirm_aim(self) -> None:
        if self._aim_skill is None:
            return
        skill = self._aim_skill
        self._aim_skill = None
        self._fire_hotbar_at(skill, self._aim_wx, self._aim_wy)

    def _on_key_up(self, e: tk.Event) -> None:
        self._keys.discard((e.keysym or "").lower())

    def _schedule(self) -> None:
        if self._playing and not self._paused_levelup:
            self._after_id = self.root.after(FRAME_MS, self._tick_safe)

    def _tick_safe(self) -> None:
        """Never let an exception freeze the run forever."""
        try:
            self._tick()
        except Exception:
            traceback.print_exc()
            # If draw failed mid-frame, canvas may be blank — try a safe redraw
            try:
                if self._playing:
                    self.canvas.delete("all")
                    self.canvas.create_rectangle(0, 0, self._cw, self._ch, fill=FLOOR, outline="")
                    self.canvas.create_text(
                        self._cw * 0.5,
                        self._ch * 0.5,
                        text="(draw glitch — recovering…)",
                        fill=ACCENT,
                        font=("Helvetica", 14),
                    )
            except tk.TclError:
                pass
            if self._playing and not self._paused_levelup:
                self._schedule()

    # --- run ---------------------------------------------------------------

    def start_run(self, campaign: int) -> None:
        if campaign > self._progress["unlocked"]:
            return
        self._stop()
        self._campaign = campaign
        self._px = self._py = 0.0
        self._facing = 0.0
        shop = self._progress.get("shop", {})
        self._loadout = PlayerLoadout(
            shop_hp=int(shop.get("hp", 0)),
            shop_dmg=int(shop.get("dmg", 0)),
            shop_spd=int(shop.get("spd", 0)),
            shop_magnet=int(shop.get("magnet", 0)),
            shop_goldfind=int(shop.get("goldfind", 0)),
        )
        if int(shop.get("orbit", 0)) > 0:
            self._loadout.weapons["orbit"] = 1
        if int(shop.get("aura", 0)) > 0:
            self._loadout.weapons["aura"] = 1
        self._max_hp = float(BASE_HP + self._loadout.bonus_hp())
        self._hp = self._max_hp
        self._invuln = 0.0
        self._xp = 0
        self._plvl = 1
        self._xp_need = XP_PER_LEVEL
        self._monsters.clear()
        self._gems.clear()
        self._drops.clear()
        self._crates.clear()
        self._coins.clear()
        self._bullets.clear()
        self._rings.clear()
        self._particles.clear()
        self._acids.clear()
        self._meteors.clear()
        self._spawn_t = 0.0
        self._crate_t = 1.0
        self._gem_idle_t = 0.5
        self._mini_t = 18.0
        self._run_t = 0.0
        self._bosses_spawned = 0
        self._bosses_killed = 0
        self._kills = 0
        self._run_gold = 0
        self._ooc_t = 0.0
        self._orbit_angle = 0.0
        self._bolt_cd = self._aura_cd = self._wave_cd = self._meteor_cd = 0.0
        self._hot_cd = {h["id"]: 0.0 for h in HOTBAR}
        self._whirl_t = 0.0
        self._whirl_x = self._whirl_y = 0.0
        self._aim_skill = None
        self._keys.clear()
        self._pending_end = None
        self._pending_termite_msg = False
        self._active_boss = None
        self._hit_this_frame = False
        self._on_title = False
        self._playing = True
        self._paused_levelup = False
        self._hide_levelup()
        self._show(self.play_screen)
        self.root.update_idletasks()
        self._cw = max(400, int(self.canvas.winfo_width()))
        self._ch = max(300, int(self.canvas.winfo_height()))
        self._cam_x = self._px - self._cw * 0.5
        self._cam_y = self._py - self._ch * 0.5
        self._update_hud()
        SFX.play("start", volume=0.45, min_gap=0.2)
        self.canvas.focus_set()
        for _ in range(12):
            self._spawn_mob(near=360)
        for _ in range(6):
            self._spawn_crate(near=280)
        if self._is_giant_stage():
            self._spawn_giant_boss()
        self._schedule()

    def _diff(self) -> float:
        # Much harder curve
        return 1.55 + (self._campaign - 1) * 0.45 + self._run_t * 0.007 + (self._plvl - 1) * 0.04

    def _update_hud(self) -> None:
        try:
            need = self._bosses_needed()
            tag = " GIANT" if self._is_giant_stage() else ""
            self._hud_lbl.config(
                text=(
                    f"Stage {self._campaign}/50{tag}   Lv {self._plvl}  "
                    f"XP {self._xp}/{self._xp_need}   "
                    f"Bosses {self._bosses_killed}/{need}   "
                    f"Kills {self._kills}   Gold +{self._run_gold}"
                )
            )
        except tk.TclError:
            pass

    # --- spawn -------------------------------------------------------------

    def _spawn_mob(self, *, near: float = 520, rank: str = "mob") -> None:
        d = self._diff()
        ang = random.uniform(0, math.tau)
        dist = random.uniform(near * 0.75, near * 1.2)
        x = self._px + math.cos(ang) * dist
        y = self._py + math.sin(ang) * dist

        if rank == "mini":
            kid, bname, hp_b, spd, r, body, accent, attack = random.choice(MINI_BOSSES)
            hp = (hp_b + self._campaign * 16) * (1 + d * 0.35)
            speed = spd * (1.1 + d * 0.05)
            kind, name = kid, bname
        else:
            weights = [t[7] for t in MOB_KINDS]
            kid, hp_b, spd, r, body, accent, attack, _w = random.choices(MOB_KINDS, weights=weights, k=1)[0]
            hp = hp_b * (2.2 + d * 1.1)
            speed = spd * (1.2 + d * 0.1)
            kind = kid
            name = {
                "zombie": "Zombie",
                "zdog": "Zombie Dog",
                "spider_r": "Red Zombie Spider",
                "spider_b": "Blue Zombie Spider",
                "worker": "Zombie Worker",
            }.get(kid, kid.title())

        self._monsters.append(
            Monster(
                x,
                y,
                hp,
                hp,
                speed,
                r,
                kind,
                body,
                accent,
                attack,
                rank,
                name=name,
                atk_cd=random.uniform(0.4, 1.4),
            )
        )

    def _spawn_minion_near(self, bx: float, by: float, n: int = 4) -> None:
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            dist = random.uniform(40, 90)
            # reuse mob spawn placement but force near boss
            weights = [t[7] for t in MOB_KINDS]
            name, hp_b, spd, r, body, accent, attack, _w = random.choices(MOB_KINDS, weights=weights, k=1)[0]
            d = self._diff()
            hp = hp_b * (1.1 + d * 0.45)
            self._monsters.append(
                Monster(
                    bx + math.cos(ang) * dist,
                    by + math.sin(ang) * dist,
                    hp,
                    hp,
                    spd * (1.05 + d * 0.05),
                    r,
                    name,
                    body,
                    accent,
                    attack,
                    "mob",
                    name=name.title(),
                    atk_cd=random.uniform(0.2, 0.8),
                )
            )

    def _is_giant_stage(self) -> bool:
        return self._campaign in GIANT_STAGES

    def _bosses_needed(self) -> int:
        return 1 if self._is_giant_stage() else BOSSES_PER_LEVEL

    def _boss_scale(self) -> float:
        return 1.0 + BOSS_SCALE_PER_LEVEL * (self._campaign - 1)

    def _spawn_boss(self, boss_i: int) -> None:
        # Cycle stage kits 1–10 for variety on stages 11–49
        roster_key = ((self._campaign - 1) % 10) + 1
        roster = STAGE_BOSSES.get(roster_key, STAGE_BOSSES[1])
        kid, bname, body, accent, kit = roster[min(boss_i, len(roster)) - 1]
        d = self._diff()
        scale = self._boss_scale()
        ang = random.uniform(0, math.tau)
        x = self._px + math.cos(ang) * 480
        y = self._py + math.sin(ang) * 480
        hp = (180 + self._campaign * 55 + boss_i * 70 + d * 45) * scale
        speed = 90 + self._campaign * 6 + boss_i * 6
        m = Monster(
            x,
            y,
            hp,
            hp,
            speed,
            36.0,
            kid,
            body,
            accent,
            kit[0],
            "boss",
            boss_i=boss_i,
            name=bname,
            kit=kit,
            kit_i=0,
            atk_cd=1.0,
        )
        self._monsters.append(m)
        self._active_boss = m
        SFX.play("warn", volume=0.55, min_gap=0.3)
        self._update_hud()

    def _spawn_giant_boss(self) -> None:
        info = GIANT_BOSSES[self._campaign]
        scale = self._boss_scale()
        ang = random.uniform(0, math.tau)
        x = self._px + math.cos(ang) * 420
        y = self._py + math.sin(ang) * 420
        if info.get("immobile"):
            x, y = self._px + 280, self._py
        hp = float(info["hp"]) * scale * (1.0 + self._diff() * 0.15) * GIANT_HP_MULT
        kit = tuple(info.get("kit") or GIANT_FULL_KIT)
        m = Monster(
            x,
            y,
            hp,
            hp,
            float(info["speed"]),
            float(info["r"]),
            info["id"],
            info["body"],
            info["accent"],
            kit[0],
            "boss",
            boss_i=1,
            name=info["name"],
            kit=kit,
            kit_i=0,
            atk_cd=0.8,
            immobile=bool(info.get("immobile")),
            summon_every=float(info.get("summon_every", 0.0)),
            lightning=bool(info.get("lightning")),
            giant=True,
        )
        self._monsters.append(m)
        self._active_boss = m
        self._bosses_spawned = 1
        SFX.play("warn", volume=0.7, min_gap=0.2)
        self._update_hud()

    def _maybe_spawn_boss_by_level(self) -> None:
        if self._is_giant_stage():
            return
        if self._bosses_spawned >= BOSSES_PER_LEVEL:
            return
        if any(m.rank == "boss" and not m.dead for m in self._monsters):
            return
        need = BOSS_AT_PLAYER_LV[self._bosses_spawned]
        if self._plvl >= need:
            self._bosses_spawned += 1
            self._spawn_boss(self._bosses_spawned)

    def _maybe_spawn_mini(self, dt: float) -> None:
        self._mini_t -= dt
        if self._mini_t > 0:
            return
        self._mini_t = random.uniform(28.0, 42.0) / max(1.0, 0.7 + self._diff() * 0.15)
        if sum(1 for m in self._monsters if m.rank == "mini") < 2:
            self._spawn_mob(near=460, rank="mini")
            SFX.play("warn", volume=0.3, min_gap=0.4)

    # --- gems --------------------------------------------------------------

    def _drop_gems(self, m: Monster) -> None:
        # green=1, blue=5, gold=10
        if m.rank == "boss":
            bag = [("gold", 10, GEM_GOLD)] * 4 + [("blue", 5, GEM_BLUE)] * 3 + [("green", 1, GEM_GREEN)] * 2
        elif m.rank == "mini":
            bag = [("gold", 10, GEM_GOLD)] * 1 + [("blue", 5, GEM_BLUE)] * 2 + [("green", 1, GEM_GREEN)] * 2
        else:
            roll = random.random()
            if roll < 0.55:
                bag = [("green", 1, GEM_GREEN)]
            elif roll < 0.88:
                bag = [("blue", 5, GEM_BLUE)]
            else:
                bag = [("gold", 10, GEM_GOLD)]
        for i, (_n, val, col) in enumerate(bag):
            ox = random.uniform(-14, 14) + i * 3
            oy = random.uniform(-14, 14)
            self._gems.append(Gem(m.x + ox, m.y + oy, val, col, 5.5 if val == 1 else (7.0 if val == 5 else 9.0)))

    def _spawn_idle_gems(self, n: int = IDLE_GEM_COUNT) -> None:
        """Scatter gems around the map (near the player) over time."""
        for _ in range(n):
            ang = random.uniform(0, math.tau)
            dist = random.uniform(120, 780)
            x = self._px + math.cos(ang) * dist
            y = self._py + math.sin(ang) * dist
            roll = random.random()
            if roll < 0.55:
                val, col, r = 1, GEM_GREEN, 5.5
            elif roll < 0.88:
                val, col, r = 5, GEM_BLUE, 7.0
            else:
                val, col, r = 10, GEM_GOLD, 9.0
            self._gems.append(Gem(x, y, val, col, r))

    # --- combat ------------------------------------------------------------

    def _damage_monster(self, m: Monster, dmg: float) -> None:
        if m.dead:
            return
        m.hp -= dmg * self._loadout.dmg_mult()
        m.hurt_t = 0.12
        if m.hp <= 0:
            m.hp = 0
            m.dead = True

    def _flush_dead(self) -> None:
        survivors: list[Monster] = []
        for m in self._monsters:
            if not m.dead:
                survivors.append(m)
                continue
            if m.rank == "ally":
                continue  # expire quietly
            self._kills += 1
            self._drop_gems(m)
            # Bomb + ham at kill 5, then every 50 kills (50, 100, …)
            if not self._bombing and (
                self._kills == KILL_DROP_FIRST
                or (self._kills >= KILL_DROP_EVERY and self._kills % KILL_DROP_EVERY == 0)
            ):
                self._drops.append(PowerDrop(m.x - 16, m.y, "bomb"))
                self._drops.append(PowerDrop(m.x + 16, m.y, "ham"))
                SFX.play("ui", volume=0.35, min_gap=0.1)
            self._burst(m.x, m.y, m.body, 12 if m.rank != "mob" else 5)
            SFX.play(
                "explode_big" if m.rank == "boss" else "explode_small",
                volume=0.35,
                min_gap=0.04,
            )
            if m.rank == "boss":
                self._bosses_killed += 1
                if self._active_boss is m:
                    self._active_boss = None
                # Termite Queen → scrap into Zombie Destroyer + unlock hotbar
                if m.kind == "termite_queen":
                    self._progress.setdefault("skills", {})["unlock_termite"] = 1
                    _save_progress(self._progress)
                    self._pending_termite_msg = True
                SFX.play("win", volume=0.3, min_gap=0.2)
                if self._bosses_killed >= self._bosses_needed():
                    self._pending_end = "win"
        self._monsters = survivors
        self._update_hud()

    def _detonate_bomb(self) -> None:
        """Clear on-screen fodder; bosses only take a chunk of damage (no instakill)."""
        self._bombing = True
        camx, camy = self._cam_x, self._cam_y
        w, h = self._cw, self._ch
        for m in self._monsters:
            if m.dead:
                continue
            if not (camx - 40 <= m.x <= camx + w + 40 and camy - 40 <= m.y <= camy + h + 40):
                continue
            if m.rank == "boss":
                # Chip the boss — never one-shot
                chunk = max(12.0, m.max_hp * 0.12)
                m.hp = max(1.0, m.hp - chunk)
                m.hurt_t = 0.25
            elif m.rank == "ally":
                continue
            else:
                m.dead = True
                m.hp = 0
        self._rings.append(RingFX(self._px, self._py, 20, max(w, h) * 0.7, 0.55, "#ff8844"))
        self._burst(self._px, self._py, "#ff8844", 24)
        SFX.play("explode_big", volume=0.55, min_gap=0.15)
        self._flush_dead()
        self._bombing = False

    def _add_xp(self, amount: int) -> None:
        self._xp += amount
        if self._xp >= self._xp_need and not self._paused_levelup:
            self._xp -= self._xp_need
            self._plvl += 1
            self._xp_need = int(XP_PER_LEVEL + self._plvl * 1.6)
            self._update_hud()
            self._maybe_spawn_boss_by_level()
            SFX.play("ui", volume=0.45, min_gap=0.15)
            self._open_levelup()
        else:
            self._update_hud()

    def _offer_pool(self) -> list[tuple[str, str]]:
        pool: list[tuple[str, str]] = []
        for wid, wdef in WEAPON_DEFS.items():
            lv = self._loadout.weapons.get(wid, 0)
            if lv == 0:
                pool.append(("new", wid))
            elif lv < wdef["max"]:
                pool.append(("up", wid))
        for aid in AMP_DEFS:
            pool.append(("amp", aid))
        random.shuffle(pool)
        picks: list[tuple[str, str]] = []
        seen: set[str] = set()
        for item in pool:
            key = f"{item[0]}:{item[1]}"
            if key in seen:
                continue
            picks.append(item)
            seen.add(key)
            if len(picks) >= 3:
                break
        while len(picks) < 3:
            picks.append(("amp", random.choice(list(AMP_DEFS))))
        return picks[:3]

    def _open_levelup(self) -> None:
        self._paused_levelup = True
        self._levelup_choices = self._offer_pool()
        for child in self._lu_cards.winfo_children():
            child.destroy()
        for kind, oid in self._levelup_choices:
            if kind in ("new", "up"):
                d = WEAPON_DEFS[oid]
                title = d["name"]
                cur = self._loadout.weapons.get(oid, 0)
                sub = f"NEW · {d['desc']}" if kind == "new" else f"Upgrade to Lv {cur + 1} · {d['desc']}"
            else:
                d = AMP_DEFS[oid]
                title = d["name"]
                n = self._loadout.amps.get(oid, 0)
                sub = f"Amplifier ×{n + 1} · {d['desc']}"
            card = tk.Frame(self._lu_cards, bg="#2a323c", highlightbackground=CARD_EDGE, highlightthickness=1)
            card.pack(side=tk.LEFT, padx=6, pady=4)
            tk.Label(card, text=title, font=self.card_font, fg=TITLE_FG, bg="#2a323c").pack(padx=10, pady=(8, 2))
            tk.Label(card, text=sub, font=self.small_font, fg=MUTED, bg="#2a323c", wraplength=160).pack(
                padx=10, pady=(0, 6)
            )
            self._btn(card, "Take", lambda k=kind, i=oid: self._pick_levelup(k, i)).pack(pady=(0, 10))
        try:
            self.canvas.update_idletasks()
            self._lu_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        except tk.TclError:
            self._paused_levelup = False

    def _hide_levelup(self) -> None:
        try:
            self._lu_frame.place_forget()
        except tk.TclError:
            pass

    def _pick_levelup(self, kind: str, oid: str) -> None:
        if kind in ("new", "up"):
            self._loadout.weapons[oid] = self._loadout.weapons.get(oid, 0) + 1
        else:
            self._loadout.amps[oid] = self._loadout.amps.get(oid, 0) + 1
            if oid == "vital":
                self._max_hp = float(BASE_HP + self._loadout.bonus_hp())
                self._hp = min(self._max_hp, self._hp + 2)
        SFX.play("ui", volume=0.4, min_gap=0.05)
        self._hide_levelup()
        self._paused_levelup = False
        self._maybe_spawn_boss_by_level()
        self._update_hud()
        if self._xp >= self._xp_need:
            self._xp -= self._xp_need
            self._plvl += 1
            self._xp_need = int(XP_PER_LEVEL + self._plvl * 1.6)
            self._maybe_spawn_boss_by_level()
            self._open_levelup()
            return
        self._schedule()

    def _burst(self, x: float, y: float, color: str, n: int) -> None:
        for _ in range(n):
            a = random.uniform(0, math.tau)
            sp = random.uniform(40, 200)
            self._particles.append(
                Particle(x, y, math.cos(a) * sp, math.sin(a) * sp, random.uniform(0.15, 0.4), color)
            )

    def _hurt_player(self, amount: float = 1.0) -> None:
        if self._invuln > 0 or self._pending_end or self._hit_this_frame:
            return
        # Cap chip damage so overlapping foes can't delete you instantly
        amount = min(amount, 2.0)
        self._hit_this_frame = True
        self._hp -= amount
        self._invuln = HIT_INVULN
        self._ooc_t = 0.0
        SFX.play("warn", volume=0.35, min_gap=0.12)
        self._update_hud()
        if self._hp <= 0:
            self._hp = 0
            self._pending_end = "die"

    def _finish_if_pending(self) -> None:
        end = self._pending_end
        if not end:
            return
        self._pending_end = None
        gold_earned = self._run_gold
        self._bank_run_gold()
        self._stop()
        if self._pending_termite_msg:
            self._pending_termite_msg = False
            messagebox.showinfo(
                "Zombie Destroyer",
                "The Termite Queen was scrapped and remade into the Zombie Destroyer!\n"
                "Hotbar unlocked: Termite Summon (key 6) — stronger than skeletons.",
            )
        if end == "win":
            SFX.play("win", volume=0.6, min_gap=0.2)
            nxt = min(CAMPAIGN_LEVELS, self._campaign + 1)
            if nxt > self._progress["unlocked"]:
                self._progress["unlocked"] = nxt
            _save_progress(self._progress)
            msg = f"Stage {self._campaign} cleared!\nKills {self._kills} · Gold +{gold_earned}."
            msg += f"\nStage {nxt} unlocked." if self._campaign < CAMPAIGN_LEVELS else "\nYou beat all 50 stages!"
            messagebox.showinfo("Victory", msg)
        else:
            SFX.play("die", volume=0.55, min_gap=0.1)
            messagebox.showinfo(
                "Run over",
                f"Stage {self._campaign} failed.\nKills {self._kills} · Bosses {self._bosses_killed}/{self._bosses_needed()}"
                f"\nGold banked: +{gold_earned}",
            )
        self.show_title()

    def _spawn_crate(self, *, near: float = 420) -> None:
        ang = random.uniform(0, math.tau)
        dist = random.uniform(near * 0.6, near * 1.3)
        x = self._px + math.cos(ang) * dist
        y = self._py + math.sin(ang) * dist
        hp = 8 + self._campaign * 2 + self._diff() * 2
        self._crates.append(Crate(x, y, hp, hp, 15.0))

    def _damage_crate(self, c: Crate, dmg: float) -> None:
        c.hp -= dmg * self._loadout.dmg_mult()
        if c.hp <= 0:
            c.hp = 0
            base = random.randint(3, 8) + self._campaign
            val = max(1, int(base * self._loadout.gold_mult()))
            self._coins.append(Coin(c.x, c.y, val))
            self._burst(c.x, c.y, CRATE_COL, 8)
            SFX.play("rock", volume=0.25, min_gap=0.06)
            try:
                self._crates.remove(c)
            except ValueError:
                pass

    # --- enemy attacks -----------------------------------------------------

    def _update_monster_ai(self, m: Monster, dt: float) -> None:
        m.atk_cd = max(0.0, m.atk_cd - dt)
        m.state_t = max(0.0, m.state_t - dt)

        # Allied skeletons — chase enemies, expire with state_t
        if m.rank == "ally":
            if m.state_t <= 0:
                m.dead = True
                return
            foes = [e for e in self._monsters if not e.dead and e.rank != "ally"]
            if not foes:
                return
            t = min(foes, key=lambda e: math.hypot(e.x - m.x, e.y - m.y))
            dx, dy = t.x - m.x, t.y - m.y
            dist = math.hypot(dx, dy) or 1.0
            m.facing = math.atan2(dy, dx)
            m.x += (dx / dist) * m.speed * dt
            m.y += (dy / dist) * m.speed * dt
            if dist < m.r + t.r + 4 and m.atk_cd <= 0:
                # Termites = 3× skeles damage
                dmg = 6.6 if m.kind == "termite" else 2.2
                m.atk_cd = 0.35 if m.kind == "termite" else 0.45
                self._damage_monster(t, dmg * self._loadout.dmg_mult())
            return

        dx, dy = self._px - m.x, self._py - m.y
        dist = math.hypot(dx, dy) or 1.0
        m.facing = math.atan2(dy, dx)

        if m.rank == "boss":
            self._boss_ai(m, dt, dx, dy, dist)
            return
        if m.rank == "mini":
            m.x += (dx / dist) * m.speed * dt
            m.y += (dy / dist) * m.speed * dt
            if m.atk_cd <= 0:
                m.atk_cd = 2.8
                self._rings.append(RingFX(m.x, m.y, 8, 80, 0.4, MINI_COL))
                if dist < 70:
                    self._hurt_player(1.0)
                SFX.play("hit", volume=0.25, min_gap=0.15)
            if dist < PLAYER_R + m.r - 4:
                self._hurt_player(1.0)
            return

        if m.attack == "dash" and m.atk_cd <= 0 and dist < 260:
            m.atk_cd = 2.5
            m.state_t = 0.3
            m.vx = (dx / dist) * (m.speed * 2.8)
            m.vy = (dy / dist) * (m.speed * 2.8)
        if m.state_t > 0 and m.attack == "dash":
            m.x += m.vx * dt
            m.y += m.vy * dt
        else:
            m.x += (dx / dist) * m.speed * dt
            m.y += (dy / dist) * m.speed * dt

        if m.attack == "shoot" and m.atk_cd <= 0 and dist < 400:
            m.atk_cd = 2.1
            sp = 260.0
            self._bullets.append(
                Bullet(m.x, m.y, dx / dist * sp, dy / dist * sp, 1.0, 2.0, 5.0, "#ffe080", True)
            )
        elif m.attack == "orb" and m.atk_cd <= 0 and dist < 360:
            m.atk_cd = 2.8
            for off in (-0.3, 0.3):
                a = m.facing + off
                self._bullets.append(
                    Bullet(m.x, m.y, math.cos(a) * 200, math.sin(a) * 200, 1.0, 2.0, 6.0, "#d090ff", True)
                )
        elif m.attack == "spin" and m.atk_cd <= 0 and dist < 60:
            m.atk_cd = 1.4
            self._hurt_player(1.0)
            self._rings.append(RingFX(m.x, m.y, 5, 45, 0.25, m.accent))

        if m.attack in ("melee", "dash", "spin") and dist < PLAYER_R + m.r - 4:
            self._hurt_player(1.0)

    def _boss_cast(self, m: Monster, ability: str, dx: float, dy: float, dist: float) -> None:
        if ability == "summon":
            m.atk_cd = 3.0
            n = 5 + self._campaign // 2
            self._spawn_minion_near(m.x, m.y, n=n)
            self._rings.append(RingFX(m.x, m.y, 10, 70, 0.35, m.accent))
            SFX.play("warn", volume=0.4, min_gap=0.2)
        elif ability == "slam":
            m.atk_cd = 2.8
            self._rings.append(RingFX(m.x, m.y, 10, 130, 0.5, "#ff6644"))
            if dist < 120:
                self._hurt_player(2.0)
            SFX.play("rock", volume=0.4, min_gap=0.2)
        elif ability == "volley":
            m.atk_cd = 2.4
            for i in range(8):
                a = i * (math.tau / 8) + self._run_t
                self._bullets.append(
                    Bullet(m.x, m.y, math.cos(a) * 250, math.sin(a) * 250, 1.0, 2.3, 6.0, m.accent, True)
                )
            SFX.play("whoosh", volume=0.3, min_gap=0.15)
        elif ability == "charge":
            m.atk_cd = 3.0
            m.state_t = 0.5
            m.vx = (dx / dist) * 500
            m.vy = (dy / dist) * 500
            self._rings.append(RingFX(m.x, m.y, 8, 40, 0.3, "#a0c0ff"))
            SFX.play("warn", volume=0.35, min_gap=0.2)
        elif ability == "nova":
            m.atk_cd = 2.6
            self._rings.append(RingFX(m.x, m.y, 12, 160, 0.55, "#ffaa44"))
            if dist < 150:
                self._hurt_player(2.0)
            SFX.play("explode_small", volume=0.4, min_gap=0.15)
        elif ability == "beam":
            m.atk_cd = 2.5
            for i in range(6):
                t = 0.15 * i
                self._bullets.append(
                    Bullet(
                        m.x + dx / dist * 20,
                        m.y + dy / dist * 20,
                        dx / dist * (320 + i * 10),
                        dy / dist * (320 + i * 10),
                        1.0,
                        1.4 + t,
                        6.0,
                        "#ffee88",
                        True,
                    )
                )
            SFX.play("whoosh", volume=0.35, min_gap=0.12)
        elif ability == "rain":
            m.atk_cd = 2.7
            for _ in range(5):
                tx = self._px + random.uniform(-80, 80)
                ty = self._py + random.uniform(-80, 80)
                self._rings.append(RingFX(tx, ty, 5, 45, 0.4, "#ff9966"))
                if math.hypot(tx - self._px, ty - self._py) < 50:
                    self._hurt_player(1.0)
            SFX.play("rock", volume=0.3, min_gap=0.12)
        elif ability == "swirl":
            m.atk_cd = 2.5
            for i in range(10):
                a = i * (math.tau / 10) + self._run_t * 2
                self._bullets.append(
                    Bullet(
                        m.x,
                        m.y,
                        math.cos(a) * 180,
                        math.sin(a) * 180,
                        1.0,
                        2.4,
                        5.0,
                        m.accent,
                        True,
                    )
                )
            SFX.play("whoosh", volume=0.3, min_gap=0.12)
        elif ability == "leap":
            m.atk_cd = 2.8
            m.x = self._px + random.uniform(-40, 40)
            m.y = self._py + random.uniform(-40, 40)
            self._rings.append(RingFX(m.x, m.y, 8, 70, 0.35, m.accent))
            if math.hypot(m.x - self._px, m.y - self._py) < 70:
                self._hurt_player(1.5)
            SFX.play("dash_jump", volume=0.35, min_gap=0.15)
        elif ability == "poison":
            m.atk_cd = 2.9
            self._rings.append(RingFX(m.x, m.y, 15, 110, 0.7, "#66ff66"))
            if dist < 100:
                self._hurt_player(1.5)
            SFX.play("hit", volume=0.3, min_gap=0.15)
        else:
            m.atk_cd = 2.5

    def _boss_ai(self, m: Monster, dt: float, dx: float, dy: float, dist: float) -> None:
        # Immobile giants (Termite Queen / Generator) — keep special spawn + still cast full kit
        if m.immobile:
            m.facing = math.atan2(dy, dx)
            if m.summon_every > 0 and m.state_t <= 0:
                m.state_t = m.summon_every
                n = 5 if m.kind == "termite_queen" else 3
                self._spawn_minion_near(m.x, m.y, n=n)
                if m.lightning:
                    # Generator lightning bolts toward player
                    ux, uy = (dx / dist, dy / dist) if dist > 1e-3 else (1.0, 0.0)
                    for _ in range(2):
                        jitter = random.uniform(-0.25, 0.25)
                        ca, sa = math.cos(jitter), math.sin(jitter)
                        vx = (ux * ca - uy * sa) * 380
                        vy = (ux * sa + uy * ca) * 380
                        self._bullets.append(
                            Bullet(m.x, m.y, vx, vy, 1.5, 1.6, 7.0, "#88e0ff", True)
                        )
                    SFX.play("warn", volume=0.25, min_gap=0.12)
            if m.atk_cd <= 0:
                kit = m.kit or GIANT_FULL_KIT
                # Skip movement abilities so immobile bosses stay planted
                for _ in range(len(kit)):
                    ability = kit[m.kit_i % len(kit)]
                    m.kit_i += 1
                    if ability not in ("leap", "charge"):
                        self._boss_cast(m, ability, dx, dy, dist)
                        break
            if dist < PLAYER_R + m.r - 4:
                self._hurt_player(1.0)
            return

        if m.state_t <= 0:
            m.x += (dx / dist) * m.speed * dt
            m.y += (dy / dist) * m.speed * dt
        else:
            m.x += m.vx * dt
            m.y += m.vy * dt

        if m.atk_cd > 0:
            if dist < PLAYER_R + m.r - 6:
                self._hurt_player(1.0)
            return

        kit = m.kit or GIANT_FULL_KIT
        ability = kit[m.kit_i % len(kit)]
        m.kit_i += 1
        self._boss_cast(m, ability, dx, dy, dist)

        if dist < PLAYER_R + m.r - 6:
            self._hurt_player(1.0)

    # --- hotbar skills (aimed) ---------------------------------------------

    def _fire_hotbar_at(self, skill_id: str, ax: float, ay: float) -> None:
        if self._hot_cd.get(skill_id, 0) > 0 or self._pending_end:
            return
        meta = next(h for h in HOTBAR if h["id"] == skill_id)
        self._hot_cd[skill_id] = float(meta["cd"])
        dmg_m = self._loadout.dmg_mult()

        if skill_id == "rockets":
            for _ in range(8):
                tx = ax + random.uniform(-90, 90)
                ty = ay + random.uniform(-90, 90)
                self._rings.append(RingFX(tx, ty, 6, 52, 0.4, "#ff6644"))
                for m in list(self._monsters):
                    if m.dead or m.rank == "ally":
                        continue
                    if math.hypot(m.x - tx, m.y - ty) < 52:
                        self._damage_monster(m, 3.5 * dmg_m)
                self._burst(tx, ty, "#ff8844", 6)
            SFX.play("explode_big", volume=0.4, min_gap=0.15)

        elif skill_id == "acid":
            self._acids.append(AcidPool(ax, ay, 75.0, 5.5, 9.0 * dmg_m))
            self._rings.append(RingFX(ax, ay, 10, 75, 0.45, "#88ff44"))
            SFX.play("hit", volume=0.35, min_gap=0.1)

        elif skill_id == "skeles":
            for i in range(4):
                ang = i * (math.tau / 4)
                self._monsters.append(
                    Monster(
                        ax + math.cos(ang) * 28,
                        ay + math.sin(ang) * 28,
                        18 + self._campaign * 2,
                        18 + self._campaign * 2,
                        160.0,
                        12.0,
                        "skel",
                        "#d8dce8",
                        "#ffffff",
                        "melee",
                        "ally",
                        name="Skeleton",
                        atk_cd=0.3,
                        state_t=18.0,
                    )
                )
            SFX.play("warn", volume=0.3, min_gap=0.15)

        elif skill_id == "whirl":
            self._whirl_t = 2.4
            self._whirl_x, self._whirl_y = ax, ay
            self._rings.append(RingFX(ax, ay, 20, 110, 0.4, "#88ccff"))
            SFX.play("whoosh", volume=0.4, min_gap=0.1)

        elif skill_id == "meteor":
            for i in range(7):
                self._meteors.append(
                    FallingMeteor(
                        x=ax + random.uniform(-110, 110),
                        y=ay + random.uniform(-110, 110),
                        height=random.uniform(220, 380),
                        delay=i * 0.12 + random.uniform(0, 0.08),
                        dmg=5.5 * dmg_m,
                    )
                )
            SFX.play("warn", volume=0.4, min_gap=0.15)

        elif skill_id == "termite":
            # Exactly 3× skeles: count, HP, and (via ally AI) damage
            n = 12  # 4 skeles × 3
            skel_hp = 18 + self._campaign * 2
            for i in range(n):
                ang = i * (math.tau / n)
                self._monsters.append(
                    Monster(
                        ax + math.cos(ang) * 36,
                        ay + math.sin(ang) * 36,
                        skel_hp * 3,
                        skel_hp * 3,
                        185.0,
                        13.0,
                        "termite",
                        "#c8a060",
                        "#ffe0a0",
                        "melee",
                        "ally",
                        name="Termite",
                        atk_cd=0.25,
                        state_t=26.0,
                    )
                )
            SFX.play("warn", volume=0.35, min_gap=0.12)

        self._flush_dead()

    # --- player weapons ----------------------------------------------------

    def _fire_weapons(self, dt: float) -> None:
        asap = self._loadout.asap_mult()
        w = self._loadout.weapons

        if "orbit" in w:
            lv = w["orbit"]
            n = 3 + lv
            rad = 72 + lv * 14
            blade_r = 14 + lv * 2
            self._orbit_angle += (2.2 + lv * 0.3) * asap * dt
            for i in range(n):
                a = self._orbit_angle + i * (math.tau / n)
                bx = self._px + math.cos(a) * rad
                by = self._py + math.sin(a) * rad
                dmg = 1.4 + lv * 0.55
                for m in self._monsters:
                    if m.dead or m.rank == "ally":
                        continue
                    if math.hypot(m.x - bx, m.y - by) < m.r + blade_r:
                        self._damage_monster(m, dmg * dt * 10)
                for cr in list(self._crates):
                    if math.hypot(cr.x - bx, cr.y - by) < cr.r + blade_r:
                        self._damage_crate(cr, dmg * dt * 10)

        self._bolt_cd = max(0.0, self._bolt_cd - dt)
        if "bolt" in w and self._bolt_cd <= 0:
            # Prefer monsters; otherwise break nearest crate
            alive = [m for m in self._monsters if not m.dead and m.rank != "ally"]
            target_xy = None
            if alive:
                t = min(alive, key=lambda m: math.hypot(m.x - self._px, m.y - self._py))
                target_xy = (t.x, t.y)
            elif self._crates:
                t = min(self._crates, key=lambda c: math.hypot(c.x - self._px, c.y - self._py))
                target_xy = (t.x, t.y)
            if target_xy is not None:
                lv = w["bolt"]
                # Buffed wand: faster fire, faster shots, more damage
                self._bolt_cd = max(0.10, (0.34 - lv * 0.045) / asap)
                dx, dy = target_xy[0] - self._px, target_xy[1] - self._py
                dist = math.hypot(dx, dy) or 1.0
                sp = 620 + lv * 55
                self._bullets.append(
                    Bullet(self._px, self._py, dx / dist * sp, dy / dist * sp, 2.2 + lv * 0.85, 1.0, 6 + lv * 0.6)
                )

        self._aura_cd = max(0.0, self._aura_cd - dt)
        if "aura" in w and self._aura_cd <= 0:
            lv = w["aura"]
            self._aura_cd = 0.2 / asap
            rad = 70 + lv * 12
            dmg = 0.35 + lv * 0.2
            for m in self._monsters:
                if m.dead or m.rank == "ally":
                    continue
                if math.hypot(m.x - self._px, m.y - self._py) < rad + m.r:
                    self._damage_monster(m, dmg)
            for cr in list(self._crates):
                if math.hypot(cr.x - self._px, cr.y - self._py) < rad + cr.r:
                    self._damage_crate(cr, dmg)

        self._wave_cd = max(0.0, self._wave_cd - dt)
        if "wave" in w and self._wave_cd <= 0:
            lv = w["wave"]
            self._wave_cd = max(1.2, (2.8 - lv * 0.22) / asap)
            max_r = 180 + lv * 40
            self._rings.append(RingFX(self._px, self._py, 14, max_r, 0.5, "#ffe08a"))
            dmg = 2.4 + lv * 0.9
            for m in self._monsters:
                if m.dead or m.rank == "ally":
                    continue
                if math.hypot(m.x - self._px, m.y - self._py) < max_r:
                    self._damage_monster(m, dmg)
            for cr in list(self._crates):
                if math.hypot(cr.x - self._px, cr.y - self._py) < max_r:
                    self._damage_crate(cr, dmg)
            SFX.play("hit", volume=0.25, min_gap=0.12)

        self._meteor_cd = max(0.0, self._meteor_cd - dt)
        if "meteor" in w and self._meteor_cd <= 0:
            alive = [m for m in self._monsters if not m.dead and m.rank != "ally"]
            pool: list = list(alive) if alive else list(self._crates)
            if pool:
                lv = w["meteor"]
                self._meteor_cd = max(1.0, (2.8 - lv * 0.25) / asap)
                targets = random.sample(pool, k=min(1 + lv // 2, len(pool)))
                for t in targets:
                    self._rings.append(RingFX(t.x, t.y, 5, 55 + lv * 8, 0.35, "#ff9966"))
                    if isinstance(t, Crate):
                        self._damage_crate(t, 2.0 + lv * 0.8)
                    else:
                        self._damage_monster(t, 2.0 + lv * 0.8)
                    self._burst(t.x, t.y, "#ff9966", 6)
                SFX.play("rock", volume=0.3, min_gap=0.12)

    # --- tick --------------------------------------------------------------

    def _tick(self) -> None:
        if not self._playing or self._paused_levelup:
            return
        dt = FRAME_MS / 1000.0
        self._run_t += dt
        self._invuln = max(0.0, self._invuln - dt)
        self._hit_this_frame = False
        for hid in list(self._hot_cd):
            self._hot_cd[hid] = max(0.0, self._hot_cd[hid] - dt)
        self._whirl_t = max(0.0, self._whirl_t - dt)
        if self._whirl_t > 0:
            for m in list(self._monsters):
                if m.dead or m.rank == "ally":
                    continue
                if math.hypot(m.x - self._whirl_x, m.y - self._whirl_y) < 100:
                    self._damage_monster(m, 14.0 * dt * self._loadout.dmg_mult())

        # Falling meteors → realistic ground burst
        mets: list[FallingMeteor] = []
        for met in self._meteors:
            if met.state == "fall":
                if met.delay > 0:
                    met.delay -= dt
                else:
                    met.height -= 520 * dt
                    if met.height <= 0:
                        met.height = 0
                        met.state = "boom"
                        met.boom_r = 8.0
                        met.boom_life = 0.45
                        self._burst(met.x, met.y, "#ff9944", 16)
                        self._burst(met.x, met.y, "#ffe088", 10)
                        SFX.play("explode_big", volume=0.45, min_gap=0.08)
                        for m in list(self._monsters):
                            if m.dead or m.rank == "ally":
                                continue
                            if math.hypot(m.x - met.x, m.y - met.y) < 70:
                                self._damage_monster(m, met.dmg)
                        for cr in list(self._crates):
                            if math.hypot(cr.x - met.x, cr.y - met.y) < 70:
                                self._damage_crate(cr, met.dmg)
            elif met.state == "boom":
                met.boom_life -= dt
                met.boom_r = min(85.0, met.boom_r + 220 * dt)
                if met.boom_life <= 0:
                    met.state = "done"
            if met.state != "done":
                mets.append(met)
        self._meteors = mets

        # Out of combat regen: +1 HP after 5s without taking a hit
        if self._invuln <= 0 and self._hp < self._max_hp:
            self._ooc_t += dt
            if self._ooc_t >= OOC_REGEN_S:
                self._ooc_t = 0.0
                self._hp = min(self._max_hp, self._hp + 1)
                self._update_hud()
        else:
            if self._invuln > 0:
                self._ooc_t = 0.0

        mx = my = 0.0
        if self._keys & {"a", "left"}:
            mx -= 1
        if self._keys & {"d", "right"}:
            mx += 1
        if self._keys & {"w", "up"}:
            my -= 1
        if self._keys & {"s", "down"}:
            my += 1
        speed = BASE_SPEED * self._loadout.speed_mult()
        if mx or my:
            mag = math.hypot(mx, my)
            mx, my = mx / mag, my / mag
            self._facing = math.atan2(my, mx)
            self._px += mx * speed * dt
            self._py += my * speed * dt

        # Enemies keep coming hard the whole run (no mob cap)
        spawn_every = max(0.10, SPAWN_BASE / self._diff())
        self._spawn_t -= dt
        if self._spawn_t <= 0:
            self._spawn_t = spawn_every
            self._spawn_mob()
            self._spawn_mob()
            if random.random() < 0.55:
                self._spawn_mob()
            if self._diff() > 1.4 and random.random() < 0.5:
                self._spawn_mob()

        self._crate_t -= dt
        if self._crate_t <= 0:
            self._crate_t = CRATE_SPAWN_EVERY
            if len(self._crates) < 14:
                self._spawn_crate()
                if random.random() < 0.4:
                    self._spawn_crate()

        # Idle gems: 5 every 3 seconds around the map
        self._gem_idle_t -= dt
        if self._gem_idle_t <= 0:
            self._gem_idle_t = IDLE_GEM_EVERY
            self._spawn_idle_gems(IDLE_GEM_COUNT)

        self._maybe_spawn_mini(dt)
        self._maybe_spawn_boss_by_level()
        self._fire_weapons(dt)

        for m in self._monsters:
            if m.dead:
                continue
            m.hurt_t = max(0.0, m.hurt_t - dt)
            self._update_monster_ai(m, dt)

        # bullets
        alive_b: list[Bullet] = []
        for b in self._bullets:
            b.life -= dt
            b.x += b.vx * dt
            b.y += b.vy * dt
            if b.life <= 0:
                continue
            if b.hostile:
                if math.hypot(b.x - self._px, b.y - self._py) < PLAYER_R + b.r:
                    self._hurt_player(b.dmg)
                    continue
                alive_b.append(b)
            else:
                hit = False
                for m in self._monsters:
                    if m.dead or m.rank == "ally":
                        continue
                    if math.hypot(m.x - b.x, m.y - b.y) < m.r + b.r:
                        self._damage_monster(m, b.dmg)
                        hit = True
                        break
                if not hit:
                    for cr in list(self._crates):
                        if math.hypot(cr.x - b.x, cr.y - b.y) < cr.r + b.r:
                            self._damage_crate(cr, b.dmg)
                            hit = True
                            break
                if not hit:
                    alive_b.append(b)
        self._bullets = alive_b

        self._flush_dead()

        # acid pools
        acids2: list[AcidPool] = []
        for pool in self._acids:
            pool.life -= dt
            if pool.life <= 0:
                continue
            for m in list(self._monsters):
                if m.dead or m.rank == "ally":
                    continue
                if math.hypot(m.x - pool.x, m.y - pool.y) < pool.r + m.r:
                    self._damage_monster(m, pool.dps * dt)
            acids2.append(pool)
        self._acids = acids2
        self._flush_dead()

        # gems
        magnet = PICKUP_BASE * self._loadout.magnet_mult()
        kept: list[Gem] = []
        xp_gain = 0
        for g in self._gems:
            dx, dy = self._px - g.x, self._py - g.y
            dist = math.hypot(dx, dy)
            if dist < magnet and dist > 1:
                pull = 340 * dt
                g.x += dx / dist * pull
                g.y += dy / dist * pull
            if math.hypot(self._px - g.x, self._py - g.y) < PLAYER_R + g.r + 4:
                xp_gain += g.value
            else:
                kept.append(g)
        self._gems = [g for g in kept if math.hypot(g.x - self._px, g.y - self._py) < 1600]
        if xp_gain:
            SFX.play("dash_orb", volume=0.12, min_gap=0.04)
            self._add_xp(xp_gain)

        # bomb / ham pickups
        kept_d: list[PowerDrop] = []
        for d in self._drops:
            if math.hypot(d.x - self._px, d.y - self._py) < PLAYER_R + d.r + 6:
                if d.kind == "bomb":
                    self._detonate_bomb()
                else:
                    self._hp = min(self._max_hp, self._hp + 10)
                    self._burst(self._px, self._py, "#ff99aa", 10)
                    SFX.play("win", volume=0.25, min_gap=0.15)
                    self._update_hud()
            elif math.hypot(d.x - self._px, d.y - self._py) < 1800:
                kept_d.append(d)
        self._drops = kept_d

        # gold coins
        magnet = PICKUP_BASE * self._loadout.magnet_mult()
        kept_c: list[Coin] = []
        for coin in self._coins:
            dx, dy = self._px - coin.x, self._py - coin.y
            dist = math.hypot(dx, dy)
            if dist < magnet and dist > 1:
                coin.x += dx / dist * 360 * dt
                coin.y += dy / dist * 360 * dt
            if math.hypot(self._px - coin.x, self._py - coin.y) < PLAYER_R + coin.r + 4:
                self._run_gold += coin.value
                SFX.play("ui", volume=0.15, min_gap=0.04)
                self._update_hud()
            elif dist < 1800:
                kept_c.append(coin)
        self._coins = kept_c
        self._crates = [c for c in self._crates if math.hypot(c.x - self._px, c.y - self._py) < 1600]

        self._monsters = [
            m
            for m in self._monsters
            if m.rank in ("boss", "ally") or math.hypot(m.x - self._px, m.y - self._py) < 1400
        ]

        rings2: list[RingFX] = []
        for r in self._rings:
            r.life -= dt
            r.r = min(r.max_r, r.r + r.max_r * dt * 2.5)
            if r.life > 0:
                rings2.append(r)
        self._rings = rings2

        alive_p: list[Particle] = []
        for p in self._particles:
            p.life -= dt
            if p.life <= 0:
                continue
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.vx *= 0.9
            p.vy *= 0.9
            alive_p.append(p)
        self._particles = alive_p

        self._cam_x = self._px - self._cw * 0.5
        self._cam_y = self._py - self._ch * 0.5
        self._draw()

        if self._pending_end:
            self._finish_if_pending()
            return
        if self._playing and not self._paused_levelup:
            self._schedule()

    # --- draw --------------------------------------------------------------

    def _draw_hp_bar(self, c: tk.Canvas, x0: float, y0: float, x1: float, y1: float, frac: float, fill: str) -> None:
        c.create_rectangle(x0, y0, x1, y1, fill=HP_BG, outline="#111", width=1)
        frac = max(0.0, min(1.0, frac))
        if frac > 0:
            c.create_rectangle(x0, y0, x0 + (x1 - x0) * frac, y1, fill=fill, outline="")

    def _draw_humanoid(
        self,
        c: tk.Canvas,
        sx: Callable[[float], float],
        sy: Callable[[float], float],
        m: Monster | None,
        *,
        px: float,
        py: float,
        r: float,
        body: str,
        accent: str,
        facing: float,
        hurt: bool = False,
        wand: bool = False,
    ) -> None:
        col = HURT if hurt else body
        skin = SKIN if wand or (m is None) else accent
        # boots / legs
        lx = math.cos(facing + 0.55) * r * 0.6
        ly = math.sin(facing + 0.55) * r * 0.6
        rx = math.cos(facing - 0.55) * r * 0.6
        ry = math.sin(facing - 0.55) * r * 0.6
        c.create_line(sx(px), sy(py + r * 0.1), sx(px + lx), sy(py + ly + r * 0.45), fill="#3a3a4a", width=4)
        c.create_line(sx(px), sy(py + r * 0.1), sx(px + rx), sy(py + ry + r * 0.45), fill="#3a3a4a", width=4)
        # torso / clothes
        c.create_oval(
            sx(px - r * 0.75),
            sy(py - r * 0.5),
            sx(px + r * 0.75),
            sy(py + r * 0.75),
            fill=col,
            outline="#111",
            width=2,
        )
        # belt
        c.create_rectangle(sx(px - r * 0.55), sy(py + r * 0.15), sx(px + r * 0.55), sy(py + r * 0.32), fill="#2a2a33", outline="")
        # head + hair
        hx = px + math.cos(facing) * r * 0.12
        hy = py - r * 0.95
        c.create_oval(
            sx(hx - r * 0.48),
            sy(hy - r * 0.48),
            sx(hx + r * 0.48),
            sy(hy + r * 0.48),
            fill=skin,
            outline="#111",
            width=2,
        )
        c.create_arc(
            sx(hx - r * 0.5),
            sy(hy - r * 0.55),
            sx(hx + r * 0.5),
            sy(hy + r * 0.1),
            start=0,
            extent=180,
            fill="#3b2a1a",
            outline="",
        )
        # eyes + mouth
        ex = math.cos(facing)
        ey = math.sin(facing)
        c.create_oval(sx(hx + ex * 4 - 2.5), sy(hy + ey * 2 - 2), sx(hx + ex * 4 + 1), sy(hy + ey * 2 + 1.5), fill="#111", outline="")
        c.create_oval(sx(hx + ex * 1 - 1), sy(hy + ey * 2 - 2), sx(hx + ex * 1 + 2.5), sy(hy + ey * 2 + 1.5), fill="#111", outline="")
        c.create_line(sx(hx - 3), sy(hy + 5), sx(hx + 3), sy(hy + 5), fill="#a07050", width=1)
        # arms
        ax = math.cos(facing + 1.05) * r * 0.95
        ay = math.sin(facing + 1.05) * r * 0.95
        bx = math.cos(facing - 1.05) * r * 0.95
        by = math.sin(facing - 1.05) * r * 0.95
        c.create_line(sx(px), sy(py - r * 0.05), sx(px + ax), sy(py + ay), fill=skin, width=3)
        c.create_line(sx(px), sy(py - r * 0.05), sx(px + bx), sy(py + by), fill=skin, width=3)
        if wand:
            # magic wand in front hand
            tipx = px + math.cos(facing) * (r + 22)
            tipy = py + math.sin(facing) * (r + 22)
            hx2 = px + bx * 0.7
            hy2 = py + by * 0.7
            c.create_line(sx(hx2), sy(hy2), sx(tipx), sy(tipy), fill=WAND_COL, width=3)
            c.create_oval(sx(tipx - 5), sy(tipy - 5), sx(tipx + 5), sy(tipy + 5), fill="#88eeff", outline="#dff")
        if m and m.rank == "boss":
            c.create_polygon(
                sx(hx - r * 0.4),
                sy(hy - r * 0.35),
                sx(hx),
                sy(hy - r * 0.95),
                sx(hx + r * 0.4),
                sy(hy - r * 0.35),
                fill=BOSS_COL,
                outline="#111",
            )
        if m and m.rank == "mini":
            c.create_oval(sx(hx - 3), sy(hy - r * 0.7), sx(hx + 3), sy(hy - r * 0.4), fill=MINI_COL, outline="")

    def _draw_zombie(
        self,
        c: tk.Canvas,
        sx: Callable[[float], float],
        sy: Callable[[float], float],
        m: Monster,
    ) -> None:
        col = HURT if m.hurt_t > 0 else m.body
        px, py, r, facing = m.x, m.y, m.r, m.facing
        kind = m.kind

        if kind in ("zdog",):
            # Four-legged rotting dog (side-ish view along facing)
            fx, fy = math.cos(facing), math.sin(facing)
            pxr, pyr = -fy, fx  # perpendicular
            # torso
            c.create_oval(
                sx(px - fx * r * 1.1 - pxr * r * 0.45),
                sy(py - fy * r * 1.1 - pyr * r * 0.45),
                sx(px + fx * r * 1.1 + pxr * r * 0.45),
                sy(py + fy * r * 1.1 + pyr * r * 0.45),
                fill=col,
                outline="#2a3a28",
                width=2,
            )
            # head / snout
            hx = px + fx * r * 1.35
            hy = py + fy * r * 1.35
            c.create_oval(sx(hx - r * 0.45), sy(hy - r * 0.4), sx(hx + r * 0.45), sy(hy + r * 0.4), fill="#6a8058", outline="#111")
            c.create_oval(
                sx(hx + fx * r * 0.35 - 3),
                sy(hy + fy * r * 0.35 - 2),
                sx(hx + fx * r * 0.55 + 3),
                sy(hy + fy * r * 0.35 + 2),
                fill="#4a5a40",
                outline="#111",
            )
            # pointed ears
            for side in (-1, 1):
                ex = hx + pxr * side * r * 0.35 - fx * 2
                ey = hy + pyr * side * r * 0.35 - fy * 2
                c.create_polygon(
                    sx(ex),
                    sy(ey),
                    sx(ex + pxr * side * 4 - fx * 8),
                    sy(ey + pyr * side * 4 - fy * 8),
                    sx(ex - pxr * side * 3),
                    sy(ey - pyr * side * 3),
                    fill="#5a7048",
                    outline="#111",
                )
            # four legs
            for along, side in ((-0.7, -1), (-0.7, 1), (0.55, -1), (0.55, 1)):
                lx = px + fx * r * along + pxr * side * r * 0.35
                ly = py + fy * r * along + pyr * side * r * 0.35
                c.create_line(sx(lx), sy(ly), sx(lx + pxr * side * 2), sy(ly + r * 0.85), fill="#3a4a38", width=3)
            # glowing zombie eye
            c.create_oval(sx(hx + fx * 2 - 2), sy(hy + fy * 2 - 2), sx(hx + fx * 2 + 2), sy(hy + fy * 2 + 2), fill="#7dff6a", outline="")
            # ragged tail
            tx = px - fx * r * 1.25
            ty = py - fy * r * 1.25
            c.create_line(sx(px - fx * r * 0.9), sy(py - fy * r * 0.9), sx(tx), sy(ty), fill="#4a5a40", width=2)
            return

        if kind in ("spider_r", "spider_b", "spike_spider"):
            # Body first — legs from body SIDES only (not out of the head)
            c.create_oval(
                sx(px - r), sy(py - r * 0.55), sx(px + r), sy(py + r * 0.65), fill=col, outline="#111", width=2
            )
            # side legs (left/right of abdomen)
            for side in (-1, 1):
                for i in range(3):
                    along = -0.35 + i * 0.35
                    base_x = px + math.cos(facing) * r * along
                    base_y = py + math.sin(facing) * r * along
                    out = facing + side * (0.9 + i * 0.15)
                    c.create_line(
                        sx(base_x),
                        sy(base_y),
                        sx(base_x + math.cos(out) * r * 1.35),
                        sy(base_y + math.sin(out) * r * 1.35),
                        fill=col,
                        width=2,
                    )
            # head in front of body (no legs from here)
            hx = px + math.cos(facing) * r * 0.85
            hy = py + math.sin(facing) * r * 0.85
            c.create_oval(sx(hx - r * 0.4), sy(hy - r * 0.35), sx(hx + r * 0.4), sy(hy + r * 0.35), fill=m.accent, outline="#111")
            c.create_oval(sx(hx - 3), sy(hy - 2), sx(hx - 0.5), sy(hy + 1), fill="#fff", outline="")
            c.create_oval(sx(hx + 0.5), sy(hy - 2), sx(hx + 3), sy(hy + 1), fill="#fff", outline="")
            if kind == "spike_spider":
                for i in range(4):
                    a = facing + math.pi + (i - 1.5) * 0.35
                    c.create_line(
                        sx(px - math.cos(facing) * r * 0.4),
                        sy(py - math.sin(facing) * r * 0.4),
                        sx(px + math.cos(a) * r * 1.15),
                        sy(py + math.sin(a) * r * 1.15),
                        fill="#ff80d0",
                        width=2,
                    )
            return

        # Giant bosses — distinct silhouettes
        if kind == "queen_witch":
            self._draw_humanoid(
                c, sx, sy, m, px=px, py=py, r=r, body=col, accent=m.accent, facing=facing, hurt=m.hurt_t > 0, wand=True
            )
            # tall witch hat
            hx = px + math.cos(facing) * r * 0.12
            hy = py - r * 1.05
            c.create_polygon(
                sx(hx - r * 0.55), sy(hy - r * 0.1),
                sx(hx), sy(hy - r * 1.35),
                sx(hx + r * 0.55), sy(hy - r * 0.1),
                fill="#2a1038", outline="#111",
            )
            c.create_oval(sx(hx - r * 0.5), sy(hy - r * 0.2), sx(hx + r * 0.5), sy(hy + r * 0.15), fill="#4a2060", outline="#111")
            return
        if kind == "king_zombie":
            self._draw_humanoid(
                c, sx, sy, m, px=px, py=py, r=r, body=col, accent=m.accent, facing=facing, hurt=m.hurt_t > 0
            )
            hx = px + math.cos(facing) * r * 0.12
            hy = py - r * 0.95
            # crown
            c.create_polygon(
                sx(hx - r * 0.55), sy(hy - r * 0.35),
                sx(hx - r * 0.35), sy(hy - r * 0.85),
                sx(hx - r * 0.1), sy(hy - r * 0.4),
                sx(hx), sy(hy - r * 0.95),
                sx(hx + r * 0.1), sy(hy - r * 0.4),
                sx(hx + r * 0.35), sy(hy - r * 0.85),
                sx(hx + r * 0.55), sy(hy - r * 0.35),
                fill="#e0c040", outline="#111",
            )
            return
        if kind == "termite_queen":
            # Immobile burrowed queen — big abdomen + small head (no legs from head)
            c.create_oval(sx(px - r * 1.1), sy(py - r * 0.7), sx(px + r * 0.6), sy(py + r * 0.85), fill=col, outline="#111", width=3)
            hx = px + r * 0.75
            hy = py - r * 0.15
            c.create_oval(sx(hx - r * 0.4), sy(hy - r * 0.35), sx(hx + r * 0.4), sy(hy + r * 0.35), fill=m.accent, outline="#111", width=2)
            c.create_oval(sx(hx + 2), sy(hy - 4), sx(hx + 8), sy(hy + 2), fill="#111", outline="")
            # mandible
            c.create_line(sx(hx + r * 0.25), sy(hy + 2), sx(hx + r * 0.55), sy(hy + 10), fill="#5a4020", width=3)
            c.create_line(sx(hx + r * 0.25), sy(hy - 2), sx(hx + r * 0.55), sy(hy - 10), fill="#5a4020", width=3)
            return
        if kind == "the_one":
            self._draw_humanoid(
                c, sx, sy, m, px=px, py=py, r=r, body=col, accent=m.accent, facing=facing, hurt=m.hurt_t > 0
            )
            # glowing mono-eye
            hx = px + math.cos(facing) * r * 0.12
            hy = py - r * 0.95
            c.create_oval(sx(hx - 8), sy(hy - 6), sx(hx + 8), sy(hy + 6), fill="#ff3040", outline="#fff", width=2)
            return
        if kind == "generator":
            # Immobile machine core
            c.create_rectangle(sx(px - r * 0.85), sy(py - r * 0.85), sx(px + r * 0.85), sy(py + r * 0.85), fill=col, outline="#111", width=3)
            c.create_oval(sx(px - r * 0.45), sy(py - r * 0.45), sx(px + r * 0.45), sy(py + r * 0.45), fill=m.accent, outline="#dff")
            for i in range(4):
                a = i * (math.pi / 2) + self._run_t * 2.5
                c.create_line(
                    sx(px), sy(py),
                    sx(px + math.cos(a) * r * 0.95), sy(py + math.sin(a) * r * 0.95),
                    fill="#88e0ff", width=2,
                )
            return

        # biped zombie / worker / skeleton / lead worker
        self._draw_humanoid(
            c, sx, sy, m, px=px, py=py, r=r, body=col, accent=m.accent, facing=facing, hurt=m.hurt_t > 0
        )
        if kind in ("worker", "lead_worker"):
            # hard hat
            hx = px + math.cos(facing) * r * 0.12
            hy = py - r * 0.95
            c.create_arc(
                sx(hx - r * 0.55),
                sy(hy - r * 0.7),
                sx(hx + r * 0.55),
                sy(hy + r * 0.15),
                start=0,
                extent=180,
                fill="#f0c020",
                outline="#111",
            )
        if kind in ("skel", "termite"):
            c.create_line(sx(px - 6), sy(py - 2), sx(px + 6), sy(py - 2), fill="#fff", width=1)
            c.create_line(sx(px - 6), sy(py + 3), sx(px + 6), sy(py + 3), fill="#fff", width=1)

    def _draw(self) -> None:
        c = self.canvas
        c.delete("all")
        w, h = self._cw, self._ch
        camx, camy = self._cam_x, self._cam_y

        def sx(x: float) -> float:
            return x - camx

        def sy(y: float) -> float:
            return y - camy

        # Survivor.io-ish grassy field
        c.create_rectangle(0, 0, w, h, fill=FLOOR, outline="")
        step = 64
        gx0 = int(math.floor(camx / step) * step)
        gy0 = int(math.floor(camy / step) * step)
        yy = gy0
        while yy < camy + h + step:
            xx = gx0
            row = int(yy // step)
            while xx < camx + w + step:
                if (int(xx // step) + row) % 2 == 0:
                    c.create_rectangle(sx(xx), sy(yy), sx(xx + step), sy(yy + step), fill=FLOOR2, outline="")
                # tiny grass tufts
                if (int(xx) * 17 + int(yy) * 31) % 9 == 0:
                    c.create_line(sx(xx + 20), sy(yy + 30), sx(xx + 20), sy(yy + 18), fill="#3a6a34", width=2)
                    c.create_line(sx(xx + 24), sy(yy + 30), sx(xx + 28), sy(yy + 16), fill="#4a7a40", width=2)
                xx += step
            yy += step

        # crates
        for cr in self._crates:
            if cr.x < camx - 40 or cr.x > camx + w + 40 or cr.y < camy - 40 or cr.y > camy + h + 40:
                continue
            rr = cr.r
            c.create_rectangle(
                sx(cr.x - rr),
                sy(cr.y - rr),
                sx(cr.x + rr),
                sy(cr.y + rr),
                fill=CRATE_COL,
                outline=CRATE_EDGE,
                width=2,
            )
            c.create_line(sx(cr.x - rr), sy(cr.y), sx(cr.x + rr), sy(cr.y), fill=CRATE_EDGE)
            c.create_line(sx(cr.x), sy(cr.y - rr), sx(cr.x), sy(cr.y + rr), fill=CRATE_EDGE)
            self._draw_hp_bar(
                c,
                sx(cr.x) - rr,
                sy(cr.y + rr + 4),
                sx(cr.x) + rr,
                sy(cr.y + rr + 8),
                cr.hp / cr.max_hp,
                GOLD_COL,
            )

        # coins
        for coin in self._coins:
            c.create_oval(
                sx(coin.x - coin.r),
                sy(coin.y - coin.r),
                sx(coin.x + coin.r),
                sy(coin.y + coin.r),
                fill=GOLD_COL,
                outline="#fff0a0",
            )

        for g in self._gems:
            c.create_oval(
                sx(g.x - g.r),
                sy(g.y - g.r),
                sx(g.x + g.r),
                sy(g.y + g.r),
                fill=g.color,
                outline="#fff",
            )

        for d in self._drops:
            if d.kind == "bomb":
                c.create_oval(
                    sx(d.x - d.r),
                    sy(d.y - d.r),
                    sx(d.x + d.r),
                    sy(d.y + d.r),
                    fill="#333333",
                    outline="#ff6644",
                    width=2,
                )
                c.create_text(sx(d.x), sy(d.y), text="B", fill="#ff6644", font=("Helvetica", 11, "bold"))
            else:
                c.create_oval(
                    sx(d.x - d.r),
                    sy(d.y - d.r),
                    sx(d.x + d.r),
                    sy(d.y + d.r),
                    fill="#e87890",
                    outline="#ffe0e8",
                    width=2,
                )
                c.create_text(sx(d.x), sy(d.y), text="+", fill="#fff", font=("Helvetica", 12, "bold"))

        for r in self._rings:
            c.create_oval(sx(r.x - r.r), sy(r.y - r.r), sx(r.x + r.r), sy(r.y + r.r), outline=r.color, width=3)

        for pool in self._acids:
            c.create_oval(
                sx(pool.x - pool.r),
                sy(pool.y - pool.r),
                sx(pool.x + pool.r),
                sy(pool.y + pool.r),
                outline="#88ff44",
                width=2,
                dash=(4, 3),
            )
            c.create_oval(
                sx(pool.x - pool.r * 0.7),
                sy(pool.y - pool.r * 0.7),
                sx(pool.x + pool.r * 0.7),
                sy(pool.y + pool.r * 0.7),
                outline="#66cc33",
                width=1,
            )

        # Meteors falling + boom rings
        for met in self._meteors:
            if met.state == "fall":
                if met.delay > 0:
                    # ground warning circle
                    c.create_oval(
                        sx(met.x - 18),
                        sy(met.y - 10),
                        sx(met.x + 18),
                        sy(met.y + 10),
                        outline="#ff6644",
                        width=1,
                        dash=(3, 3),
                    )
                else:
                    my = met.y - met.height
                    c.create_oval(sx(met.x - 10), sy(my - 14), sx(met.x + 10), sy(my + 10), fill="#ff6622", outline="#ffcc88")
                    c.create_line(sx(met.x), sy(my + 10), sx(met.x), sy(met.y), fill="#ffaa66", dash=(2, 2))
                    # shadow
                    c.create_oval(sx(met.x - 14), sy(met.y - 6), sx(met.x + 14), sy(met.y + 6), outline="#333", width=1)
            elif met.state == "boom":
                c.create_oval(
                    sx(met.x - met.boom_r),
                    sy(met.y - met.boom_r * 0.55),
                    sx(met.x + met.boom_r),
                    sy(met.y + met.boom_r * 0.55),
                    outline="#ff9944",
                    width=3,
                )
                c.create_oval(
                    sx(met.x - met.boom_r * 0.55),
                    sy(met.y - met.boom_r * 0.35),
                    sx(met.x + met.boom_r * 0.55),
                    sy(met.y + met.boom_r * 0.35),
                    outline="#ffe088",
                    width=2,
                )

        if self._whirl_t > 0:
            wr = 100
            c.create_oval(
                sx(self._whirl_x - wr),
                sy(self._whirl_y - wr),
                sx(self._whirl_x + wr),
                sy(self._whirl_y + wr),
                outline="#88ccff",
                width=3,
                dash=(5, 3),
            )

        for m in self._monsters:
            if m.x < camx - 60 or m.x > camx + w + 60 or m.y < camy - 60 or m.y > camy + h + 60:
                continue
            self._draw_zombie(c, sx, sy, m)
            # HP under feet for mobs + minibosses + allies
            if m.rank != "boss":
                bw = max(28.0, m.r * 2.2)
                by = sy(m.y + m.r + 6)
                fill = MINI_COL if m.rank == "mini" else ("#dde0e8" if m.rank == "ally" else HP_FG)
                self._draw_hp_bar(c, sx(m.x) - bw * 0.5, by, sx(m.x) + bw * 0.5, by + 5, m.hp / m.max_hp, fill)

        if "orbit" in self._loadout.weapons:
            lv = self._loadout.weapons["orbit"]
            n = 3 + lv
            rad = 72 + lv * 14
            br = 10 + lv
            for i in range(n):
                a = self._orbit_angle + i * (math.tau / n)
                bx = self._px + math.cos(a) * rad
                by = self._py + math.sin(a) * rad
                c.create_oval(
                    sx(bx - br), sy(by - br), sx(bx + br), sy(by + br), fill="#ddeeff", outline="#8888aa"
                )

        for b in self._bullets:
            c.create_oval(sx(b.x - b.r), sy(b.y - b.r), sx(b.x + b.r), sy(b.y + b.r), fill=b.color, outline="")

        for p in self._particles:
            c.create_oval(sx(p.x - p.r), sy(p.y - p.r), sx(p.x + p.r), sy(p.y + p.r), fill=p.color, outline="")

        blink = self._invuln > 0 and int(self._invuln * 16) % 2 == 0
        if not blink:
            self._draw_humanoid(
                c,
                sx,
                sy,
                None,
                px=self._px,
                py=self._py,
                r=PLAYER_R,
                body=PLAYER_COL,
                accent=SKIN,
                facing=self._facing,
                wand=True,
            )

        # Burn aura ring (drawn after people so a bad color never blanks the scene)
        if "aura" in self._loadout.weapons:
            lv = self._loadout.weapons["aura"]
            rad = 70 + lv * 12
            c.create_oval(
                sx(self._px - rad),
                sy(self._py - rad),
                sx(self._px + rad),
                sy(self._py + rad),
                outline="#66cc44",
                width=2,
                dash=(6, 4),
            )

        # Boss HP bar — top of screen
        boss = next((m for m in self._monsters if m.rank == "boss" and not m.dead), None)
        self._active_boss = boss
        if boss is not None:
            pad = 40
            c.create_text(w * 0.5, 14, text=boss.name.upper(), fill=BOSS_COL, font=("Helvetica", 12, "bold"))
            self._draw_hp_bar(c, pad, 24, w - pad, 38, boss.hp / boss.max_hp, BOSS_COL)

        # Player HP — bottom left (above hotbar)
        self._draw_hp_bar(c, 14, h - 78, 160, h - 64, self._hp / max(1.0, self._max_hp), HP_FG)
        c.create_text(
            14,
            h - 84,
            text=f"HP {int(self._hp)}/{int(self._max_hp)}",
            fill=TITLE_FG,
            anchor=tk.W,
            font=("Helvetica", 11, "bold"),
        )

        # XP bar
        pad = 16
        bar_y = h - 58
        c.create_rectangle(pad, bar_y, w - pad, bar_y + 7, fill="#333844", outline="")
        frac = 0 if self._xp_need <= 0 else self._xp / self._xp_need
        c.create_rectangle(pad, bar_y, pad + (w - 2 * pad) * frac, bar_y + 7, fill=GEM_BLUE, outline="")

        # Aim sniper mark
        if self._aim_skill is not None:
            mx, my = sx(self._aim_wx), sy(self._aim_wy)
            c.create_oval(mx - 22, my - 22, mx + 22, my + 22, outline="#ff2244", width=2)
            c.create_oval(mx - 6, my - 6, mx + 6, my + 6, outline="#ff2244", width=2)
            c.create_line(mx - 32, my, mx - 10, my, fill="#ff2244", width=2)
            c.create_line(mx + 10, my, mx + 32, my, fill="#ff2244", width=2)
            c.create_line(mx, my - 32, mx, my - 10, fill="#ff2244", width=2)
            c.create_line(mx, my + 10, mx, my + 32, fill="#ff2244", width=2)
            c.create_text(mx, my - 40, text="CLICK TO FIRE", fill="#ff4466", font=("Helvetica", 10, "bold"))

        # Hotbar — bottom center (clickable)
        slot_w, slot_h = 88, 40
        total_w = len(HOTBAR) * (slot_w + 6) - 6
        hx0 = w * 0.5 - total_w * 0.5
        hy0 = h - 48
        self._hotbar_geom = []
        for i, hdef in enumerate(HOTBAR):
            x0 = hx0 + i * (slot_w + 6)
            cd = self._hot_cd.get(hdef["id"], 0.0)
            unlocked = self._hotbar_is_unlocked(hdef["id"])
            ready = cd <= 0 and unlocked
            aiming = self._aim_skill == hdef["id"]
            bg = "#3a2030" if aiming else ("#2a3340" if ready else "#1a1e24")
            outline = "#ff2244" if aiming else (hdef["color"] if unlocked else "#555")
            c.create_rectangle(x0, hy0, x0 + slot_w, hy0 + slot_h, fill=bg, outline=outline, width=2)
            c.create_text(
                x0 + 10,
                hy0 + 12,
                text=hdef["key"],
                fill=outline,
                font=("Helvetica", 12, "bold"),
                anchor=tk.W,
            )
            if not unlocked:
                label = "LOCKED"
            elif aiming:
                label = "AIM…"
            elif ready:
                label = hdef["name"]
            else:
                label = f"{cd:.1f}s"
            c.create_text(
                x0 + 10,
                hy0 + 28,
                text=label,
                fill=TITLE_FG if ready or aiming else MUTED,
                font=("Helvetica", 8),
                anchor=tk.W,
            )
            self._hotbar_geom.append((hdef["id"], x0, hy0, x0 + slot_w, hy0 + slot_h))

        # next boss hint
        if self._is_giant_stage():
            c.create_text(
                w * 0.5,
                52 if boss else 16,
                text="GIANT BOSS STAGE — defeat the titan!",
                fill=BOSS_COL,
                font=("Helvetica", 11, "bold"),
            )
        elif self._bosses_spawned < BOSSES_PER_LEVEL:
            need = BOSS_AT_PLAYER_LV[self._bosses_spawned]
            c.create_text(
                w * 0.5,
                52 if boss else 16,
                text=f"Next boss at player Lv {need} (now {self._plvl})",
                fill=BOSS_COL,
                font=("Helvetica", 11, "bold"),
            )


def main() -> None:
    BattlingMonstersApp().run()


if __name__ == "__main__":
    main()
