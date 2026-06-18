/* ===== Hセクション：JavaScript処理 ===== */
const myName = window.BATTLE_CONFIG.myName;
const roomId = window.BATTLE_CONFIG.roomId;

let lastEventId = -1;
let lastTurn = 0;
let previousPhase = null;
let actionSubmitted = false;
let isPlayingEvent = false;
let selectingTarget = null;
let selectedEnemyTarget = null;
let selectedWeaponId = "";
let selectedShieldId = "";
let selectedSkillId = "";
let victoryBgmPlayed = false;
let selectingWeaponAction = null;
let selectingShieldAction = false;
let selectingSkillAction = false;

let currentBossMax = 1;
let lastPlayers = [];
let previousHpMap = {};
let previousBossHp = null;
let previousEnemiesHpMap = {};
let lastEnemiesRenderKey = "";
let defeatedEnemyIds = new Set();
let damageFlashNames = new Set();
let damageFlashTimer = null;
let bossFlashTimer = null;
let bossFlashTimers = {};
let lastChatId = -1;

let soundUnlocked = false;
let lastBattleData = null;

/* ===== H-1Bセクション：非表示メッセージ判定 ===== */
function isHiddenBattleMessage(text) {
  return String(text || "").includes("行動順");
}

function getVisibleBattleEvents(events) {
  return (events || []).filter(event => !isHiddenBattleMessage(event && event.text));
}

function getVisibleBattleLogs(logs) {
  return (logs || []).filter(text => !isHiddenBattleMessage(text));
}

/* ===== H-2セクション：効果音設定 ===== */
const sounds = {
  hero_attack: new Audio("/static/sounds/hero_attack.mp3"),
  mage_attack: new Audio("/static/sounds/mage_attack.mp3"),
  tank_attack: new Audio("/static/sounds/tank_attack.mp3"),
  heal_single: new Audio("/static/sounds/heal_single.mp3"),
  heal_all: new Audio("/static/sounds/heal_all.mp3"),
  guard: new Audio("/static/sounds/guard.mp3"),
  magic_defense: new Audio("/static/sounds/magic_defense.mp3"),
  boss_attack: new Audio("/static/sounds/boss_attack.mp3"),
  boss_breath: new Audio("/static/sounds/boss_breath.mp3")
}; 

/* ===== H-2Bセクション：BGM設定 ===== */

let battleBgmFile = "/static/sounds/battle_bgm.mp3";
let battleBgm = new Audio(battleBgmFile);
battleBgm.loop = true;
battleBgm.volume = 0.35;

const victoryBgm = new Audio("/static/sounds/victory.mp3");
victoryBgm.loop = false;
victoryBgm.volume = 0.55;

const defeatBgm = new Audio("/static/sounds/defeat.mp3");
defeatBgm.loop = false;
defeatBgm.volume = 0.55;

let battleEnded = false;
let victoryPlayed = false;
let rematchInProgress = false;
let leavingBattle = false;

function getBattleBgmFileByRoomName(roomName) {
  const name = String(roomName || "");

  if (name.includes("ランダム雑魚戦（1体）") || name.includes("ランダム雑魚戦(1体)")) {
    return "/static/sounds/battle_bgm_1.mp3";
  }

  if (name.includes("ランダム雑魚戦（2体）") || name.includes("ランダム雑魚戦(2体)")) {
    return "/static/sounds/battle_bgm_2.mp3";
  }

  if (name.includes("ランダム雑魚戦（3体）") || name.includes("ランダム雑魚戦(3体)")) {
    return "/static/sounds/battle_bgm_3.mp3";
  }

  if (name.includes("ランダム雑魚戦（4体）") || name.includes("ランダム雑魚戦(4体)")) {
    return "/static/sounds/battle_bgm_4.mp3";
  }

  return "/static/sounds/battle_bgm.mp3";
}

function switchBattleBgmByRoomName(roomName) {
  const nextFile = getBattleBgmFileByRoomName(roomName);

  if (nextFile === battleBgmFile) {
    return;
  }

  const shouldPlay =
    soundUnlocked &&
    !battleEnded &&
    !rematchInProgress &&
    !battleBgm.paused;

  battleBgm.pause();
  battleBgm.currentTime = 0;

  battleBgmFile = nextFile;
  battleBgm = new Audio(battleBgmFile);
  battleBgm.loop = true;
  battleBgm.volume = 0.35;
  battleBgm.load();

  if (shouldPlay) {
    battleBgm.play().catch(() => {});
  }
}

Object.values(sounds).forEach(sound => {
  sound.preload = "auto";
  sound.volume = 0.8;
});

/* ===== H-3セクション：効果音再生処理 ===== */
function unlockSounds() {
  if (soundUnlocked) return;
  soundUnlocked = true;

  Object.values(sounds).forEach(sound => {
    sound.load();
  });

  battleBgm.load();
  victoryBgm.load();
  defeatBgm.load();

  startBattleBgm();
}

document.addEventListener("click", unlockSounds, { once: true });
document.addEventListener("touchstart", unlockSounds, { once: true });

function playSound(soundName) {
  const sound = sounds[soundName];
  if (!sound) return;

  try {
    sound.currentTime = 0;
    sound.play().catch(() => {});
  } catch (e) {
    // ブラウザで再生が止められた場合は何もしない
  }
}

function startBattleBgm() {
  victoryBgmPlayed = false; // 新しい戦闘開始
  if (battleEnded) return;

  victoryBgm.pause();
  victoryBgm.currentTime = 0;

  if (battleBgm.paused) {
    battleBgm.play().catch(() => {});
  }
}

function stopBattleBgm() {
  battleBgm.pause();
  battleBgm.currentTime = 0;
}

function playVictoryBgm() {
  if (victoryPlayed) return;

  victoryPlayed = true;

  battleBgm.pause();
  battleBgm.currentTime = 0;

  defeatBgm.pause();
  defeatBgm.currentTime = 0;

  victoryBgm.pause();
  victoryBgm.currentTime = 0;
  victoryBgm.play().catch(() => {});
}

function playDefeatBgm() {
  if (victoryPlayed) return;

  victoryPlayed = true;

  stopBattleBgm();

  victoryBgm.pause();
  victoryBgm.currentTime = 0;

  defeatBgm.currentTime = 0;
  defeatBgm.play().catch(() => {});
}

function stopAllMusic() {
  battleBgm.pause();
  battleBgm.currentTime = 0;

  victoryBgm.pause();
  victoryBgm.currentTime = 0;

  defeatBgm.pause();
  defeatBgm.currentTime = 0;
}

function handleEndMusic(data) {
  if (data.phase !== "end") return;

  if (rematchInProgress) return;

  battleEnded = true;

  if (data.winner === "players") {
    playVictoryBgm();
  } else if (data.winner === "boss") {
    playDefeatBgm();
  } else {
    stopBattleBgm();
  }
}

function getPlayerJobByName(name) {
  const player = lastPlayers.find(p => p.name === name);
  return player ? player.job : null;
}

function playSoundForEventText(text) {
  if (!text) return;

  if (text.includes("ボスの全体ブレス攻撃")) {
    playSound("boss_breath");
    return;
  }

  if (text.includes("ボスの攻撃")) {
    playSound("boss_attack");
    return;
  }

  if (text.includes("魔法防御")) {
    playSound("magic_defense");
    return;
  }

  if (text.includes("の全体回復")) {
    playSound("heal_all");
    return;
  }

  if (text.includes("の選択回復")) {
    playSound("heal_single");
    return;
  }

  if (text.includes("をかばう") || text.includes("は身構えた")) {
    playSound("guard");
    return;
  }

  if (text.includes("の攻撃")) {
    const attackerName = text.split("の攻撃")[0];
    const job = getPlayerJobByName(attackerName);

    if (job === "勇者") {
      playSound("hero_attack");
    } else if (job === "魔術師") {
      playSound("mage_attack");
    } else if (job === "タンク") {
      playSound("tank_attack");
    } else {
      playSound("hero_attack");
    }
  }
}


/* ===== Iセクション：HP色判定 ===== */
function getHpColor(hp, maxHp) {
  const r = hp / maxHp;
  if (r < 0.3) return "#ff5252";
  if (r < 0.6) return "#ffb300";
  return "#3ddc84";
}

/* ===== Jセクション：プレイヤー描画 ===== */
function renderPlayers(players, compact=false) {
  const area = document.getElementById("playersArea");
  area.innerHTML = "";

  const grid = document.createElement("div");
  grid.className = "players-grid";

  players.forEach(p => {
    grid.appendChild(createPlayerCard(p, compact));
  });

  area.appendChild(grid);
}

/* ===== Kセクション：プレイヤーカード生成 ===== */
function createPlayerCard(p, compact=false) {
  const div = document.createElement("div");

  const percent = p.max_hp > 0 ? (p.hp / p.max_hp) * 100 : 0;
  const color = getHpColor(p.hp, p.max_hp);

  let selectableClass = "";
  if (selectingTarget === "heal" && p.hp > 0 && !compact) {
    selectableClass = " selectable-heal";
  }
  if (selectingTarget === "guard" && p.hp > 0 && !compact) {
    selectableClass = " selectable-guard";
  }

  div.className =
    "player-card" +
    (p.name === myName ? " me" : "") +
    (p.hp <= 0 ? " dead" : "") +
    selectableClass +
    (damageFlashNames.has(p.name) ? " damage-flash" : "");

  if (selectingTarget === "heal" && p.hp > 0 && !compact) {
    div.onclick = () => {
      sendAction("heal", p.name);
    };
  }

  if (selectingTarget === "guard" && p.hp > 0 && !compact) {
    div.onclick = () => {
      sendAction("guard", p.name);
    };
  }

  if (compact) {
    div.innerHTML = `
      <div class="player-row">
        <div class="player-name">${p.name}（${p.job || "未設定"}）${p.online === false ? "（通信切断）" : ""}</div>
        <div class="hp-bar-wrap">
          <div class="hp-bar" style="width:${percent}%; background:${color}"></div>
        </div>
      </div>
    `;
  } else {
    div.innerHTML = `
      <div class="player-row">
        <div class="player-name">${p.name}（${p.job || "未設定"}）${p.online === false ? "（通信切断）" : ""}</div>
        <div class="player-stats">
          HP:${p.hp}/${p.max_hp} ATK:${p.attack} HEAL:${p.heal}<br>
          <span style="color:#ffcc80;">
            持込:${p.carried_weapons && p.carried_weapons.length
              ? p.carried_weapons.map(w => w.name).join(" / ")
              : (p.weapon_name || "武器なし")}
          </span>
        </div>
      </div>
      <div class="hp-bar-wrap" style="margin-top:6px;">
        <div class="hp-bar" style="width:${percent}%; background:${color}"></div>
      </div>
    `;
  }

  return div;
}

/* ===== Lセクション：イベント再生 ===== */
function playEvents(events) {
  events = getVisibleBattleEvents(events);
  if (!events || events.length === 0) return;

  isPlayingEvent = true;
  selectingTarget = null;

  clearDamageFlash();
  clearBossFlash();

  let i = 0;

  function finishEvents() {
    isPlayingEvent = false;
    clearDamageFlash();
    clearBossFlash();

    // ===== 全演出終了後だけ、最終状態と操作UIを反映する =====
    if (lastBattleData) {
      updateBossDisplay(lastBattleData);
      renderPlayers(lastBattleData.players, false);
      syncPreviousHpFromData(lastBattleData);
      renderMainPanel(lastBattleData);
    } else {
      renderPlayers(lastPlayers, false);
    }

    const hasVictoryEvent = events.some(event => event && event.text === "勝利！");
    const hasDefeatEvent = events.some(event => event && event.text === "敗北");

    // ===== 敗北BGMはイベント演出が全部終わってから鳴らす =====
    // 勝利BGMは「勝利！」表示と同時に鳴らす。
    // ただし古いイベントや途中復帰で未再生だった場合の保険として、ここでも一度だけ確認する。
    if (hasVictoryEvent && !victoryPlayed) {
      battleEnded = true;
      playVictoryBgm();
    }

    if (hasDefeatEvent) {
      battleEnded = true;
      playDefeatBgm();
    }
  }

  function next() {
    if (i >= events.length) {
      finishEvents();
      return;
    }

    const mainPanel = document.getElementById("mainPanel");

    // ===== ボスセリフは赤表示 =====
    if (events[i].text && events[i].text.includes("ボス「")) {
      mainPanel.style.color = "#ff4040";
    } else {
      mainPanel.style.color = "";
    }

    mainPanel.innerText = events[i].text;
    playSoundForEventText(events[i].text);

    // ===== 勝利BGMは「勝利！」の字幕が表示された瞬間に鳴らす =====
    if (events[i].text === "勝利！") {
      battleEnded = true;
      playVictoryBgm();
    }

    if (events[i].flash_enemy) {
      if (events[i].target_enemies && events[i].target_enemies.length > 0) {
        flashBossMany(events[i].target_enemies, events[i].flash_type || "physical", events[i].flash_element || "light");
      } else {
        flashBoss(events[i].target_enemy, events[i].flash_type || "physical", events[i].flash_element || "light");
      }
    }

    if (events[i].state) {
      applyEventState(events[i].state);
    }

    // ===== 「倒した！」表示の瞬間にグレーアウト反映 =====
    if (
      events[i].text &&
      events[i].text.includes("を倒した") &&
      events[i].target_enemy
    ) {
      defeatedEnemyIds.add(events[i].target_enemy);

      const defeatedCard = document.getElementById("enemy-" + events[i].target_enemy);

      if (defeatedCard) {
        defeatedCard.classList.add("dead");
      }
    }

    i++;
    setTimeout(next, 2000);
  }

  next();
}

/* ===== Mセクション：イベント中のHP反映・被ダメージ判定 ===== */
function applyEventState(state) {
  const oldHpMap = {...previousHpMap};
  const oldBossHp = previousBossHp;

  document.getElementById("bossHpText").innerText =
    `${state.boss_hp} / ${currentBossMax}`;

  const bossPercent = currentBossMax > 0 ? (state.boss_hp / currentBossMax) * 100 : 0;
  document.getElementById("bossBar").style.width = bossPercent + "%";

  if (state.enemies_hp) {
      previousEnemiesHpMap = {...state.enemies_hp};
  }

previousBossHp = state.boss_hp;

  // ===== 敵HPバーだけイベント中に反映。倒れグレーアウトは演出終了後 =====
  if (state.enemies_hp) {
    Object.keys(state.enemies_hp).forEach(enemyId => {
      const card = document.getElementById("enemy-" + enemyId);

      if (!card) return;

      const enemy =
        lastBattleData &&
        lastBattleData.enemies
          ? lastBattleData.enemies.find(e => e.id === enemyId)
          : null;

      if (!enemy) return;

      const hp = state.enemies_hp[enemyId];
      const percent = enemy.max_hp > 0 ? (hp / enemy.max_hp) * 100 : 0;

      const hpText = card.querySelector(".enemy-hp-text");
      const hpBar = card.querySelector(".enemy-bar");

      if (hpText) {
        hpText.innerText = `HP:${hp}/${enemy.max_hp}`;
      }

      if (hpBar) {
        hpBar.style.width = percent + "%";
      }

      // 「○○を倒した！」が出るまではグレーアウトしない。
      // ただし、すでに倒した表示済みの敵はグレーアウトを維持する。
      if (!defeatedEnemyIds.has(enemyId)) {
        card.classList.remove("dead");
      }
    });
  }



  const oldTemp = lastPlayers.map(p => ({
    ...p,
    hp: oldHpMap[p.name] !== undefined ? oldHpMap[p.name] : p.hp
  }));

  const newTemp = lastPlayers.map(p => ({
    ...p,
    hp: state.players_hp[p.name]
  }));

  clearDamageFlash();

  const damagedNames = [];

  newTemp.forEach(p => {
    if (
      oldHpMap[p.name] !== undefined &&
      p.hp < oldHpMap[p.name]
    ) {
      damagedNames.push(p.name);
      damageFlashNames.add(p.name);
    }
  });

  // ===== ダメージがある場合：先に赤点滅、その後にHPバーを同時に減らす =====
  if (damagedNames.length > 0) {

    // まずは旧HPのまま赤く光らせる
    renderPlayers(oldTemp, true);

    setTimeout(() => {
      // 少し遅れて新HPを同時反映する
      renderPlayers(newTemp, true);

      previousHpMap = {};
      newTemp.forEach(p => {
        previousHpMap[p.name] = p.hp;
      });

      damageFlashTimer = setTimeout(() => {
        damageFlashNames.clear();
        renderPlayers(newTemp, true);
        damageFlashTimer = null;
      }, 900);

    }, 350);

    return;
  }

  // ===== ダメージがない場合は通常更新 =====
  previousHpMap = {};
  newTemp.forEach(p => {
    previousHpMap[p.name] = p.hp;
  });

  renderPlayers(newTemp, true);
}

/* ===== M-2セクション：点滅解除処理 ===== */
function clearDamageFlash() {
  if (damageFlashTimer) {
    clearTimeout(damageFlashTimer);
    damageFlashTimer = null;
  }

  damageFlashNames.clear();
}


function getMagicEffectColors(element) {
  const colorMap = {
    fire: {
      color: "#ff3b30",
      strong: "rgba(255,59,48,0.95)",
      solid: "rgba(255,59,48,1)",
      soft: "rgba(255,120,80,0.9)"
    },
    ice: {
      color: "#66d9ff",
      strong: "rgba(102,217,255,0.95)",
      solid: "rgba(102,217,255,1)",
      soft: "rgba(150,235,255,0.9)"
    },
    wind: {
      color: "#4ade80",
      strong: "rgba(74,222,128,0.95)",
      solid: "rgba(74,222,128,1)",
      soft: "rgba(134,239,172,0.9)"
    },
    thunder: {
      color: "#ffd700",
      strong: "rgba(255,215,0,0.95)",
      solid: "rgba(255,215,0,1)",
      soft: "rgba(255,235,120,0.9)"
    },
    light: {
      color: "#ffffff",
      strong: "rgba(255,255,255,0.95)",
      solid: "rgba(255,255,255,1)",
      soft: "rgba(255,255,255,0.9)"
    },
    dark: {
      color: "#b266ff",
      strong: "rgba(178,102,255,0.95)",
      solid: "rgba(178,102,255,1)",
      soft: "rgba(210,160,255,0.9)"
    }
  };

  return colorMap[element] || colorMap.light;
}


function getPhysicalEffectColors(element) {
  const colorMap = {
    fire: {
      strong: "rgba(255,70,45,0.95)",
      solid: "rgba(255,60,40,1)",
      soft: "rgba(255,130,70,0.9)"
    },
    ice: {
      strong: "rgba(180,245,255,0.95)",
      solid: "rgba(90,220,255,1)",
      soft: "rgba(150,235,255,0.9)"
    },
    wind: {
      strong: "rgba(180,255,210,0.95)",
      solid: "rgba(70,230,130,1)",
      soft: "rgba(130,245,170,0.9)"
    },
    thunder: {
      strong: "rgba(255,245,150,0.98)",
      solid: "rgba(255,215,0,1)",
      soft: "rgba(255,235,90,0.95)"
    },
    light: {
      strong: "rgba(255,255,255,0.98)",
      solid: "rgba(255,255,255,1)",
      soft: "rgba(255,255,220,0.95)"
    },
    dark: {
      strong: "rgba(220,170,255,0.95)",
      solid: "rgba(170,80,255,1)",
      soft: "rgba(200,130,255,0.9)"
    },
    none: {
      strong: "rgba(255,255,255,0.95)",
      solid: "rgba(120,220,255,1)",
      soft: "rgba(120,220,255,0.9)"
    }
  };

  return colorMap[element] || colorMap.none;
}

function flashBoss(enemyId=null, flashType='physical', flashElement='light') {
  let effect = null;
  let targetElement = null;

  if (enemyId) {
    const enemyCard = document.getElementById("enemy-" + enemyId);

    if (enemyCard) {
      targetElement = enemyCard;
      effect = enemyCard.querySelector(".enemy-hit-effect");
    }
  }

  if (!effect) {
    const firstEnemy = document.querySelector(".enemy-card:not(.dead)");

    if (firstEnemy) {
      targetElement = firstEnemy;
      effect = firstEnemy.querySelector(".enemy-hit-effect");
    }
  }

  if (!targetElement || !effect) return;

  clearBossFlashTarget(targetElement);

  targetElement.classList.add("boss-damage-flash");

  if (flashType === "magic") {
    const magicColors = getMagicEffectColors(flashElement);

    effect.style.setProperty("--magic-effect-color", magicColors.color);
    effect.style.setProperty("--magic-effect-color-strong", magicColors.strong);
    effect.style.setProperty("--magic-effect-color-solid", magicColors.solid);
    effect.style.setProperty("--magic-effect-color-soft", magicColors.soft);

    effect.innerHTML = `
      <div class="magic-burst-effect"></div>
      <div class="magic-sparkle-effect"></div>
      <div class="magic-star-effect"></div>
    `;
  } else {
    const physicalColors = getPhysicalEffectColors(flashElement);

    effect.style.setProperty("--physical-effect-color-strong", physicalColors.strong);
    effect.style.setProperty("--physical-effect-color-solid", physicalColors.solid);
    effect.style.setProperty("--physical-effect-color-soft", physicalColors.soft);

    effect.innerHTML = `
      <div class="slash-effect"></div>
      <div class="slash-effect second"></div>
      <div class="slash-effect third"></div>
    `;
  }

  const timerKey = targetElement.id || "single_enemy";

  bossFlashTimers[timerKey] = setTimeout(() => {
    targetElement.classList.remove("boss-damage-flash");
    effect.innerHTML = "";
    delete bossFlashTimers[timerKey];
  }, 700);
}

function flashBossMany(enemyIds, flashType='physical', flashElement='light') {
  if (!enemyIds || enemyIds.length === 0) return;

  enemyIds.forEach(enemyId => {
    flashBoss(enemyId, flashType, flashElement);
  });
}

function clearBossFlashTarget(targetElement) {
  if (!targetElement) return;

  const timerKey = targetElement.id || "single_enemy";

  if (bossFlashTimers[timerKey]) {
    clearTimeout(bossFlashTimers[timerKey]);
    delete bossFlashTimers[timerKey];
  }

  targetElement.classList.remove("boss-damage-flash");

  const effect = targetElement.querySelector(".enemy-hit-effect");
  if (effect) {
    effect.innerHTML = "";
    effect.style.removeProperty("--magic-effect-color");
    effect.style.removeProperty("--magic-effect-color-strong");
    effect.style.removeProperty("--magic-effect-color-solid");
    effect.style.removeProperty("--magic-effect-color-soft");
    effect.style.removeProperty("--physical-effect-color-strong");
    effect.style.removeProperty("--physical-effect-color-solid");
    effect.style.removeProperty("--physical-effect-color-soft");
  }
}

function clearBossFlash() {
  if (bossFlashTimer) {
    clearTimeout(bossFlashTimer);
    bossFlashTimer = null;
  }

  Object.keys(bossFlashTimers).forEach(timerKey => {
    clearTimeout(bossFlashTimers[timerKey]);
  });
  bossFlashTimers = {};

  document.querySelectorAll(".enemy-card").forEach(card => {
    card.classList.remove("boss-damage-flash");
  });

  document.querySelectorAll(".enemy-hit-effect").forEach(effect => {
    effect.innerHTML = "";
    effect.style.removeProperty("--magic-effect-color");
    effect.style.removeProperty("--magic-effect-color-strong");
    effect.style.removeProperty("--magic-effect-color-solid");
    effect.style.removeProperty("--magic-effect-color-soft");
    effect.style.removeProperty("--physical-effect-color-strong");
    effect.style.removeProperty("--physical-effect-color-solid");
    effect.style.removeProperty("--physical-effect-color-soft");
  });
}


/* ===== N-0セクション：接続維持処理 ===== */
async function sendHeartbeat() {
  const fd = new FormData();
  fd.append("name", myName);
  fd.append("room_id", roomId);

  try {
    await fetch("/heartbeat", {
      method: "POST",
      body: fd
    });
  } catch (e) {
    // 通信失敗時は何もしない
  }
}


/* ===== Nセクション：画面更新 ===== */
function hasMyActionOnServer(data) {
  return Boolean(
    data &&
    data.actions &&
    Object.prototype.hasOwnProperty.call(data.actions, myName)
  );
}

function syncPreviousHpFromData(data) {
  if (!data) return;

  previousHpMap = {};
  (data.players || []).forEach(p => {
    previousHpMap[p.name] = p.hp;
  });

  previousBossHp = data.boss_hp;

  previousEnemiesHpMap = {};
  (data.enemies || []).forEach(e => {
    previousEnemiesHpMap[e.id] = e.hp;
  });
}

function rememberDefeatedEnemies(data) {
  (data.enemies || []).forEach(e => {
    if (e.hp <= 0) {
      defeatedEnemyIds.add(e.id);
    }
  });
}

function handlePageTransition(data) {
  if (leavingBattle) {
    return true;
  }

  // ===== 念のため：旧版の再戦ジョブ選択モードが残っていた場合だけジョブ選択へ移動 =====
  if (data.rematch_select) {
    window.location.href = "/character_select?room_id=" + encodeURIComponent(roomId);
    return true;
  }

  if (data.viewer_blocked) {
    stopAllMusic();
    alert("投票によりパーティーから退出しました。1時間は再参加できません。");
    location.href = "/";
    return true;
  }

  if (data.viewer_removed) {
    stopAllMusic();
    alert("パーティーから退出しました。");
    location.href = "/";
    return true;
  }

  if (!data.started && data.phase === "waiting") {
    stopAllMusic();
    location.href = "/lobby?name=" + encodeURIComponent(myName) + "&room_id=" + encodeURIComponent(roomId);
    return true;
  }

  const myPlayerStillExists =
    data.players && data.players.some(p => p.name === myName);

  if (!myPlayerStillExists) {
    stopAllMusic();
    location.href = "/";
    return true;
  }

  return false;
}

function syncBattleFlags(data) {
  lastBattleData = data;
  currentBossMax = data.boss_max_hp;
  switchBattleBgmByRoomName(data.room_name);
  lastPlayers = data.players || [];

  rememberDefeatedEnemies(data);

  if (Object.keys(previousEnemiesHpMap).length === 0 && data.enemies) {
    data.enemies.forEach(e => {
      previousEnemiesHpMap[e.id] = e.hp;
    });
  }

  if (Object.keys(previousHpMap).length === 0) {
    (data.players || []).forEach(p => {
      previousHpMap[p.name] = p.hp;
    });
  }

  // ===== 再戦検出：全端末で勝利/敗北BGMから戦闘BGMへ戻す =====
  if (previousPhase === "end" && data.phase === "choice") {
    battleEnded = false;
    victoryPlayed = false;
    victoryBgmPlayed = false;
    rematchInProgress = false;
    actionSubmitted = false;
    selectingTarget = null;
    selectingWeaponAction = null;
    selectingShieldAction = false;
    selectingSkillAction = false;
    selectedWeaponId = "";
    selectedShieldId = "";
    defeatedEnemyIds.clear();
    lastEnemiesRenderKey = "";

    victoryBgm.pause();
    victoryBgm.currentTime = 0;

    defeatBgm.pause();
    defeatBgm.currentTime = 0;

    battleBgm.currentTime = 0;
    battleBgm.play().catch(() => {});
  }

  previousPhase = data.phase;

  let displayTurn = data.turn;

  if (isPlayingEvent) {
      displayTurn = Math.max(1, data.turn - 1);
  }

  document.getElementById("turn").innerText = displayTurn;

  if (data.turn !== lastTurn) {
    actionSubmitted = false;
    selectingTarget = null;
    selectingWeaponAction = null;
    selectingShieldAction = false;
    selectingSkillAction = false;
    selectedWeaponId = "";
    selectedShieldId = "";
    selectedSkillId = "";
    clearDamageFlash();
    clearBossFlash();
    lastTurn = data.turn;
  }

  // ===== サーバー側で行動が消えていたら、画面側の「行動済み」も解除する =====
  // 一人プレイや通信タイミングのズレで、ローカルだけ待機状態が残るのを防ぐ。
  if (data.phase === "choice" && !hasMyActionOnServer(data) && actionSubmitted) {
    actionSubmitted = false;
  }
}

function renderStableBattleScreen(data) {
  updateBossDisplay(data);
  renderPlayers(data.players || [], false);
  syncPreviousHpFromData(data);
}

function renderBattleSubPanels(data) {
  document.getElementById("logBox").innerHTML =
    getVisibleBattleLogs(data.log || []).map(l => `<div>${l}</div>`).join("");

  renderChat(data.chat_messages || [], data);
  renderKickVote(data);
}

async function update() {
  let data = null;

  try {
    const res = await fetch(`/state?name=${encodeURIComponent(myName)}&room_id=${encodeURIComponent(roomId)}`);
    data = await res.json();
  } catch (e) {
    document.getElementById("actionStatus").innerText = "通信確認中...";
    return;
  }

  if (handlePageTransition(data)) {
    return;
  }

  syncBattleFlags(data);

  const hasNewEvent = data.event_id !== lastEventId;

  if (hasNewEvent) {
    lastEventId = data.event_id;
    playEvents(data.turn_events || []);
  }

  // ===== イベント中は最終状態を先に描画しない =====
  if (!isPlayingEvent && !hasNewEvent) {
    renderStableBattleScreen(data);
  }

  renderBattleSubPanels(data);

  // ===== 操作UIは最後に描画する =====
  // イベント中は renderMainPanel 内で「戦闘中...」だけを表示する。
  renderMainPanel(data);
}

/* ===== Oセクション：ボス表示更新 ===== */
function updateBossDisplay(data) {
  document.getElementById("enemyTitle").innerText =
    data.room_name || "敵";

  document.getElementById("bossHpText").innerText =
    `${data.boss_hp} / ${data.boss_max_hp}`;

  const bossPercent = data.boss_max_hp > 0 ? (data.boss_hp / data.boss_max_hp) * 100 : 0;
  document.getElementById("bossBar").style.width = bossPercent + "%";

  renderEnemies(data.enemies || [], false);
}

function renderEnemies(enemies, force=false) {
  const area = document.getElementById("enemiesArea");

  if (!area) return;

  const renderKey = enemies.map(e =>
    `${e.id}:${e.name}:${e.hp}:${e.max_hp}:${e.image}:${defeatedEnemyIds.has(e.id)}`
  ).join("|");

  // ===== 同じ内容なら敵表示を作り直さない =====
  if (!force && renderKey === lastEnemiesRenderKey) {
    return;
  }

  lastEnemiesRenderKey = renderKey;

  const grid = document.createElement("div");
  grid.className = "enemies-grid";

  enemies.forEach(enemy => {
    const card = document.createElement("div");
    card.className = "enemy-card" + ((enemy.hp <= 0 || defeatedEnemyIds.has(enemy.id)) ? " dead" : "");
    card.onclick = () => {
      if ((selectingTarget === "enemy_attack" || selectingTarget === "skill_enemy_attack") && enemy.hp > 0) {
        selectEnemyTarget(enemy.id);
      }
    };
    card.id = "enemy-" + enemy.id;

    const percent = enemy.max_hp > 0 ? (enemy.hp / enemy.max_hp) * 100 : 0;

    card.innerHTML = `
      <div class="boss-hit-effect enemy-hit-effect"></div>
      <div class="enemy-name">${enemy.name}</div>
      <img class="enemy-image" src="${enemy.image}" alt="${enemy.name}">
      <div class="enemy-hp-text">HP:${enemy.hp}/${enemy.max_hp}</div>
      <div class="enemy-bar-wrap">
        <div class="enemy-bar" style="width:${percent}%"></div>
      </div>
    `;

    grid.appendChild(card);
  });

  area.innerHTML = "";
  area.appendChild(grid);
}

/* ===== Pセクション：メインパネル切り替え ===== */
function renderMainPanel(data) {
  const panel = document.getElementById("mainPanel");
  const status = document.getElementById("actionStatus");

  const me = data.players.find(p => p.name === myName);
  const meAlive = me && me.hp > 0;

  status.innerText = "";

  if (isPlayingEvent) {
    status.innerText = "戦闘中...";
    return;
  }

  if (data.phase === "end") {
    actionSubmitted = false;
    selectingTarget = null;
    if (data.host_name === myName) {
      panel.innerHTML = `
        <div class="actions">
          <button class="rematch-btn" onclick="rematch()">再戦</button>
          <button class="end-btn" onclick="finishBattle()">ロビーに戻る</button>
        </div>
      `;
    } else {
      panel.innerText = "最初の参加者の選択待ち";
    }

    return;
  }

  if (!meAlive) {
    panel.innerText = "仲間の行動を見守ろう";
    status.innerText = "あなたは倒れています";
    return;
  }

  const serverActionSubmitted = hasMyActionOnServer(data);

  // ===== 待機表示はサーバーに自分の行動が残っている時だけ優先する =====
  // actionSubmitted は押した直後の一時表示用。サーバーで行動が消えていたら解除する。
  if (serverActionSubmitted) {
    panel.innerText = "全員の行動を待っています";
    status.innerText = "行動済み";
    return;
  }

  if (actionSubmitted && isPlayingEvent) {
    panel.innerText = "全員の行動を待っています";
    status.innerText = "行動済み";
    return;
  }

  if (actionSubmitted && !serverActionSubmitted) {
    actionSubmitted = false;
  }

  if (selectingWeaponAction) {
    showWeaponSelect(selectingWeaponAction);
    return;
  }

  if (selectingShieldAction) {
    showShieldSelect();
    return;
  }

  if (selectingSkillAction) {
    showSkillSelect();
    return;
  }

  if (selectingTarget === "enemy_attack" || selectingTarget === "skill_enemy_attack") {
    panel.innerHTML = `
      <div>
        攻撃対象を選択してください<br>
        <button class="cancel-btn" onclick="cancelTargetSelect()">キャンセル</button>
      </div>
    `;

    status.innerText = selectingTarget === "skill_enemy_attack" ? "魔法を当てたい敵の絵をタップしてください" : "攻撃したい敵の絵をタップしてください";
    return;
  }

  if (selectingTarget === "heal") {
    panel.innerHTML = `
      <div>
        回復対象を選択してください<br>
        <button class="cancel-btn" onclick="cancelTargetSelect()">キャンセル</button>
      </div>
    `;
    status.innerText = "回復したいメンバーの枠をタップしてください";
    renderPlayers(data.players, false);
    return;
  }

  if (selectingTarget === "guard") {
    panel.innerHTML = `
      <div>
        対象を選択してください<br>
        <button class="cancel-btn" onclick="cancelTargetSelect()">キャンセル</button>
      </div>
    `;
    status.innerText = "対象の枠をタップしてください";
    renderPlayers(data.players, false);
    return;
  }

  let buttonsHtml = "";

  if (me.job === "勇者") {
    buttonsHtml = `
      <button class="attack-btn" onclick="showWeaponSelect('attack')">攻撃</button>
      <button class="heal-btn" onclick="startHealSelect()">選択回復</button>
      <button class="heal-btn" onclick="sendAction('heal_all')">全体回復</button>
    `;
  } else if (me.job === "タンク") {
    buttonsHtml = `
      <button class="attack-btn" onclick="showWeaponSelect('attack')">攻撃</button>
      <button class="guard-btn" onclick="showShieldSelect()">シールド（挑発）</button>
      <button class="heal-btn" onclick="startHealSelect()">選択回復</button>
    `;
  } else if (me.job === "魔術師") {
    buttonsHtml = `
      <button class="attack-btn" onclick="showSkillSelect()">魔法</button>
      <button class="heal-btn" onclick="startHealSelect()">選択回復</button>
      <button class="heal-btn" onclick="sendAction('heal_all')">全体回復</button>
      <button class="guard-btn" onclick="sendAction('magic_defense')">魔法防御</button>
    `;
  } else {
    buttonsHtml = `
      <button class="attack-btn" onclick="showWeaponSelect('attack')">攻撃</button>
    `;
  }

  panel.innerHTML = `
    <div class="actions">
      ${buttonsHtml}
    </div>
  `;

  status.innerText = "行動を選択してください";
}

/* ===== Qセクション：対象選択処理 ===== */
function startHealSelect() {
  unlockSounds();
  startBattleBgm();

  if (isPlayingEvent) return;

  selectingWeaponAction = null;
  selectedWeaponId = "";
  selectingTarget = "heal";

  const players =
    lastBattleData && lastBattleData.players
      ? lastBattleData.players
      : lastPlayers;

  renderPlayers(players, false);

  document.getElementById("mainPanel").innerHTML = `
    <div>
      回復対象を選択してください<br>
      <button class="cancel-btn" onclick="cancelTargetSelect()">キャンセル</button>
    </div>
  `;

  document.getElementById("actionStatus").innerText =
    "回復したいメンバーの枠をタップしてください";
}

function startGuardSelect() {
  unlockSounds();
  startBattleBgm();

  if (isPlayingEvent) return;

  selectingTarget = "guard";
  renderPlayers(lastPlayers, false);

  document.getElementById("mainPanel").innerHTML = `
    <div>
      対象を選択してください<br>
      <button class="cancel-btn" onclick="cancelTargetSelect()">キャンセル</button>
    </div>
  `;

  document.getElementById("actionStatus").innerText =
    "対象の枠をタップしてください";
}

function cancelTargetSelect() {
  selectingTarget = null;
  selectedEnemyTarget = null;
  selectedWeaponId = "";
  selectedShieldId = "";
  selectedSkillId = "";
  selectingWeaponAction = null;
  selectingShieldAction = false;
  selectingSkillAction = false;

  if (lastBattleData) {
    renderMainPanel(lastBattleData);
  }
}



/* ===== Q-2セクション：攻撃時の武器選択 ===== */
function showWeaponSelect(actionType) {
  unlockSounds();
  startBattleBgm();

  if (isPlayingEvent) return;

  selectingTarget = null;
  selectingWeaponAction = actionType;

  const panel = document.getElementById("mainPanel");
  const status = document.getElementById("actionStatus");

  const myPlayer =
    lastBattleData && lastBattleData.players
      ? lastBattleData.players.find(p => p.name === myName)
      : null;

  const weapons =
    myPlayer && myPlayer.carried_weapons
      ? myPlayer.carried_weapons
      : [];

  let buttonsHtml = "";

  if (weapons.length === 0) {
    buttonsHtml += `
      <button type="button" class="cancel-btn" style="width:100%; min-width:0;"
        onclick="selectWeaponForAction('${actionType}', '')">
        武器なし
      </button>
    `;
  } else {
    weapons.forEach(w => {
      buttonsHtml += `
        <button type="button" class="attack-btn" style="width:100%; min-width:0;"
          onclick="selectWeaponForAction('${actionType}', '${w.id}')">
          ${w.name}
        </button>
      `;
    });
  }

  panel.innerHTML = `
    <div style="width:100%; display:flex; flex-direction:column; gap:12px; align-items:stretch;">
      <div style="margin-bottom:4px; color:#ffd54f; font-weight:bold; font-size:18px; text-align:center;">
        使用武器を選択してください
      </div>

      ${buttonsHtml}

      <button type="button" class="guard-btn" style="width:100%; min-width:0;" onclick="cancelWeaponSelect()">
        戻る
      </button>
    </div>
  `;

  status.innerText = "今回の攻撃に使う武器を選択してください";
}

function selectWeaponForAction(actionType, weaponId) {
  selectedWeaponId = weaponId || "";
  selectingWeaponAction = null;

  // ===== テンペストは全体攻撃なので敵選択なし =====
  if (actionType === "attack" && selectedWeaponId === "tempest") {
    selectedEnemyTarget = "";
    selectingTarget = null;
    document.getElementById("mainPanel").innerText = "行動を送信中...";
    document.getElementById("actionStatus").innerText = "テンペストを送信しています";
    sendAction("attack");
    return;
  }

  if (actionType === "attack") {
    startEnemyAttackSelect();
    return;
  }

  sendAction(actionType);
}

function cancelWeaponSelect() {
  selectedWeaponId = "";
  selectingWeaponAction = null;
  selectingTarget = null;

  if (lastBattleData) {
    renderMainPanel(lastBattleData);
  }
}



/* ===== Q-4セクション：魔術師の魔法選択 ===== */
function showSkillSelect() {
  unlockSounds();
  startBattleBgm();

  if (isPlayingEvent) return;

  selectingTarget = null;
  selectingWeaponAction = null;
  selectingShieldAction = false;
  // ===== 魔法選択中フラグをONにして、定期更新で通常ボタンに戻らないようにする =====
  selectingSkillAction = true;

  const panel = document.getElementById("mainPanel");
  const status = document.getElementById("actionStatus");

  const myPlayer =
    lastBattleData && lastBattleData.players
      ? lastBattleData.players.find(p => p.name === myName)
      : null;

  const skills =
    myPlayer && myPlayer.carried_skills
      ? myPlayer.carried_skills
      : [];

  let buttonsHtml = "";

  if (skills.length === 0) {
    buttonsHtml = `
      <div style="color:#ccc; line-height:1.6;">
        この戦闘に持ち込んだ魔法がありません。<br>
        ロビー前の魔法選択で最大3つまで選んでください。
      </div>
    `;
  } else {
    skills.forEach(skill => {
      const isSupport = skill.type === "support";
      const buttonClass = isSupport ? "guard-btn" : "attack-btn";
      const detail = makeSkillDetailText(skill);

      buttonsHtml += `
        <button type="button" class="${buttonClass}" style="width:100%; min-width:0; text-align:left;"
          onclick="selectSkillForAction('${skill.id}')">
          ${escapeHtml(skill.name)}<br>
          <span style="font-size:12px; font-weight:normal;">${escapeHtml(detail)}</span>
        </button>
      `;
    });
  }

  panel.innerHTML = `
    <div style="width:100%; display:flex; flex-direction:column; gap:12px; align-items:stretch;">
      <div style="margin-bottom:4px; color:#ce93d8; font-weight:bold; font-size:18px; text-align:center;">
        使用する魔法を選択してください
      </div>

      ${buttonsHtml}

      <button type="button" class="cancel-btn" style="width:100%; min-width:0;" onclick="cancelTargetSelect()">
        戻る
      </button>
    </div>
  `;

  status.innerText = "このターンに使う魔法を選択してください";
}

function makeSkillDetailText(skill) {
  if (!skill) return "";

  if (skill.type === "support") {
    return skill.description || "支援魔法";
  }

  const elementNames = {
    fire: "炎",
    ice: "氷",
    thunder: "雷",
    wind: "風",
    light: "光",
    dark: "闇",
    none: "無"
  };

  const targetText = skill.target_type === "all" ? "敵全体" : "敵単体";
  const elementText = elementNames[skill.element] || skill.element || "無";

  return `${elementText}属性 / ${targetText} / 魔力×7`;
}

function selectSkillForAction(skillId) {
  selectedSkillId = skillId || "";
  selectingSkillAction = false;

  const myPlayer =
    lastBattleData && lastBattleData.players
      ? lastBattleData.players.find(p => p.name === myName)
      : null;

  const skills = myPlayer && myPlayer.carried_skills ? myPlayer.carried_skills : [];
  const skill = skills.find(s => s.id === selectedSkillId);

  if (!skill) {
    alert("この魔法は使用できません");
    selectedSkillId = "";
    return;
  }

  if (skill.type === "support") {
    document.getElementById("mainPanel").innerText = "魔法を送信中...";
    document.getElementById("actionStatus").innerText = `${skill.name}を送信しています`;
    sendAction("skill");
    return;
  }

  if (skill.target_type === "all") {
    selectedEnemyTarget = "";
    selectingTarget = null;
    document.getElementById("mainPanel").innerText = "魔法を送信中...";
    document.getElementById("actionStatus").innerText = `${skill.name}を送信しています`;
    sendAction("skill");
    return;
  }

  startSkillEnemySelect();
}

function startSkillEnemySelect() {
  if (isPlayingEvent) return;

  const enemies =
    lastBattleData && lastBattleData.enemies
      ? lastBattleData.enemies.filter(e => e.hp > 0)
      : [];

  if (enemies.length <= 1) {
    if (enemies.length === 1) {
      selectedEnemyTarget = enemies[0].id;
    }

    document.getElementById("mainPanel").innerText = "魔法を送信中...";
    document.getElementById("actionStatus").innerText = "魔法を送信しています";
    sendAction("skill");
    return;
  }

  selectingTarget = "skill_enemy_attack";
  selectedEnemyTarget = null;

  document.getElementById("mainPanel").innerHTML = `
    <div>
      魔法の対象を選択してください<br>
      <button class="cancel-btn" onclick="cancelTargetSelect()">キャンセル</button>
    </div>
  `;

  document.getElementById("actionStatus").innerText = "魔法を当てたい敵の絵をタップしてください";
}


/* ===== R-0セクション：チャット処理 ===== */
function escapeHtml(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function renderChat(messages, data) {
  const chatBox = document.getElementById("chatBox");
  const chatInput = document.getElementById("chatInput");
  const chatSendBtn = document.getElementById("chatSendBtn");
  const chatNote = document.getElementById("chatNote");

  if (!chatBox || !chatInput || !chatSendBtn || !chatNote) return;

  const latest = messages.slice(-8);

  chatBox.innerHTML = latest.map(m => `
    <div class="chat-message">
      <span class="chat-name">${escapeHtml(m.name)}：</span>
      <span>${escapeHtml(m.message)}</span>
    </div>
  `).join("");

  const newestId = messages.length > 0 ? messages[messages.length - 1].id : -1;

  if (newestId !== lastChatId) {
    lastChatId = newestId;
    chatBox.scrollTop = chatBox.scrollHeight;
  }

  // ===== 戦闘中・演出中・勝敗後もチャット可能 =====
  const canChat =
    data.phase !== "waiting";

  chatInput.disabled = !canChat;
  chatSendBtn.disabled = !canChat;

  if (canChat) {
    chatNote.innerText = "チャットできます。";
  } else {
    chatNote.innerText = "戦闘開始待ちです。";
  }
}

async function sendChat() {
  const chatInput = document.getElementById("chatInput");

  if (!chatInput) return;

  const message = chatInput.value.trim();

  if (!message) return;

  const fd = new FormData();
  fd.append("name", myName);
  fd.append("room_id", roomId);
  fd.append("message", message);

  const res = await fetch("/send_chat", {
    method: "POST",
    body: fd
  });

  const data = await res.json();

  if (data.ok) {
    chatInput.value = "";
    update();
  } else if (data.message) {
    alert(data.message);
  }
}

document.addEventListener("keydown", event => {
  if (event.key !== "Enter") return;

  const chatInput = document.getElementById("chatInput");

  if (document.activeElement === chatInput) {
    event.preventDefault();
    sendChat();
  }
});


/* ===== Rセクション：API通信 ===== */
function startEnemyAttackSelect() {
  unlockSounds();
  startBattleBgm();

  if (isPlayingEvent) return;

  // ===== 魔術師の魔法攻撃では武器を使わない =====
  const myPlayerForAttack =
    lastBattleData && lastBattleData.players
      ? lastBattleData.players.find(p => p.name === myName)
      : null;

  if (myPlayerForAttack && myPlayerForAttack.job === "魔術師") {
    selectedWeaponId = "";
    selectingWeaponAction = null;
  }

  selectingWeaponAction = null;

  const enemies =
    lastBattleData && lastBattleData.enemies
      ? lastBattleData.enemies.filter(e => e.hp > 0)
      : [];

  // ===== 敵が1体だけなら自動で攻撃 =====
  if (enemies.length <= 1) {
    if (enemies.length === 1) {
      selectedEnemyTarget = enemies[0].id;
    }

    document.getElementById("mainPanel").innerText = "行動を送信中...";
    document.getElementById("actionStatus").innerText = "攻撃を送信しています";
    sendAction("attack");
    return;
  }

  // ===== 敵が複数なら対象選択 =====
  selectingTarget = "enemy_attack";
  selectedEnemyTarget = null;

  const panel = document.getElementById("mainPanel");
  const status = document.getElementById("actionStatus");

  panel.innerHTML = `
    <div>
      攻撃対象を選択してください<br>
      <button class="cancel-btn" onclick="cancelTargetSelect()">キャンセル</button>
    </div>
  `;

  status.innerText = "攻撃したい敵の絵をタップしてください";
}

function selectEnemyTarget(enemyId) {
  if (selectingTarget !== "enemy_attack" && selectingTarget !== "skill_enemy_attack") return;

  const actionType = selectingTarget === "skill_enemy_attack" ? "skill" : "attack";
  selectedEnemyTarget = enemyId;
  sendAction(actionType);
}

async function sendAction(type, target=null) {
  unlockSounds();
  startBattleBgm();

  if (isPlayingEvent) return;

  const fd = new FormData();
  fd.append("name", myName);
  fd.append("room_id", roomId);
  fd.append("action", type);

  if (target) {
    fd.append("target", target);
  }

  if ((type === "attack" || type === "skill") && selectedEnemyTarget) {
    fd.append("enemy_target", selectedEnemyTarget);
  }

  if (type === "attack") {
    fd.append("weapon_id", selectedWeaponId || "");
  }

  if (type === "shield") {
    fd.append("shield_id", selectedShieldId || "");
  }

  if (type === "skill") {
    fd.append("skill_id", selectedSkillId || "");
  }

  try {
    const res = await fetch("/action", { method: "POST", body: fd });
    const data = await res.json();

    if (data.ok) {
      actionSubmitted = true;
      selectingTarget = null;
      selectingWeaponAction = null;
      selectingShieldAction = false;
    selectingSkillAction = false;
      selectedEnemyTarget = null;
      selectedWeaponId = "";
      selectedShieldId = "";
      selectedSkillId = "";
      lastEnemiesRenderKey = "";
      defeatedEnemyIds.clear();

      document.getElementById("mainPanel").innerText = "全員の行動を待っています";
      document.getElementById("actionStatus").innerText = "行動済み";

      update();
    } else if (data.message) {
      alert(data.message);
    } else {
      alert("行動送信に失敗しました");
    }
  } catch (e) {
    alert("通信エラーで行動を送信できませんでした");
  }
}

async function rematch() {
  unlockSounds();

  rematchInProgress = true;

  // 勝利・敗北BGMを確実に停止
  victoryBgm.pause();
  victoryBgm.currentTime = 0;

  defeatBgm.pause();
  defeatBgm.currentTime = 0;

  battleBgm.pause();
  battleBgm.currentTime = 0;

  const fd = new FormData();
  fd.append("name", myName);
  fd.append("room_id", roomId);

  const res = await fetch("/rematch", { method: "POST", body: fd });
  const data = await res.json();

  if (data.ok) {
    battleEnded = false;
    victoryPlayed = false;
    actionSubmitted = false;
    selectingTarget = null;

    clearDamageFlash();
    clearBossFlash();

    // 再戦時は戦闘BGMを最初から流す
    battleBgm.currentTime = 0;
    battleBgm.play().catch(() => {});

    lastEventId = -1;
    lastTurn = 0;
    previousPhase = null;
    lastEnemiesRenderKey = "";
    defeatedEnemyIds.clear();

    update();

  } else {
    rematchInProgress = false;

    if (data.message) {
      alert(data.message);
    }
  }
}

async function finishBattle() {
  unlockSounds();
  stopAllMusic();

  const fd = new FormData();
  fd.append("name", myName);
  fd.append("room_id", roomId);

  const res = await fetch("/finish_battle", { method: "POST", body: fd });
  const data = await res.json();

  if (data.ok) {
    // ===== サーバー側で waiting に戻ったことを、通常の定期更新処理で検知させる =====
    // これにより、押した本人も他メンバーと同じ経路でロビーへ戻る。
    update();
  } else if (data.message) {
    alert(data.message);
  }
}


/* ===== R-2セクション：投票退出処理 ===== */
function renderKickVote(data) {
  const area = document.getElementById("kickVoteArea");
  if (!area) return;

  const players = data.players || [];
  const kickVotes = data.kick_votes || {};

  if (players.length < 3) {
    area.innerHTML = `<div style="color:#ccc; font-size:13px;">3人以上のときに使用できます。</div>`;
    return;
  }

  const myActiveTarget = kickVotes[myName] || "";

  area.innerHTML = `
    <div class="kick-vote-status">
      追放したい相手をONにしてください。もう一度押すとOFFになります。<br>
      対象者以外の全員が同じ人をONにすると追放されます。
    </div>
  `;

  players.forEach(p => {
    if (p.name === myName) return;

    const targetName = p.name;
    const isOn = myActiveTarget === targetName;

    const btn = document.createElement("button");
    btn.className = "kick-member-btn" + (isOn ? " kick-on" : "");
    btn.type = "button";
    btn.innerText = `${isOn ? "ON：" : "OFF："}${targetName}を退出`;
    btn.onclick = () => voteKick(targetName);

    area.appendChild(btn);
  });
}

async function voteKick(targetName) {
  const fd = new FormData();
  fd.append("voter", myName);
  fd.append("room_id", roomId);
  fd.append("target", targetName);

  try {
    const res = await fetch("/vote_kick", {
      method: "POST",
      body: fd
    });

    const data = await res.json();

    if (!data.ok && data.message) {
      alert(data.message);
      return;
    }

    update();
  } catch (e) {
    alert("通信エラーで投票を送信できませんでした");
  }
}


async function leaveParty() {
  if (!confirm("パーティーから退出しますか？")) return;

  leavingBattle = true;
  stopAllMusic();

  const fd = new FormData();
  fd.append("name", myName);
  fd.append("room_id", roomId);

  const res = await fetch("/leave_party", {
    method: "POST",
    body: fd
  });

  const data = await res.json();

  if (data.ok) {
    location.href = "/";
  } else if (data.message) {
    alert(data.message);
  }
}

/* ===== Sセクション：定期更新 ===== */
setInterval(update, 500);
setInterval(sendHeartbeat, 5000);
sendHeartbeat();
update();

setTimeout(() => {
  startBattleBgm();
}, 500);


/* ===== Q-3セクション：シールド時の盾選択 ===== */
function showShieldSelect() {
  unlockSounds();
  startBattleBgm();

  if (isPlayingEvent) return;

  selectingTarget = null;
  selectingWeaponAction = null;
  selectingShieldAction = true;

  const panel = document.getElementById("mainPanel");
  const status = document.getElementById("actionStatus");

  const myPlayer =
    lastBattleData && lastBattleData.players
      ? lastBattleData.players.find(p => p.name === myName)
      : null;

  const shields =
    myPlayer && myPlayer.carried_shields
      ? myPlayer.carried_shields
      : [];

  let buttonsHtml = "";

  if (shields.length === 0) {
    buttonsHtml += `
      <button type="button" class="guard-btn" style="width:100%; min-width:0;" onclick="sendShieldAction('')">
        通常シールド
      </button>
    `;
  } else {
    shields.forEach(s => {
      const imagePath = s.image || `/static/images/shields/${s.id}.png`;
      const effectText = s.effect_type || "効果未設定";

      buttonsHtml += `
        <button type="button" class="guard-btn battle-shield-btn" onclick="sendShieldAction('${s.id}')">
          <img class="battle-shield-img" src="${imagePath}" alt="${s.name}" onerror="this.style.display='none';">
          <span>
            <span class="battle-shield-name">${s.name}</span>
            <span class="battle-shield-meta">${effectText}</span>
          </span>
        </button>
      `;
    });
  }

  panel.innerHTML = `
    <div style="width:100%; display:flex; flex-direction:column; gap:12px; align-items:stretch;">
      <div style="margin-bottom:4px; color:#81d4fa; font-weight:bold; font-size:18px; text-align:center;">
        使用する盾を選択してください
      </div>

      ${buttonsHtml}

      <button type="button" class="cancel-btn" style="width:100%; min-width:0;" onclick="cancelTargetSelect()">
        戻る
      </button>
    </div>
  `;

  status.innerText = "このターンに使う盾を選択してください";
}

function sendShieldAction(shieldId) {
  selectedShieldId = shieldId || "";
  selectingShieldAction = false;
  sendAction("shield");
}
