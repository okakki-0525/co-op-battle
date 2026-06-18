# ===== Aセクション：敵AI分離モジュール =====

import random


# ===== Bセクション：app.pyから受け取る共通処理 =====

def bind_enemy_ai_context(ctx):
    # ===== enemy_ai.py内でapp.py側の状態・関数を使えるようにする =====
    globals().update(ctx)


def get_shield_users(turn_effects):
    # ===== 盾使用者一覧を取得 =====
    return turn_effects.get("shield_users", set())


def get_taunt_user(turn_effects):
    # ===== 挑発中のプレイヤーを取得 =====
    return turn_effects.get("taunt_user")


def is_magic_defense_active(turn_effects):
    # ===== 魔法防御が有効か判定 =====
    return bool(turn_effects.get("magic_defense_active"))


# ===== Cセクション：盾データ共通処理 =====

def get_action_shield_id(player_name):
    action = game_state.get("actions", {}).get(player_name, {})
    return action.get("shield_id", "")


def get_action_shield(player_name):
    shield_id = get_action_shield_id(player_name)

    if not shield_id:
        return None

    return get_shield(shield_id)


def get_active_party_shield_infos(effect_type=None, trigger=None):
    infos = []

    for info in game_state.get("active_party_shields", []):
        shield_id = info.get("id")
        shield = get_shield(shield_id)

        if not shield:
            continue

        if effect_type and shield.get("effect_type") != effect_type:
            continue

        if trigger and shield.get("trigger") != trigger:
            continue

        infos.append({
            "id": shield_id,
            "user": info.get("user", ""),
            "shield": shield
        })

    return infos


def get_counter_value(player, shield):
    stat_name = shield.get("counter_stat", "attack")
    rate = float(shield.get("counter_rate", 1.0))

    if stat_name == "magic":
        if "get_magic" in globals():
            base = get_magic(player)
        else:
            base = player.get("magic", player.get("heal", 0))
    else:
        if "get_attack" in globals():
            base = get_attack(player)
        else:
            base = player.get("attack", 0)

    return max(1, int(base * rate))


def record_counter_shield_hit(player, damage):
    # ===== カウンターシールド：実際にダメージを受けた時だけ蓄積 =====
    if damage <= 0:
        return

    shield = get_action_shield(player.get("name", ""))

    if not shield:
        return

    if shield.get("effect_type") != "hit_counter":
        return

    turn_effects = game_state.setdefault("_current_turn_effects", {})
    counter_hits = turn_effects.setdefault("counter_shield_hits", {})
    counter_hits[player["name"]] = counter_hits.get(player["name"], 0) + 1


def release_counter_shields(events, turn_effects):
    # ===== カウンターシールド：ターン最後にランダムな敵へ放出 =====
    counter_hits = turn_effects.get("counter_shield_hits", {})

    if not counter_hits:
        return

    for player_name, hit_count in list(counter_hits.items()):
        if hit_count <= 0:
            continue

        player = get_player(player_name)

        if player is None or player.get("hp", 0) <= 0:
            continue

        shield = get_action_shield(player_name)

        if not shield or shield.get("effect_type") != "hit_counter":
            continue

        living_enemies = alive_enemies()

        if not living_enemies:
            continue

        target_enemy = random.choice(living_enemies)
        damage = get_counter_value(player, shield) * hit_count

        damage_enemy(target_enemy, damage)

        shield_name = shield.get("name", "カウンターシールド")
        events.append({
            "text": f"{player_name}の{shield_name}が怒りを放出！",
            "state": snapshot()
        })
        events.append({
            "text": f"{target_enemy['name']}に{damage}ダメージ！",
            "state": snapshot(),
            "target_enemy": target_enemy["id"]
        })
        add_log(f"{player_name}の{shield_name}が怒りを放出！")
        add_log(f"{target_enemy['name']}に{damage}ダメージ！")

        if target_enemy["hp"] <= 0:
            events.append({
                "text": f"{target_enemy['name']}を倒した！",
                "state": snapshot(),
                "target_enemy": target_enemy["id"]
            })
            add_log(f"{target_enemy['name']}を倒した！")

    counter_hits.clear()


def try_auto_shield_avoid(events, target):
    # ===== オートシールド：パーティの誰かへの単体物理攻撃を100％回避 =====
    auto_infos = get_active_party_shield_infos("physical_avoid", "single_physical")

    if not auto_infos:
        return False

    # 複数あっても最初の1枚だけ発動表示
    info = auto_infos[0]
    shield = info["shield"]
    user_name = info.get("user", "")
    avoid_rate = float(shield.get("avoid_rate", 0))

    if avoid_rate < 1.0 and random.random() > avoid_rate:
        return False

    shield_name = shield.get("name", "オートシールド")

    events.append({
        "text": f"{user_name}の{shield_name}が発動！",
        "state": snapshot()
    })
    events.append({
        "text": f"{target['name']}への単体物理攻撃を完全回避した！",
        "state": snapshot()
    })

    add_log(f"{user_name}の{shield_name}が発動！")
    add_log(f"{target['name']}への単体物理攻撃を完全回避した！")

    return True


def try_attack_shield_counter(events, target, enemy):
    # ===== アタックシールド：物理攻撃にATK×1.0で即反撃 =====
    shield = get_action_shield(target.get("name", ""))

    if not shield:
        return

    if shield.get("effect_type") != "physical_counter":
        return

    if enemy is None or enemy.get("hp", 0) <= 0:
        return

    counter_damage = get_counter_value(target, shield)
    damage_enemy(enemy, counter_damage)

    shield_name = shield.get("name", "アタックシールド")
    events.append({
        "text": f"{shield_name}反撃！ {enemy['name']}に{counter_damage}ダメージ！",
        "state": snapshot(),
        "target_enemy": enemy["id"]
    })
    add_log(f"{shield_name}反撃！ {enemy['name']}に{counter_damage}ダメージ！")

    if enemy["hp"] <= 0:
        events.append({
            "text": f"{enemy['name']}を倒した！",
            "state": snapshot(),
            "target_enemy": enemy["id"]
        })
        add_log(f"{enemy['name']}を倒した！")


def trigger_guardian_counter(events, source_enemy, target_type):
    # ===== ガーディアンシールド：魔法攻撃にMAGIC×1.0で反撃 =====
    guardian_infos = get_active_party_shield_infos("magic_counter")

    if not guardian_infos:
        return

    for info in guardian_infos:
        user_name = info.get("user", "")
        user = get_player(user_name)
        shield = info["shield"]

        if user is None or user.get("hp", 0) <= 0:
            continue

        counter_damage = get_counter_value(user, shield)
        shield_name = shield.get("name", "ガーディアンシールド")

        if target_type == "all":
            events.append({
                "text": f"{user_name}の{shield_name}が魔法に全体反撃！",
                "state": snapshot()
            })
            add_log(f"{user_name}の{shield_name}が魔法に全体反撃！")

            for enemy in list(alive_enemies()):
                damage_enemy(enemy, counter_damage)

                events.append({
                    "text": f"{enemy['name']}に{counter_damage}ダメージ！",
                    "state": snapshot(),
                    "target_enemy": enemy["id"]
                })
                add_log(f"{enemy['name']}に{counter_damage}ダメージ！")

                if enemy["hp"] <= 0:
                    events.append({
                        "text": f"{enemy['name']}を倒した！",
                        "state": snapshot(),
                        "target_enemy": enemy["id"]
                    })
                    add_log(f"{enemy['name']}を倒した！")

        else:
            if source_enemy is None or source_enemy.get("hp", 0) <= 0:
                continue

            damage_enemy(source_enemy, counter_damage)

            events.append({
                "text": f"{user_name}の{shield_name}が魔法に反撃！ {source_enemy['name']}に{counter_damage}ダメージ！",
                "state": snapshot(),
                "target_enemy": source_enemy["id"]
            })
            add_log(f"{user_name}の{shield_name}が魔法に反撃！ {source_enemy['name']}に{counter_damage}ダメージ！")

            if source_enemy["hp"] <= 0:
                events.append({
                    "text": f"{source_enemy['name']}を倒した！",
                    "state": snapshot(),
                    "target_enemy": source_enemy["id"]
                })
                add_log(f"{source_enemy['name']}を倒した！")


def apply_damage_to_player(events, target, damage, protected_by_effect=False, damage_category="physical"):
    # ===== プレイヤーへダメージを与え、カウンター蓄積も行う =====
    target["hp"] -= damage
    target["hp"] = max(0, target["hp"])

    record_counter_shield_hit(target, damage)

    reset_combo_if_unprotected_damage(target, protected_by_effect)

    events.append({"text": f"{target['name']}に{damage}ダメージ！", "state": snapshot()})
    add_log(f"{target['name']}に{damage}ダメージ！")

    if target["hp"] == 0:
        events.append({"text": f"{target['name']}は倒れた…", "state": snapshot()})
        add_log(f"{target['name']}は倒れた…")


def handle_single_physical_attack(events, enemy, target, base_dmg, turn_effects, attacker_text):
    # ===== 単体物理攻撃の共通処理 =====
    events.append({"text": attacker_text, "state": snapshot(), "target_enemy": enemy["id"] if enemy else None})
    add_log(attacker_text)

    # ===== ディフェンダー回避 =====
    if is_defender_active(target["name"]):
        events.append({
            "text": f"{target['name']}はディフェンダーで物理攻撃を回避した！",
            "state": snapshot()
        })
        add_log(f"{target['name']}はディフェンダーで物理攻撃を回避した！")
        return

    # ===== オートシールド回避 =====
    if try_auto_shield_avoid(events, target):
        return

    shield_users = get_shield_users(turn_effects)

    if target["name"] in shield_users:
        shield_damage = max(1, int(base_dmg * 0.2))
        shield_damage, resist_weapon_name = apply_used_weapon_resist(target, shield_damage, "none", "single")

        if resist_weapon_name:
            events.append({
                "text": f"{target['name']}の{resist_weapon_name}が攻撃を受け流した！",
                "state": snapshot()
            })
            add_log(f"{target['name']}の{resist_weapon_name}が攻撃を受け流した！")

        shield_name = get_selected_shield_name(target["name"])
        events.append({"text": f"{target['name']}は{shield_name}で受け止めた！", "state": snapshot()})

        apply_damage_to_player(
            events,
            target,
            shield_damage,
            protected_by_effect=True,
            damage_category="physical"
        )

        try_attack_shield_counter(events, target, enemy)

    else:
        dmg = physical_damage(target, base_dmg)
        dmg, resist_weapon_name = apply_used_weapon_resist(target, dmg, "none", "single")

        if resist_weapon_name:
            events.append({
                "text": f"{target['name']}の{resist_weapon_name}が攻撃を受け流した！",
                "state": snapshot()
            })
            add_log(f"{target['name']}の{resist_weapon_name}が攻撃を受け流した！")

        apply_damage_to_player(
            events,
            target,
            dmg,
            protected_by_effect=bool(resist_weapon_name),
            damage_category="physical"
        )


def handle_all_magic_attack(events, source_enemy, targets, base_dmg, element, skill_name, magic_defense_active):
    # ===== 全体魔法攻撃の共通処理 =====
    if magic_defense_active:
        base_dmg = int(base_dmg * 0.5)
        events.append({"text": f"魔法防御が{skill_name}を軽減した！", "state": snapshot()})
        add_log(f"魔法防御が{skill_name}を軽減した！")

    shield_effects = get_active_party_shield_effects(element, "magic")
    for effect in shield_effects:
        events.append({"text": effect["message"], "state": snapshot()})
        add_log(effect["message"])

    damage_records = []

    for target in targets:
        dmg = magic_damage(target, base_dmg)

        before_magic_blade = dmg
        dmg = apply_magic_blade_reduction(target["name"], dmg)
        magic_blade_reduced = dmg < before_magic_blade

        if magic_blade_reduced:
            events.append({
                "text": f"{target['name']}のマジックブレードが魔法を軽減した！",
                "state": snapshot()
            })
            add_log(f"{target['name']}のマジックブレードが魔法を軽減した！")

        dmg = apply_shield_effects_to_damage(dmg, shield_effects)
        dmg, resist_weapon_name = apply_used_weapon_resist(target, dmg, element, "all")

        if resist_weapon_name:
            events.append({
                "text": f"{target['name']}の{resist_weapon_name}が{element}属性攻撃を受け流した！",
                "state": snapshot()
            })
            add_log(f"{target['name']}の{resist_weapon_name}が{element}属性攻撃を受け流した！")

        protected_by_effect = bool(
            magic_defense_active or
            shield_effects or
            magic_blade_reduced or
            resist_weapon_name
        )

        damage_records.append((target, dmg, protected_by_effect))

    for target, dmg, protected_by_effect in damage_records:
        apply_damage_to_player(
            events,
            target,
            dmg,
            protected_by_effect=protected_by_effect,
            damage_category="magic"
        )

    trigger_guardian_counter(events, source_enemy, "all")


# ===== E-7セクション：敵別行動 =====

def process_volcano_dragon_action(ctx, events, targets, turn_effects):
    bind_enemy_ai_context(ctx)
    game_state["_current_turn_effects"] = turn_effects

    taunt_user = get_taunt_user(turn_effects)
    magic_defense_active = is_magic_defense_active(turn_effects)
    enemy = choose_attack_enemy()

    if enemy is None:
        return

    if game_state["same_boss_action_count"] >= 2:
        if game_state["last_boss_action"] == "breath":
            boss_action = "attack"
            selected_skill = choose_enemy_skill(enemy, "single")
        else:
            boss_action = "breath"
            selected_skill = choose_enemy_skill(enemy, "all")
    else:
        selected_skill = choose_enemy_skill(enemy)
        if selected_skill.get("target") == "all":
            boss_action = "breath"
        else:
            boss_action = "attack"

    if boss_action == "breath":
        if game_state["last_boss_action"] == "breath":
            events.append({"text": "ボス「まとめて燃やし尽くしてやるわ！」", "state": snapshot()})
            add_log("ボス「まとめて燃やし尽くしてやるわ！」")

        events.append({"text": "ボスの全体ブレス攻撃！", "state": snapshot(), "target_enemy": enemy["id"]})
        add_log("ボスの全体ブレス攻撃！")

        base_dmg = get_enemy_skill_damage(selected_skill, 30, 58)

        handle_all_magic_attack(
            events,
            enemy,
            targets,
            base_dmg,
            "fire",
            "ブレス",
            magic_defense_active
        )

    else:
        if game_state["last_boss_action"] == "attack":
            events.append({"text": "ボス「全身を食いちぎってやるわ！」", "state": snapshot()})
            add_log("ボス「全身を食いちぎってやるわ！」")

        target = random.choice(targets)

        if taunt_user:
            taunt_player = get_player(taunt_user)

            if (
                taunt_player is not None and
                taunt_player["hp"] > 0 and
                taunt_player.get("online", True)
            ):
                target = taunt_player

        base_dmg = get_enemy_skill_damage(selected_skill, 28, 55)

        handle_single_physical_attack(
            events,
            enemy,
            target,
            base_dmg,
            turn_effects,
            "ボスの攻撃！"
        )

    release_counter_shields(events, turn_effects)

    if game_state["last_boss_action"] == boss_action:
        game_state["same_boss_action_count"] += 1
    else:
        game_state["last_boss_action"] = boss_action
        game_state["same_boss_action_count"] = 1

    game_state.pop("_current_turn_effects", None)


def process_training_golem_action(ctx, events, targets, turn_effects):
    bind_enemy_ai_context(ctx)
    game_state["_current_turn_effects"] = turn_effects

    taunt_user = get_taunt_user(turn_effects)
    enemy = choose_attack_enemy()

    if enemy is None or enemy["hp"] <= 0:
        return

    target = random.choice(targets)

    if taunt_user:
        taunt_player = get_player(taunt_user)

        if (
            taunt_player is not None and
            taunt_player["hp"] > 0 and
            taunt_player.get("online", True)
        ):
            target = taunt_player

    selected_skill = choose_enemy_skill(enemy, "single")
    skill_name = selected_skill.get("name", "打撃")
    base_dmg = get_enemy_skill_damage(selected_skill, 12, 24)

    handle_single_physical_attack(
        events,
        enemy,
        target,
        base_dmg,
        turn_effects,
        f"訓練用ゴーレムの{skill_name}！"
    )

    release_counter_shields(events, turn_effects)
    game_state.pop("_current_turn_effects", None)


def process_goblin_action(ctx, events, turn_effects):
    bind_enemy_ai_context(ctx)
    game_state["_current_turn_effects"] = turn_effects

    taunt_user = get_taunt_user(turn_effects)
    magic_defense_active = is_magic_defense_active(turn_effects)

    for enemy in list(alive_enemies()):
        if len(alive_enemies()) == 0:
            break

        targets = online_alive_players()

        if not targets:
            break

        if enemy["hp"] <= 0:
            continue

        role = enemy.get("role")

        if role == "fighter":
            target = random.choice(targets)

            if taunt_user:
                taunt_player = get_player(taunt_user)

                if (
                    taunt_player is not None and
                    taunt_player["hp"] > 0 and
                    taunt_player.get("online", True)
                ):
                    target = taunt_player

            fighter_skill = choose_enemy_skill(enemy, "single")
            fighter_skill_name = fighter_skill.get("name", "斬りつけ")
            base_dmg = get_enemy_skill_damage(fighter_skill, 20, 35)

            handle_single_physical_attack(
                events,
                enemy,
                target,
                base_dmg,
                turn_effects,
                f"{enemy['name']}の{fighter_skill_name}！"
            )

        elif role == "mage":
            mage_skill = choose_enemy_skill(enemy, "all")
            mage_skill_name = mage_skill.get("name", "闇魔法")
            mage_element = mage_skill.get("element", "dark")

            events.append({"text": f"{enemy['name']}の{mage_skill_name}！", "state": snapshot(), "target_enemy": enemy["id"]})
            add_log(f"{enemy['name']}の{mage_skill_name}！")

            base_dmg = get_enemy_skill_damage(mage_skill, 14, 26)

            handle_all_magic_attack(
                events,
                enemy,
                targets,
                base_dmg,
                mage_element,
                mage_skill_name,
                magic_defense_active
            )

        elif role == "healer":
            injured = [e for e in alive_enemies() if e["hp"] < e["max_hp"]]

            if injured:
                target_enemy = min(injured, key=lambda e: e["hp"])
                heal_skill = choose_enemy_skill(enemy, "ally_heal")
                heal_amount = get_enemy_skill_heal(heal_skill, 22, 38)

                target_enemy["hp"] += heal_amount
                target_enemy["hp"] = min(target_enemy["hp"], target_enemy["max_hp"])
                game_state["boss_hp"] = sum(e["hp"] for e in game_state.get("enemies", []))

                events.append({"text": f"{enemy['name']}の回復！", "state": snapshot(), "target_enemy": enemy["id"]})
                events.append({"text": f"{target_enemy['name']}が{heal_amount}回復！", "state": snapshot(), "target_enemy": target_enemy["id"]})

                add_log(f"{target_enemy['name']}が{heal_amount}回復！")
            else:
                target = random.choice(targets)

                if taunt_user:
                    taunt_player = get_player(taunt_user)

                    if (
                        taunt_player is not None and
                        taunt_player["hp"] > 0 and
                        taunt_player.get("online", True)
                    ):
                        target = taunt_player

                attack_skill = choose_enemy_skill(enemy, "single")
                attack_skill_name = attack_skill.get("name", "杖攻撃")
                base_dmg = get_enemy_skill_damage(attack_skill, 8, 16)

                handle_single_physical_attack(
                    events,
                    enemy,
                    target,
                    base_dmg,
                    turn_effects,
                    f"{enemy['name']}の{attack_skill_name}！"
                )

    release_counter_shields(events, turn_effects)
    game_state.pop("_current_turn_effects", None)
