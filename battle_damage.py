# ===== Aセクション：初期設定 =====
# battle_engine.py から切り出した、ダメージ・防御・反撃処理です。
# 既存の players / game_state / 各種共通関数は app.py 側から共有します。

_CONTEXT_PROVIDER = None


def configure_battle_damage(context_provider):
    # ===== app.py 側の現在の部屋コンテキストを参照するための設定 =====
    global _CONTEXT_PROVIDER
    _CONTEXT_PROVIDER = context_provider


def _refresh_context():
    # ===== 複数部屋対応のため、処理開始時に app.py 側の最新状態を取り込む =====
    if _CONTEXT_PROVIDER is None:
        return

    globals().update(_CONTEXT_PROVIDER())


# ===== Bセクション：ターゲット選択・防御判定 =====

def choose_enemy_single_target(targets, turn_effects):
    _refresh_context()
    # ===== 挑発中のタンクがいれば優先して狙う =====
    taunt_user = turn_effects.get("taunt_user")

    if taunt_user:
        taunt_player = get_player(taunt_user)
        if taunt_player is not None and taunt_player.get("hp", 0) > 0 and taunt_player in targets:
            return taunt_player

    return random.choice(targets) if targets else None


def is_physical_avoid_active():
    _refresh_context()
    # ===== オートシールドなど、物理攻撃を完全回避する盾が有効か判定 =====
    for info in game_state.get("active_party_shields", []):
        shield = get_shield(info.get("id"))
        if not shield:
            continue

        if shield.get("effect_type") == "physical_avoid":
            return shield

    return None


def is_tank_basic_shield_physical_avoid_active(target):
    _refresh_context()
    # ===== シールド行動中のタンク本人は、物理攻撃を100％回避 =====
    # 盾の基本防御は行動順に関係なく、選択ターンの最初から有効。
    # オートシールドはパーティ全体回避、アタックシールドは反撃盾として別処理に任せる。
    if target is None:
        return None

    if target.get("job") != "タンク":
        return None

    target_name = target.get("name", "")
    action = game_state.get("actions", {}).get(target_name, {})

    if action.get("type") != "shield":
        return None

    shield_id = action.get("shield_id", "")
    shield = get_shield(shield_id)

    if not shield:
        return {"name": "シールド"}

    # ===== すべての盾で、タンク本人への物理攻撃は100％回避 =====
    # オートシールドやアタックシールドも例外にしない。
    return shield



# ===== Cセクション：盾反撃処理 =====

def process_counter_after_enemy_attack(enemy, target, attack_category, target_type, events, original_damage=0):
    _refresh_context()
    # ===== 盾による反撃・蓄積処理 =====
    if enemy is None or enemy.get("hp", 0) <= 0:
        return

    # ===== アタックシールド：単体物理攻撃を受けた時に反撃 =====
    if target_type == "single" and attack_category == "physical" and target is not None:
        if is_attack_shield_active(target.get("name", "")):
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

          
    # ===== カウンターソード：単体物理攻撃を受けた時に反撃 =====
    if target_type == "single" and attack_category == "physical" and target is not None:
        target_name = target.get("name", "")
        weapon_id = get_used_weapon_id_this_turn(target)

        if weapon_id == "counter_sword":
            counter_damage = max(1, int(get_attack(target) * 1.0))
            damage_enemy(enemy, counter_damage)

            events.append({
                "text": f"{target_name}のカウンターソードが反撃！ {enemy['name']}に{counter_damage}ダメージ！",
                "state": snapshot(),
                "target_enemy": enemy.get("id"),
                "flash_enemy": True,
                "flash_type": "physical",
                "flash_element": "none"
            })

            add_log(f"{target_name}のカウンターソードが反撃！ {enemy['name']}に{counter_damage}ダメージ！")

    # ===== カウンターシールド：本来受けるはずだったダメージを蓄積 =====
    if target is not None:
        target_name = target.get("name", "")

        for info in game_state.get("active_party_shields", []):
            if info.get("user") != target_name:
                continue

            shield = get_shield(info.get("id"))
            if not shield or shield.get("effect_type") != "hit_counter":
                continue

            damage_pool = game_state.setdefault("active_counter_shield_damage", {})
            stored_damage = int(damage_pool.get(target_name, 0)) + max(0, int(original_damage))
            damage_pool[target_name] = stored_damage

            events.append({
                "text": f"{target_name}の{shield.get('name', 'カウンターシールド')}がダメージを蓄積した！",
                "state": snapshot()
            })
            add_log(f"{target_name}の{shield.get('name', 'カウンターシールド')}がダメージを蓄積した！")

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


# ===== Dセクション：魔法防御判定 =====

def turn_effects_global_magic_defense_active():
    _refresh_context()
    # ===== 魔法防御がこのターン中に展開されているか判定 =====
    return bool(game_state.get("active_magic_defense", False))



# ===== Eセクション：敵からプレイヤーへのダメージ処理 =====

def apply_enemy_damage_to_player(enemy, target, base_damage, attack_category, element, target_type, events):
    _refresh_context()
    # ===== 敵からプレイヤーへのダメージ処理 =====
    if target is None or target.get("hp", 0) <= 0:
        return

    damage = int(base_damage)
    protected_by_effect = False

    if attack_category == "physical":
        avoid_shield = is_physical_avoid_active()
        if avoid_shield:
            events.append({
                "text": f"{avoid_shield.get('name', 'オートシールド')}が物理攻撃を防いだ！",
                "state": snapshot()
            })
            add_log(f"{avoid_shield.get('name', 'オートシールド')}が物理攻撃を防いだ！")
            process_counter_after_enemy_attack(enemy, target, attack_category, target_type, events, original_damage=base_damage)
            reset_combo_if_unprotected_damage(target, protected_by_effect=True)
            return

        tank_shield = is_tank_basic_shield_physical_avoid_active(target)
        if tank_shield:
            events.append({
                "text": f"{target['name']}の{tank_shield.get('name', 'シールド')}が物理攻撃を防いだ！",
                "state": snapshot()
            })
            add_log(f"{target['name']}の{tank_shield.get('name', 'シールド')}が物理攻撃を防いだ！")
            process_counter_after_enemy_attack(enemy, target, attack_category, target_type, events, original_damage=base_damage)
            reset_combo_if_unprotected_damage(target, protected_by_effect=True)
            return

        if is_defender_active(target.get("name", "")):
            events.append({
                "text": f"{target['name']}はディフェンダーで物理攻撃を受け流した！",
                "state": snapshot()
            })
            add_log(f"{target['name']}はディフェンダーで物理攻撃を受け流した！")
            reset_combo_if_unprotected_damage(target, protected_by_effect=True)
            return

        if is_bazooka_active(target.get("name", "")):
            events.append({
                "text": f"{target['name']}はバズーカを構えて物理攻撃を回避した！",
                "state": snapshot()
            })
            add_log(f"{target['name']}はバズーカを構えて物理攻撃を回避した！")
            reset_combo_if_unprotected_damage(target, protected_by_effect=True)
            return

        damage = physical_damage(target, damage)

    elif attack_category == "magic":
        # ===== ミラーソード：使用ターン中、受けた単体魔法攻撃を反射 =====
        if target_type == "single" and get_used_weapon_id_this_turn(target) == "mirror_sword":
            weapon_id = get_used_weapon_id_this_turn(target)
            weapon = get_weapon(weapon_id)

            reflect_rate = float(weapon.get("power_rate", 2.0)) if weapon else 2.0
            reflect_damage = max(1, int(damage * reflect_rate))

            damage_enemy(enemy, reflect_damage)

            events.append({
                "text": f"{target['name']}のミラーソードが単体魔法を反射！",
                "state": snapshot(),
                "target_enemy": enemy.get("id"),
                "flash_enemy": True,
                "flash_type": "magic",
                "flash_element": element
            })

            events.append({
                "text": f"{enemy['name']}に{reflect_damage}反射ダメージ！",
                "state": snapshot(),
                "target_enemy": enemy.get("id")
            })

            add_log(f"{target['name']}のミラーソードが単体魔法を反射！")
            add_log(f"{enemy['name']}に{reflect_damage}反射ダメージ！")

            if enemy.get("hp", 0) <= 0:
                events.append({
                    "text": f"{enemy['name']}を倒した！",
                    "state": snapshot(),
                    "target_enemy": enemy.get("id")
                })
                add_log(f"{enemy['name']}を倒した！")

            reset_combo_if_unprotected_damage(target, protected_by_effect=True)
            return

        # ===== リフレクト：単体魔法攻撃を反射 =====
        if (
            target_type == "single"
            and target.get("name", "")
            in game_state.get("active_reflect_targets", [])
        ):

            reflect_damage = max(1, int(damage))

            damage_enemy(enemy, reflect_damage)

            events.append({
                "text": f"{target['name']}のリフレクトが単体魔法を反射！",
                "state": snapshot(),
                "target_enemy": enemy.get("id"),
                "flash_enemy": True,
                "flash_type": "magic",
                "flash_element": element
            })

            events.append({
                "text": f"{enemy['name']}に{reflect_damage}反射ダメージ！",
                "state": snapshot(),
                "target_enemy": enemy.get("id")
            })

            add_log(f"{target['name']}のリフレクトが単体魔法を反射！")
            add_log(f"{enemy['name']}に{reflect_damage}反射ダメージ！")

            if enemy.get("hp", 0) <= 0:
                events.append({
                    "text": f"{enemy['name']}を倒した！",
                    "state": snapshot(),
                    "target_enemy": enemy.get("id")
                })

                add_log(f"{enemy['name']}を倒した！")

            reset_combo_if_unprotected_damage(
                target,
                protected_by_effect=True
            )

            return


        # ===== リフレクトシールド：単体魔法攻撃を反射 =====
        if target_type == "single":
            for info in game_state.get("active_party_shields", []):
                shield = get_shield(info.get("id"))

                if not shield:
                    continue

                if shield.get("effect_type") != "single_magic_reflect":
                    continue

                user_name = info.get("user", "タンク")
                shield_name = shield.get("name", "リフレクトシールド")

                reflect_damage = max(1, int(damage * 2.0))
                damage_enemy(enemy, reflect_damage)

                events.append({
                    "text": f"{user_name}の{shield_name}が単体魔法を反射！",
                    "state": snapshot(),
                    "target_enemy": enemy.get("id"),
                    "flash_enemy": True,
                    "flash_type": "magic",
                    "flash_element": element
                })

                events.append({
                    "text": f"{enemy['name']}に{reflect_damage}反射ダメージ！",
                    "state": snapshot(),
                    "target_enemy": enemy.get("id")
                })

                add_log(f"{user_name}の{shield_name}が単体魔法を反射！")
                add_log(f"{enemy['name']}に{reflect_damage}反射ダメージ！")

                if enemy.get("hp", 0) <= 0:
                    events.append({
                        "text": f"{enemy['name']}を倒した！",
                        "state": snapshot(),
                        "target_enemy": enemy.get("id")
                    })
                    add_log(f"{enemy['name']}を倒した！")

                reset_combo_if_unprotected_damage(target, protected_by_effect=True)
                return

        damage = magic_damage(target, damage)

        if turn_effects_global_magic_defense_active():
            skill = get_skill("magic_defense")
            skill_name = skill.get("name", "魔法障壁") if skill else "魔法障壁"
            cut_rate = float(skill.get("cut_rate", 0.40)) if skill else 0.40
            cut_rate = max(0.0, min(cut_rate, 0.90))

            damage = max(1, int(damage * (1 - cut_rate)))
            protected_by_effect = True

            events.append({
                "text": f"{skill_name}が魔法ダメージを軽減した！",
                "state": snapshot()
            })
            add_log(f"{skill_name}が魔法ダメージを軽減した！")

        if is_magic_blade_active(target.get("name", "")):
            damage = apply_magic_blade_reduction(target.get("name", ""), damage)
            protected_by_effect = True

    weapon_reduced_damage, weapon_name = apply_used_weapon_resist(target, damage, element, target_type)
    if weapon_name:
        damage = weapon_reduced_damage
        protected_by_effect = True
        events.append({
            "text": f"{target['name']}の{weapon_name}が属性ダメージを軽減した！",
            "state": snapshot()
        })
        add_log(f"{target['name']}の{weapon_name}が属性ダメージを軽減した！")

    shield_effects = get_active_party_shield_effects(element, attack_category, target_type)
    if shield_effects:
        damage = apply_shield_effects_to_damage(damage, shield_effects)
        protected_by_effect = True
        for effect in shield_effects:
            events.append({
                "text": effect.get("message", "盾がダメージを軽減した！"),
                "state": snapshot()
            })
            add_log(effect.get("message", "盾がダメージを軽減した！"))


    target_name = target.get("name", "")

    # ===== ヒーリングシールド蓄積 =====
    if target_name in game_state.get("active_healing_shield_users", []):

        current = game_state["healing_shield_damage"].get(
            target_name,
            0
        )

        game_state["healing_shield_damage"][target_name] = (
            current + damage
        )

    if target_name in game_state.get("active_aegis_users", []):
        game_state["active_aegis_users"].remove(target_name)
        game_state["aegis_used"] = True

        events.append({
            "text": f"{target_name}はイージスシールドで攻撃を無効化した！",
            "state": snapshot()
        })
        add_log(f"{target_name}はイージスシールドで攻撃を無効化した！")
        reset_combo_if_unprotected_damage(target, protected_by_effect=True)
        return


    # ===== ガッツシールド =====
    fatal_damage = int(target.get("hp", 0)) - int(damage) <= 0

    if fatal_damage and target_name in game_state.get("active_guts_users", []):

        all_attack_batch_active = bool(
            game_state.get("guts_all_attack_batch_active", False)
        )

        all_attack_batch_triggered = bool(
            game_state.get("guts_all_attack_batch_triggered", False)
        )

        can_use_guts = (
            not game_state.get("guts_used", False)
            or (
                target_type == "all"
                and all_attack_batch_active
                and all_attack_batch_triggered
            )
        )

        if can_use_guts:

            if target_name in game_state.get("active_guts_users", []):
                game_state["active_guts_users"].remove(target_name)

            game_state["guts_used"] = True

            if target_type == "all" and all_attack_batch_active:
                game_state["guts_all_attack_batch_triggered"] = True

            target["hp"] = 1

            events.append({
                "text": f"{target_name}はガッツシールドの力でHP1で踏みとどまった！",
                "state": snapshot()
            })

            add_log(
                f"{target_name}はガッツシールドの力でHP1で踏みとどまった！"
            )

            reset_combo_if_unprotected_damage(
                target,
                protected_by_effect=True
            )

            return


    target["hp"] = max(0, int(target.get("hp", 0)) - damage)

    events.append({
        "text": f"{target['name']}に{damage}ダメージ！",
        "state": snapshot()
    })
    add_log(f"{target['name']}に{damage}ダメージ！")

    # ===== 生き残った場合だけ反撃する =====
    if target.get("hp", 0) > 0:
        process_counter_after_enemy_attack(enemy, target, attack_category, target_type, events, original_damage=base_damage)

    # ===== 無防備にダメージを受けた場合は勇者コンボ解除 =====
    if damage > 0:
        reset_combo_if_unprotected_damage(target, protected_by_effect=protected_by_effect)

    # ===== 反撃後に死亡判定 =====
    if target["hp"] <= 0:
        events.append({
            "text": f"{target['name']}は倒れた！",
            "state": snapshot()
        })
        add_log(f"{target['name']}は倒れた！")