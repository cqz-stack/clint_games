/* Battling Monsters — browser port of the survivor-style desktop game. */
const canvas = document.getElementById("c");
const ctx = canvas.getContext("2d");
const lobbyEl = document.getElementById("lobby");
const levelEl = document.getElementById("levelup");
const picksEl = document.getElementById("picks");
const stagesEl = document.getElementById("stages");
const shopEl = document.getElementById("shop");

const CAMPAIGN = 10;
const BOSS_AT = [6, 12, 18];
const XP_NEED = 6;
const KEY = "battling-monsters-web";

const MOBS = [
  ["zombie", 8, 90, 14, "#5a7a52", "#a8c0a0"],
  ["zdog", 5, 170, 11, "#6a6a48", "#c0b880"],
  ["spider", 6, 130, 12, "#a02828", "#ff7070"],
  ["worker", 12, 72, 16, "#c9a038", "#ffe08a"],
];

const BOSSES = {
  1: [["Slime Lord", "#3a8a3a"], ["Bog Toad", "#4a6a2a"], ["Root Hulk", "#5a4030"]],
  2: [["Ash Fiend", "#a04020"], ["Ember Witch", "#902020"], ["Cinder Knight", "#6a3030"]],
  3: [["Frost Queen", "#5080c0"], ["Yeti Chief", "#7090a0"], ["Ice Warden", "#4060a0"]],
  4: [["Sand Pharaoh", "#c0a040"], ["Scarab King", "#806020"], ["Mirage Mage", "#a08050"]],
  5: [["Storm Titan", "#4050a0"], ["Gale Archer", "#6080b0"], ["Thunder Ogre", "#303870"]],
  6: [["Vine Hydra", "#2a6a40"], ["Bloom Witch", "#408060"], ["Thorn Beast", "#306030"]],
  7: [["Bone Lord", "#c8c0b0"], ["Grave Knight", "#8a8070"], ["Wraith Queen", "#706890"]],
  8: [["Magma Baron", "#c03010"], ["Lava Witch", "#a02020"], ["Basalt Golem", "#503028"]],
  9: [["Void Herald", "#301848"], ["Rift Stalker", "#201030"], ["Abyss Knight", "#181028"]],
  10: [["Queen Witch", "#6a2a8a"], ["King Zombie", "#4a6a40"], ["Termite Queen", "#8a7030"]],
};

const SHOP = {
  hp: { name: "Max HP", desc: "+2 max HP", max: 12, base: 40, step: 25 },
  dmg: { name: "Damage", desc: "+10% damage", max: 12, base: 50, step: 30 },
  spd: { name: "Speed", desc: "+6% move speed", max: 8, base: 45, step: 28 },
  magnet: { name: "Magnet", desc: "+20% pickup", max: 8, base: 35, step: 22 },
  orbit: { name: "Start Orbit", desc: "Begin with blades", max: 1, base: 180, step: 0 },
  aura: { name: "Start Aura", desc: "Begin with burn aura", max: 1, base: 180, step: 0 },
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
let player, foes, gems, coins, bullets, rings, crates, allies;
let stage = 1, bossesKilled = 0, msg = "", msgT = 0, orbitA = 0;

function load() {
  const base = { unlocked: 1, gold: 0, shop: {} };
  for (const k of Object.keys(SHOP)) base.shop[k] = 0;
  try {
    const d = JSON.parse(localStorage.getItem(KEY) || "null");
    if (!d) return base;
    base.unlocked = Math.max(1, Math.min(CAMPAIGN, d.unlocked | 0));
    base.gold = Math.max(0, d.gold | 0);
    for (const k of Object.keys(SHOP)) base.shop[k] = Math.max(0, Math.min(SHOP[k].max, (d.shop && d.shop[k]) | 0));
  } catch (e) { /* keep defaults */ }
  return base;
}
function save() { localStorage.setItem(KEY, JSON.stringify(progress)); }
function cost(id) { const d = SHOP[id]; return d.base + d.step * progress.shop[id]; }
function dmgMult() { return 1 + 0.1 * progress.shop.dmg + 0.2 * (player ? player.amps.dmg || 0 : 0); }
function spdMult() { return Math.min(1.8, 1 + 0.06 * progress.shop.spd + 0.08 * (player ? player.amps.spd || 0 : 0)); }

function resize() {
  W = canvas.width = window.innerWidth;
  H = canvas.height = window.innerHeight;
}
window.addEventListener("resize", resize);
resize();
window.addEventListener("keydown", (e) => {
  keys.add(e.key.toLowerCase());
  if (["arrowup", "arrowdown", "arrowleft", "arrowright", " "].includes(e.key.toLowerCase())) e.preventDefault();
});
window.addEventListener("keyup", (e) => keys.delete(e.key.toLowerCase()));

function renderLobby() {
  stagesEl.innerHTML = "";
  for (let i = 1; i <= CAMPAIGN; i++) {
    const b = document.createElement("button");
    const open = i <= progress.unlocked;
    b.textContent = (i === 10 ? "GIANT " : "") + "Stage " + i;
    b.disabled = !open;
    b.onclick = () => startRun(i);
    stagesEl.appendChild(b);
  }
  shopEl.innerHTML = "";
  const gold = document.createElement("p");
  gold.textContent = "Gold: " + progress.gold;
  gold.style.gridColumn = "1 / -1";
  gold.style.margin = "0";
  shopEl.appendChild(gold);
  for (const [id, d] of Object.entries(SHOP)) {
    const owned = progress.shop[id];
    const b = document.createElement("button");
    b.textContent = owned >= d.max ? d.name + " MAX" : d.name + " · " + cost(id) + "g (" + owned + "/" + d.max + ")";
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

function startRun(n) {
  stage = n;
  bossesKilled = 0;
  state = "play";
  lobbyEl.style.display = "none";
  levelEl.style.display = "none";
  const hp = 14 + 2 * progress.shop.hp;
  player = {
    x: 0, y: 0, r: 16, hp, max: hp, lvl: 1, xp: 0,
    weapons: { bolt: 1 },
    amps: {},
    inv: 0, regen: 0,
    cds: { bolt: 0, aura: 0, wave: 0, meteor: 0 },
  };
  if (progress.shop.orbit) player.weapons.orbit = 1;
  if (progress.shop.aura) player.weapons.aura = 1;
  foes = []; gems = []; coins = []; bullets = []; rings = []; crates = []; allies = [];
  toast("Stage " + n + " — defeat 3 bosses");
}

function toast(t) { msg = t; msgT = 2.4; }

function levelChoices() {
  const opts = [];
  for (const [id, d] of Object.entries(WEAPONS)) {
    const have = player.weapons[id] || 0;
    if (have < d.max) opts.push(["w", id, (have ? "Upgrade " : "New ") + d.name + " " + (have + 1), d.desc]);
  }
  if ((player.amps.dmg || 0) < 8) opts.push(["a", "dmg", "Power Amp", "+20% damage"]);
  if ((player.amps.spd || 0) < 6) opts.push(["a", "spd", "Swift Boots", "+8% move speed"]);
  for (let i = opts.length - 1; i > 0; i--) {
    const j = (Math.random() * (i + 1)) | 0;
    [opts[i], opts[j]] = [opts[j], opts[i]];
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
      else player.amps[id] = (player.amps[id] || 0) + 1;
      state = "play";
      levelEl.style.display = "none";
    };
    picksEl.appendChild(b);
  }
}

function addXp(n) {
  player.xp += n;
  while (player.xp >= XP_NEED) {
    player.xp -= XP_NEED;
    player.lvl++;
    openLevelUp();
    if (BOSS_AT.includes(player.lvl) && bossesKilled < 3) spawnBoss(bossesKilled);
    break;
  }
}

function spawnMob(near) {
  const k = MOBS[(Math.random() * MOBS.length) | 0];
  const a = Math.random() * Math.PI * 2;
  const d = near || 480 + Math.random() * 160;
  const scale = 1 + (stage - 1) * 0.12;
  foes.push({
    x: player.x + Math.cos(a) * d, y: player.y + Math.sin(a) * d,
    hp: k[1] * scale, max: k[1] * scale, speed: k[2], r: k[3],
    body: k[4], accent: k[5], rank: "mob", name: k[0],
  });
}

function spawnBoss(i) {
  const row = BOSSES[stage][i];
  const scale = 1 + (stage - 1) * 0.18;
  const giant = stage === 10;
  const hp = (90 + i * 40) * scale * (giant ? 2.2 : 1);
  const a = Math.random() * Math.PI * 2;
  foes.push({
    x: player.x + Math.cos(a) * 420, y: player.y + Math.sin(a) * 420,
    hp, max: hp, speed: giant && i === 2 ? 0 : 70, r: giant ? 46 : 32,
    body: row[1], accent: "#fff", rank: "boss", name: row[0], bossI: i,
  });
  toast("Boss: " + row[0]);
}

function nearestFoe() {
  let best = null, bd = 1e9;
  for (const f of foes) {
    const d = Math.hypot(f.x - player.x, f.y - player.y);
    if (d < bd) { bd = d; best = f; }
  }
  return best;
}

function hurtFoe(f, dmg) {
  f.hp -= dmg * dmgMult();
  if (f.hp <= 0) {
    f.dead = true;
    const roll = Math.random();
    const val = roll < 0.12 ? 10 : roll < 0.35 ? 5 : 1;
    const col = val === 10 ? "#ffd24a" : val === 5 ? "#4aa8ff" : "#5dcf5a";
    gems.push({ x: f.x, y: f.y, v: val, c: col });
    if (Math.random() < 0.25) coins.push({ x: f.x + 8, y: f.y, v: 2 + stage });
    if (f.rank === "boss") {
      bossesKilled++;
      toast(f.name + " fell (" + bossesKilled + "/3)");
      if (bossesKilled >= 3) winStage();
    }
  }
}

function winStage() {
  const bonus = 30 + stage * 10;
  progress.gold += bonus;
  if (stage >= progress.unlocked && progress.unlocked < CAMPAIGN) progress.unlocked = stage + 1;
  save();
  state = "lobby";
  lobbyEl.style.display = "flex";
  renderLobby();
  alert("Stage " + stage + " cleared! +" + bonus + " gold");
}

function die() {
  progress.gold += Math.floor(player.lvl);
  save();
  state = "lobby";
  lobbyEl.style.display = "flex";
  renderLobby();
  alert("You fell on stage " + stage + ". Gold kept: " + progress.gold);
}

let spawnT = 0, crateT = 3;
function tick(dt) {
  if (state !== "play") return;
  let mx = 0, my = 0;
  if (keys.has("a") || keys.has("arrowleft")) mx -= 1;
  if (keys.has("d") || keys.has("arrowright")) mx += 1;
  if (keys.has("w") || keys.has("arrowup")) my -= 1;
  if (keys.has("s") || keys.has("arrowdown")) my += 1;
  const mag = Math.hypot(mx, my) || 1;
  const spd = 280 * spdMult();
  player.x += (mx / mag) * spd * dt * (mx || my ? 1 : 0);
  player.y += (my / mag) * spd * dt * (mx || my ? 1 : 0);
  player.inv = Math.max(0, player.inv - dt);
  if (player.inv <= 0) {
    player.regen += dt;
    if (player.regen > 5 && player.hp < player.max) { player.hp = Math.min(player.max, player.hp + dt * 2); }
  } else player.regen = 0;

  spawnT -= dt;
  if (spawnT <= 0) { spawnT = Math.max(0.35, 1.05 - stage * 0.06); spawnMob(); }
  crateT -= dt;
  if (crateT <= 0) {
    crateT = 6;
    const a = Math.random() * Math.PI * 2;
    crates.push({ x: player.x + Math.cos(a) * 260, y: player.y + Math.sin(a) * 260, hp: 8, r: 16 });
  }

  orbitA += dt * (2.2 + (player.weapons.orbit || 0));
  const blades = player.weapons.orbit || 0;
  for (let i = 0; i < blades; i++) {
    const a = orbitA + (i / blades) * Math.PI * 2;
    const bx = player.x + Math.cos(a) * (52 + blades * 4);
    const by = player.y + Math.sin(a) * (52 + blades * 4);
    for (const f of foes) if (Math.hypot(f.x - bx, f.y - by) < f.r + 12) hurtFoe(f, 7 * dt * (1 + blades * 0.15));
  }
  if (player.weapons.aura) {
    player.cds.aura -= dt;
    const rad = 70 + player.weapons.aura * 10;
    if (player.cds.aura <= 0) {
      player.cds.aura = 0.35;
      for (const f of foes) if (Math.hypot(f.x - player.x, f.y - player.y) < rad + f.r) hurtFoe(f, 2.2 * player.weapons.aura);
    }
  }
  if (player.weapons.wave) {
    player.cds.wave -= dt;
    if (player.cds.wave <= 0) {
      player.cds.wave = Math.max(1.4, 3.2 - player.weapons.wave * 0.3);
      rings.push({ x: player.x, y: player.y, r: 10, max: 160 + player.weapons.wave * 20, dmg: 6 * player.weapons.wave });
    }
  }
  if (player.weapons.meteor) {
    player.cds.meteor -= dt;
    if (player.cds.meteor <= 0 && foes.length) {
      player.cds.meteor = Math.max(0.7, 2.4 - player.weapons.meteor * 0.25);
      const f = foes[(Math.random() * foes.length) | 0];
      rings.push({ x: f.x, y: f.y, r: 8, max: 48, dmg: 8 * player.weapons.meteor });
    }
  }
  player.cds.bolt -= dt;
  const boltLv = player.weapons.bolt || 0;
  if (boltLv && player.cds.bolt <= 0) {
    const t = nearestFoe();
    if (t) {
      player.cds.bolt = Math.max(0.18, 0.55 - boltLv * 0.06);
      const ang = Math.atan2(t.y - player.y, t.x - player.x);
      const shots = 1 + Math.floor((boltLv - 1) / 2);
      for (let i = 0; i < shots; i++) {
        const spread = (i - (shots - 1) / 2) * 0.12;
        bullets.push({
          x: player.x, y: player.y,
          vx: Math.cos(ang + spread) * 460, vy: Math.sin(ang + spread) * 460,
          dmg: 3 + boltLv, life: 1.2, r: 4, hostile: false, color: "#e8d080",
        });
      }
    }
  }

  for (const r of rings) {
    const prev = r.r;
    r.r += 280 * dt;
    for (const f of foes) {
      const d = Math.hypot(f.x - r.x, f.y - r.y);
      if (d < r.r + f.r && d > prev - f.r) hurtFoe(f, r.dmg);
    }
  }
  rings = rings.filter((r) => r.r < r.max);

  for (const b of bullets) {
    b.x += b.vx * dt; b.y += b.vy * dt; b.life -= dt;
    if (b.hostile) {
      if (Math.hypot(b.x - player.x, b.y - player.y) < player.r + b.r) hitPlayer(b.dmg);
    } else {
      for (const f of foes) if (Math.hypot(f.x - b.x, f.y - b.y) < f.r + b.r) { hurtFoe(f, b.dmg); b.life = 0; }
    }
  }
  bullets = bullets.filter((b) => b.life > 0);

  for (const f of foes) {
    if (f.dead) continue;
    const ang = Math.atan2(player.y - f.y, player.x - f.x);
    f.x += Math.cos(ang) * f.speed * dt;
    f.y += Math.sin(ang) * f.speed * dt;
    if (Math.hypot(f.x - player.x, f.y - player.y) < f.r + player.r) hitPlayer(f.rank === "boss" ? 2 : 1);
    if (f.rank === "boss" && Math.random() < dt * 0.35) {
      bullets.push({
        x: f.x, y: f.y,
        vx: Math.cos(ang) * 220, vy: Math.sin(ang) * 220,
        dmg: 1, life: 2, r: 5, hostile: true, color: "#ff5566",
      });
    }
  }
  foes = foes.filter((f) => !f.dead);

  const magnet = 70 * (1 + 0.2 * progress.shop.magnet);
  for (const g of gems) {
    const d = Math.hypot(g.x - player.x, g.y - player.y);
    if (d < magnet) {
      g.x += (player.x - g.x) / d * 220 * dt;
      g.y += (player.y - g.y) / d * 220 * dt;
    }
    if (d < player.r + 8) { addXp(g.v); g.got = true; }
  }
  gems = gems.filter((g) => !g.got);
  for (const c of coins) {
    if (Math.hypot(c.x - player.x, c.y - player.y) < player.r + 10) {
      progress.gold += c.v;
      save();
      c.got = true;
    }
  }
  coins = coins.filter((c) => !c.got);
  for (const c of crates) {
    if (Math.hypot(c.x - player.x, c.y - player.y) < player.r + c.r + 8) {
      c.hp -= 6 * dt * dmgMult();
      if (c.hp <= 0) {
        coins.push({ x: c.x, y: c.y, v: 8 + stage * 2 });
        c.dead = true;
      }
    }
  }
  crates = crates.filter((c) => !c.dead);
  msgT = Math.max(0, msgT - dt);
  camX = player.x - W / 2;
  camY = player.y - H / 2;
}

function hitPlayer(n) {
  if (player.inv > 0) return;
  player.hp -= n;
  player.inv = 0.7;
  player.regen = 0;
  if (player.hp <= 0) die();
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
    }
  }
  for (const c of crates) {
    ctx.fillStyle = "#8a6238";
    ctx.fillRect(c.x - c.r, c.y - c.r, c.r * 2, c.r * 2);
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
    ctx.arc(player.x + Math.cos(a) * (52 + blades * 4), player.y + Math.sin(a) * (52 + blades * 4), 7, 0, Math.PI * 2);
    ctx.fill();
  }
  if (player.weapons.aura) {
    ctx.strokeStyle = "rgba(255,120,40,0.45)";
    ctx.beginPath();
    ctx.arc(player.x, player.y, 70 + player.weapons.aura * 10, 0, Math.PI * 2);
    ctx.stroke();
  }
  for (const r of rings) {
    ctx.strokeStyle = "#c4e06a";
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
    ctx.fillStyle = f.body;
    ctx.beginPath();
    ctx.arc(f.x, f.y, f.r, 0, Math.PI * 2);
    ctx.fill();
    ctx.strokeStyle = f.rank === "boss" ? "#ff4466" : f.accent;
    ctx.stroke();
    if (f.rank === "boss") {
      ctx.fillStyle = "#e8eaf0";
      ctx.font = "12px Arial";
      ctx.textAlign = "center";
      ctx.fillText(f.name, f.x, f.y - f.r - 8);
      ctx.fillStyle = "#2a3038";
      ctx.fillRect(f.x - 24, f.y - f.r - 6, 48, 4);
      ctx.fillStyle = "#ff5566";
      ctx.fillRect(f.x - 24, f.y - f.r - 6, 48 * Math.max(0, f.hp / f.max), 4);
    }
  }
  ctx.fillStyle = player.inv > 0 ? "#ff5566" : "#6ec8ff";
  ctx.beginPath();
  ctx.arc(player.x, player.y, player.r, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  document.getElementById("left").textContent =
    "Stage " + stage + "  Lv " + player.lvl + "  Bosses " + bossesKilled + "/3";
  document.getElementById("right").textContent = "Gold " + progress.gold;
  document.getElementById("hpfill").style.width = Math.max(0, (player.hp / player.max) * 100) + "%";
  document.getElementById("xpfill").style.width = (player.xp / XP_NEED) * 100 + "%";
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
