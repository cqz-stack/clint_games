/* Battling Monsters — browser build matching the 50-stage desktop game. */
const canvas = document.getElementById("c");
const ctx = canvas.getContext("2d");
const lobbyEl = document.getElementById("lobby");
const levelEl = document.getElementById("levelup");
const picksEl = document.getElementById("picks");
const stagesEl = document.getElementById("stages");
const shopEl = document.getElementById("shop");
const hotbarEl = document.getElementById("hotbar");

const CAMPAIGN = 50;
const GIANTS = new Set([10, 20, 30, 40, 50]);
const BOSS_AT = [10, 25, 40];
const XP_NEED = 5;
const KEY = "battling-monsters-web";

const MOBS = [
  ["zombie", 4, 88, 14, "#5a7a52", "#a8c0a0", "Zombie"],
  ["zdog", 2.5, 170, 11, "#6a6a48", "#c0b880", "Zombie Dog"],
  ["spider_r", 3.2, 135, 12, "#a02828", "#ff7070", "Red Zombie Spider"],
  ["spider_b", 3.6, 125, 12, "#2838a0", "#7090ff", "Blue Zombie Spider"],
  ["worker", 6.5, 72, 16, "#c9a038", "#ffe08a", "Zombie Worker"],
];
const MINIS = [
  ["lead_worker", "Lead Zombie Worker", 55, 85, 26, "#d4b040", "#fff0a0"],
  ["spike_spider", "Spiky Zombie Spider", 48, 140, 24, "#802060", "#ff80d0"],
];
const AMPS = {
  dmg: ["Power Amp", "+20% weapon damage"],
  spd: ["Swift Boots", "+6% move speed"],
  asap: ["Rapid Amp", "+15% attack speed"],
  magnet: ["Gem Magnet", "+30% gem pickup range"],
  vital: ["Vital Core", "+2 max HP and heal 2"],
};

const KITS = {
  1: [["Slime Lord", "#3a8a3a", "#b0ffb0"], ["Bog Toad", "#4a6a2a", "#d0e080"], ["Root Hulk", "#5a4030", "#c0a080"]],
  2: [["Ash Fiend", "#a04020", "#ffc090"], ["Ember Witch", "#902020", "#ff8080"], ["Cinder Knight", "#6a3030", "#e0a090"]],
  3: [["Frost Queen", "#5080c0", "#d0e8ff"], ["Yeti Chief", "#7090a0", "#e8f0ff"], ["Ice Warden", "#4060a0", "#a0c0ff"]],
  4: [["Sand Pharaoh", "#c0a040", "#ffe0a0"], ["Scarab King", "#806020", "#e0c060"], ["Mirage Mage", "#a08050", "#fff0c0"]],
  5: [["Storm Titan", "#4050a0", "#a0b0ff"], ["Gale Archer", "#6080b0", "#c0d8ff"], ["Thunder Ogre", "#303870", "#8090e0"]],
  6: [["Vine Hydra", "#2a6a40", "#80e0a0"], ["Bloom Witch", "#408060", "#a0ffc0"], ["Thorn Beast", "#306030", "#70c070"]],
  7: [["Bone Lord", "#c8c0b0", "#fff8e0"], ["Grave Knight", "#8a8070", "#d0c8b0"], ["Wraith Queen", "#706890", "#d0c0ff"]],
  8: [["Magma Baron", "#c03010", "#ff9040"], ["Lava Witch", "#a02020", "#ff6060"], ["Basalt Golem", "#503028", "#c08060"]],
  9: [["Void Herald", "#301848", "#a060e0"], ["Rift Stalker", "#201030", "#8050c0"], ["Abyss Knight", "#181028", "#6040a0"]],
  10: [["Chaos Emperor", "#801030", "#ff4060"], ["Doom Sorcerer", "#601040", "#e040a0"], ["Final Colossus", "#401020", "#c02040"]],
};

const GIANTS_INFO = {
  10: { name: "Queen Witch", kind: "queen_witch", body: "#6a2a8a", accent: "#e0a0ff", hp: 420, r: 48, speed: 95 },
  20: { name: "King Zombie", kind: "king_zombie", body: "#4a6a40", accent: "#b0d0a0", hp: 560, r: 52, speed: 80 },
  30: { name: "Termite Queen", kind: "termite_queen", body: "#8a7030", accent: "#e0c070", hp: 700, r: 56, speed: 0, immobile: true },
  40: { name: "The One Zombie", kind: "the_one", body: "#1a1a1a", accent: "#ff3040", hp: 900, r: 50, speed: 120 },
  50: { name: "The Generator", kind: "generator", body: "#406080", accent: "#88e0ff", hp: 1100, r: 58, speed: 0, immobile: true },
};

const HOTBAR = [
  { id: "rockets", name: "Rockets", key: "1", cd: 9, color: "#ff7744", unlock: "rockets" },
  { id: "acid", name: "Acid", key: "2", cd: 8, color: "#88ff44", unlock: "acid" },
  { id: "skeles", name: "Skeles", key: "3", cd: 14, color: "#dde0e8", unlock: "skeles" },
  { id: "whirl", name: "Whirl", key: "4", cd: 7, color: "#88ccff", unlock: "whirl" },
  { id: "meteor", name: "Meteors", key: "5", cd: 12, color: "#ff9944", unlock: "meteor" },
  { id: "termite", name: "Termites", key: "6", cd: 11, color: "#c8a060", unlock: "termite" },
];

const SHOP = {
  hp: { name: "Max HP", desc: "+2 max HP", max: 12, base: 40, step: 25 },
  dmg: { name: "Damage", desc: "+10% damage", max: 12, base: 50, step: 30 },
  spd: { name: "Speed", desc: "+6% move speed", max: 8, base: 45, step: 28 },
  magnet: { name: "Magnet", desc: "+20% pickup", max: 8, base: 35, step: 22 },
  goldfind: { name: "Gold Find", desc: "+25% crate gold", max: 8, base: 40, step: 30 },
  orbit: { name: "Start Orbit", desc: "Begin with blades", max: 1, base: 180, step: 0 },
  aura: { name: "Start Aura", desc: "Begin with burn aura", max: 1, base: 180, step: 0 },
  rockets: { name: "Unlock Rockets", desc: "Hotbar aim: rocket rain", max: 1, base: 120, step: 0 },
  acid: { name: "Unlock Acid", desc: "Hotbar aim: acid bomb", max: 1, base: 140, step: 0 },
  whirl: { name: "Unlock Whirl", desc: "Hotbar aim: whirlwind", max: 1, base: 150, step: 0 },
  meteor: { name: "Unlock Meteors", desc: "Hotbar aim: meteor shower", max: 1, base: 200, step: 0 },
};

const WEAPONS = {
  bolt: { name: "Magic Bolt", desc: "Auto-fires at the nearest foe.", max: 5 },
  orbit: { name: "Orbit Blades", desc: "Spinning blades around you.", max: 5 },
  aura: { name: "Burn Aura", desc: "Burns monsters that get close.", max: 5 },
  wave: { name: "Shock Wave", desc: "A big damaging pulse.", max: 5 },
  meteor: { name: "Meteor", desc: "Drops rocks on random foes.", max: 5 },
};

let progress = load();
let keys = new Set();
let state = "lobby";
let W = 800, H = 600, camX = 0, camY = 0;
let player, foes, gems, coins, bullets, rings, crates, pools;
let stage = 1, bossesKilled = 0, bossesSpawned = 0, msg = "", msgT = 0, orbitA = 0;
let runT = 0, miniT = 18, crateT = 1;
let aimSkill = null, aimX = 0, aimY = 0, whirl = null;
const hotCd = {};

function load() {
  const base = { unlocked: 1, gold: 0, shop: {}, termite: 0 };
  for (const k of Object.keys(SHOP)) base.shop[k] = 0;
  try {
    const d = JSON.parse(localStorage.getItem(KEY) || "null");
    if (!d) return base;
    base.unlocked = Math.max(1, Math.min(CAMPAIGN, d.unlocked | 0));
    base.gold = Math.max(0, d.gold | 0);
    base.termite = d.termite ? 1 : 0;
    for (const k of Object.keys(SHOP)) base.shop[k] = Math.max(0, Math.min(SHOP[k].max, (d.shop && d.shop[k]) | 0));
  } catch (e) { /* keep defaults */ }
  return base;
}
function save() { localStorage.setItem(KEY, JSON.stringify(progress)); }
function cost(id) { const d = SHOP[id]; return d.base + d.step * progress.shop[id]; }
function dmgMult() { return 1 + 0.1 * (progress.shop.dmg || 0) + 0.2 * (player ? player.amps.dmg || 0 : 0); }
function spdMult() { return Math.min(1.8, 1 + 0.06 * (progress.shop.spd || 0) + 0.08 * (player ? player.amps.spd || 0 : 0)); }
function asapMult() { return 1 + 0.15 * (player ? player.amps.asap || 0 : 0); }
function magnetMult() { return 1 + 0.3 * (player ? player.amps.magnet || 0 : 0) + 0.2 * (progress.shop.magnet || 0); }
function goldMult() { return 1 + 0.25 * (progress.shop.goldfind || 0); }
function diff() {
  const lvl = player ? player.lvl : 1;
  return 1.55 + (stage - 1) * 0.45 + runT * 0.007 + (lvl - 1) * 0.04;
}
function unlocked(id) {
  if (id === "skeles") return true;
  if (id === "termite") return progress.termite === 1;
  return (progress.shop[id] || 0) >= 1;
}

function resize() {
  W = canvas.width = window.innerWidth;
  H = canvas.height = window.innerHeight;
}
window.addEventListener("resize", resize);
resize();
window.addEventListener("keydown", (e) => {
  const k = e.key.toLowerCase();
  keys.add(k);
  if (["arrowup", "arrowdown", "arrowleft", "arrowright", " "].includes(k)) e.preventDefault();
  if (state === "play" && "123456".includes(k)) {
    const skill = HOTBAR[Number(k) - 1];
    if (skill) selectAim(skill.id);
  }
});
window.addEventListener("keyup", (e) => keys.delete(e.key.toLowerCase()));
canvas.addEventListener("mousemove", (e) => {
  if (state !== "play" || !aimSkill) return;
  aimX = e.clientX + camX;
  aimY = e.clientY + camY;
});
canvas.addEventListener("click", (e) => {
  if (state !== "play" || !aimSkill || !player) return;
  aimX = e.clientX + camX;
  aimY = e.clientY + camY;
  fireAim(aimSkill, aimX, aimY);
  aimSkill = null;
});

function renderLobby() {
  stagesEl.innerHTML = "";
  for (let i = 1; i <= CAMPAIGN; i++) {
    const b = document.createElement("button");
    b.textContent = (GIANTS.has(i) ? "G" : "") + i;
    b.title = GIANTS.has(i) ? "Giant stage " + i : "Stage " + i;
    b.disabled = i > progress.unlocked;
    b.onclick = () => startRun(i);
    stagesEl.appendChild(b);
  }
  shopEl.innerHTML = "";
  const gold = document.createElement("p");
  gold.textContent = "Gold: " + progress.gold + (progress.termite ? " · Termite unlocked" : "");
  gold.style.gridColumn = "1 / -1";
  gold.style.margin = "0";
  shopEl.appendChild(gold);
  for (const [id, d] of Object.entries(SHOP)) {
    const owned = progress.shop[id];
    const b = document.createElement("button");
    b.textContent = owned >= d.max ? d.name + " MAX" : d.name + " · " + cost(id) + "g";
    b.disabled = owned >= d.max || progress.gold < cost(id);
    b.onclick = () => {
      if (progress.gold < cost(id) || owned >= d.max) return;
      progress.gold -= cost(id);
      progress.shop[id]++;
      save();
      renderLobby();
    };
    shopEl.appendChild(b);
  }
}

function renderHotbar() {
  hotbarEl.style.display = "flex";
  hotbarEl.innerHTML = "";
  for (const h of HOTBAR) {
    const b = document.createElement("button");
    const cd = hotCd[h.id] || 0;
    const on = unlocked(h.unlock);
    b.textContent = h.key + " " + h.name + (cd > 0 ? " " + cd.toFixed(0) : "");
    b.style.borderColor = aimSkill === h.id ? "#fff" : h.color;
    b.disabled = !on || cd > 0;
    b.onclick = (ev) => { ev.stopPropagation(); selectAim(h.id); };
    hotbarEl.appendChild(b);
  }
}

function selectAim(id) {
  const h = HOTBAR.find((x) => x.id === id);
  if (!h || !unlocked(h.unlock) || (hotCd[id] || 0) > 0) {
    toast(unlocked(h && h.unlock) ? "Skill cooling down" : "Buy this skill in the shop");
    return;
  }
  aimSkill = aimSkill === id ? null : id;
  if (aimSkill && player) {
    aimX = player.x + Math.cos(player.facing) * 140;
    aimY = player.y + Math.sin(player.facing) * 140;
    toast("Click the ground to fire " + h.name);
  }
  renderHotbar();
}

function startRun(n) {
  stage = n;
  bossesKilled = 0;
  bossesSpawned = 0;
  runT = 0;
  miniT = 18;
  crateT = 1;
  aimSkill = null;
  whirl = null;
  state = "play";
  lobbyEl.style.display = "none";
  levelEl.style.display = "none";
  for (const h of HOTBAR) hotCd[h.id] = 0;
  const hp = 14 + 2 * progress.shop.hp;
  player = {
    x: 0, y: 0, r: 16, hp, max: hp, lvl: 1, xp: 0, xpNeed: 5, facing: 0,
    weapons: { bolt: 1 }, amps: {}, inv: 0, regen: 0,
    cds: { bolt: 0, aura: 0, wave: 0, meteor: 0 },
  };
  if (progress.shop.orbit) player.weapons.orbit = 1;
  if (progress.shop.aura) player.weapons.aura = 1;
  foes = []; gems = []; coins = []; bullets = []; rings = []; crates = []; pools = [];
  for (let i = 0; i < 6; i++) spawnCrate(280);
  renderHotbar();
  if (GIANTS.has(n)) {
    spawnGiant();
    toast("Giant stage " + n + " — defeat " + GIANTS_INFO[n].name);
  } else {
    toast("Stage " + n + " — bosses at level 10, 25, and 40");
  }
}

function toast(t) { msg = t; msgT = 2.6; }

function levelChoices() {
  const opts = [];
  for (const [id, d] of Object.entries(WEAPONS)) {
    const have = player.weapons[id] || 0;
    if (have < d.max) opts.push(["w", id, (have ? "Upgrade " : "New ") + d.name + " " + (have + 1), d.desc]);
  }
  for (const [id, pair] of Object.entries(AMPS)) {
    const n = player.amps[id] || 0;
    opts.push(["a", id, pair[0] + " ×" + (n + 1), pair[1]]);
  }
  for (let i = opts.length - 1; i > 0; i--) {
    const j = (Math.random() * (i + 1)) | 0;
    [opts[i], opts[j]] = [opts[j], opts[i]];
  }
  while (opts.length < 3) {
    const ids = Object.keys(AMPS);
    const id = ids[(Math.random() * ids.length) | 0];
    opts.push(["a", id, AMPS[id][0], AMPS[id][1]]);
  }
  return opts.slice(0, 3);
}

function openLevelUp() {
  state = "level";
  levelEl.style.display = "flex";
  picksEl.innerHTML = "";
  for (const [kind, id, name, desc] of levelChoices()) {
    const b = document.createElement("button");
    b.innerHTML = "<b>" + name + "</b><br><span style='opacity:.75'>" + desc + "</span>";
    b.onclick = () => {
      if (kind === "w") player.weapons[id] = (player.weapons[id] || 0) + 1;
      else {
        player.amps[id] = (player.amps[id] || 0) + 1;
        if (id === "vital") { player.max += 2; player.hp = Math.min(player.max, player.hp + 2); }
      }
      state = "play";
      levelEl.style.display = "none";
      maybeBoss();
    };
    picksEl.appendChild(b);
  }
}

function addXp(n) {
  player.xp += n;
  const need = player.xpNeed || 5;
  if (player.xp >= need && state === "play") {
    player.xp -= need;
    player.lvl++;
    player.xpNeed = Math.floor(5 + player.lvl * 1.6);
    maybeBoss();
    openLevelUp();
  }
}

function spawnMob() {
  const k = MOBS[(Math.random() * MOBS.length) | 0];
  const a = Math.random() * Math.PI * 2;
  const dist = 420 + Math.random() * 160;
  const d = diff();
  const hp = k[1] * (2.2 + d * 1.1);
  foes.push({
    x: player.x + Math.cos(a) * dist, y: player.y + Math.sin(a) * dist,
    hp, max: hp, speed: k[2] * (1.2 + d * 0.1), r: k[3],
    body: k[4], accent: k[5], rank: "mob", kind: k[0], name: k[6], facing: a + Math.PI, atk: 0,
  });
}

function spawnMini() {
  const k = MINIS[(Math.random() * MINIS.length) | 0];
  const a = Math.random() * Math.PI * 2;
  const d = diff();
  const hp = (k[2] + stage * 16) * (1 + d * 0.35);
  foes.push({
    x: player.x + Math.cos(a) * 460, y: player.y + Math.sin(a) * 460,
    hp, max: hp, speed: k[3] * (1.1 + d * 0.05), r: k[4],
    body: k[5], accent: k[6], rank: "mini", kind: k[0], name: k[1], facing: a + Math.PI, atk: 0,
  });
  toast("Miniboss: " + k[1]);
}

function spawnCrate(near) {
  const a = Math.random() * Math.PI * 2;
  const dist = near * (0.6 + Math.random() * 0.7);
  const hp = 8 + stage * 2 + diff() * 2;
  crates.push({
    x: player.x + Math.cos(a) * dist, y: player.y + Math.sin(a) * dist,
    hp, max: hp, r: 15,
  });
}

function damageCrate(c, dmg) {
  if (!c || c.hp <= 0) return;
  c.hp -= dmg * dmgMult();
  if (c.hp <= 0) {
    const val = Math.max(1, Math.round((3 + Math.random() * 5 + stage) * goldMult()));
    coins.push({ x: c.x, y: c.y, v: val });
    c.gone = true;
  }
}

function maybeBoss() {
  if (GIANTS.has(stage) || bossesSpawned >= 3) return;
  if (foes.some((f) => f.rank === "boss" && !f.dead)) return;
  if (player.lvl >= BOSS_AT[bossesSpawned]) {
    bossesSpawned++;
    spawnBoss(bossesSpawned);
  }
}

function spawnBoss(i) {
  const kit = KITS[((stage - 1) % 10) + 1];
  const row = kit[i - 1];
  const scale = 1 + 0.1 * (stage - 1);
  const d = diff();
  const hp = (180 + stage * 55 + i * 70 + d * 45) * scale;
  const a = Math.random() * Math.PI * 2;
  foes.push({
    x: player.x + Math.cos(a) * 460, y: player.y + Math.sin(a) * 460,
    hp, max: hp, speed: 80 + stage * 2, r: 34,
    body: row[1], accent: row[2], rank: "boss", kind: "boss", name: row[0], facing: a + Math.PI,
  });
  toast("Boss: " + row[0] + " (" + i + "/3)");
}

function spawnGiant() {
  const info = GIANTS_INFO[stage];
  const scale = 1 + 0.1 * (stage - 1);
  const hp = info.hp * scale * (1 + diff() * 0.15) * 5;
  foes.push({
    x: player.x + 320, y: player.y,
    hp, max: hp, speed: info.speed, r: info.r,
    body: info.body, accent: info.accent, rank: "boss", kind: info.kind, name: info.name, facing: Math.PI, giant: true, immobile: !!info.immobile,
  });
  bossesSpawned = 1;
}

function hurtFoe(f, dmg) {
  if (!f || f.dead || f.rank === "ally") return;
  f.hp -= dmg * dmgMult();
  f.hurt = 0.12;
  if (f.hp <= 0) {
    f.dead = true;
    const roll = Math.random();
    const val = roll < 0.12 ? 10 : roll < 0.35 ? 5 : 1;
    gems.push({ x: f.x, y: f.y, v: val, c: val === 10 ? "#ffd24a" : val === 5 ? "#4aa8ff" : "#5dcf5a" });
    if (Math.random() < 0.25) coins.push({ x: f.x + 8, y: f.y, v: 2 + Math.ceil(stage / 5) });
    if (f.rank === "boss") {
      bossesKilled++;
      const need = GIANTS.has(stage) ? 1 : 3;
      toast(f.name + " fell (" + bossesKilled + "/" + need + ")");
      if (bossesKilled >= need) winStage();
    }
  }
}

function fireAim(id, x, y) {
  if ((hotCd[id] || 0) > 0) return;
  const meta = HOTBAR.find((h) => h.id === id);
  hotCd[id] = meta.cd;
  if (id === "rockets") {
    for (let i = 0; i < 8; i++) {
      const tx = x + (Math.random() - 0.5) * 180;
      const ty = y + (Math.random() - 0.5) * 180;
      rings.push({ x: tx, y: ty, r: 6, max: 52, dmg: 3.5, hit: new Set() });
    }
  } else if (id === "acid") {
    pools.push({ x, y, r: 75, life: 5.5, dps: 9 });
  } else if (id === "skeles" || id === "termite") {
    const n = id === "termite" ? 12 : 4;
    const hp = (18 + stage * 2) * (id === "termite" ? 3 : 1);
    for (let i = 0; i < n; i++) {
      const a = (i / n) * Math.PI * 2;
      foes.push({
        x: x + Math.cos(a) * 30, y: y + Math.sin(a) * 30,
        hp, max: hp, speed: id === "termite" ? 185 : 160, r: 12,
        body: id === "termite" ? "#c8a060" : "#d8dce8",
        accent: "#fff", rank: "ally", kind: id === "termite" ? "termite" : "skel",
        name: id === "termite" ? "Termite" : "Skeleton", facing: 0, life: id === "termite" ? 26 : 18, atk: 0,
      });
    }
  } else if (id === "whirl") {
    whirl = { x, y, t: 2.4 };
  } else if (id === "meteor") {
    for (let i = 0; i < 7; i++) {
      rings.push({
        x: x + (Math.random() - 0.5) * 220,
        y: y + (Math.random() - 0.5) * 220,
        r: 4, max: 56, dmg: 5.5, delay: i * 0.12, hit: new Set(),
      });
    }
  }
  toast(meta.name + " fired");
  renderHotbar();
}

function winStage() {
  const bonus = 25 + stage * 8;
  progress.gold += bonus;
  if (stage === 30) progress.termite = 1;
  if (stage >= progress.unlocked && progress.unlocked < CAMPAIGN) progress.unlocked = stage + 1;
  save();
  endRun("Stage " + stage + " cleared! +" + bonus + " gold" + (stage === 30 ? "\nTermite summon unlocked." : ""));
}

function die() {
  progress.gold += Math.floor(player.lvl);
  save();
  endRun("You fell on stage " + stage + ". Gold kept: " + progress.gold);
}

function endRun(text) {
  state = "lobby";
  hotbarEl.style.display = "none";
  lobbyEl.style.display = "flex";
  renderLobby();
  alert(text);
}

function hitPlayer(n) {
  if (!player || player.inv > 0 || state !== "play") return;
  player.hp -= n;
  player.inv = 0.7;
  player.regen = 0;
  if (player.hp <= 0) die();
}

let spawnT = 0.4;
function tick(dt) {
  if (state !== "play" || !player) return;
  let mx = 0, my = 0;
  if (keys.has("a") || keys.has("arrowleft")) mx -= 1;
  if (keys.has("d") || keys.has("arrowright")) mx += 1;
  if (keys.has("w") || keys.has("arrowup")) my -= 1;
  if (keys.has("s") || keys.has("arrowdown")) my += 1;
  if (mx || my) {
    const mag = Math.hypot(mx, my);
    player.facing = Math.atan2(my, mx);
    const spd = 280 * spdMult();
    player.x += (mx / mag) * spd * dt;
    player.y += (my / mag) * spd * dt;
  }
  runT += dt;
  player.inv = Math.max(0, player.inv - dt);
  if (player.inv <= 0) {
    player.regen += dt;
    if (player.regen > 5 && player.hp < player.max) player.hp = Math.min(player.max, player.hp + dt * 2);
  } else player.regen = 0;
  for (const h of HOTBAR) hotCd[h.id] = Math.max(0, (hotCd[h.id] || 0) - dt);

  spawnT -= dt;
  if (spawnT <= 0) {
    spawnT = Math.max(0.1, 0.14 / diff());
    spawnMob();
    if (Math.random() < 0.55) spawnMob();
  }
  crateT -= dt;
  if (crateT <= 0) {
    crateT = 4.5;
    if (crates.length < 14) spawnCrate(420);
  }
  miniT -= dt;
  if (miniT <= 0) {
    miniT = (28 + Math.random() * 14) / Math.max(1, 0.7 + diff() * 0.15);
    if (foes.filter((f) => f.rank === "mini" && !f.dead).length < 2) spawnMini();
  }
  maybeBoss();

  const asap = asapMult();
  orbitA += dt * (2.2 + (player.weapons.orbit || 0) * 0.3) * asap;
  const blades = player.weapons.orbit || 0;
  const bladeN = blades ? 3 + blades : 0;
  for (let i = 0; i < bladeN; i++) {
    const a = orbitA + (i / bladeN) * Math.PI * 2;
    const rad = 72 + blades * 14;
    const bx = player.x + Math.cos(a) * rad;
    const by = player.y + Math.sin(a) * rad;
    const od = (1.4 + blades * 0.55) * dt * 10;
    for (const f of foes) if (f.rank !== "ally" && Math.hypot(f.x - bx, f.y - by) < f.r + 14) hurtFoe(f, od);
    for (const c of crates) if (Math.hypot(c.x - bx, c.y - by) < c.r + 14) damageCrate(c, od);
  }
  if (player.weapons.aura) {
    player.cds.aura -= dt;
    const rad = 70 + player.weapons.aura * 12;
    if (player.cds.aura <= 0) {
      player.cds.aura = 0.2 / asap;
      const ad = 0.35 + player.weapons.aura * 0.2;
      for (const f of foes) if (f.rank !== "ally" && Math.hypot(f.x - player.x, f.y - player.y) < rad + f.r) hurtFoe(f, ad);
      for (const c of crates) if (Math.hypot(c.x - player.x, c.y - player.y) < rad + c.r) damageCrate(c, ad);
    }
  }
  if (player.weapons.wave) {
    player.cds.wave -= dt;
    if (player.cds.wave <= 0) {
      const lv = player.weapons.wave;
      player.cds.wave = Math.max(1.2, (2.8 - lv * 0.22) / asap);
      const maxR = 180 + lv * 40;
      rings.push({ x: player.x, y: player.y, r: 14, max: maxR, dmg: 0, hit: new Set() });
      const wd = 2.4 + lv * 0.9;
      for (const f of foes) if (f.rank !== "ally" && Math.hypot(f.x - player.x, f.y - player.y) < maxR) hurtFoe(f, wd);
      for (const c of crates) if (Math.hypot(c.x - player.x, c.y - player.y) < maxR) damageCrate(c, wd);
    }
  }
  if (player.weapons.meteor) {
    player.cds.meteor -= dt;
    if (player.cds.meteor <= 0) {
      const lv = player.weapons.meteor;
      const pool = foes.filter((f) => !f.dead && f.rank !== "ally");
      const target = pool.length ? pool[(Math.random() * pool.length) | 0] : crates[0];
      if (target) {
        player.cds.meteor = Math.max(1, (2.8 - lv * 0.25) / asap);
        rings.push({ x: target.x, y: target.y, r: 5, max: 55 + lv * 8, dmg: 0, hit: new Set() });
        const md = 2 + lv * 0.8;
        if (target.rank) hurtFoe(target, md);
        else damageCrate(target, md);
      }
    }
  }
  player.cds.bolt -= dt;
  const boltLv = player.weapons.bolt || 0;
  if (boltLv && player.cds.bolt <= 0) {
    const t = nearestEnemy() || nearestCrate();
    if (t) {
      player.cds.bolt = Math.max(0.1, (0.34 - boltLv * 0.045) / asap);
      player.facing = Math.atan2(t.y - player.y, t.x - player.x);
      const ang = player.facing;
      bullets.push({
        x: player.x, y: player.y,
        vx: Math.cos(ang) * (620 + boltLv * 55), vy: Math.sin(ang) * (620 + boltLv * 55),
        dmg: 2.2 + boltLv * 0.85, life: 1.1, r: 6, hostile: false, color: "#e8d080",
      });
    }
  }

  if (whirl) {
    whirl.t -= dt;
    for (const f of foes) if (f.rank !== "ally" && Math.hypot(f.x - whirl.x, f.y - whirl.y) < 100) hurtFoe(f, 14 * dt);
    for (const c of crates) if (Math.hypot(c.x - whirl.x, c.y - whirl.y) < 100) damageCrate(c, 14 * dt);
    if (whirl.t <= 0) whirl = null;
  }
  for (const p of pools) {
    p.life -= dt;
    for (const f of foes) if (f.rank !== "ally" && Math.hypot(f.x - p.x, f.y - p.y) < p.r) hurtFoe(f, p.dps * dt);
    for (const c of crates) if (Math.hypot(c.x - p.x, c.y - p.y) < p.r) damageCrate(c, p.dps * dt);
  }
  pools = pools.filter((p) => p.life > 0);

  for (const r of rings) {
    if (r.delay > 0) { r.delay -= dt; continue; }
    const prev = r.r;
    r.r += 260 * dt;
    if (!r.dmg) continue;
    for (const f of foes) {
      if (f.rank === "ally" || r.hit.has(f)) continue;
      const d = Math.hypot(f.x - r.x, f.y - r.y);
      if (d < r.r + f.r && d > prev - f.r) { r.hit.add(f); hurtFoe(f, r.dmg); }
    }
    for (const c of crates) {
      if (r.hit.has(c)) continue;
      const d = Math.hypot(c.x - r.x, c.y - r.y);
      if (d < r.r + c.r && d > prev - c.r) { r.hit.add(c); damageCrate(c, r.dmg); }
    }
  }
  rings = rings.filter((r) => r.r < r.max);

  for (const b of bullets) {
    b.x += b.vx * dt; b.y += b.vy * dt; b.life -= dt;
    if (b.hostile) {
      if (Math.hypot(b.x - player.x, b.y - player.y) < player.r + b.r) { hitPlayer(b.dmg); b.life = 0; }
    } else {
      let hit = false;
      for (const f of foes) if (f.rank !== "ally" && Math.hypot(f.x - b.x, f.y - b.y) < f.r + b.r) { hurtFoe(f, b.dmg); hit = true; break; }
      if (!hit) for (const c of crates) if (Math.hypot(c.x - b.x, c.y - b.y) < c.r + b.r) { damageCrate(c, b.dmg); hit = true; break; }
      if (hit) b.life = 0;
    }
  }
  bullets = bullets.filter((b) => b.life > 0);

  for (const f of foes) {
    if (f.dead) continue;
    f.hurt = Math.max(0, (f.hurt || 0) - dt);
    if (f.rank === "ally") {
      f.life -= dt;
      const foe = nearestEnemy(f);
      if (!foe) continue;
      const ang = Math.atan2(foe.y - f.y, foe.x - f.x);
      f.facing = ang;
      f.x += Math.cos(ang) * f.speed * dt;
      f.y += Math.sin(ang) * f.speed * dt;
      f.atk = Math.max(0, (f.atk || 0) - dt);
      if (Math.hypot(foe.x - f.x, foe.y - f.y) < f.r + foe.r + 4 && f.atk <= 0) {
        hurtFoe(foe, f.kind === "termite" ? 6.6 : 2.2);
        f.atk = f.kind === "termite" ? 0.35 : 0.45;
      }
      if (f.life <= 0) f.dead = true;
      continue;
    }
    const ang = Math.atan2(player.y - f.y, player.x - f.x);
    f.facing = ang;
    if (!f.immobile) {
      f.x += Math.cos(ang) * f.speed * dt;
      f.y += Math.sin(ang) * f.speed * dt;
    }
    if (Math.hypot(f.x - player.x, f.y - player.y) < f.r + player.r) hitPlayer(f.rank === "boss" ? 2 : 1);
    if (f.rank === "boss" && Math.random() < dt * 0.4) {
      bullets.push({
        x: f.x, y: f.y, vx: Math.cos(ang) * 240, vy: Math.sin(ang) * 240,
        dmg: 1, life: 2, r: 5, hostile: true, color: "#ff5566",
      });
    }
  }
  foes = foes.filter((f) => !f.dead);
  crates = crates.filter((c) => !c.gone && Math.hypot(c.x - player.x, c.y - player.y) < 1600);

  const magnet = 70 * magnetMult();
  for (const g of gems) {
    const d = Math.hypot(g.x - player.x, g.y - player.y) || 1;
    if (d < magnet) {
      g.x += (player.x - g.x) / d * 240 * dt;
      g.y += (player.y - g.y) / d * 240 * dt;
    }
    if (d < player.r + 8) { addXp(g.v); g.got = true; }
  }
  gems = gems.filter((g) => !g.got);
  for (const c of coins) {
    if (Math.hypot(c.x - player.x, c.y - player.y) < player.r + 10) {
      progress.gold += c.v; save(); c.got = true;
    }
  }
  coins = coins.filter((c) => !c.got);
  msgT = Math.max(0, msgT - dt);
  camX = player.x - W / 2;
  camY = player.y - H / 2;
  if (Math.floor(msgT * 4) !== Math.floor((msgT + dt) * 4)) renderHotbar();
}

function drawWorldBar(x, y, w, h, frac, fill) {
  ctx.fillStyle = "#2a3038";
  ctx.fillRect(x, y, w, h);
  ctx.fillStyle = fill;
  ctx.fillRect(x, y, w * Math.max(0, Math.min(1, frac)), h);
  ctx.strokeStyle = "#111";
  ctx.lineWidth = 1;
  ctx.strokeRect(x, y, w, h);
}

function nearestCrate() {
  let best = null, bd = 1e9;
  for (const c of crates) {
    const d = Math.hypot(c.x - player.x, c.y - player.y);
    if (d < bd) { bd = d; best = c; }
  }
  return best;
}

function nearestEnemy(from) {
  const ox = from ? from.x : player.x;
  const oy = from ? from.y : player.y;
  let best = null, bd = 1e9;
  for (const f of foes) {
    if (f.dead || f.rank === "ally") continue;
    const d = Math.hypot(f.x - ox, f.y - oy);
    if (d < bd) { bd = d; best = f; }
  }
  return best;
}

function drawPerson(x, y, r, facing, body, skin, wand, boss) {
  const lx = Math.cos(facing + 0.55) * r * 0.6;
  const ly = Math.sin(facing + 0.55) * r * 0.6;
  const rx = Math.cos(facing - 0.55) * r * 0.6;
  const ry = Math.sin(facing - 0.55) * r * 0.6;
  ctx.strokeStyle = "#3a3a4a";
  ctx.lineWidth = 4;
  ctx.beginPath();
  ctx.moveTo(x, y + r * 0.1);
  ctx.lineTo(x + lx, y + ly + r * 0.45);
  ctx.moveTo(x, y + r * 0.1);
  ctx.lineTo(x + rx, y + ry + r * 0.45);
  ctx.stroke();
  ctx.fillStyle = body;
  ctx.strokeStyle = "#111";
  ctx.lineWidth = 2;
  ctx.beginPath();
  ctx.ellipse(x, y + r * 0.12, r * 0.75, r * 0.62, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.stroke();
  ctx.fillStyle = "#2a2a33";
  ctx.fillRect(x - r * 0.55, y + r * 0.15, r * 1.1, r * 0.17);
  const hx = x + Math.cos(facing) * r * 0.12;
  const hy = y - r * 0.95;
  ctx.fillStyle = skin;
  ctx.beginPath();
  ctx.arc(hx, hy, r * 0.48, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "#111";
  ctx.stroke();
  ctx.fillStyle = "#3b2a1a";
  ctx.beginPath();
  ctx.arc(hx, hy - r * 0.05, r * 0.48, Math.PI, 0);
  ctx.fill();
  const ex = Math.cos(facing);
  const ey = Math.sin(facing);
  ctx.fillStyle = "#111";
  ctx.beginPath();
  ctx.ellipse(hx + ex * 4 - 1, hy + ey * 2, 1.8, 1.4, 0, 0, Math.PI * 2);
  ctx.ellipse(hx + ex * 1 + 1, hy + ey * 2, 1.8, 1.4, 0, 0, Math.PI * 2);
  ctx.fill();
  ctx.strokeStyle = "#a07050";
  ctx.lineWidth = 1;
  ctx.beginPath();
  ctx.moveTo(hx - 3, hy + 5);
  ctx.lineTo(hx + 3, hy + 5);
  ctx.stroke();
  ctx.strokeStyle = skin;
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(x, y - r * 0.05);
  ctx.lineTo(x + Math.cos(facing + 1.05) * r * 0.95, y + Math.sin(facing + 1.05) * r * 0.95);
  ctx.moveTo(x, y - r * 0.05);
  ctx.lineTo(x + Math.cos(facing - 1.05) * r * 0.95, y + Math.sin(facing - 1.05) * r * 0.95);
  ctx.stroke();
  if (wand) {
    const tipx = x + Math.cos(facing) * (r + 22);
    const tipy = y + Math.sin(facing) * (r + 22);
    ctx.strokeStyle = "#e8d080";
    ctx.lineWidth = 3;
    ctx.beginPath();
    ctx.moveTo(x + Math.cos(facing - 1.05) * r * 0.7, y + Math.sin(facing - 1.05) * r * 0.7);
    ctx.lineTo(tipx, tipy);
    ctx.stroke();
    ctx.fillStyle = "#88eeff";
    ctx.beginPath();
    ctx.arc(tipx, tipy, 5, 0, Math.PI * 2);
    ctx.fill();
  }
  if (boss) {
    ctx.fillStyle = "#ff4466";
    ctx.strokeStyle = "#111";
    ctx.beginPath();
    ctx.moveTo(hx - r * 0.4, hy - r * 0.35);
    ctx.lineTo(hx, hy - r * 0.95);
    ctx.lineTo(hx + r * 0.4, hy - r * 0.35);
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
  }
}

function drawMonster(f) {
  const col = f.hurt > 0 ? "#ff5566" : f.body;
  if (f.kind === "zdog") {
    ctx.save();
    ctx.translate(f.x, f.y);
    ctx.rotate(f.facing);
    ctx.fillStyle = col;
    ctx.beginPath();
    ctx.ellipse(0, 0, f.r * 1.2, f.r * 0.5, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.beginPath();
    ctx.arc(f.r * 1.2, 0, f.r * 0.42, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = "#7dff6a";
    ctx.beginPath();
    ctx.arc(f.r * 1.35, -2, 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#3a4a38";
    ctx.lineWidth = 3;
    ctx.beginPath();
    for (const [ax, side] of [[-0.6, -1], [-0.6, 1], [0.5, -1], [0.5, 1]]) {
      ctx.moveTo(f.r * ax, side * f.r * 0.35);
      ctx.lineTo(f.r * ax, side * f.r * 0.35 + f.r * 0.8);
    }
    ctx.stroke();
    ctx.restore();
    return;
  }
  if (f.kind === "spider_r" || f.kind === "spider_b" || f.kind === "spike_spider") {
    ctx.fillStyle = col;
    ctx.beginPath();
    ctx.ellipse(f.x, f.y, f.r, f.r * 0.6, f.facing, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = col;
    ctx.lineWidth = 2;
    for (const side of [-1, 1]) {
      for (let i = 0; i < 3; i++) {
        const along = -0.35 + i * 0.35;
        const bx = f.x + Math.cos(f.facing) * f.r * along;
        const by = f.y + Math.sin(f.facing) * f.r * along;
        const out = f.facing + side * (0.9 + i * 0.12);
        ctx.beginPath();
        ctx.moveTo(bx, by);
        ctx.lineTo(bx + Math.cos(out) * f.r * 1.3, by + Math.sin(out) * f.r * 1.3);
        ctx.stroke();
      }
    }
    const hx = f.x + Math.cos(f.facing) * f.r * 0.85;
    const hy = f.y + Math.sin(f.facing) * f.r * 0.85;
    ctx.fillStyle = f.accent;
    ctx.beginPath();
    ctx.arc(hx, hy, f.r * 0.38, 0, Math.PI * 2);
    ctx.fill();
    if (f.kind === "spike_spider") {
      ctx.strokeStyle = "#ff80d0";
      ctx.beginPath();
      for (let i = 0; i < 4; i++) {
        const a = f.facing + Math.PI + (i - 1.5) * 0.35;
        ctx.moveTo(f.x - Math.cos(f.facing) * f.r * 0.4, f.y - Math.sin(f.facing) * f.r * 0.4);
        ctx.lineTo(f.x + Math.cos(a) * f.r * 1.15, f.y + Math.sin(a) * f.r * 1.15);
      }
      ctx.stroke();
    }
    return;
  }
  if (f.kind === "queen_witch" || f.kind === "king_zombie" || f.kind === "the_one") {
    drawPerson(f.x, f.y, f.r, f.facing, col, f.accent, f.kind === "queen_witch", false);
    const hx = f.x + Math.cos(f.facing) * f.r * 0.12;
    const hy = f.y - f.r * 0.95;
    if (f.kind === "queen_witch") {
      ctx.fillStyle = "#2a1038";
      ctx.beginPath();
      ctx.moveTo(hx - f.r * 0.55, hy - f.r * 0.1);
      ctx.lineTo(hx, hy - f.r * 1.35);
      ctx.lineTo(hx + f.r * 0.55, hy - f.r * 0.1);
      ctx.fill();
    } else if (f.kind === "king_zombie") {
      ctx.fillStyle = "#e0c040";
      ctx.beginPath();
      ctx.moveTo(hx - f.r * 0.55, hy - f.r * 0.35);
      ctx.lineTo(hx - f.r * 0.35, hy - f.r * 0.85);
      ctx.lineTo(hx, hy - f.r * 0.4);
      ctx.lineTo(hx + f.r * 0.35, hy - f.r * 0.85);
      ctx.lineTo(hx + f.r * 0.55, hy - f.r * 0.35);
      ctx.fill();
    } else {
      ctx.fillStyle = "#ff3040";
      ctx.beginPath();
      ctx.arc(hx, hy, 8, 0, Math.PI * 2);
      ctx.fill();
    }
    return;
  }
  if (f.kind === "termite_queen") {
    ctx.fillStyle = col;
    ctx.beginPath();
    ctx.ellipse(f.x - f.r * 0.2, f.y, f.r * 0.85, f.r * 0.75, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = f.accent;
    ctx.beginPath();
    ctx.arc(f.x + f.r * 0.75, f.y - f.r * 0.15, f.r * 0.38, 0, Math.PI * 2);
    ctx.fill();
    return;
  }
  if (f.kind === "generator") {
    ctx.fillStyle = col;
    ctx.fillRect(f.x - f.r * 0.85, f.y - f.r * 0.85, f.r * 1.7, f.r * 1.7);
    ctx.fillStyle = f.accent;
    ctx.beginPath();
    ctx.arc(f.x, f.y, f.r * 0.45, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = "#88e0ff";
    ctx.beginPath();
    const spin = performance.now() / 400;
    for (let i = 0; i < 4; i++) {
      const a = spin + i * Math.PI / 2;
      ctx.moveTo(f.x, f.y);
      ctx.lineTo(f.x + Math.cos(a) * f.r * 0.95, f.y + Math.sin(a) * f.r * 0.95);
    }
    ctx.stroke();
    return;
  }
  drawPerson(f.x, f.y, f.r, f.facing, col, f.accent, false, f.rank === "boss");
  if (f.kind === "worker" || f.kind === "lead_worker") {
    const hx = f.x + Math.cos(f.facing) * f.r * 0.12;
    const hy = f.y - f.r * 0.95;
    ctx.fillStyle = "#f0c020";
    ctx.beginPath();
    ctx.arc(hx, hy - f.r * 0.15, f.r * 0.5, Math.PI, 0);
    ctx.fill();
  }
  if (f.kind === "skel" || f.kind === "termite") {
    ctx.strokeStyle = "#fff";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(f.x - 6, f.y - 2);
    ctx.lineTo(f.x + 6, f.y - 2);
    ctx.moveTo(f.x - 6, f.y + 3);
    ctx.lineTo(f.x + 6, f.y + 3);
    ctx.stroke();
  }
}

function draw() {
  ctx.fillStyle = "#1c2a18";
  ctx.fillRect(0, 0, W, H);
  if (state === "lobby" || !player) return;
  ctx.save();
  ctx.translate(-camX, -camY);
  const x0 = Math.floor(camX / 48) * 48;
  const y0 = Math.floor(camY / 48) * 48;
  for (let x = x0; x < camX + W + 48; x += 48) {
    for (let y = y0; y < camY + H + 48; y += 48) {
      ctx.fillStyle = ((x / 48 + y / 48) & 1) ? "#254022" : "#2d4a28";
      ctx.fillRect(x, y, 48, 48);
      if (((x * 17 + y * 31) | 0) % 9 === 0) {
        ctx.strokeStyle = "#3a6a34";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(x + 20, y + 30);
        ctx.lineTo(x + 20, y + 18);
        ctx.moveTo(x + 24, y + 30);
        ctx.lineTo(x + 28, y + 16);
        ctx.stroke();
      }
    }
  }
  for (const p of pools) {
    ctx.fillStyle = "rgba(120,220,60,0.35)";
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fill();
  }
  if (whirl) {
    ctx.strokeStyle = "#88ccff";
    ctx.beginPath();
    ctx.arc(whirl.x, whirl.y, 100, 0, Math.PI * 2);
    ctx.stroke();
  }
  for (const c of crates) {
    ctx.fillStyle = "#8a6238";
    ctx.strokeStyle = "#c49a5a";
    ctx.lineWidth = 2;
    ctx.fillRect(c.x - c.r, c.y - c.r, c.r * 2, c.r * 2);
    ctx.strokeRect(c.x - c.r, c.y - c.r, c.r * 2, c.r * 2);
    ctx.beginPath();
    ctx.moveTo(c.x - c.r, c.y);
    ctx.lineTo(c.x + c.r, c.y);
    ctx.moveTo(c.x, c.y - c.r);
    ctx.lineTo(c.x, c.y + c.r);
    ctx.stroke();
    drawWorldBar(c.x - c.r, c.y + c.r + 4, c.r * 2, 5, c.hp / c.max, "#ffd24a");
  }
  for (const g of gems) {
    ctx.fillStyle = g.c;
    ctx.beginPath();
    ctx.arc(g.x, g.y, 6, 0, Math.PI * 2);
    ctx.fill();
  }
  for (const c of coins) {
    ctx.fillStyle = "#ffd24a";
    ctx.beginPath();
    ctx.arc(c.x, c.y, 5, 0, Math.PI * 2);
    ctx.fill();
  }
  const blades = player.weapons.orbit || 0;
  for (let i = 0; i < blades; i++) {
    const a = orbitA + (i / blades) * Math.PI * 2;
    ctx.fillStyle = "#e8eaf0";
    ctx.beginPath();
    ctx.arc(player.x + Math.cos(a) * (70 + blades * 6), player.y + Math.sin(a) * (70 + blades * 6), 8, 0, Math.PI * 2);
    ctx.fill();
  }
  for (const r of rings) {
    if (r.delay > 0) continue;
    ctx.strokeStyle = "#ff9966";
    ctx.beginPath();
    ctx.arc(r.x, r.y, r.r, 0, Math.PI * 2);
    ctx.stroke();
  }
  for (const b of bullets) {
    ctx.fillStyle = b.color;
    ctx.beginPath();
    ctx.arc(b.x, b.y, b.r, 0, Math.PI * 2);
    ctx.fill();
  }
  for (const f of foes) {
    drawMonster(f);
    const bw = Math.max(28, f.r * 2.2);
    const fill = f.rank === "boss" ? "#ff4466" : f.rank === "mini" ? "#ffd24a" : f.rank === "ally" ? "#dde0e8" : "#7cff6b";
    drawWorldBar(f.x - bw * 0.5, f.y + f.r + 6, bw, 5, f.hp / f.max, fill);
    if (f.rank === "boss" || f.rank === "mini") {
      ctx.fillStyle = "#e8eaf0";
      ctx.font = "13px Arial";
      ctx.textAlign = "center";
      ctx.fillText(f.name, f.x, f.y - f.r - 10);
    }
  }
  drawPerson(player.x, player.y, player.r, player.facing, player.inv > 0 ? "#ff8899" : "#6ec8ff", "#f0c8a0", true, false);
  if (aimSkill) {
    ctx.strokeStyle = "#fff";
    ctx.setLineDash([4, 4]);
    ctx.beginPath();
    ctx.arc(aimX, aimY, 18, 0, Math.PI * 2);
    ctx.moveTo(player.x, player.y);
    ctx.lineTo(aimX, aimY);
    ctx.stroke();
    ctx.setLineDash([]);
  }
  ctx.restore();

  const boss = foes.find((f) => f.rank === "boss" && !f.dead);
  if (boss) {
    ctx.fillStyle = "#ff4466";
    ctx.font = "bold 13px Arial";
    ctx.textAlign = "center";
    ctx.fillText(boss.name.toUpperCase(), W * 0.5, 78);
    ctx.fillStyle = "#2a3038";
    ctx.fillRect(40, 84, W - 80, 12);
    ctx.fillStyle = "#ff4466";
    ctx.fillRect(40, 84, (W - 80) * Math.max(0, boss.hp / boss.max), 12);
    ctx.strokeStyle = "#111";
    ctx.strokeRect(40, 84, W - 80, 12);
  }

  const need = GIANTS.has(stage) ? 1 : 3;
  document.getElementById("left").textContent =
    "Stage " + stage + "/" + CAMPAIGN + "  Lv " + player.lvl + "  Bosses " + bossesKilled + "/" + need + (aimSkill ? "  AIM " + aimSkill : "");
  document.getElementById("right").textContent = "Gold " + progress.gold;
  document.getElementById("hpfill").style.width = Math.max(0, (player.hp / player.max) * 100) + "%";
  document.getElementById("xpfill").style.width = (player.xp / (player.xpNeed || 5)) * 100 + "%";
  document.getElementById("msg").textContent = msgT > 0 ? msg : "";
}

let last = performance.now();
function frame(now) {
  const dt = Math.min(0.05, (now - last) / 1000);
  last = now;
  tick(dt);
  draw();
  requestAnimationFrame(frame);
}
renderLobby();
requestAnimationFrame(frame);
