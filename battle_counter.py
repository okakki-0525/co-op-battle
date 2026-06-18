# ===== Aセクション：初期設定 =====
# battle_damage.py から切り出した、盾反撃専用処理です。
# 既存の players / game_state / 各種共通関数は app.py 側から共有します。

_CONTEXT_PROVIDER = None


def configure_battle_counter(context_provider):
    # ===== app.py 側の現在の部屋コンテキストを参照するための設定 =====
    global _CONTEXT_PROVIDER
    _CONTEXT_PROVIDER = context_provider


def _refresh_context():
    # ===== 複数部屋対応のため、処理開始時に app.py 側の最新状態を取り込む =====
    if _CONTEXT_PROVIDER is None:
        return

    globals().update(_CONTEXT_PROVIDER())


# ===== Bセクション：盾反撃処理 =====

def process_counter_after_enemy_attack(enemy, target, attack_category, target_type, events):
    _refresh_context()
    # ===== 盾による反撃処理 =====
    if enemy is None or enemy.get("hp", 0) <= 0:
        return

    if target_type == "single" and attack_category == "physical" and is_attack_shield_active(target.get("name", "")):
        shield_name = get_selected_shield_name(target.get("name", ""))
        counter_damage = max(1, int(get_attack(target) * 0.8))
        damage_enemy(enemy, counter_damage)
        events.append({
            "text": f"{target['name']}の{shield_name}が反撃！ {enemy['name']}に{counter_damage}ダメージ！",
            "state": snapshot(),
            "target_enemy": enemy.get("id"),
            "flash_enemy": True,
            "flash_type": "physical",
            "flash_element": "none"
        })
        add_log(f"{target['name']}の{shield_name}が反撃！ {enemy['name']}に{counter_damage}ダメージ！")

    # ===== カウンターシールド：攻撃対象になった回数に応じて反撃 =====
    if target is not None:
        target_name = target.get("name", "")

        for info in game_state.get("active_party_shields", []):
            if info.get("user") != target_name:
                continue

            shield = get_shield(info.get("id"))
            if not shield or shield.get("effect_type") != "hit_counter":
                continue

            hits = game_state.setdefault("active_counter_shield_hits", {})
            hit_count = int(hits.get(target_name, 0)) + 1
            hits[target_name] = hit_count

            counter_damage = max(1, int(get_attack(target) * (0.45 + 0.20 * hit_count)))
            damage_enemy(enemy, counter_damage)
            events.append({
                "text": f"{target_name}の{shield.get('name', 'カウンターシールド')}が{hit_count}回目の反撃！ {enemy['name']}に{counter_damage}ダメージ！",
                "state": snapshot(),
                "target_enemy": enemy.get("id"),
                "flash_enemy": True,
                "flash_type": "physical",
                "flash_element": "none"
            })
            add_log(f"{target_name}の{shield.get('name', 'カウンターシールド')}が{hit_count}回目の反撃！ {enemy['name']}に{counter_damage}ダメージ！")

    if attack_category == "magic":
        for info in game_state.get("active_party_shields", []):
            shield = get_shield(info.get("id"))
            if not shield or shield.get("effect_type") != "magic_counter":
                continue

            user_name = info.get("user", "タンク")
            counter_damage = 25
            user = get_player(user_name)
            if user is not None:
                counter_damage = max(1, int(get_attack(user) * 0.8))

            damage_enemy(enemy, counter_damage)
            events.append({
                "text": f"{user_name}の{shield.get('name', 'ガーディアンシールド')}が魔法に反撃！ {enemy['name']}に{counter_damage}ダメージ！",
                "state": snapshot(),
                "target_enemy": enemy.get("id"),
                "flash_enemy": True,
                "flash_type": "magic",
                "flash_element": "none"
            })
            add_log(f"{user_name}の{shield.get('name', 'ガーディアンシールド')}が魔法に反撃！ {enemy['name']}に{counter_damage}ダメージ！")



