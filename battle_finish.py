# ===== Aセクション：初期設定 =====
import random

# app.py から切り出した、ターン終了・勝敗終了・戦闘後成長処理です。
# 既存の players / game_state / 各種共通関数は app.py 側から共有します。

_CONTEXT_PROVIDER = None


def configure_battle_finish(context_provider):
    # ===== app.py 側の現在の部屋コンテキストを参照するための設定 =====
    global _CONTEXT_PROVIDER
    _CONTEXT_PROVIDER = context_provider


def _refresh_context():
    # ===== 複数部屋対応のため、処理開始時に app.py 側の最新状態を取り込む =====
    if _CONTEXT_PROVIDER is None:
        return

    globals().update(_CONTEXT_PROVIDER())


# ===== Bセクション：戦闘後成長イベント処理 =====

def choose_growth_type_for_job(job):
    _refresh_context()
    # ===== ジョブごとに伸びやすい成長項目を変える =====
    # 勇者：攻撃が伸びやすい
    # タンク：HPが伸びやすい
    # 魔術師：MAGICが伸びやすい
    growth_tables = {
        "勇者": ["attack", "attack", "attack", "hp", "magic"],
        "タンク": ["hp", "hp", "hp", "attack", "magic"],
        "魔術師": ["magic", "magic", "magic", "hp", "attack"]
    }

    return random.choice(growth_tables.get(job, ["hp", "attack", "magic"]))


def apply_growth_after_battle():
    _refresh_context()
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
    _refresh_context()
    growth_messages = apply_growth_after_battle()

    for msg in growth_messages:
        events.append({
            "text": msg,
            "state": snapshot()
        })

    return events


# ===== Cセクション：ターン終了・勝敗終了共通処理 =====

def finalize_turn_events(events):
    _refresh_context()
    # ===== 通常ターン終了時のイベント確定 =====
    game_state["last_actor"] = None
    game_state["turn_events"] = events
    game_state["event_id"] += 1


def finish_with_victory(events):
    _refresh_context()
    # ===== 勝利時の共通出口 =====
    events.append({"text": "敵をすべて倒した！", "state": snapshot()})
    events.append({"text": "勝利！", "state": snapshot()})

    add_log("敵をすべて倒した！")
    add_log("勝利！")

    append_growth_events(events)
    append_normal_battle_drop_events(events)

    game_state["phase"] = "end"
    game_state["winner"] = "players"
    game_state["last_actor"] = None
    game_state["turn_events"] = events
    game_state["event_id"] += 1


def finish_with_defeat(events):
    _refresh_context()
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
