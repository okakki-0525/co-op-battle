# ==================================================
# Aセクション：初期設定・外部データ読み込み
# ==================================================

from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import random
import time
import json
import os
import hashlib
import copy
import uuid
import threading
from battle_engine import configure_battle_engine, process_turn

try:
    from enemy_ai import (
        process_volcano_dragon_action as enemy_ai_process_volcano_dragon_action,
        process_training_golem_action as enemy_ai_process_training_golem_action,
        process_goblin_action as enemy_ai_process_goblin_action
    )
except Exception:
    enemy_ai_process_volcano_dragon_action = None
    enemy_ai_process_training_golem_action = None
    enemy_ai_process_goblin_action = None

try:
    from weapons import WEAPONS, get_weapons_for_job, get_weapon
except Exception:
    WEAPONS = {
        "flame_sword": {
            "name": "炎剣",
            "description": "炎の力を宿した剣。",
            "attack_bonus": 20,
            "allowed_jobs": ["勇者", "タンク"],
            "image": "/static/images/weapons/flame_sword.png",
            "resist": {
                "fire_single": 0.70,
                "fire_all": 0.50
            }
        }
    }

    def get_weapon(weapon_id):
        return WEAPONS.get(weapon_id)

    def get_weapons_for_job(job):
        return {
            weapon_id: weapon
            for weapon_id, weapon in WEAPONS.items()
            if job in weapon.get("allowed_jobs", [])
        }


try:
    from skills import SKILLS, get_skill, get_skills_for_job, get_skill_display_name
except Exception:
    SKILLS = {
        "ice_arrow": {
            "name": "アイスアロー",
            "job": "魔術師",
            "type": "attack",
            "element": "ice",
            "target_type": "single",
            "power_stat": "magic",
            "power_rate": 1.0,
            "battle_text": "アイスアロー！"
        }
    }

    def get_skill(skill_id):
        return SKILLS.get(skill_id)

    def get_skills_for_job(job):
        return {
            skill_id: skill
            for skill_id, skill in SKILLS.items()
            if skill.get("job") == job
        }

    def get_skill_display_name(skill_id):
        skill = get_skill(skill_id)
        if skill:
            return skill.get("name", "スキル")
        return "スキル"


try:
    from shields import SHIELDS, get_shield, get_shields_for_job, get_shield_display_name
except Exception:
    # ===== shields.py が見つからない時の保険データ =====
    SHIELDS = {
        "flame_shield": {
            "name": "フレイムシールド",
            "element": "fire",
            "effect_type": "element_guard",
            "target_scope": "party",
            "cut_rate": 0.80,
            "description": "火属性ダメージを8割軽減する盾。"
        },

        "ice_shield": {
            "name": "アイスシールド",
            "element": "ice",
            "effect_type": "element_guard",
            "target_scope": "party",
            "cut_rate": 0.80,
            "description": "氷属性ダメージを8割軽減する盾。"
        },

        "thunder_shield": {
            "name": "サンダーシールド",
            "element": "thunder",
            "effect_type": "element_guard",
            "target_scope": "party",
            "cut_rate": 0.80,
            "description": "雷属性ダメージを8割軽減する盾。"
        },

        "holy_shield": {
            "name": "ホーリーシールド",
            "element": "light",
            "effect_type": "element_guard",
            "target_scope": "party",
            "cut_rate": 0.80,
            "description": "光属性ダメージを8割軽減する盾。"
        },

        "dark_shield": {
            "name": "ダークシールド",
            "element": "dark",
            "effect_type": "element_guard",
            "target_scope": "party",
            "cut_rate": 0.80,
            "description": "闇属性ダメージを8割軽減する盾。"
        },

        "attack_shield": {
            "name": "アタックシールド",
            "element": "none",
            "effect_type": "physical_counter",
            "target_scope": "self",
            "counter_type": "physical",
            "description": "物理攻撃に対して反撃する盾。"
        },

        "magic_shield": {
            "name": "マジックシールド",
            "element": "all_magic",
            "effect_type": "magic_guard",
            "target_scope": "party",
            "cut_rate": 0.40,
            "description": "全属性魔法ダメージを4割軽減する盾。"
        },

        "auto_shield": {
            "name": "オートシールド",
            "element": "none",
            "effect_type": "physical_avoid",
            "target_scope": "party",
            "avoid_rate": 1.00,
            "description": "パーティ全員への物理攻撃を100％回避する盾。"
        },

        "guardian_shield": {
            "name": "ガーディアンシールド",
            "element": "none",
            "effect_type": "magic_counter",
            "target_scope": "party",
            "counter_type": "magic",
            "description": "魔法攻撃に対して反撃する盾。全体攻撃には全体反撃、単体攻撃には単体反撃。"
        },

        "counter_shield": {
            "name": "カウンターシールド",
            "element": "none",
            "effect_type": "hit_counter",
            "target_scope": "self",
            "description": "被弾回数に応じて反撃する盾。"
        }
    }

    def get_shield(shield_id):
        return SHIELDS.get(shield_id)

    def get_shields_for_job(job):
        if job != "タンク":
            return {}
        return SHIELDS

    def get_shield_display_name(shield_id):
        shield = get_shield(shield_id)
        if shield:
            return shield.get("name", "盾")
        return "盾"



try:
    from enemies import ENEMIES
except Exception:
    # ===== enemies.py が見つからない時の保険データ =====
    ENEMIES = {
        "volcano_dragon": {
            "name": "ボルケーノドラゴン",
            "max_hp": 1000,
            "image": "/static/images/vdragon.png",
            "role": "boss",
            "weakness": ["ice"],
            "resist": ["fire"],
            "skills": [
                {"name": "ひっかき", "rate": 70, "target": "single", "category": "physical", "element": "none", "damage": [28, 55]},
                {"name": "全体ブレス", "rate": 30, "target": "all", "category": "magic", "element": "fire", "damage": [30, 58]}
            ]
        },
        "goblin_fighter": {
            "name": "ゴブリンファイター",
            "max_hp": 350,
            "image": "/static/images/goblin_fighter.png",
            "role": "fighter",
            "weakness": [],
            "resist": [],
            "skills": [
                {"name": "斬りつけ", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [20, 35]}
            ]
        },
        "goblin_mage": {
            "name": "ゴブリンメイジ",
            "max_hp": 150,
            "image": "/static/images/goblin_mage.png",
            "role": "mage",
            "weakness": ["light"],
            "resist": ["dark"],
            "skills": [
                {"name": "闇魔法", "rate": 100, "target": "all", "category": "magic", "element": "dark", "damage": [14, 26]}
            ]
        },
        "goblin_healer": {
            "name": "ゴブリンヒーラー",
            "max_hp": 200,
            "image": "/static/images/goblin_healer.png",
            "role": "healer",
            "weakness": [],
            "resist": [],
            "skills": [
                {"name": "杖攻撃", "rate": 70, "target": "single", "category": "physical", "element": "none", "damage": [8, 16]},
                {"name": "回復", "rate": 30, "target": "ally_heal", "category": "heal", "element": "none", "heal": [22, 38]}
            ]
        },
        "training_golem": {
            "name": "訓練用ゴーレム",
            "max_hp": 200,
            "image": "/static/images/training_golem.png",
            "role": "training_golem",
            "weakness": ["thunder"],
            "resist": [],
            "skills": [
                {"name": "打撃", "rate": 80, "target": "single", "category": "physical", "element": "none", "damage": [12, 24]},
                {"name": "重い一撃", "rate": 20, "target": "single", "category": "physical", "element": "none", "damage": [25, 38]}
            ]
        }
    }

app = Flask(__name__)
app.secret_key = "battle_game_secret_key_change_later"

# ==================================================
# A-1セクション：リクエスト直列化・基本定数
# ==================================================
# 複数部屋対応では、処理中だけ players / game_state を対象部屋に切り替える。
# ブラウザ複数タブの同時ポーリングで部屋コンテキストが混線しないよう、
# 1リクエストずつ順番に処理する。
REQUEST_LOCK = threading.RLock()
_original_wsgi_app = app.wsgi_app

def locked_wsgi_app(environ, start_response):
    with REQUEST_LOCK:
        return _original_wsgi_app(environ, start_response)

app.wsgi_app = locked_wsgi_app

MAX_PLAYERS = 6
BOSS_MAX_HP = 1000
OFFLINE_LIMIT_SECONDS = 15
EMPTY_ROOM_RESET_SECONDS = 30
KICK_BLOCK_SECONDS = 60 * 60
PLAYER_DATA_FILE = "players_data.json"
EMPTY_WAITING_ROOM_KEEP_SECONDS = 10 * 60

#
# ==================================================
# A-7セクション：Supabase接続設定
# ==================================================

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "").strip()
supabase = None

if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase接続準備OK")
    except Exception as e:
        supabase = None
        print("Supabase接続準備失敗:", e)
else:
    print("Supabase環境変数なし。players_data.jsonを使用します。")


def is_supabase_enabled():
    return supabase is not None

# ==================================================
# A-2セクション：初期装備・開発者用所持設定
# ==================================================
# 通常プレイヤーは、初期装備だけを所持して開始する。
# レイド報酬装備は、将来的に勝利アイテムとして追加する想定。
INITIAL_WEAPON_IDS_BY_JOB = {
    "勇者": ["long_sword"],
    "タンク": ["great_sword"],
    "魔術師": []
}

INITIAL_SHIELD_IDS_BY_JOB = {
    "勇者": [],
    "タンク": ["iron_shield"],
    "魔術師": []
}

INITIAL_SKILL_IDS = ["light_bolt"]

# ===== 開発者テスト用：最初から全装備・全魔法を所持するプレイヤー =====
DEVELOPER_FULL_INVENTORY_PLAYERS = {
    "おかっきー",
    "アドミニ１",
    "アドミニ２",
    "アドミニ３"
}

# ==================================================
# A-3セクション：敵部屋データ
# ==================================================

ROOMS = {
    "volcano": {
        "name": "双竜レイド",
        "type": "raid",
        "enemies": [
            {"id": "volcano_dragon"},
            {"id": "tempest_dragon"}
        ]
    },
    "training_golem": {
        "name": "訓練用ゴーレム（敵１体戦）",
        "type": "single",
        "enemies": [
            {"id": "training_golem"}
        ]
    },
    "random_zako_1": {
        "name": "敵１体戦",
        "type": "random_zako",
        "random_count": 1,
        "enemies": []
    },
    "random_zako_2": {
        "name": "敵２体戦",
        "type": "random_zako",
        "random_count": 2,
        "enemies": []
    },
    "random_zako_3": {
        "name": "敵３体戦",
        "type": "random_zako",
        "random_count": 3,
        "enemies": []
    },
    "random_zako_4": {
        "name": "敵４体戦",
        "type": "random_zako",
        "random_count": 4,
        "enemies": []
    }
}



# ==================================================
# A-4セクション：ランダム雑魚戦用プール
# ==================================================
# ボルケーノドラゴンは看板ボスとして独立運用するため、このプールには入れない。
# ==================================================
# A-4セクション：ランダム雑魚戦用プール
# ==================================================

RANDOM_ZAKO_ENEMY_IDS = [
    "slime",
    "goblin",
    "orc",
    "ice_wolf",
    "thunder_bird",
    "wind_fairy",
    "holy_slime",
    "shadow_bat",
    "fire_lizard",
    "stone_beetle",
    "goblin_fighter",
    "goblin_mage",
    "goblin_healer",
    "training_golem",

    "kobold",
    "kobold_archer",
    "harpy",
    "minotaur",
    "treant",
    "gargoyle",
    "skeleton",
    "skeleton_knight",
    "ghost",
    "lich",

    "goblin_archer",
    "dark_scout",
    "bomb_slime",
    "imp",
    "skeleton_mage",
    "kobold_thief",
    "blood_bat",
    "shadow",
    "poison_mushroom",
    "curse_doll",

    "dark_priest",
    "flame_witch",
    "ice_sorcerer",
    "thunder_shaman",
    "wind_oracle",
    "blood_vampire",
    "hell_hound",
    "death_knight",
    "chaos_eye",
    "demon_lord"
]

def build_random_zako_enemy_refs(count):
    # ===== 雑魚敵プールから指定数だけランダムに選ぶ =====
    usable_enemy_ids = [
        enemy_id
        for enemy_id in RANDOM_ZAKO_ENEMY_IDS
        if enemy_id in ENEMIES and enemy_id != "volcano_dragon"
    ]

    if not usable_enemy_ids:
        return []

    count = max(1, min(int(count), len(usable_enemy_ids)))
    selected_enemy_ids = random.sample(usable_enemy_ids, count)

    return [
        {"id": enemy_id}
        for enemy_id in selected_enemy_ids
    ]

def get_enemy_master(enemy_id):
    # ===== enemies.py の敵データを取得 =====
    return ENEMIES.get(enemy_id, {})

# ==================================================
# A-5セクション：基本ゲーム状態
# ==================================================

players = []
kicked_devices = {}

game_state = {
    "started": False,
    "phase": "waiting",   # waiting / choice / end
    "turn": 1,
    "actions": {},
    "kick_votes": {},
    "left_players": {},
    "boss_hp": BOSS_MAX_HP,
    "boss_max_hp": BOSS_MAX_HP,
    "host_name": None,
    "starter_name": None,
    "log": ["ロビーで参加者を待っています"],
    "winner": None,
    "growth_applied": False,
    "growth_messages": [],
    "last_actor": None,
    "turn_events": [],
    "event_id": 0,
    "chat_messages": [],
    "chat_id": 0,
    "all_offline_since": None,
    "last_boss_action": None,
    "same_boss_action_count": 0,
    "selected_room": "volcano",
    "selected_enemy_room": "random_zako_1",
    "party_title": "",
    "room_title": "",
    "room_name": "ボルケーノドラゴン",
    "enemies": [],
    "rematch_select": False,
    "rematch_expected_names": [],
    "rematch_room_id": "volcano",
    "party_buffs": {
        "defend_turns": 0,
        "physical_up_turns": 0,
        "magic_boost_turns": 0
    },
    "active_magic_wall": False,
    "active_magic_defense": False,
    "raid_reward_available": False,
    "raid_reward_claims": {}
}



# ==================================================
# A-6セクション：複数部屋管理
# ==================================================
# 既存の戦闘処理は players / game_state を参照する構造のまま残し、
# リクエストごとに「現在操作している部屋」の players / game_state へ差し替える。
# これにより、戦闘処理本体を大きく壊さずに複数部屋へ戻す。
DEFAULT_GAME_STATE_TEMPLATE = copy.deepcopy(game_state)
active_room_id = "main"


def create_default_game_state(room_title="冒険者募集"):
    # ===== 新しい部屋用の game_state を作成 =====
    state = copy.deepcopy(DEFAULT_GAME_STATE_TEMPLATE)
    state["party_title"] = room_title or "冒険者募集"
    state["room_title"] = room_title or "冒険者募集"
    state["log"] = ["ロビーで参加者を待っています"]
    return state


def create_game_room(room_id=None, room_title="冒険者募集", room_password=""):
    # ===== 部屋データ本体 =====
    if not room_id:
        room_id = f"room_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"

    room_password = str(room_password or "").strip()[:20]

    return room_id, {
        "room_id": room_id,
        "players": [],
        "game_state": create_default_game_state(room_title),
        "room_password": room_password,
        "created_at": time.time(),
        "updated_at": time.time()
    }


# ===== 初期部屋。古い単一部屋構造との互換用 =====
GAME_ROOMS = {
    "main": {
        "room_id": "main",
        "players": players,
        "game_state": game_state,
        "created_at": time.time(),
        "updated_at": time.time()
    }
}


def get_request_room_id(default_to_session=True):
    # ===== GET/POST/セッションから room_id を取得 =====
    room_id = (
        request.form.get("room_id", "").strip() or
        request.args.get("room_id", "").strip()
    )

    if not room_id and default_to_session:
        room_id = session.get("current_room_id", "")

    if not room_id:
        room_id = "main"

    return room_id


def switch_room_context(room_id=None, create_if_missing=False, room_title="冒険者募集", save_to_session=True):
    # ===== 現在の処理対象部屋へ players / game_state を切り替える =====
    global players, game_state, active_room_id

    if not room_id:
        room_id = get_request_room_id()

    if room_id not in GAME_ROOMS:
        if not create_if_missing:
            return False

        new_room_id, room = create_game_room(room_id, room_title)
        GAME_ROOMS[new_room_id] = room
        room_id = new_room_id

    room = GAME_ROOMS[room_id]
    players = room["players"]
    game_state = room["game_state"]
    active_room_id = room_id
    room["updated_at"] = time.time()
    if save_to_session:
        session["current_room_id"] = room_id
    return True


def create_new_room(room_title="冒険者募集", room_password=""):
    # ===== 新規部屋を作成して、その部屋へ切り替える =====
    room_id, room = create_game_room(room_title=room_title, room_password=room_password)
    GAME_ROOMS[room_id] = room
    switch_room_context(room_id)
    return room_id


def remove_empty_waiting_rooms():
    # ===== 完全に空の待機部屋を整理。main は互換用なので残す =====
    # 新規作成直後は、キャラクター選択・武器選択の途中でまだ players が0人。
    # ここで即削除すると、別タブの受付ページ自動更新により作成中の部屋が消えてしまう。
    # そのため、空の待機部屋でも一定時間は残す。
    now = time.time()

    for room_id in list(GAME_ROOMS.keys()):
        if room_id == "main":
            continue

        room = GAME_ROOMS.get(room_id)
        if not room:
            continue

        room_players = room.get("players", [])
        room_state = room.get("game_state", {})
        created_at = float(room.get("created_at", now))
        updated_at = float(room.get("updated_at", created_at))
        last_touch = max(created_at, updated_at)

        if (
            len(room_players) == 0 and
            not room_state.get("started", False) and
            now - last_touch >= EMPTY_WAITING_ROOM_KEEP_SECONDS
        ):
            del GAME_ROOMS[room_id]


def get_room_summary(room_id, room):
    # ===== 受付ページ用の部屋概要 =====
    room_players = room.get("players", [])
    room_state = room.get("game_state", {})

    job_counts = {
        "勇者": 0,
        "タンク": 0,
        "魔術師": 0
    }

    for player in room_players:
        job = player.get("job")
        if job in job_counts:
            job_counts[job] += 1

    return {
        "room_id": room_id,
        "title": room_state.get("party_title") or room_state.get("room_title") or "冒険者募集",
        "total": len(room_players),
        "max_players": MAX_PLAYERS,
        "job_counts": job_counts,
        "started": room_state.get("started", False),
        "phase": room_state.get("phase", "waiting"),
        "room_exists": len(room_players) > 0 or room_state.get("started", False),
        "has_password": bool(str(room.get("room_password", "")).strip())
    }


def get_room_summaries():
    # ===== 受付ページに表示する部屋一覧 =====
    remove_empty_waiting_rooms()

    summaries = []

    for room_id, room in GAME_ROOMS.items():
        summary = get_room_summary(room_id, room)

        if summary["room_exists"] or room_id != "main":
            summaries.append(summary)

    summaries.sort(key=lambda item: item.get("room_id", ""))
    return summaries


# ==================================================
# Bセクション：プレイヤーデータ管理
# B-1：ログイン・セーブデータ
# ==================================================

def row_to_player_data(row):
    # ===== Supabaseの1行を、従来のplayers_data.json形式へ戻す =====
    growth = row.get("growth") or {}
    owned_items = row.get("owned_items") or {}

    return {
        "password_hash": row.get("password_hash", ""),
        "display_name": growth.get("display_name", row.get("name", row.get("player_id", ""))),
        "created_at": growth.get("created_at", time.time()),
        "created_at_text": growth.get("created_at_text", ""),
        "last_login": growth.get("last_login", ""),
        "login_count": int(growth.get("login_count", 0)),
        "characters": growth.get("characters", {
            "勇者": {"hp_bonus": 0, "attack_bonus": 0, "magic_bonus": 0, "total_battles": 0, "wins": 0},
            "タンク": {"hp_bonus": 0, "attack_bonus": 0, "magic_bonus": 0, "total_battles": 0, "wins": 0},
            "魔術師": {"hp_bonus": 0, "attack_bonus": 0, "magic_bonus": 0, "total_battles": 0, "wins": 0}
        }),
        "items": owned_items.get("items", []),
        "owned_weapons": owned_items.get("owned_weapons", []),
        "owned_shields": owned_items.get("owned_shields", []),
        "owned_skills": owned_items.get("owned_skills", [])
    }


def player_data_to_row(player_id, player_data):
    # ===== 従来のplayers_data.json形式を、Supabase保存用の1行へ変換 =====
    growth = {
        "display_name": player_data.get("display_name", player_id),
        "created_at": player_data.get("created_at", time.time()),
        "created_at_text": player_data.get("created_at_text", ""),
        "last_login": player_data.get("last_login", ""),
        "login_count": int(player_data.get("login_count", 0)),
        "characters": player_data.get("characters", {})
    }

    owned_items = {
        "items": player_data.get("items", []),
        "owned_weapons": player_data.get("owned_weapons", []),
        "owned_shields": player_data.get("owned_shields", []),
        "owned_skills": player_data.get("owned_skills", [])
    }

    return {
        "player_id": player_id,
        "name": player_data.get("display_name", player_id),
        "password_hash": player_data.get("password_hash", ""),
        "job": "",
        "level": 1,
        "exp": 0,
        "gold": 0,
        "owned_items": owned_items,
        "growth": growth
    }


def load_player_data_from_json():
    if not os.path.exists(PLAYER_DATA_FILE):
        return {}

    try:
        with open(PLAYER_DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_player_data_to_json(data):
    with open(PLAYER_DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_player_data():
    # ===== Supabaseが使える場合はSupabaseから読む。失敗時はjsonへ退避 =====
    if is_supabase_enabled():
        try:
            response = supabase.table("player_growth").select("*").execute()
            rows = response.data or {}

            result = {}

            for row in rows:
                player_id = row.get("player_id", "")
                if not player_id:
                    continue
                result[player_id] = row_to_player_data(row)

            return result

        except Exception as e:
            print("Supabase読込失敗。jsonへ退避:", e)

    return load_player_data_from_json()


def save_player_data(data):
    # ===== Supabaseが使える場合はSupabaseへ保存。失敗時はjsonへ保存 =====
    if is_supabase_enabled():
        try:
            rows = [
                player_data_to_row(player_id, player_data)
                for player_id, player_data in data.items()
            ]

            if rows:
                supabase.table("player_growth").upsert(rows).execute()

            return

        except Exception as e:
            print("Supabase保存失敗。jsonへ退避:", e)

    save_player_data_to_json(data)


def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_new_player_data(player_id, password):
    now_text = time.strftime("%Y-%m-%d %H:%M:%S")

    return {
        "password_hash": hash_password(password),
        "display_name": player_id,
        "created_at": time.time(),
        "created_at_text": now_text,
        "last_login": now_text,
        "login_count": 1,
        "characters": {
            "勇者": {"hp_bonus": 0, "attack_bonus": 0, "magic_bonus": 0, "total_battles": 0, "wins": 0},
            "タンク": {"hp_bonus": 0, "attack_bonus": 0, "magic_bonus": 0, "total_battles": 0, "wins": 0},
            "魔術師": {"hp_bonus": 0, "attack_bonus": 0, "magic_bonus": 0, "total_battles": 0, "wins": 0}
        },
        "items": [],
        "owned_weapons": get_initial_owned_weapons(player_id),
        "owned_shields": get_initial_owned_shields(player_id),
        "owned_skills": get_initial_owned_skills(player_id)
    }


def is_logged_in():
    return bool(session.get("player_id"))


def get_login_player_id():
    return session.get("player_id")

# ==================================================
# B-2セクション：所持品管理（武器・盾・魔法）
# ==================================================

def get_initial_owned_weapons(player_id):
    # ===== 新規アカウントの初期武器 =====
    # 開発者テスト用プレイヤーは、全武器を最初から所持する。
    if player_id in DEVELOPER_FULL_INVENTORY_PLAYERS:
        return list(WEAPONS.keys())

    owned = []

    for weapon_ids in INITIAL_WEAPON_IDS_BY_JOB.values():
        for weapon_id in weapon_ids:
            if weapon_id not in owned:
                owned.append(weapon_id)

    return owned


def get_initial_owned_shields(player_id):
    # ===== 新規アカウントの初期盾 =====
    # 開発者テスト用プレイヤーは、全盾を最初から所持する。
    if player_id in DEVELOPER_FULL_INVENTORY_PLAYERS:
        return list(SHIELDS.keys())

    owned = []

    for shield_ids in INITIAL_SHIELD_IDS_BY_JOB.values():
        for shield_id in shield_ids:
            if shield_id not in owned:
                owned.append(shield_id)

    return owned


def get_initial_owned_skills(player_id):
    # ===== 新規アカウントの初期魔法 =====
    # 開発者テスト用プレイヤーは、全魔法を最初から所持する。
    if player_id in DEVELOPER_FULL_INVENTORY_PLAYERS:
        return list(SKILLS.keys())

    owned = []

    # ===== 従来の初期魔法リスト =====
    for skill_id in INITIAL_SKILL_IDS:
        if skill_id not in owned:
            owned.append(skill_id)

    # ===== skills.py側で obtain_type: initial が付いた魔法も初期所持にする =====
    for skill_id, skill in SKILLS.items():
        if skill.get("obtain_type") != "initial":
            continue

        if skill_id not in owned:
            owned.append(skill_id)

    return owned

def ensure_player_inventory_data(player_id):
    # ===== 既存プレイヤーにも初期装備・初期魔法の所持欄を補完 =====
    data = load_player_data()

    if player_id not in data:
        data[player_id] = create_new_player_data(player_id, "")

    player_data = data[player_id]
    changed = False

    if "owned_weapons" not in player_data:
        player_data["owned_weapons"] = []
        changed = True

    if "owned_shields" not in player_data:
        player_data["owned_shields"] = []
        changed = True

    if "owned_skills" not in player_data:
        player_data["owned_skills"] = []
        changed = True

    for weapon_id in get_initial_owned_weapons(player_id):
        if weapon_id not in player_data["owned_weapons"]:
            player_data["owned_weapons"].append(weapon_id)
            changed = True

    for shield_id in get_initial_owned_shields(player_id):
        if shield_id not in player_data["owned_shields"]:
            player_data["owned_shields"].append(shield_id)
            changed = True

    for skill_id in get_initial_owned_skills(player_id):
        if skill_id not in player_data["owned_skills"]:
            player_data["owned_skills"].append(skill_id)
            changed = True

    if changed:
        save_player_data(data)

    return player_data


def ensure_player_skill_data(player_id):
    # ===== 互換用：魔法所持データだけ返す =====
    return ensure_player_inventory_data(player_id).get("owned_skills", [])

# ==================================================
# B-3セクション：通常戦闘ドロップ報酬
# ==================================================

NORMAL_BATTLE_DROP_RATES = {
    1: 4,
    2: 6,
    3: 8,
    4: 10
}

# ===== テスト用：Trueなら通常戦闘勝利時に必ずドロップ =====
# 本番公開前に False に戻す。
NORMAL_DROP_TEST_MODE = False


def is_normal_battle_room():
    # ===== 通常戦闘（ランダム雑魚戦）かどうか判定 =====
    room_id = game_state.get("selected_room", "")
    room = ROOMS.get(room_id, {})
    return room.get("type") == "random_zako"


def get_normal_battle_enemy_count():
    # ===== 通常戦闘の敵数を取得 =====
    room_id = game_state.get("selected_room", "")
    room = ROOMS.get(room_id, {})

    if room.get("type") == "random_zako":
        return int(room.get("random_count", len(game_state.get("enemies", [])) or 1))

    return len(game_state.get("enemies", []))


def should_drop_normal_battle_reward():
    # ===== 通常戦闘勝利時のドロップ判定 =====
    if not is_normal_battle_room():
        return False

    if NORMAL_DROP_TEST_MODE:
        return True

    enemy_count = get_normal_battle_enemy_count()
    drop_rate = int(NORMAL_BATTLE_DROP_RATES.get(enemy_count, 0))

    if drop_rate <= 0:
        return False

    return random.randint(1, 100) <= drop_rate


def get_normal_drop_candidates_for_player(player_name, job):
    # ===== 戦闘で使ったジョブに応じて、未所持の通常戦闘報酬候補を作る =====
    player_data = ensure_player_inventory_data(player_name)
    candidates = []

    if job == "勇者":
        owned_weapon_ids = set(player_data.get("owned_weapons", []))

        for weapon_id, weapon in WEAPONS.items():
            if weapon.get("obtain_type") != "normal_drop":
                continue

            if job not in weapon.get("allowed_jobs", []):
                continue

            if weapon_id in owned_weapon_ids:
                continue

            candidates.append({
                "kind": "weapon",
                "id": weapon_id,
                "name": weapon.get("name", weapon_id)
            })

    elif job == "タンク":
        owned_weapon_ids = set(player_data.get("owned_weapons", []))
        owned_shield_ids = set(player_data.get("owned_shields", []))

        for weapon_id, weapon in WEAPONS.items():
            if weapon.get("obtain_type") != "normal_drop":
                continue

            if job not in weapon.get("allowed_jobs", []):
                continue

            if weapon_id in owned_weapon_ids:
                continue

            candidates.append({
                "kind": "weapon",
                "id": weapon_id,
                "name": weapon.get("name", weapon_id)
            })

        for shield_id, shield in SHIELDS.items():
            if shield.get("obtain_type") != "normal_drop":
                continue

            if shield_id in owned_shield_ids:
                continue

            candidates.append({
                "kind": "shield",
                "id": shield_id,
                "name": shield.get("name", shield_id)
            })

    elif job == "魔術師":
        owned_skill_ids = set(player_data.get("owned_skills", []))

        for skill_id, skill in SKILLS.items():
            if skill.get("obtain_type") != "normal_drop":
                continue

            if skill.get("job") != job:
                continue

            if skill_id in owned_skill_ids:
                continue

            candidates.append({
                "kind": "skill",
                "id": skill_id,
                "name": skill.get("name", skill_id)
            })

    return candidates


def grant_drop_reward_to_player(player_name, reward):
    # ===== 通常戦闘報酬をplayers_data.jsonへ保存 =====
    if not player_name or not reward:
        return False

    data = load_player_data()

    if player_name not in data:
        data[player_name] = create_new_player_data(player_name, "")

    player_data = data[player_name]
    player_data.setdefault("owned_weapons", [])
    player_data.setdefault("owned_shields", [])
    player_data.setdefault("owned_skills", [])

    reward_kind = reward.get("kind", "")
    reward_id = reward.get("id", "")

    if reward_kind == "weapon":
        if reward_id in player_data["owned_weapons"]:
            return False
        player_data["owned_weapons"].append(reward_id)

    elif reward_kind == "shield":
        if reward_id in player_data["owned_shields"]:
            return False
        player_data["owned_shields"].append(reward_id)

    elif reward_kind == "skill":
        if reward_id in player_data["owned_skills"]:
            return False
        player_data["owned_skills"].append(reward_id)

    else:
        return False

    save_player_data(data)
    return True


def apply_normal_battle_drops_after_victory():
    # ===== 通常戦闘勝利時、パーティ全体で1回だけ抽選し、当選したら全員に自動付与 =====
    if game_state.get("normal_drop_applied"):
        return game_state.get("normal_drop_messages", [])

    game_state["normal_drop_applied"] = True
    messages = []

    if not should_drop_normal_battle_reward():
        game_state["normal_drop_messages"] = messages
        return messages

    messages.append("戦利品を発見した！")

    for player in players:
        player_name = player.get("name", "")
        job = player.get("job", "")

        if not player_name or not job:
            continue

        candidates = get_normal_drop_candidates_for_player(player_name, job)

        if not candidates:
            messages.append(f"{player_name}（{job}）は入手できる通常報酬をすべて持っていた！")
            continue

        reward = random.choice(candidates)
        granted = grant_drop_reward_to_player(player_name, reward)

        if granted:
            messages.append(f"{player_name}は{reward.get('name', reward.get('id', '報酬'))}を手に入れた！")
        else:
            messages.append(f"{player_name}は報酬を受け取れなかった。")

    game_state["normal_drop_messages"] = messages
    return messages


def append_normal_battle_drop_events(events):
    # ===== 通常戦闘ドロップ結果を戦闘イベントへ追加 =====
    drop_messages = apply_normal_battle_drops_after_victory()

    for msg in drop_messages:
        events.append({
            "text": msg,
            "state": snapshot()
        })
        add_log(msg)

    return events


def get_owned_weapon_ids(player_id, job=None):
    # ===== 所持武器のうち、現在ジョブで使えるものだけ返す =====
    player_data = ensure_player_inventory_data(player_id)
    owned_weapon_ids = player_data.get("owned_weapons", [])
    result = []

    for weapon_id in owned_weapon_ids:
        weapon = get_weapon(weapon_id)

        if not weapon:
            continue

        if job and job not in weapon.get("allowed_jobs", []):
            continue

        result.append(weapon_id)

    return result


def get_owned_weapons_for_job(player_id, job):
    # ===== ロビー・装備選択用の所持武器一覧 =====
    return {
        weapon_id: get_weapon(weapon_id)
        for weapon_id in get_owned_weapon_ids(player_id, job)
        if get_weapon(weapon_id)
    }


def get_owned_shield_ids(player_id, job=None):
    # ===== 所持盾のうち、現在ジョブで使えるものだけ返す =====
    if job and job != "タンク":
        return []

    player_data = ensure_player_inventory_data(player_id)
    owned_shield_ids = player_data.get("owned_shields", [])
    result = []

    for shield_id in owned_shield_ids:
        shield = get_shield(shield_id)

        if not shield:
            continue

        result.append(shield_id)

    return result


def get_owned_shields_for_job(player_id, job):
    # ===== ロビー・装備選択用の所持盾一覧 =====
    if job != "タンク":
        return {}

    return {
        shield_id: get_shield(shield_id)
        for shield_id in get_owned_shield_ids(player_id, job)
        if get_shield(shield_id)
    }


def get_owned_skill_ids(player_id, job=None):
    # ===== 所持スキルのうち、現在ジョブで使えるものだけ返す =====
    # 開発者テスト用プレイヤーは、players_data.json の保存内容に関係なく全魔法を使える。
    if player_id in DEVELOPER_FULL_INVENTORY_PLAYERS:
        owned_skill_ids = list(SKILLS.keys())
    else:
        owned_skill_ids = ensure_player_skill_data(player_id)

    result = []

    for skill_id in owned_skill_ids:
        skill = get_skill(skill_id)

        if not skill:
            continue

        if job and skill.get("job") != job:
            continue

        result.append(skill_id)

    return result

def build_owned_skill_list(player_id, job):
    # ===== 戦闘画面へ渡す所持魔法リスト =====
    result = []

    for skill_id in get_owned_skill_ids(player_id, job):
        skill = get_skill(skill_id)

        if not skill:
            continue

        result.append({
            "id": skill_id,
            "name": skill.get("name", skill_id),
            "type": skill.get("type", "attack"),
            "element": skill.get("element", "none"),
            "target_type": skill.get("target_type", "single"),
            "power_rate": skill.get("power_rate", 1.0),
            "effect_type": skill.get("effect_type", ""),
            "description": skill.get("description", "")
        })

    return result


def clean_skill_ids_for_job(player_id, job, skill_ids=None):
    # ===== 所持魔法の中から、現在ジョブで使えるものだけ最大3つに整理 =====
    if job != "魔術師":
        return []

    owned_skill_ids = get_owned_skill_ids(player_id, job)
    skill_ids = skill_ids or []

    if isinstance(skill_ids, str):
        skill_ids = [
            skill_id.strip()
            for skill_id in skill_ids.split(",")
            if skill_id.strip()
        ]

    cleaned_skill_ids = []

    for skill_id in skill_ids:
        if skill_id in owned_skill_ids and skill_id not in cleaned_skill_ids:
            cleaned_skill_ids.append(skill_id)

    return cleaned_skill_ids[:3]


def build_carried_skill_ids_for_job(player_id, job, current_skill_ids=None):
    # ===== 魔術師だけ、所持魔法から最大3つ持ち込む =====
    if job != "魔術師":
        return []

    cleaned_skill_ids = clean_skill_ids_for_job(player_id, job, current_skill_ids or [])

    if cleaned_skill_ids:
        return cleaned_skill_ids

    # ===== 何も選ばれていない場合は、所持魔法の先頭3つを初期持ち込みにする =====
    return get_owned_skill_ids(player_id, job)[:3]


def build_carried_skill_list(player_id, job, carried_skill_ids=None):
    # ===== 戦闘画面へ渡す持ち込み魔法リスト =====
    result = []
    carried_skill_ids = carried_skill_ids or []

    for skill_id in clean_skill_ids_for_job(player_id, job, carried_skill_ids):
        skill = get_skill(skill_id)

        if not skill:
            continue

        result.append({
            "id": skill_id,
            "name": skill.get("name", skill_id),
            "type": skill.get("type", "attack"),
            "element": skill.get("element", "none"),
            "target_type": skill.get("target_type", "single"),
            "power_rate": skill.get("power_rate", 1.0),
            "effect_type": skill.get("effect_type", ""),
            "description": skill.get("description", "")
        })

    return result


def get_party_buffs():
    game_state.setdefault("party_buffs", {})
    game_state["party_buffs"].setdefault("defend_turns", 0)
    game_state["party_buffs"].setdefault("physical_up_turns", 0)
    game_state["party_buffs"].setdefault("magic_boost_turns", 0)
    return game_state["party_buffs"]


def set_party_buff(effect_type, duration_turns):
    buffs = get_party_buffs()

    if effect_type == "defend":
        buffs["defend_turns"] = max(int(buffs.get("defend_turns", 0)), int(duration_turns))

    elif effect_type == "physical_up":
        buffs["physical_up_turns"] = max(int(buffs.get("physical_up_turns", 0)), int(duration_turns))

    elif effect_type == "magic_boost":
        buffs["magic_boost_turns"] = max(int(buffs.get("magic_boost_turns", 0)), int(duration_turns))


def decrement_party_buffs_after_turn(events=None):
    # ===== 使用ターンを含む持続なので、ターン終了時に1減らす =====
    # 効果が0になった瞬間だけ、戦闘イベントとログに終了メッセージを出す。
    buffs = get_party_buffs()

    buff_messages = {
        "defend_turns": "ディフェンドの効果が切れた。",
        "physical_up_turns": "フィジカルアップの効果が切れた。",
        "magic_boost_turns": "マジックブーストの効果が切れた。"
    }

    for key, message in buff_messages.items():
        before = int(buffs.get(key, 0))

        if before <= 0:
            buffs[key] = 0
            continue

        after = max(0, before - 1)
        buffs[key] = after

        if after == 0:
            if events is not None:
                events.append({
                    "text": message,
                    "state": snapshot()
                })

            add_log(message)


def get_attack(player):
    base = int(player.get("attack", 0))
    buffs = get_party_buffs()

    if int(buffs.get("physical_up_turns", 0)) > 0:
        return max(1, int(base * 1.5))

    return base


# ==================================================
# B-4セクション：レイド報酬選択
# ==================================================

def is_raid_battle_room():
    room_id = game_state.get("selected_room", "")
    room = ROOMS.get(room_id, {})
    return room.get("type") == "raid"


def build_raid_reward_candidates_for_player(player_name, job):
    player_data = ensure_player_inventory_data(player_name)

    owned_weapon_ids = set(player_data.get("owned_weapons", []))
    owned_shield_ids = set(player_data.get("owned_shields", []))
    owned_skill_ids = set(player_data.get("owned_skills", []))

    candidates = []

    if job in ["勇者", "タンク"]:
        for weapon_id, weapon in WEAPONS.items():
            if weapon.get("obtain_type") != "raid_drop":
                continue

            if job not in weapon.get("allowed_jobs", []):
                continue

            candidates.append({
                "kind": "weapon",
                "id": weapon_id,
                "name": weapon.get("name", weapon_id),
                "description": weapon.get("description", ""),
                "image": weapon.get("image", ""),
                "owned": weapon_id in owned_weapon_ids
            })

    if job == "タンク":
        for shield_id, shield in SHIELDS.items():
            if shield.get("obtain_type") != "raid_drop":
                continue

            candidates.append({
                "kind": "shield",
                "id": shield_id,
                "name": shield.get("name", shield_id),
                "description": shield.get("description", ""),
                "image": shield.get("image", ""),
                "owned": shield_id in owned_shield_ids
            })

    if job == "魔術師":
        for skill_id, skill in SKILLS.items():
            if skill.get("obtain_type") != "raid_drop":
                continue

            if skill.get("job") != job:
                continue

            candidates.append({
                "kind": "skill",
                "id": skill_id,
                "name": skill.get("name", skill_id),
                "description": skill.get("description", ""),
                "image": skill.get("image", ""),
                "owned": skill_id in owned_skill_ids
            })

    return candidates


def find_raid_reward_candidate(player_name, job, reward_kind, reward_id):
    candidates = build_raid_reward_candidates_for_player(player_name, job)

    for reward in candidates:
        if reward.get("kind") == reward_kind and reward.get("id") == reward_id:
            return reward

    return None

# ==================================================
# Cセクション：共通ゲーム処理
# C-1：接続・退出ブロック・部屋リセット
# ==================================================

def get_block_key():
    device_id = (
        request.form.get("device_id", "").strip() or
        request.args.get("device_id", "").strip()
    )

    if device_id:
        return f"device:{device_id}"

    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
    ip = ip.split(",")[0].strip()
    ua = request.headers.get("User-Agent", "unknown")
    return f"fallback:{ip}|{ua}"


def cleanup_kick_blocks():
    now = time.time()
    expired_keys = [key for key, until in kicked_devices.items() if until <= now]

    for key in expired_keys:
        del kicked_devices[key]


def is_device_blocked():
    cleanup_kick_blocks()
    key = get_block_key()
    until = kicked_devices.get(key)

    if until is None:
        return False, 0

    remaining = max(0, int(until - time.time()))
    return remaining > 0, remaining


def reset_game():
    global players, game_state

    players = []

    game_state = {
        "started": False,
        "phase": "waiting",
        "turn": 1,
        "actions": {},
        "kick_votes": {},
        "left_players": {},
        "boss_hp": BOSS_MAX_HP,
        "boss_max_hp": BOSS_MAX_HP,
        "host_name": None,
        "starter_name": None,
        "log": ["ロビーで参加者を待っています"],
        "winner": None,
        "growth_applied": False,
        "growth_messages": [],
        "normal_drop_applied": False,
        "normal_drop_messages": [],
        "last_actor": None,
        "turn_events": [],
        "event_id": 0,
        "chat_messages": [],
        "chat_id": 0,
        "all_offline_since": None,
        "last_boss_action": None,
        "same_boss_action_count": 0,
        "selected_room": "volcano",
        "selected_enemy_room": "random_zako_1",
        "party_title": "",
        "room_title": "",
        "room_name": "ボルケーノドラゴン",
        "enemies": [],
        "rematch_select": False,
        "rematch_expected_names": [],
        "rematch_room_id": "volcano",
        "party_buffs": {
            "defend_turns": 0,
            "physical_up_turns": 0,
            "magic_boost_turns": 0
        },
        "active_magic_wall": False,
        "active_magic_defense": False
    }

    if active_room_id in GAME_ROOMS:
        GAME_ROOMS[active_room_id]["players"] = players
        GAME_ROOMS[active_room_id]["game_state"] = game_state
        GAME_ROOMS[active_room_id]["updated_at"] = time.time()


def get_player(name):
    for p in players:
        if p["name"] == name:
            return p
    return None


def alive_players():
    return [p for p in players if p["hp"] > 0]


def alive_names():
    return [p["name"] for p in alive_players()]


def online_players():
    now = time.time()

    for p in players:
        last_seen = p.get("last_seen", 0)

        if now - last_seen > OFFLINE_LIMIT_SECONDS:
            p["online"] = False
        else:
            p["online"] = True

    return [p for p in players if p.get("online", True)]


def online_alive_players():
    online_players()
    return [p for p in alive_players() if p.get("online", True)]


def check_empty_room_reset():
    online = online_players()

    if len(players) == 0:
        if game_state.get("started") and game_state.get("left_players"):
            now = time.time()

            if game_state.get("all_offline_since") is None:
                game_state["all_offline_since"] = now

            if now - game_state["all_offline_since"] >= EMPTY_ROOM_RESET_SECONDS:
                reset_game()
                return True

            return False

        game_state["all_offline_since"] = None
        return False

    if len(online) > 0:
        game_state["all_offline_since"] = None
        return False

    now = time.time()

    if game_state.get("all_offline_since") is None:
        last_seen_list = [p.get("last_seen", 0) for p in players]
        latest_last_seen = max(last_seen_list) if last_seen_list else now
        game_state["all_offline_since"] = latest_last_seen + OFFLINE_LIMIT_SECONDS

    if now - game_state["all_offline_since"] >= EMPTY_ROOM_RESET_SECONDS:
        reset_game()
        return True

    return False


def all_actions_selected():
    online_players()

    target_names = []

    for p in alive_players():
        if p.get("online", True):
            target_names.append(p["name"])

    if len(target_names) == 0:
        return False

    return all(name in game_state["actions"] for name in target_names)


def snapshot():
    return {
        "boss_hp": game_state["boss_hp"],
        "players_hp": {p["name"]: p["hp"] for p in players},
        "enemies_hp": {e["id"]: e["hp"] for e in game_state.get("enemies", [])}
    }


def add_log(msg):
    game_state["log"].append(msg)
    game_state["log"] = game_state["log"][-30:]


def reset_combo(player):
    player["combo"] = 0


def reset_combo_if_unprotected_damage(player, protected_by_effect=False):
    # ===== 勇者コンボ解除判定 =====
    # 勇者は「無防備な状態でダメージを受けた時」だけコンボ解除。
    # 盾・魔法防御・属性武器・マジックブレード・ディフェンダー等で守られている場合は継続。
    if protected_by_effect:
        return

    reset_combo(player)


def get_magic(player):
    base = int(player.get("magic", player.get("heal", 0)))
    buffs = get_party_buffs()

    if int(buffs.get("magic_boost_turns", 0)) > 0:
        return max(1, int(base * 1.5))

    return base


def get_job_counts():
    job_counts = {
        "勇者": 0,
        "タンク": 0,
        "魔術師": 0
    }

    for p in players:
        job = p.get("job")

        if job in job_counts:
            job_counts[job] += 1

    return job_counts


def get_party_summary():
    room_exists = len(players) > 0 or game_state.get("started", False)

    return {
        "room_id": active_room_id,
        "total": len(players),
        "max_players": MAX_PLAYERS,
        "job_counts": get_job_counts(),
        "title": game_state.get("party_title") or game_state.get("room_title") or "冒険者募集",
        "started": game_state.get("started", False),
        "phase": game_state.get("phase", "waiting"),
        "room_exists": room_exists
    }


def add_chat_message(name, message):
    game_state["chat_id"] += 1

    game_state["chat_messages"].append({
        "id": game_state["chat_id"],
        "name": name,
        "message": message
    })

    game_state["chat_messages"] = game_state["chat_messages"][-50:]


def physical_damage(target, damage):
    result = damage

    if target.get("job") == "タンク":
        result = max(1, int(result * 0.7))

    if int(get_party_buffs().get("defend_turns", 0)) > 0:
        result = max(1, int(result * 0.5))

    return result


def magic_damage(target, damage):
    if target.get("job") == "魔術師":
        return max(1, int(damage * 0.6))
    return damage


# ==================================================
# Dセクション：武器システム
# D-1：武器基本処理・属性軽減
# ==================================================

def get_weapon_attack_bonus(job, weapon_id):
    weapon = get_weapon(weapon_id)

    if not weapon:
        return 0

    if job not in weapon.get("allowed_jobs", []):
        return 0

    bonus = weapon.get("attack_bonus", 0)

    if job == "タンク":
        bonus = int(bonus * 0.7)

    return bonus


def get_weapon_display_name(weapon_id):
    weapon = get_weapon(weapon_id)

    if not weapon:
        return "武器なし"

    return weapon.get("name", "武器なし")


def get_used_weapon_id_this_turn(player):
    action = game_state.get("actions", {}).get(player.get("name"))

    if not action:
        return ""

    return action.get("weapon_id", "")


def apply_used_weapon_resist(player, damage, element, target_type):
    # ===== 使用武器による属性軽減 =====
    # element例：fire / ice / thunder / none
    # target_type例：single / all
    if element in ["", "none", None]:
        return damage, None

    weapon_id = get_used_weapon_id_this_turn(player)

    if not weapon_id:
        return damage, None

    weapon = get_weapon(weapon_id)

    if not weapon:
        return damage, None

    resist = weapon.get("resist", {})

    cut_rate = None

    # ===== 新形式：{"fire": {"single": 0.7, "all": 0.5}} =====
    element_resist = resist.get(element)

    if isinstance(element_resist, dict):
        cut_rate = element_resist.get(target_type)

    # ===== 旧形式互換：{"fire_single": 0.7, "fire_all": 0.5} =====
    if cut_rate is None:
        cut_rate = resist.get(f"{element}_{target_type}")

    if cut_rate is None:
        return damage, None

    reduced_damage = max(1, int(damage * (1 - cut_rate)))
    weapon_name = weapon.get("name", "武器")

    return reduced_damage, weapon_name



# ==================================================
# Eセクション：盾システム
# E-1：使用盾による防御効果
# ==================================================

def get_active_party_shield_effects(element, attack_category, target_type):
    # ===== パーティ全体に効く盾効果を取得 =====
    # element例：fire / ice / thunder / light / dark / none
    # attack_category例：physical / magic
    effects = []

    for info in game_state.get("active_party_shields", []):
        shield = get_shield(info.get("id"))

        if not shield:
            continue

        effect_type = shield.get("effect_type")
        shield_name = shield.get("name", "盾")
        user_name = info.get("user", "タンク")

        if effect_type == "element_guard":
            if shield.get("element") == element:
                effects.append({
                    "name": shield_name,
                    "user": user_name,
                    "cut_rate": shield.get("cut_rate", 0),
                    "message": f"{user_name}の{shield_name}が{element}属性攻撃を軽減した！"
                })

        elif effect_type == "magic_guard":
            if attack_category == "magic":
                effects.append({
                    "name": shield_name,
                    "user": user_name,
                    "cut_rate": shield.get("cut_rate", 0),
                    "message": f"{user_name}の{shield_name}が魔法ダメージを軽減した！"
                })

        elif effect_type == "all_attack_guard":
            if target_type == "all":
                effects.append({
                    "name": shield_name,
                    "user": user_name,
                    "cut_rate": shield.get("cut_rate", 0),
                    "message": f"{user_name}の{shield_name}が全体攻撃ダメージを軽減した！"
                })

    if attack_category == "magic" and game_state.get("active_magic_wall"):
        effects.append({
            "name": "マジックウォール",
            "user": "魔術師",
            "cut_rate": 0.70,
            "message": "マジックウォールが魔法ダメージを軽減した！"
        })

    return effects


def apply_shield_effects_to_damage(damage, effects):
    # ===== 軽減系は加算し、上限90％で適用 =====
    total_cut_rate = 0

    for effect in effects:
        total_cut_rate += float(effect.get("cut_rate", 0))

    total_cut_rate = min(total_cut_rate, 0.90)

    return max(1, int(damage * (1 - total_cut_rate)))


def is_attack_shield_active(player_name):
    # ===== アタックシールド使用中か判定 =====
    return player_name in game_state.get("active_attack_shield_users", [])


def get_selected_shield_name(player_name):
    # ===== このターンに選択した盾名を取得 =====
    action = game_state.get("actions", {}).get(player_name, {})
    shield_id = action.get("shield_id", "")
    return get_shield_display_name(shield_id) if shield_id else "シールド"


def register_turn_start_shield_effects(turn_effects):
    # ===== ターン開始時に、選択済みの盾効果をすべて先に有効化 =====
    # 盾の実効果は行動順に左右されない。
    # 行動順が来た時は「盾を構えた！」という演出だけを出す。
    actions = game_state.get("actions", {})
    game_state.setdefault("active_party_shields", [])
    game_state.setdefault("active_attack_shield_users", [])
    game_state.setdefault("active_counter_shield_hits", {})
    game_state.setdefault("active_aegis_users", [])
    game_state.setdefault("active_guts_users", [])
    game_state.setdefault("active_healing_shield_users", [])

    for player in alive_players():
        if player.get("job") != "タンク":
            continue

        player_name = player.get("name", "")
        action = actions.get(player_name, {})

        if action.get("type") != "shield":
            continue

        shield_id = action.get("shield_id", "")
        shield = get_shield(shield_id)

        if not shield:
            continue

        effect_type = shield.get("effect_type", "")

        # ===== タンク本人の基本シールド状態と挑発はターン開始時から有効 =====
        turn_effects["shield_users"].add(player_name)

        if turn_effects.get("taunt_user") is None:
            turn_effects["taunt_user"] = player_name

        # ===== 属性軽減・魔法軽減・オート回避・反撃系など全盾を登録 =====
        already_registered = any(
            info.get("id") == shield_id and info.get("user") == player_name
            for info in game_state.get("active_party_shields", [])
        )

        if not already_registered:
            game_state["active_party_shields"].append({
                "id": shield_id,
                "user": player_name
            })

        # ===== 既存のアタックシールド処理用リストにも先行登録 =====
        if effect_type == "physical_counter":
            if player_name not in game_state.get("active_attack_shield_users", []):
                game_state["active_attack_shield_users"].append(player_name)

        elif effect_type == "first_hit_nullify":
            if game_state.get("aegis_used", False):
                continue

            for member in alive_players():
                member_name = member.get("name")

                if member_name not in game_state["active_aegis_users"]:
                    game_state["active_aegis_users"].append(member_name)

        elif effect_type == "healing_guard":
            if player_name not in game_state["active_healing_shield_users"]:
                game_state["active_healing_shield_users"].append(player_name)


        elif effect_type == "fatal_survive":
            if game_state.get("guts_used", False):
                continue

            for member in alive_players():
                member_name = member.get("name")

                if member_name not in game_state["active_guts_users"]:
                    game_state["active_guts_users"].append(member_name)


# ==================================================
# Fセクション：属性処理
# F-1：弱点・耐性・属性名
# ==================================================

def get_weapon_element(weapon_id):
    weapon = get_weapon(weapon_id)

    if not weapon:
        return "none"

    return weapon.get("element", "none")


def apply_enemy_element_modifier(damage, enemy, element):
    # ===== 敵の弱点・耐性によるダメージ補正 =====
    # 弱点：1.5倍
    # 耐性：0.5倍
    # それ以外：等倍
    if not enemy:
        return damage, None

    if element in ["", "none", None]:
        return damage, None

    weakness = enemy.get("weakness", [])
    resist = enemy.get("resist", [])

    if element in weakness:
        return max(1, int(damage * 1.5)), "weak"

    if element in resist:
        return max(1, int(damage * 0.5)), "resist"

    return damage, None


def get_element_display_name(element):
    names = {
        "fire": "火",
        "ice": "氷",
        "thunder": "雷",
        "wind": "風",
        "light": "光",
        "dark": "闇",
        "none": "無"
    }

    return names.get(element, element)



# ==================================================
# Gセクション：特殊武器判定
# G-1：特殊武器フラグ・ターン開始効果
# ==================================================

def is_tempest_weapon(weapon_id):
    return weapon_id == "tempest"

def is_all_attack_weapon(weapon_id):
    return weapon_id in ["tempest", "laser_blade"]

def is_blood_saver(weapon_id):
    return weapon_id == "blood_saver"

def is_defender_weapon(weapon_id):
    return weapon_id == "defender"

def is_magic_blade(weapon_id):
    return weapon_id == "magic_blade"

def is_bazooka_weapon(weapon_id):
    return weapon_id == "bazooka"

def is_bazooka_active(player_name):
    return player_name in game_state.get("active_bazooka_users", [])

def is_defender_active(player_name):
    return player_name in game_state.get("active_defender_users", [])

def is_magic_blade_active(player_name):
    return player_name in game_state.get("active_magic_blade_users", [])

def apply_magic_blade_reduction(player_name, damage):
    if is_magic_blade_active(player_name):
        return max(1, int(damage * 0.7))
    return damage


def register_turn_start_weapon_effects(events):
    # ===== ターン開始時に、選択済みの特殊武器効果を先に有効化 =====
    # ディフェンダー／マジックブレードの防御効果は、行動順に左右されない。
    # 敵が先に動いても、このターンにその武器で攻撃を選んでいれば効果を受けられる。
    actions = game_state.get("actions", {})
    game_state.setdefault("active_defender_users", [])
    game_state.setdefault("active_magic_blade_users", [])
    game_state.setdefault("active_bazooka_users", [])

    for player in alive_players():
        player_name = player.get("name", "")
        action = actions.get(player_name, {})

        if action.get("type") != "attack":
            continue

        weapon_id = action.get("weapon_id", "")

        if is_defender_weapon(weapon_id):
            if player_name not in game_state.get("active_defender_users", []):
                game_state["active_defender_users"].append(player_name)
                events.append({
                    "text": f"{player_name}はディフェンダーの守りを構えた！",
                    "state": snapshot()
                })
                add_log(f"{player_name}はディフェンダーの守りを構えた！")

        if is_magic_blade(weapon_id):
            if player_name not in game_state.get("active_magic_blade_users", []):
                game_state["active_magic_blade_users"].append(player_name)
                events.append({
                    "text": f"{player_name}はマジックブレードの魔法障壁を展開した！",
                    "state": snapshot()
                })
                add_log(f"{player_name}はマジックブレードの魔法障壁を展開した！")

        if is_bazooka_weapon(weapon_id):
            if player_name not in game_state.get("active_bazooka_users", []):
                game_state["active_bazooka_users"].append(player_name)
                events.append({
                    "text": f"{player_name}はバズーカを構えた！",
                    "state": snapshot()
                })
                add_log(f"{player_name}はバズーカを構えた！")


# ==================================================
# Hセクション：成長システム
# H-1：保存済み成長値・成長保存
# ==================================================

def get_saved_character_growth(player_id, job):
    # ===== 保存済みの成長値を取得 =====
    data = load_player_data()
    player_data = data.get(player_id, {})
    characters = player_data.get("characters", {})

    return characters.get(job, {
        "hp_bonus": 0,
        "attack_bonus": 0,
        "magic_bonus": 0,
        "total_battles": 0,
        "wins": 0
    })


def make_status_with_saved_growth(player_id, job):
    # ===== 名前由来の基本ステータスに保存済み成長を加算 =====
    stats = make_status_from_name(player_id, job)
    growth = get_saved_character_growth(player_id, job)

    hp_bonus = int(growth.get("hp_bonus", 0))
    attack_bonus = int(growth.get("attack_bonus", 0))
    magic_bonus = int(growth.get("magic_bonus", 0))

    stats["max_hp"] += hp_bonus
    stats["hp"] = stats["max_hp"]
    stats["attack"] += attack_bonus
    stats["magic"] += magic_bonus
    stats["heal"] = stats["magic"]

    return stats


def save_growth_to_player_data(player_name, job, hp_up, attack_up, magic_up):
    # ===== 成長値を players_data.json に保存 =====
    data = load_player_data()

    if player_name not in data:
        data[player_name] = create_new_player_data(player_name, "")

    data[player_name].setdefault("characters", {})

    if job not in data[player_name]["characters"]:
        data[player_name]["characters"][job] = {
            "hp_bonus": 0,
            "attack_bonus": 0,
            "magic_bonus": 0,
            "total_battles": 0,
            "wins": 0
        }

    character = data[player_name]["characters"][job]

    character["hp_bonus"] = int(character.get("hp_bonus", 0)) + hp_up
    character["attack_bonus"] = int(character.get("attack_bonus", 0)) + attack_up
    character["magic_bonus"] = int(character.get("magic_bonus", 0)) + magic_up
    character["total_battles"] = int(character.get("total_battles", 0)) + 1
    character["wins"] = int(character.get("wins", 0)) + 1

    save_player_data(data)




# ==================================================
# Iセクション：ロビー用ジョブ・装備処理
# I-1：持ち込み装備・ジョブ変更・装備変更
# ==================================================

def build_carried_weapons_for_job(job, current_weapon_ids=None, player_id=None):
    # ===== 現在の持ち込み武器のうち、新ジョブで使える所持武器を残す =====
    usable_weapons = get_owned_weapons_for_job(player_id, job) if player_id else get_weapons_for_job(job)
    current_weapon_ids = current_weapon_ids or []

    carried_weapon_ids = [
        weapon_id
        for weapon_id in current_weapon_ids
        if weapon_id in usable_weapons
    ]

    if not carried_weapon_ids:
        initial_ids = INITIAL_WEAPON_IDS_BY_JOB.get(job, [])
        carried_weapon_ids = [weapon_id for weapon_id in initial_ids if weapon_id in usable_weapons]

    if not carried_weapon_ids:
        carried_weapon_ids = list(usable_weapons.keys())[:3]

    carried_weapon_ids = carried_weapon_ids[:3]

    return carried_weapon_ids


def build_carried_shields_for_job(job, current_shield_ids=None, player_id=None):
    # ===== タンク以外は盾を持たない。タンクなら所持盾から補う =====
    if job != "タンク":
        return []

    usable_shields = get_owned_shields_for_job(player_id, job) if player_id else get_shields_for_job(job)
    current_shield_ids = current_shield_ids or []

    carried_shield_ids = [
        shield_id
        for shield_id in current_shield_ids
        if shield_id in usable_shields
    ]

    if not carried_shield_ids:
        initial_ids = INITIAL_SHIELD_IDS_BY_JOB.get(job, [])
        carried_shield_ids = [shield_id for shield_id in initial_ids if shield_id in usable_shields]

    if not carried_shield_ids:
        carried_shield_ids = list(usable_shields.keys())[:3]

    carried_shield_ids = carried_shield_ids[:3]

    return carried_shield_ids


def apply_job_to_player(player, job):
    # ===== ジョブ変更時に保存済み成長込みのステータスへ作り直す =====
    name = player.get("name", "")
    stats = make_status_with_saved_growth(name, job)

    carried_weapon_ids = build_carried_weapons_for_job(
        job,
        player.get("carried_weapon_ids", []),
        name
    )

    carried_shield_ids = build_carried_shields_for_job(
        job,
        player.get("carried_shield_ids", []),
        name
    )

    carried_skill_ids = build_carried_skill_ids_for_job(
        name,
        job,
        player.get("carried_skill_ids", [])
    )

    selected_weapon_id = carried_weapon_ids[0] if carried_weapon_ids else ""

    player["job"] = job
    player["attack"] = stats["attack"]
    player["hp"] = stats["hp"]
    player["max_hp"] = stats["max_hp"]
    player["magic"] = stats["magic"]
    player["heal"] = stats["heal"]
    player["combo"] = 0

    player["weapon_id"] = selected_weapon_id
    player["weapon_name"] = get_weapon_display_name(selected_weapon_id)
    player["carried_weapon_ids"] = carried_weapon_ids
    player["carried_weapons"] = [
        {
            "id": weapon_id,
            "name": get_weapon_display_name(weapon_id),
            "element": get_weapon(weapon_id).get("element", "none") if get_weapon(weapon_id) else "none"
        }
        for weapon_id in carried_weapon_ids
    ]

    player["carried_shield_ids"] = carried_shield_ids
    player["carried_shields"] = [
        {
            "id": shield_id,
            "name": get_shield_display_name(shield_id),
            "element": get_shield(shield_id).get("element", "none") if get_shield(shield_id) else "none",
            "effect_type": get_shield(shield_id).get("effect_type", "") if get_shield(shield_id) else "",
            "image": get_shield(shield_id).get("image", f"/static/images/shields/{shield_id}.png") if get_shield(shield_id) else f"/static/images/shields/{shield_id}.png"
        }
        for shield_id in carried_shield_ids
    ]

    player["owned_skill_ids"] = get_owned_skill_ids(name, job)
    player["owned_skills"] = build_owned_skill_list(name, job)
    player["carried_skill_ids"] = carried_skill_ids
    player["carried_skills"] = build_carried_skill_list(name, job, carried_skill_ids)

    return player


def build_weapon_option_list(job, player_id=None):
    # ===== ロビー装備変更用：所持していて、ジョブで使える武器一覧 =====
    weapons = get_owned_weapons_for_job(player_id, job) if player_id else get_weapons_for_job(job)

    return [
        {
            "id": weapon_id,
            "name": weapon.get("name", weapon_id),
            "element": weapon.get("element", "none"),
            "description": weapon.get("description", "")
        }
        for weapon_id, weapon in weapons.items()
    ]


def build_shield_option_list(job, player_id=None):
    # ===== ロビー装備変更用：所持していて、タンクで使える盾一覧 =====
    if job != "タンク":
        return []

    shields = get_owned_shields_for_job(player_id, job) if player_id else get_shields_for_job(job)

    return [
        {
            "id": shield_id,
            "name": shield.get("name", shield_id),
            "element": shield.get("element", "none"),
            "effect_type": shield.get("effect_type", ""),
            "description": shield.get("description", "")
        }
        for shield_id, shield in shields.items()
    ]


def apply_equipment_to_player(player, weapon_id="", shield_id="", carried_weapon_ids=None, carried_shield_ids=None, carried_skill_ids=None):
    # ===== ロビー装備変更：現在ジョブで使える装備だけ反映 =====
    # 勇者：持ち込み武器を最大3つまで選択できる。
    # それ以外：従来通り、代表武器1つを選択する。
    job = player.get("job", "")

    player_id = player.get("name", "")
    usable_weapons = get_owned_weapons_for_job(player_id, job)
    usable_shields = get_owned_shields_for_job(player_id, job) if job == "タンク" else {}

    # ===== 魔術師：武器ではなく魔法を最大3つ持ち込む =====
    if job == "魔術師":
        weapon_id = ""
        carried_weapon_ids = []

    # ===== 勇者・タンク：チェックボックスで最大3つ持ち込み =====
    elif job in ["勇者", "タンク"]:
        selected_weapon_ids = carried_weapon_ids or []

        # カンマ区切り文字列で来た場合の保険
        if isinstance(selected_weapon_ids, str):
            selected_weapon_ids = [
                wid.strip()
                for wid in selected_weapon_ids.split(",")
                if wid.strip()
            ]

        # 現在ジョブで使える武器だけ残し、重複を除く
        cleaned_weapon_ids = []
        for wid in selected_weapon_ids:
            if wid in usable_weapons and wid not in cleaned_weapon_ids:
                cleaned_weapon_ids.append(wid)

        cleaned_weapon_ids = cleaned_weapon_ids[:3]

        # 何も選ばれていない場合は、現在の持ち込みから復元。それもなければ先頭武器。
        if not cleaned_weapon_ids:
            for wid in player.get("carried_weapon_ids", []):
                if wid in usable_weapons and wid not in cleaned_weapon_ids:
                    cleaned_weapon_ids.append(wid)
                if len(cleaned_weapon_ids) >= 3:
                    break

        if not cleaned_weapon_ids and usable_weapons:
            cleaned_weapon_ids = list(usable_weapons.keys())[:1]

        carried_weapon_ids = cleaned_weapon_ids
        weapon_id = carried_weapon_ids[0] if carried_weapon_ids else ""

    # ===== その他：従来通り代表武器1つ =====
    else:
        if weapon_id and weapon_id not in usable_weapons:
            weapon_id = ""

        if not weapon_id:
            current_ids = player.get("carried_weapon_ids", [])
            for current_id in current_ids:
                if current_id in usable_weapons:
                    weapon_id = current_id
                    break

        if not weapon_id and usable_weapons:
            weapon_id = list(usable_weapons.keys())[0]

        carried_weapon_ids = [weapon_id] if weapon_id else []

    # ===== 盾処理：タンクは最大3つまで持ち込み =====
    if job != "タンク":
        shield_id = ""
        carried_shield_ids = []

    else:
        selected_shield_ids = carried_shield_ids or []

        # カンマ区切り文字列で来た場合の保険
        if isinstance(selected_shield_ids, str):
            selected_shield_ids = [
                sid.strip()
                for sid in selected_shield_ids.split(",")
                if sid.strip()
            ]

        # 現在ジョブで使える盾だけ残し、重複を除く
        cleaned_shield_ids = []
        for sid in selected_shield_ids:
            if sid in usable_shields and sid not in cleaned_shield_ids:
                cleaned_shield_ids.append(sid)

        cleaned_shield_ids = cleaned_shield_ids[:3]

        # 何も選ばれていない場合は、現在の持ち込みから復元。それもなければ先頭盾。
        if not cleaned_shield_ids:
            for sid in player.get("carried_shield_ids", []):
                if sid in usable_shields and sid not in cleaned_shield_ids:
                    cleaned_shield_ids.append(sid)
                if len(cleaned_shield_ids) >= 3:
                    break

        if not cleaned_shield_ids and usable_shields:
            cleaned_shield_ids = list(usable_shields.keys())[:1]

        carried_shield_ids = cleaned_shield_ids
        shield_id = carried_shield_ids[0] if carried_shield_ids else ""

    player["weapon_id"] = weapon_id
    player["weapon_name"] = get_weapon_display_name(weapon_id)
    player["carried_weapon_ids"] = carried_weapon_ids
    player["carried_weapons"] = [
        {
            "id": wid,
            "name": get_weapon_display_name(wid),
            "element": get_weapon(wid).get("element", "none") if get_weapon(wid) else "none"
        }
        for wid in carried_weapon_ids
    ]

    player["shield_id"] = shield_id
    player["shield_name"] = get_shield_display_name(shield_id) if shield_id else ""
    player["carried_shield_ids"] = carried_shield_ids
    player["carried_shields"] = [
        {
            "id": sid,
            "name": get_shield_display_name(sid),
            "element": get_shield(sid).get("element", "none") if get_shield(sid) else "none",
            "effect_type": get_shield(sid).get("effect_type", "") if get_shield(sid) else "",
            "image": get_shield(sid).get("image", f"/static/images/shields/{sid}.png") if get_shield(sid) else f"/static/images/shields/{sid}.png"
        }
        for sid in carried_shield_ids
    ]

    carried_skill_ids = build_carried_skill_ids_for_job(
        player.get("name", ""),
        job,
        carried_skill_ids if carried_skill_ids is not None else player.get("carried_skill_ids", [])
    )
    player["owned_skill_ids"] = get_owned_skill_ids(player.get("name", ""), job)
    player["owned_skills"] = build_owned_skill_list(player.get("name", ""), job)
    player["carried_skill_ids"] = carried_skill_ids
    player["carried_skills"] = build_carried_skill_list(player.get("name", ""), job, carried_skill_ids)

    return player


# ==================================================
# Jセクション：ステータス生成
# ==================================================

def make_status_from_name(name, job):
    # ===== Ver.12：新規・基本ステータスは名前依存ではなくジョブ固定値にする =====
    # 成長値は make_status_with_saved_growth() 側でこの基本値に加算される。

    if job == "勇者":
        hp = 105
        attack = 11
        magic = 13

    elif job == "タンク":
        hp = 150
        attack = 13
        magic = 10

    elif job == "魔術師":
        hp = 90
        attack = 8
        magic = 15

    else:
        hp = 100
        attack = 10
        magic = 10

    return {
        "attack": attack,
        "hp": hp,
        "max_hp": hp,
        "magic": magic,
        "heal": magic,
        "combo": 0
    }

# ==================================================
# Kセクション：バトル初期化・敵生成
# ==================================================

def setup_room(room_id):
    room = ROOMS.get(room_id, ROOMS["volcano"])

    game_state["selected_room"] = room_id
    game_state["room_name"] = room["name"]
    game_state["enemies"] = []

    enemy_refs = room.get("enemies", [])

    if room.get("type") == "random_zako":
        enemy_refs = build_random_zako_enemy_refs(room.get("random_count", 1))

    for index, enemy_ref in enumerate(enemy_refs):
        enemy_id = enemy_ref["id"]
        enemy_data = get_enemy_master(enemy_id)

        max_hp = enemy_data.get("max_hp", enemy_ref.get("max_hp", 1))
        battle_enemy_id = enemy_id

        # ===== ランダム雑魚戦では、戦闘中IDを一意にする =====
        # 将来、同種敵を複数出す仕様にしても target_enemy が衝突しない。
        if room.get("type") == "random_zako":
            battle_enemy_id = f"{enemy_id}_{index + 1}"

        game_state["enemies"].append({
            "id": battle_enemy_id,
            "master_id": enemy_id,
            "name": enemy_data.get("name", enemy_ref.get("name", enemy_id)),
            "hp": max_hp,
            "max_hp": max_hp,
            "image": enemy_data.get("image", enemy_ref.get("image", "")),
            "role": enemy_data.get("role", enemy_ref.get("role", "enemy")),
            "weakness": enemy_data.get("weakness", enemy_ref.get("weakness", [])),
            "resist": enemy_data.get("resist", enemy_ref.get("resist", [])),
            "skills": enemy_data.get("skills", enemy_ref.get("skills", []))
        })

    game_state["boss_max_hp"] = sum(e["max_hp"] for e in game_state["enemies"])
    game_state["boss_hp"] = game_state["boss_max_hp"]

def alive_enemies():
    return [e for e in game_state.get("enemies", []) if e["hp"] > 0]


def get_enemy(enemy_id):
    for e in game_state.get("enemies", []):
        if e["id"] == enemy_id:
            return e
    return None


def choose_attack_enemy():
    living = alive_enemies()
    if not living:
        return None
    return living[0]



def choose_enemy_skill(enemy, target_type=None):
    # ===== 敵スキルをrateに従って選ぶ =====
    skills = enemy.get("skills", []) if enemy else []

    if target_type:
        filtered = [skill for skill in skills if skill.get("target") == target_type]
        if filtered:
            skills = filtered

    if not skills:
        return {
            "name": "攻撃",
            "rate": 100,
            "target": target_type or "single",
            "category": "physical",
            "element": "none",
            "damage": [1, 1]
        }

    total_rate = sum(max(0, int(skill.get("rate", 0))) for skill in skills)

    if total_rate <= 0:
        return skills[0]

    roll = random.randint(1, total_rate)
    current = 0

    for skill in skills:
        current += max(0, int(skill.get("rate", 0)))
        if roll <= current:
            return skill

    return skills[-1]


def random_value_from_range(value_range, default_min=1, default_max=1):
    # ===== [最小, 最大]形式の数値範囲からランダム値を作る =====
    if not isinstance(value_range, list) or len(value_range) < 2:
        return random.randint(default_min, default_max)

    return random.randint(int(value_range[0]), int(value_range[1]))


def get_enemy_skill_damage(skill, default_min=1, default_max=1):
    return random_value_from_range(skill.get("damage"), default_min, default_max)


def get_enemy_skill_heal(skill, default_min=1, default_max=1):
    return random_value_from_range(skill.get("heal"), default_min, default_max)


def damage_enemy(enemy, damage):
    if enemy is None:
        return

    enemy["hp"] -= damage
    enemy["hp"] = max(0, enemy["hp"])

    game_state["boss_hp"] = sum(e["hp"] for e in game_state.get("enemies", []))
    game_state["boss_hp"] = max(0, game_state["boss_hp"])


def start_battle_state(room_id="volcano"):
    setup_room(room_id)

    game_state["started"] = True
    game_state["phase"] = "choice"
    game_state["turn"] = 1
    game_state["actions"] = {}
    game_state["kick_votes"] = {}
    game_state["boss_hp"] = game_state["boss_max_hp"]
    game_state["winner"] = None
    game_state["growth_applied"] = False
    game_state["growth_messages"] = []

    # レイド報酬状態リセット
    game_state["raid_reward_available"] = False
    game_state["raid_reward_claims"] = {}

    game_state["normal_drop_applied"] = False
    game_state["normal_drop_messages"] = []
    game_state["last_actor"] = None
    game_state["last_boss_action"] = None
    game_state["same_boss_action_count"] = 0
    game_state["turn_events"] = []
    game_state["rematch_select"] = False
    game_state["rematch_expected_names"] = []
    game_state["event_id"] += 1
    game_state["log"] = [f"{game_state['room_name']}との戦闘開始！ 行動を選んでください。"]
    game_state["party_buffs"] = {
        "defend_turns": 0,
        "physical_up_turns": 0,
        "magic_boost_turns": 0
    }
    game_state["active_magic_wall"] = False
    game_state["active_magic_defense"] = False
    game_state["aegis_used"] = False
    game_state["guts_used"] = False

    for p in players:
        p["hp"] = p["max_hp"]
        p["combo"] = 0
        p.pop("magic_charge_turn", None)


# ==================================================
# Lセクション：battle_engine連携
# ==================================================
# 戦闘処理本体は battle_engine.py に分離しました。
# process_turn は battle_engine.py から import して使用します。


def get_battle_engine_context():
    # ===== battle_engine.py に app.py 側の現在状態・共通関数を渡す =====
    return globals()


configure_battle_engine(get_battle_engine_context)


# ==================================================
# H-2セクション：戦闘後成長イベント処理
# ==================================================

def choose_growth_type_for_job(job):
    # ===== ジョブごとに伸びやすい成長項目を変える =====
    #
    # 勇者：HP40％ / ATK40％ / MAGIC20％
    # タンク：HP60％ / ATK20％ / MAGIC20％
    # 魔術師：HP40％ / ATK20％ / MAGIC40％

    growth_tables = {
        "勇者": [
            "hp", "hp", "hp", "hp",
            "attack", "attack", "attack", "attack",
            "magic", "magic"
        ],

        "タンク": [
            "hp", "hp", "hp", "hp", "hp", "hp",
            "attack", "attack",
            "magic", "magic"
        ],

        "魔術師": [
            "hp", "hp", "hp", "hp",
            "magic", "magic", "magic", "magic",
            "attack", "attack"
        ]
    }

    return random.choice(growth_tables.get(job, ["hp", "attack", "magic"]))

def apply_growth_after_battle():
    if game_state.get("growth_applied"):
        return game_state.get("growth_messages", [])

    messages = []

    for player in players:
        name = player.get("name", "")
        job = player.get("job", "")

        if not name or not job:
            continue

        growth_type = choose_growth_type_for_job(job)

        hp_up = 0
        attack_up = 0
        magic_up = 0

        if growth_type == "hp":
            hp_up = random.randint(1, 3)
            player["max_hp"] = int(player.get("max_hp", 0)) + hp_up
            player["hp"] = min(int(player.get("hp", 0)) + hp_up, player["max_hp"])
            message = f"{name}（{job}）が成長した！ HP+{hp_up}"

        elif growth_type == "attack":
            attack_up = 1
            player["attack"] = int(player.get("attack", 0)) + attack_up
            message = f"{name}（{job}）が成長した！ ATK+{attack_up}"

        else:
            magic_up = 1
            player["magic"] = int(player.get("magic", player.get("heal", 0))) + magic_up
            player["heal"] = player["magic"]
            message = f"{name}（{job}）が成長した！ MAGIC+{magic_up}"

        save_growth_to_player_data(name, job, hp_up, attack_up, magic_up)
        messages.append(message)

    game_state["growth_applied"] = True
    game_state["growth_messages"] = messages

    return messages


def append_growth_events(events):
    growth_messages = apply_growth_after_battle()

    for msg in growth_messages:
        events.append({
            "text": msg,
            "state": snapshot()
        })

    return events


# ==================================================
# Mセクション：ターン終了・勝敗終了共通処理
# ==================================================

def finalize_turn_events(events):
    # ===== 通常ターン終了時のイベント確定 =====
    game_state["last_actor"] = None
    game_state["turn_events"] = events
    game_state["event_id"] += 1


def finish_with_victory(events):
    # ===== 勝利時の共通出口 =====
    events.append({"text": "敵をすべて倒した！", "state": snapshot()})
    events.append({"text": "勝利！", "state": snapshot()})

    add_log("敵をすべて倒した！")
    add_log("勝利！")

    append_growth_events(events)
    append_normal_battle_drop_events(events)

    if is_raid_battle_room():
        game_state["raid_reward_available"] = True
        game_state["raid_reward_claims"] = {}
        events.append({
            "text": "レイド報酬を選択できます！",
            "state": snapshot()
        })
        add_log("レイド報酬を選択できます！")

    game_state["phase"] = "end"
    game_state["winner"] = "players"
    game_state["last_actor"] = None
    game_state["turn_events"] = events
    game_state["event_id"] += 1

def finish_with_defeat(events):
    # ===== 敗北時の共通出口 =====
    events.append({"text": "全滅…", "state": snapshot()})
    events.append({"text": "敗北", "state": snapshot()})

    add_log("全滅…")
    add_log("敗北")

    game_state["phase"] = "end"
    game_state["winner"] = "boss"
    game_state["last_actor"] = None
    game_state["turn_events"] = events
    game_state["event_id"] += 1


# ==================================================
# Nセクション：画面ルート
# ==================================================


# ==================================================
# N-1セクション：ログイン画面
# ==================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        if is_logged_in():
            return redirect(url_for("index"))
        return render_template("login.html", message="")

    player_id = request.form.get("player_id", "").strip()
    password = request.form.get("password", "").strip()
    mode = request.form.get("mode", "login").strip()

    if not player_id or not password:
        return render_template("login.html", message="IDとパスワードを入力してください。")

    if len(player_id) > 16:
        return render_template("login.html", message="IDは16文字以内にしてください。")

    data = load_player_data()

    if mode == "register":
        if player_id in data:
            return render_template("login.html", message="そのIDはすでに使われています。")
        data[player_id] = create_new_player_data(player_id, password)
        save_player_data(data)
        session["player_id"] = player_id
        return redirect(url_for("index"))

    if player_id not in data:
        return render_template("login.html", message="そのIDは登録されていません。")

    if data[player_id].get("password_hash") != hash_password(password):
        return render_template("login.html", message="パスワードが違います。")

    now_text = time.strftime("%Y-%m-%d %H:%M:%S")
    data[player_id]["last_login"] = now_text
    data[player_id]["login_count"] = int(data[player_id].get("login_count", 0)) + 1
    save_player_data(data)

    session["player_id"] = player_id
    return redirect(url_for("index"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



@app.route("/")
def index():
    if not is_logged_in():
        return redirect(url_for("login"))

    # ===== 互換用main部屋の状態を確認しつつ、部屋一覧を表示 =====
    switch_room_context("main", save_to_session=False)
    check_empty_room_reset()
    room_list = get_room_summaries()

    return render_template(
        "index.html",
        login_player_id=get_login_player_id(),
        party=get_party_summary(),
        room_list=room_list,
        has_players=(len(players) > 0),
        started=game_state["started"]
    )

@app.route("/battle_guide")
def battle_guide():
    if not is_logged_in():
        return redirect(url_for("login"))

    return render_template("battle_guide.html")

@app.route("/secret_admin")
def secret_admin():
    if not is_logged_in():
        return redirect(url_for("login"))

    if get_login_player_id() != "おかっきー":
        return redirect(url_for("index"))

    data = load_player_data()
    today = time.strftime("%Y-%m-%d")

    players_info = []

    for player_id, player_data in data.items():
        last_login = player_data.get("last_login", "")
        players_info.append({
            "player_id": player_id,
            "created_at_text": player_data.get("created_at_text", ""),
            "last_login": last_login,
            "login_count": int(player_data.get("login_count", 0)),
            "is_today": last_login.startswith(today)
        })

    players_info.sort(key=lambda x: x["last_login"], reverse=True)

    today_login_count = len([p for p in players_info if p["is_today"]])

    return render_template(
        "secret_admin.html",
        total_players=len(players_info),
        today_login_count=today_login_count,
        players_info=players_info
    )


@app.route("/character_select")
def character_select():
    if not is_logged_in():
        return redirect(url_for("login"))

    action = request.args.get("action", "join").strip()
    room_title = request.args.get("room_title", "").strip()
    room_password = request.args.get("room_password", "").strip()[:20]
    requested_room_id = request.args.get("room_id", "").strip()

    if action == "create":
        if not room_title:
            room_title = "冒険者募集"
        room_id = create_new_room(room_title, room_password)
    else:
        room_id = requested_room_id or get_request_room_id()

        if not switch_room_context(room_id):
            return redirect(url_for("index"))

        # ===== 合言葉チェック =====
        input_password = request.args.get(
            "room_password_input", ""
        ).strip()

        real_password = str(
            GAME_ROOMS.get(room_id, {}).get("room_password", "")
        ).strip()

        if real_password:
            if input_password != real_password:
                return redirect(url_for("index"))

    check_empty_room_reset()

    if game_state.get("started"):
        return redirect(url_for("index"))

    login_player_id = get_login_player_id()
    character_stats = {}

    for job_name in ["勇者", "タンク", "魔術師"]:
        base_stats = make_status_with_saved_growth(login_player_id, job_name)
        saved_growth = get_saved_character_growth(login_player_id, job_name)

        character_stats[job_name] = {
            "hp": base_stats.get("max_hp", base_stats.get("hp", 0)),
            "attack": base_stats.get("attack", 0),
            "magic": base_stats.get("magic", base_stats.get("heal", 0)),
            "wins": int(saved_growth.get("wins", 0))
        }

    return render_template(
        "character_select.html",
        login_player_id=login_player_id,
        my_name=login_player_id,
        action=action,
        room_title=room_title,
        room_id=active_room_id,
        party=get_party_summary(),
        characters={},
        character_stats=character_stats
    )

@app.route("/weapon_select", methods=["POST"])
def weapon_select():
    if not is_logged_in():
        return redirect(url_for("login"))

    room_id = request.form.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return redirect(url_for("index"))

    job = request.form.get("job", "").strip()
    name = get_login_player_id()
    room_title = request.form.get("room_title", "").strip()

    if job not in ["勇者", "タンク", "魔術師"]:
        return redirect(url_for("character_select"))

    if job == "魔術師":
        owned_skills = build_owned_skill_list(name, job)

        return render_template(
            "skill_select.html",
            login_player_id=get_login_player_id(),
            my_name=name,
            job=job,
            skills=owned_skills,
            room_title=room_title,
            room_id=active_room_id
        )

    usable_weapons = get_owned_weapons_for_job(name, job)

    return render_template(
        "weapon_select.html",
        login_player_id=get_login_player_id(),
        my_name=name,
        job=job,
        weapons=usable_weapons,
        room_title=room_title,
        room_id=active_room_id
    )

@app.route("/shield_select", methods=["POST"])
def shield_select():
    if "is_logged_in" in globals():
        if not is_logged_in():
            return redirect(url_for("login"))

    room_id = request.form.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return redirect(url_for("index"))

    job = request.form.get("job", "").strip()
    room_title = request.form.get("room_title", "").strip()
    weapon_id = request.form.get("weapon_id", "").strip()
    shield_id = request.form.get("shield_id", "").strip()
    skill_id = request.form.get("skill_id", "").strip()
    carried_weapon_ids = request.form.getlist("carried_weapon_ids")

    # JavaScript側からカンマ区切りで来た場合の保険
    if not carried_weapon_ids:
        carried_weapon_ids_text = request.form.get("carried_weapon_ids_text", "").strip()
        if carried_weapon_ids_text:
            carried_weapon_ids = [
                wid.strip()
                for wid in carried_weapon_ids_text.split(",")
                if wid.strip()
            ]
    carried_weapon_ids = request.form.get("carried_weapon_ids", "").strip()

    if "get_login_player_id" in globals() and get_login_player_id():
        name = get_login_player_id()
    else:
        name = request.form.get("name", "").strip()

    if job != "タンク":
        return redirect(url_for("weapon_select"))

    shields = get_owned_shields_for_job(name, job)

    return render_template(
        "shield_select.html",
        login_player_id=name,
        my_name=name,
        job=job,
        shields=shields,
        weapon_id=weapon_id,
        carried_weapon_ids=carried_weapon_ids,
        room_title=room_title,
        room_id=active_room_id
    )


@app.route("/lobby")
def lobby():
    if not is_logged_in():
        return redirect(url_for("login"))

    room_id = request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return redirect(url_for("index"))

    room_id = request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return redirect(url_for("index"))

    name = request.args.get("name", "").strip()

    if get_player(name) is None:
        return redirect(url_for("index"))

    return render_template(
        "lobby.html",
        my_name=name,
        room_id=active_room_id,
        room_title=game_state.get("party_title", "冒険者募集"),
        room_password=GAME_ROOMS.get(active_room_id, {}).get("room_password", "")
    )

@app.route("/battle")
def battle():
    if not is_logged_in():
        return redirect(url_for("login"))

    room_id = request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return redirect(url_for("index"))

    name = request.args.get("name", "").strip()

    if get_player(name) is None:
        return redirect(url_for("index"))

    if not game_state["started"]:
        return redirect(url_for("lobby", name=name, room_id=active_room_id))

    return render_template("battle.html", my_name=name, room_id=active_room_id)



# ==================================================
# N-5セクション：開発者部屋
# ==================================================

DEVELOPER_ROOM_PLAYERS = ["おかっきー", "アドミニ１", "アドミニ２", "アドミニ３"]


@app.route("/developer_room")
def developer_room():
    if not is_logged_in():
        return redirect(url_for("login"))

    name = request.args.get("name", "").strip()
    room_id = request.args.get("room_id", "").strip() or get_request_room_id()

    if name != get_login_player_id():
        return redirect(url_for("index"))

    if name not in DEVELOPER_ROOM_PLAYERS:
        return redirect(url_for("index"))

    if not switch_room_context(room_id):
        return redirect(url_for("index"))

    return render_template(
        "developer_room.html",
        my_name=name,
        room_id=active_room_id
    )


@app.route("/developer_status")
def developer_status():
    if not is_logged_in():
        return jsonify({"ok": False, "message": "ログインが必要です"})

    name = request.args.get("name", "").strip()
    room_id = request.args.get("room_id", "").strip() or get_request_room_id()

    if name != get_login_player_id() or name not in DEVELOPER_ROOM_PLAYERS:
        return jsonify({"ok": False, "message": "開発者だけが使用できます"})

    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    result = []

    for target_name in DEVELOPER_ROOM_PLAYERS:
        player = get_player(target_name)

        if player:
            result.append({
                "name": target_name,
                "in_party": True,
                "job": player.get("job", ""),
                "hp": player.get("hp", 0),
                "max_hp": player.get("max_hp", 0),
                "attack": player.get("attack", 0),
                "magic": player.get("magic", player.get("heal", 0))
            })
        else:
            result.append({
                "name": target_name,
                "in_party": False
            })

    return jsonify({
        "ok": True,
        "players": result
    })


@app.route("/developer_update_status", methods=["POST"])
def developer_update_status():
    if not is_logged_in():
        return jsonify({"ok": False, "message": "ログインが必要です"})

    name = request.form.get("name", "").strip()
    room_id = request.form.get("room_id", "").strip() or get_request_room_id()

    if name != get_login_player_id() or name not in DEVELOPER_ROOM_PLAYERS:
        return jsonify({"ok": False, "message": "開発者だけが使用できます"})

    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    target_name = request.form.get("target_name", "").strip()

    if target_name not in DEVELOPER_ROOM_PLAYERS:
        return jsonify({"ok": False, "message": "対象外のプレイヤーです"})

    player = get_player(target_name)

    if not player:
        return jsonify({"ok": False, "message": "対象プレイヤーはこの部屋にいません"})

    old_max_hp = max(1, int(player.get("max_hp", 1)))
    old_hp = max(0, int(player.get("hp", 0)))
    hp_rate = old_hp / old_max_hp

    max_hp = max(1, min(999, int(request.form.get("max_hp", 1))))
    attack = max(1, min(99, int(request.form.get("attack", 1))))
    magic = max(1, min(99, int(request.form.get("magic", 1))))

    player["max_hp"] = max_hp
    player["hp"] = max(1, min(max_hp, int(max_hp * hp_rate)))
    player["attack"] = attack
    player["magic"] = magic
    player["heal"] = magic

    add_log(f"{target_name}のステータスが開発者部屋で変更された。")

    return jsonify({
        "ok": True,
        "player": player
    })



# ==================================================
# Oセクション：参加処理
# ==================================================

@app.route("/join", methods=["POST"])
def join():
    if not is_logged_in():
        return redirect(url_for("login"))

    room_id = request.form.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id, create_if_missing=True, room_title=request.form.get("room_title", "").strip() or "冒険者募集"):
        return redirect(url_for("index"))

    check_empty_room_reset()

    blocked, remaining = is_device_blocked()
    if blocked:
        minutes = max(1, (remaining + 59) // 60)
        return f"投票により退出した端末です。あと約{minutes}分は参加できません。"

    name = get_login_player_id()
    selected_job = request.form.get("job", "").strip()
    selected_weapon_id = request.form.get("weapon_id", "").strip()
    carried_weapon_ids_text = request.form.get("carried_weapon_ids", "").strip()

    carried_weapon_ids = [
        weapon_id.strip()
        for weapon_id in carried_weapon_ids_text.split(",")
        if weapon_id.strip()
    ]

    if not carried_weapon_ids and selected_weapon_id:
        carried_weapon_ids = [selected_weapon_id]

    carried_weapon_ids = carried_weapon_ids[:3]

    selected_weapon_id = carried_weapon_ids[0] if carried_weapon_ids else ""

    carried_shield_ids_text = request.form.get("carried_shield_ids", "").strip()

    carried_shield_ids = [
        shield_id.strip()
        for shield_id in carried_shield_ids_text.split(",")
        if shield_id.strip()
    ]

    carried_shield_ids = carried_shield_ids[:3]

    carried_skill_ids_text = request.form.get("carried_skill_ids", "").strip()

    carried_skill_ids = [
        skill_id.strip()
        for skill_id in carried_skill_ids_text.split(",")
        if skill_id.strip()
    ]

    room_title = request.form.get("room_title", "").strip()

    if selected_job not in ["勇者", "タンク", "魔術師"]:
        selected_job = "勇者"

    existing_player = get_player(name)
    left_player = game_state.get("left_players", {}).get(name)

    if left_player is not None:
        restored_player = game_state["left_players"].pop(name)
        restored_player["online"] = True
        restored_player["last_seen"] = time.time()
        restored_player["block_key"] = get_block_key()
        restored_player["left_voluntarily"] = False
        players.append(restored_player)
        game_state["all_offline_since"] = None

        if game_state["host_name"] is None:
            game_state["host_name"] = name

        game_state["starter_name"] = name
        add_log(f"{name}が復帰した！")

        if game_state["started"]:
            return redirect(url_for("battle", name=name, room_id=active_room_id))
        return redirect(url_for("lobby", name=name, room_id=active_room_id))

    if game_state["started"] and game_state["phase"] != "end" and not game_state.get("rematch_select", False):
        if existing_player:
            existing_player["online"] = True
            existing_player["last_seen"] = time.time()
            existing_player["block_key"] = get_block_key()
            game_state["all_offline_since"] = None
            add_log(f"{name}が復帰した！")
            return redirect(url_for("battle", name=name, room_id=active_room_id))
        return "すでにゲーム開始済みです"

    if existing_player:
        return "同じ名前は使えません"

    if len(players) >= MAX_PLAYERS:
        return "参加人数が上限です"

    job = selected_job

    # ===== 所持している初期装備・初期魔法だけを持ち込みに反映 =====
    if job == "魔術師":
        carried_weapon_ids = []
        selected_weapon_id = ""
        carried_shield_ids = []
        carried_skill_ids = build_carried_skill_ids_for_job(name, job, carried_skill_ids)

    else:
        carried_skill_ids = []
        carried_weapon_ids = build_carried_weapons_for_job(job, carried_weapon_ids, name)
        selected_weapon_id = carried_weapon_ids[0] if carried_weapon_ids else ""
        carried_shield_ids = build_carried_shields_for_job(job, carried_shield_ids, name)

    if len(players) == 0:
        game_state["party_title"] = room_title or "冒険者募集"
        game_state["room_title"] = room_title or "冒険者募集"

    stats = make_status_with_saved_growth(name, job)
    # ===== 武器のattack_bonusは戦闘中に使用した時だけ加算 =====
    # ===== 保存済み成長値は make_status_with_saved_growth で反映済み =====
    players.append({
        "name": name,
        "attack": stats["attack"],
        "hp": stats["hp"],
        "max_hp": stats["max_hp"],
        "magic": stats["magic"],
        "heal": stats["heal"],
        "combo": stats["combo"],
        "job": job,
        "weapon_id": selected_weapon_id,
        "weapon_name": get_weapon_display_name(selected_weapon_id),
        "carried_weapon_ids": carried_weapon_ids,
        "carried_weapons": [
            {
                "id": weapon_id,
                "name": get_weapon_display_name(weapon_id),
                "element": get_weapon(weapon_id).get("element", "none") if get_weapon(weapon_id) else "none"
            }
            for weapon_id in carried_weapon_ids
        ],
        "carried_shield_ids": carried_shield_ids,
        "carried_shields": [
            {
                "id": shield_id,
                "name": get_shield_display_name(shield_id),
                "element": get_shield(shield_id).get("element", "none") if get_shield(shield_id) else "none",
                "effect_type": get_shield(shield_id).get("effect_type", "") if get_shield(shield_id) else "",
                "image": get_shield(shield_id).get("image", f"/static/images/shields/{shield_id}.png") if get_shield(shield_id) else f"/static/images/shields/{shield_id}.png"
            }
            for shield_id in carried_shield_ids
        ],
        "owned_skill_ids": get_owned_skill_ids(name, job),
        "owned_skills": build_owned_skill_list(name, job),
        "carried_skill_ids": carried_skill_ids,
        "carried_skills": build_carried_skill_list(name, job, carried_skill_ids),
        "online": True,
        "last_seen": time.time(),
        "block_key": get_block_key()
    })

    if game_state["host_name"] is None:
        game_state["host_name"] = name

    game_state["starter_name"] = name
    add_log(f"{name}が参加した！")

    # ===== 再戦ジョブ選択中：予定メンバーが全員戻ったら同じ敵で自動再戦 =====
    if game_state.get("rematch_select"):
        expected_names = game_state.get("rematch_expected_names", [])
        current_names = [p["name"] for p in players]

        if expected_names and all(expected_name in current_names for expected_name in expected_names):
            rematch_room_id = game_state.get("rematch_room_id", game_state.get("selected_room", "volcano"))
            start_battle_state(rematch_room_id)
            add_log("全員のジョブ選択が完了。同じ敵と再戦します！")
            return redirect(url_for("battle", name=name, room_id=active_room_id))

    return redirect(url_for("lobby", name=name, room_id=active_room_id))

# ==================================================
# Pセクション：ロビー・受付API
# P-1：受付ページ状態API
# ==================================================

@app.route("/index_state")
def index_state():
    switch_room_context("main", save_to_session=False)
    check_empty_room_reset()
    room_list = get_room_summaries()

    return jsonify({
        "party": get_party_summary(),
        "rooms": room_list,
        "started": game_state["started"]
    })


# ==================================================
# P-2セクション：ロビー看板変更API
# ==================================================

@app.route("/update_room_title", methods=["POST"])
def update_room_title():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    title = request.form.get("title", "").strip()

    if title == "":
        title = "冒険者募集"

    title = title[:40]

    game_state["party_title"] = title
    game_state["room_title"] = title

    add_log(f"募集看板が「{title}」に変更された。")

    return jsonify({
        "ok": True,
        "title": title
    })


# ==================================================
# P-3セクション：ロビー状態API
# ==================================================

@app.route("/lobby_state")
def lobby_state():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    check_empty_room_reset()

    # ===== lobby側勝利終了時の成長処理保証 =====
    if game_state.get("phase") == "end" and game_state.get("winner") == "players":
        if not game_state.get("growth_applied"):
            apply_growth_after_battle()

    return jsonify({
        "players": players,
        "current_players": len(players),
        "max_players": MAX_PLAYERS,
        "host_name": game_state["host_name"],
        "starter_name": game_state["starter_name"],
        "started": game_state["started"],
        "can_start": len(players) > 0,
        "kick_votes": game_state.get("kick_votes", {}),
        "chat_id": game_state["chat_id"],
        "chat_messages": game_state["chat_messages"],
        "rematch_select": game_state.get("rematch_select", False),
        "rematch_expected_names": game_state.get("rematch_expected_names", []),
        "rematch_current_names": [p["name"] for p in players],
        "party_title": game_state.get("party_title", "冒険者募集"),
        "room_title": game_state.get("party_title", "冒険者募集"),
        "room_password": GAME_ROOMS.get(active_room_id, {}).get("room_password", ""),
        "has_password": bool(str(GAME_ROOMS.get(active_room_id, {}).get("room_password", "")).strip()),
        "job_counts": get_job_counts(),
        "available_jobs": ["勇者", "タンク", "魔術師"],
        "available_weapons": build_weapon_option_list(get_player(request.args.get("name", "").strip()).get("job", "") if get_player(request.args.get("name", "").strip()) else "", request.args.get("name", "").strip()),
        "available_shields": build_shield_option_list(get_player(request.args.get("name", "").strip()).get("job", "") if get_player(request.args.get("name", "").strip()) else "", request.args.get("name", "").strip()),
        "available_skills": build_owned_skill_list(request.args.get("name", "").strip(), get_player(request.args.get("name", "").strip()).get("job", "")) if get_player(request.args.get("name", "").strip()) else [],
        "my_name": request.args.get("name", "").strip(),
        "room_id": active_room_id,
        "selected_enemy_room": game_state.get("selected_enemy_room", "random_zako_1"),
        "viewer_in_party": get_player(request.args.get("name", "").strip()) is not None,
        "viewer_blocked": is_device_blocked()[0],
        "party_buffs": get_party_buffs()
    })




@app.route("/change_job", methods=["POST"])
def change_job():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    # ===== ロビー中だけ、自分のジョブを変更できる =====
    if not is_logged_in():
        return jsonify({"ok": False, "message": "ログインが必要です"})

    if game_state.get("started") or game_state.get("phase") != "waiting":
        return jsonify({"ok": False, "message": "戦闘開始後はジョブ変更できません"})

    name = request.form.get("name", "").strip()
    job = request.form.get("job", "").strip()

    if name != get_login_player_id():
        return jsonify({"ok": False, "message": "自分のジョブだけ変更できます"})

    if job not in ["勇者", "タンク", "魔術師"]:
        return jsonify({"ok": False, "message": "不正なジョブです"})

    player = get_player(name)

    if player is None:
        return jsonify({"ok": False, "message": "プレイヤーが存在しません"})

    old_job = player.get("job", "未定")

    if old_job == job:
        return jsonify({"ok": True, "message": "変更なし", "player": player})

    apply_job_to_player(player, job)
    add_log(f"{name}がジョブを{old_job}から{job}に変更した。")

    return jsonify({
        "ok": True,
        "message": "ジョブを変更しました",
        "player": player,
        "job_counts": get_job_counts()
    })


@app.route("/change_equipment", methods=["POST"])
def change_equipment():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    # ===== ロビー中だけ、自分の装備を変更できる =====
    if not is_logged_in():
        return jsonify({"ok": False, "message": "ログインが必要です"})

    if game_state.get("started") or game_state.get("phase") != "waiting":
        return jsonify({"ok": False, "message": "戦闘開始後は装備変更できません"})

    name = request.form.get("name", "").strip()
    weapon_id = request.form.get("weapon_id", "").strip()
    shield_id = request.form.get("shield_id", "").strip()

    # ===== 勇者の持ち込み武器チェックボックスを受け取る =====
    # FormDataで同じ名前を複数appendしているので getlist() で受け取る。
    # 1つ外した場合も、残っているチェックだけを安全に反映する。
    carried_weapon_ids = request.form.getlist("carried_weapon_ids")

    if not carried_weapon_ids:
        carried_weapon_ids_text = request.form.get("carried_weapon_ids_text", "").strip()
        if carried_weapon_ids_text:
            carried_weapon_ids = [
                wid.strip()
                for wid in carried_weapon_ids_text.split(",")
                if wid.strip()
            ]

    # ===== タンクの持ち込み盾チェックボックスを受け取る =====
    carried_shield_ids = request.form.getlist("carried_shield_ids")

    if not carried_shield_ids:
        carried_shield_ids_text = request.form.get("carried_shield_ids_text", "").strip()
        if carried_shield_ids_text:
            carried_shield_ids = [
                sid.strip()
                for sid in carried_shield_ids_text.split(",")
                if sid.strip()
            ]

    # ===== 魔術師の持ち込み魔法チェックボックスを受け取る =====
    carried_skill_ids = request.form.getlist("carried_skill_ids")

    if not carried_skill_ids:
        carried_skill_ids_text = request.form.get("carried_skill_ids_text", "").strip()
        if carried_skill_ids_text:
            carried_skill_ids = [
                skill_id.strip()
                for skill_id in carried_skill_ids_text.split(",")
                if skill_id.strip()
            ]

    if name != get_login_player_id():
        return jsonify({"ok": False, "message": "自分の装備だけ変更できます"})

    player = get_player(name)

    if player is None:
        return jsonify({"ok": False, "message": "プレイヤーが存在しません"})

    old_weapon = player.get("weapon_name", "武器なし")
    old_shield = player.get("shield_name", "") or "盾なし"

    apply_equipment_to_player(player, weapon_id, shield_id, carried_weapon_ids, carried_shield_ids, carried_skill_ids)

    new_weapon = player.get("weapon_name", "武器なし")
    new_shield = player.get("shield_name", "") or "盾なし"

    if player.get("job") == "タンク":
        add_log(f"{name}が装備を変更した。武器:{old_weapon}→{new_weapon} 盾:{old_shield}→{new_shield}")
    elif player.get("job") == "勇者":
        weapon_names = " / ".join([w.get("name", "武器") for w in player.get("carried_weapons", [])]) or "武器なし"
        add_log(f"{name}が持ち込み武器を変更した。{weapon_names}")
    elif player.get("job") == "魔術師":
        skill_names = " / ".join([s.get("name", "魔法") for s in player.get("carried_skills", [])]) or "魔法なし"
        add_log(f"{name}が持ち込み魔法を変更した。{skill_names}")
    else:
        add_log(f"{name}が武器を{old_weapon}から{new_weapon}に変更した。")

    return jsonify({
        "ok": True,
        "message": "装備を変更しました",
        "player": player,
        "available_weapons": build_weapon_option_list(player.get("job", ""), player.get("name", "")),
        "available_shields": build_shield_option_list(player.get("job", ""), player.get("name", "")),
        "available_skills": build_owned_skill_list(player.get("name", ""), player.get("job", ""))
    })


@app.route("/start", methods=["GET", "POST"])
def start():
    battle_room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(battle_room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    name = request.args.get("name", "").strip()
    enemy_room_id = request.args.get(
        "room",
        game_state.get("selected_enemy_room", "random_zako_1")
    ).strip()

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        enemy_room_id = request.form.get("room", enemy_room_id).strip()

    if not name:
        name = game_state["starter_name"]

    if name != game_state["starter_name"]:
        return jsonify({"ok": False, "message": "最後にロビーへ入った人だけが開始できます"})

    if len(players) == 0:
        return jsonify({"ok": False, "message": "参加者がいません"})

    if enemy_room_id not in ROOMS:
        enemy_room_id = game_state.get("selected_enemy_room", "random_zako_1")

    if enemy_room_id not in ROOMS:
        enemy_room_id = "volcano"

    game_state["selected_enemy_room"] = enemy_room_id

    start_battle_state(enemy_room_id)

    if request.method == "GET":
        return redirect(url_for("battle", name=name, room_id=active_room_id))

    return jsonify({"ok": True})


@app.route("/update_selected_enemy_room", methods=["POST"])
def update_selected_enemy_room():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    name = request.form.get("name", "").strip()
    enemy_room = request.form.get("enemy_room", "").strip()

    if get_player(name) is None:
        return jsonify({"ok": False, "message": "プレイヤーが存在しません"})

    if name != game_state.get("starter_name"):
        return jsonify({"ok": False, "message": "開始権がある人だけが敵を選択できます"})

    if game_state.get("started"):
        return jsonify({"ok": False, "message": "戦闘開始後は敵を変更できません"})

    if enemy_room not in ROOMS:
        return jsonify({"ok": False, "message": "存在しない敵グループです"})

    game_state["selected_enemy_room"] = enemy_room

    return jsonify({
        "ok": True,
        "selected_enemy_room": enemy_room
    })


# ==================================================
# P-6セクション：チャットAPI
# ==================================================

@app.route("/send_chat", methods=["POST"])
def send_chat():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    name = request.form.get("name", "").strip()
    message = request.form.get("message", "").strip()

    if get_player(name) is None:
        return jsonify({"ok": False, "message": "プレイヤーが存在しません"})

    if not message:
        return jsonify({"ok": False, "message": "メッセージが空です"})

    message = message[:80]

    add_chat_message(name, message)

    return jsonify({"ok": True})


@app.route("/chat_state")
def chat_state():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    check_empty_room_reset()

    return jsonify({
        "chat_messages": game_state["chat_messages"],
        "chat_id": game_state["chat_id"],
        "phase": game_state["phase"],
        "started": game_state["started"]
    })


# ==================================================
# P-7セクション：接続監視API
# ==================================================

@app.route("/heartbeat", methods=["POST"])
def heartbeat():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    name = request.form.get("name", "").strip()

    player = get_player(name)

    if player is not None:
        player["last_seen"] = time.time()
        player["online"] = True
        game_state["all_offline_since"] = None

    return jsonify({"ok": True})


# ==================================================
# Qセクション：バトルAPI
# Q-1：行動選択・追放・退出
# ==================================================

@app.route("/action", methods=["POST"])
def action():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    if game_state["phase"] != "choice":
        return jsonify({"ok": False, "message": "今は行動選択フェーズではありません"})

    name = request.form.get("name", "").strip()
    act = request.form.get("action", "").strip()
    target = request.form.get("target", "").strip()
    enemy_target = request.form.get("enemy_target", "").strip()
    weapon_id = request.form.get("weapon_id", "").strip()
    shield_id = request.form.get("shield_id", "").strip()
    skill_id = request.form.get("skill_id", "").strip()

    if act not in ["attack", "skill", "heal", "heal_all", "guard", "shield", "taunt"]:
        return jsonify({"ok": False, "message": "不正な行動です"})

    player = get_player(name)

    if player is None:
        return jsonify({"ok": False, "message": "プレイヤーが存在しません"})

    if player["hp"] <= 0:
        return jsonify({"ok": False, "message": "倒れているので行動できません"})

    job = player.get("job")

    allowed_actions = {
        "勇者": ["attack", "heal", "heal_all"],
        "タンク": ["attack", "shield", "heal"],
        "魔術師": ["skill", "heal", "heal_all"]
    }

    if act not in allowed_actions.get(job, ["attack"]):
        return jsonify({"ok": False, "message": "このジョブでは使えない行動です"})

    if name in game_state["actions"]:
        return jsonify({"ok": False, "message": "すでに行動済みです"})

    # ===== 持ち込み武器・盾以外は使えないようにする =====
    if act == "attack" and weapon_id:
        carried_weapon_ids = player.get("carried_weapon_ids", [])
        if carried_weapon_ids and weapon_id not in carried_weapon_ids:
            return jsonify({"ok": False, "message": "持ち込んでいない武器です"})

    if act == "shield" and shield_id:
        carried_shield_ids = player.get("carried_shield_ids", [])
        if carried_shield_ids and shield_id not in carried_shield_ids:
            return jsonify({"ok": False, "message": "持ち込んでいない盾です"})

    if act == "skill":
        skill = get_skill(skill_id)

        if not skill:
            return jsonify({"ok": False, "message": "存在しない魔法です"})

        if skill.get("job") != job:
            return jsonify({"ok": False, "message": "このジョブでは使えない魔法です"})

        if skill_id not in get_owned_skill_ids(name, job):
            return jsonify({"ok": False, "message": "まだ習得していない魔法です"})

        if skill_id not in player.get("carried_skill_ids", []):
            return jsonify({"ok": False, "message": "戦闘に持ち込んでいない魔法です"})

    game_state["actions"][name] = {
        "type": act,
        "target": target,
        "enemy_target": enemy_target,
        "weapon_id": weapon_id,
        "shield_id": shield_id,
        "skill_id": skill_id
    }

    game_state["last_actor"] = name

    if all_actions_selected():
        process_turn()

    return jsonify({"ok": True})


@app.route("/vote_kick", methods=["POST"])
def vote_kick():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    # ===== 新ルール：各プレイヤーがONにできる追放対象は1人だけ =====
    # game_state["kick_votes"] は {"投票者名": "対象者名"} の形で管理する。
    # 同じ対象をもう一度押すとOFF、別の対象を押すと投票先を切り替える。
    voter_name = request.form.get("voter", "").strip()
    target_name = request.form.get("target", "").strip()

    voter = get_player(voter_name)
    target = get_player(target_name)

    if voter is None:
        return jsonify({"ok": False, "message": "投票者が存在しません"})

    if target is None:
        return jsonify({"ok": False, "message": "対象者が存在しません"})

    if voter_name == target_name:
        return jsonify({"ok": False, "message": "自分自身には投票できません"})

    if len(players) < 3:
        return jsonify({"ok": False, "message": "3人以上のときに使用できます"})

    game_state.setdefault("kick_votes", {})

    # ===== 旧形式が残っていた場合の保険：新形式へ初期化 =====
    if any(isinstance(value, list) for value in game_state["kick_votes"].values()):
        game_state["kick_votes"] = {}

    current_target = game_state["kick_votes"].get(voter_name)

    if current_target == target_name:
        # ===== 同じボタンをもう一度押したらOFF =====
        del game_state["kick_votes"][voter_name]
        add_log(f"{voter_name}が{target_name}への追放投票をOFFにした。")
    else:
        # ===== 別対象なら自動で切り替え。一人一票だけON =====
        game_state["kick_votes"][voter_name] = target_name
        add_log(f"{voter_name}が{target_name}への追放投票をONにした。")

    required_votes = len(players) - 1
    current_votes = len([
        player
        for player in players
        if player["name"] != target_name and game_state["kick_votes"].get(player["name"]) == target_name
    ])

    # ===== 対象者以外の全員一致で追放 =====
    if current_votes >= required_votes:
        target_block_key = target.get("block_key")

        if target_block_key:
            kicked_devices[target_block_key] = time.time() + KICK_BLOCK_SECONDS

        players.remove(target)

        game_state.setdefault("left_players", {})
        if target_name in game_state["left_players"]:
            del game_state["left_players"][target_name]

        if target_name in game_state["actions"]:
            del game_state["actions"][target_name]

        # ===== 追放成立後は全員の投票ボタンをOFFへ戻す =====
        game_state["kick_votes"] = {}

        add_log(f"{target_name}は全員一致の投票によりパーティーから退出しました。")

        if game_state["host_name"] == target_name:
            game_state["host_name"] = players[0]["name"] if players else None

        if game_state["starter_name"] == target_name:
            game_state["starter_name"] = players[-1]["name"] if players else None

        if len(players) == 0:
            reset_game()
            return jsonify({"ok": True, "kicked": True, "kick_votes": {}})

        if game_state["phase"] == "choice" and all_actions_selected():
            process_turn()

        return jsonify({
            "ok": True,
            "kicked": True,
            "target": target_name,
            "kick_votes": game_state.get("kick_votes", {})
        })

    return jsonify({
        "ok": True,
        "kicked": False,
        "target": target_name,
        "votes": current_votes,
        "required": required_votes,
        "active_target": game_state["kick_votes"].get(voter_name, ""),
        "kick_votes": game_state.get("kick_votes", {})
    })


@app.route("/leave_party", methods=["POST"])
def leave_party():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    name = request.form.get("name", "").strip()

    player = get_player(name)

    if player is None:
        return jsonify({"ok": False, "message": "プレイヤーが存在しません"})

    saved_player = player.copy()
    saved_player["online"] = False
    saved_player["left_voluntarily"] = True
    saved_player["left_at"] = time.time()

    game_state.setdefault("left_players", {})
    game_state["left_players"][name] = saved_player

    players.remove(player)

    if name in game_state["actions"]:
        del game_state["actions"][name]

    game_state.setdefault("kick_votes", {})

    # ===== 新投票形式：退出者の投票と、退出者を対象にした投票を削除 =====
    if name in game_state["kick_votes"]:
        del game_state["kick_votes"][name]

    for voter_name in list(game_state["kick_votes"].keys()):
        if game_state["kick_votes"].get(voter_name) == name:
            del game_state["kick_votes"][voter_name]

    add_log(f"{name}はパーティーから退出した。")

    if game_state["host_name"] == name:
        game_state["host_name"] = players[0]["name"] if players else None

    if game_state["starter_name"] == name:
        game_state["starter_name"] = players[-1]["name"] if players else None

    if len(players) == 0:
        game_state["all_offline_since"] = time.time()
    elif game_state["phase"] == "choice" and all_actions_selected():
        process_turn()

    return jsonify({"ok": True})



# ==================================================
# Q-4セクション：再戦・ロビー戻り処理
# ==================================================

def restart_battle_with_same_jobs(request_name):
    # ===== 再戦：ジョブ選択へ戻らず、現在のメンバー・ジョブ・装備のまま即再戦 =====
    if game_state["phase"] != "end":
        return False, "まだ戦闘終了ではありません"

    if request_name != game_state["host_name"]:
        return False, "最初の参加者だけが再戦できます"

    if len(players) == 0:
        return False, "参加者がいません"

    rematch_room_id = game_state.get("selected_room", "volcano")

    for player in players:
        player["hp"] = player.get("max_hp", player.get("hp", 1))
        player["combo"] = 0
        player["online"] = True
        player["last_seen"] = time.time()

    start_battle_state(rematch_room_id)
    add_log("同じメンバー・同じジョブで再戦します！")

    return True, ""


def return_room_to_lobby_after_battle(request_name):
    # ===== 終了：部屋は解散せず、現在メンバーのままロビーへ戻る =====
    if game_state["phase"] != "end":
        return False, "まだ戦闘終了ではありません"

    if request_name != game_state["host_name"]:
        return False, "最初の参加者だけがロビーへ戻せます"

    for player in players:
        player["hp"] = player.get("max_hp", player.get("hp", 1))
        player["combo"] = 0
        player["online"] = True
        player["last_seen"] = time.time()

    game_state["started"] = False
    game_state["phase"] = "waiting"
    game_state["turn"] = 1
    game_state["actions"] = {}
    game_state["kick_votes"] = {}
    game_state["winner"] = None
    game_state["last_actor"] = None
    game_state["turn_events"] = []
    game_state["event_id"] += 1
    game_state["boss_hp"] = 0
    game_state["boss_max_hp"] = 0
    game_state["enemies"] = []
    game_state["rematch_select"] = False
    game_state["rematch_expected_names"] = []
    game_state["party_buffs"] = {
        "defend_turns": 0,
        "physical_up_turns": 0,
        "magic_boost_turns": 0
    }
    game_state["active_magic_wall"] = False
    game_state["active_magic_defense"] = False

    add_log("戦闘を終了し、ロビーに戻りました。")

    return True, ""


@app.route("/start_rematch_job_change", methods=["POST"])
def start_rematch_job_change():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    name = request.form.get("name", "").strip()

    ok, message = restart_battle_with_same_jobs(name)

    if not ok:
        return jsonify({"ok": False, "message": message})

    return jsonify({"ok": True, "rematch_select": False})


@app.route("/rematch", methods=["POST"])
def rematch():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    name = request.form.get("name", "").strip()

    ok, message = restart_battle_with_same_jobs(name)

    if not ok:
        return jsonify({"ok": False, "message": message})

    return jsonify({"ok": True, "rematch_select": False})

@app.route("/claim_raid_reward", methods=["POST"])
def claim_raid_reward():
    room_id = request.form.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    name = request.form.get("name", "").strip()
    reward_kind = request.form.get("kind", "").strip()
    reward_id = request.form.get("reward_id", "").strip()

    if not is_logged_in() or name != get_login_player_id():
        return jsonify({"ok": False, "message": "ログイン情報が一致しません"})

    player = get_player(name)

    if player is None:
        return jsonify({"ok": False, "message": "プレイヤーが存在しません"})

    if game_state.get("phase") != "end" or game_state.get("winner") != "players":
        return jsonify({"ok": False, "message": "レイド勝利後ではありません"})

    if not game_state.get("raid_reward_available", False):
        return jsonify({"ok": False, "message": "レイド報酬はありません"})

    game_state.setdefault("raid_reward_claims", {})

    if name in game_state["raid_reward_claims"]:
        return jsonify({"ok": False, "message": "すでにレイド報酬を受け取っています"})

    reward = find_raid_reward_candidate(
        name,
        player.get("job", ""),
        reward_kind,
        reward_id
    )

    if reward is None:
        return jsonify({"ok": False, "message": "選択できない報酬です"})

    if reward.get("owned"):
        return jsonify({"ok": False, "message": "すでに持っている報酬です"})

    granted = grant_drop_reward_to_player(name, reward)

    if not granted:
        return jsonify({"ok": False, "message": "報酬を保存できませんでした"})




    game_state["raid_reward_claims"][name] = {
        "kind": reward_kind,
        "id": reward_id,
        "name": reward.get("name", reward_id)
    }

    add_log(f"{name}はレイド報酬として{reward.get('name', reward_id)}を獲得した！")

    # ===== 報酬受け取り後、部屋を戦闘待機ロビーへ戻す =====
    return_room_to_lobby_after_battle(game_state.get("host_name") or name)

    return jsonify({
        "ok": True,
        "message": f"{reward.get('name', reward_id)}を獲得しました！",
        "reward": reward
    })

@app.route("/finish_battle", methods=["POST"])
def finish_battle():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    name = request.form.get("name", "").strip()

    if game_state["phase"] != "end":
        return jsonify({"ok": False, "message": "まだ戦闘終了ではありません"})

    ok, message = return_room_to_lobby_after_battle(name)

    if not ok:
        return jsonify({"ok": False, "message": message})

    return jsonify({"ok": True, "return_to_lobby": True})


@app.route("/state")
def state():
    room_id = request.form.get("room_id", "").strip() or request.args.get("room_id", "").strip() or get_request_room_id()
    if not switch_room_context(room_id):
        return jsonify({"ok": False, "message": "部屋が見つかりません"})

    was_reset = check_empty_room_reset()

    viewer_name = request.args.get("name", "").strip()
    blocked, remaining = is_device_blocked()

    if not was_reset:
        if game_state["phase"] == "choice":
            if all_actions_selected():
                process_turn()

    # ===== 勝利終了時の成長処理保証 =====
    if game_state.get("phase") == "end" and game_state.get("winner") == "players":
        if not game_state.get("growth_applied"):
            growth_messages = apply_growth_after_battle()

            for msg in growth_messages:
                game_state["turn_events"].append({
                    "text": msg,
                    "state": snapshot()
                })

            game_state["event_id"] += 1

    return jsonify({
        "room_id": active_room_id,
        "players": players,
        "boss_hp": game_state["boss_hp"],
        "boss_max_hp": game_state["boss_max_hp"],
        "room_name": game_state.get("room_name", "ボルケーノドラゴン"),
        "selected_room": game_state.get("selected_room", "volcano"),
        "enemies": game_state.get("enemies", []),
        "log": game_state["log"],
        "turn": game_state["turn"],
        "phase": game_state["phase"],
        "started": game_state["started"],
        "actions": game_state["actions"],
        "kick_votes": game_state.get("kick_votes", {}),
        "left_players": list(game_state.get("left_players", {}).keys()),
        "winner": game_state["winner"],
        "host_name": game_state["host_name"],
        "starter_name": game_state["starter_name"],
        "last_actor": game_state["last_actor"],
        "turn_events": game_state["turn_events"],
        "event_id": game_state["event_id"],
        "chat_messages": game_state["chat_messages"],
        "chat_id": game_state["chat_id"],
        "all_offline_since": game_state.get("all_offline_since"),
        "rematch_select": game_state.get("rematch_select", False),
        # ===== 終了ボタンによる通常解散は追放扱いにしない =====
        "viewer_removed": bool(
            viewer_name and
            get_player(viewer_name) is None and
            game_state.get("started", False) and
            game_state.get("phase") != "waiting" and
            not game_state.get("rematch_select", False)
        ),
        "viewer_blocked": blocked,
        "block_remaining": remaining,
        "party_buffs": get_party_buffs(),

        "raid_reward_available": bool(game_state.get("raid_reward_available", False)),
        "raid_reward_claimed": bool(
            viewer_name and
            viewer_name in game_state.get("raid_reward_claims", {})
        ),
        "raid_reward_candidates": build_raid_reward_candidates_for_player(
            viewer_name,
            get_player(viewer_name).get("job", "")
        ) if (
            viewer_name and
            get_player(viewer_name) is not None and
            game_state.get("raid_reward_available", False)
        ) else []
    })

# ==================================================
# Rセクション：アプリ起動
# ==================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
