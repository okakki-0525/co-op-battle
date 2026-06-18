# ===== Aセクション：初期設定 =====
# app.py から切り出した戦闘処理です。
# 既存の players / game_state / 各種共通関数は app.py 側から共有します。


from battle_damage import (
    configure_battle_damage,
    choose_enemy_single_target,
    apply_enemy_damage_to_player
)
from battle_finish import (
    configure_battle_finish,
    finalize_turn_events,
    finish_with_victory,
    finish_with_defeat
)
_CONTEXT_PROVIDER = None


def configure_battle_engine(context_provider):
    # ===== app.py 側の現在の部屋コンテキストを参照するための設定 =====
    global _CONTEXT_PROVIDER
    _CONTEXT_PROVIDER = context_provider

    # ===== 分離した戦闘系モジュールにも同じコンテキストを渡す =====
    configure_battle_damage(context_provider)
    configure_battle_finish(context_provider)


def _refresh_context():
    # ===== 複数部屋対応のため、処理開始時に app.py 側の最新状態を取り込む =====
    if _CONTEXT_PROVIDER is None:
        return

    globals().update(_CONTEXT_PROVIDER())


# ===== Eセクション：バトル処理 =====

def create_turn_effects():
    _refresh_context()
    # ===== 1ターン中だけ有効な効果をまとめて管理 =====
    return {
        "shield_users": set(),
        "taunt_user": None,
        "magic_defense_active": False,
        "magic_wall_active": False,
        "counter_shield_hits": {}
    }



def calculate_action_order_value(current_hp, max_hp):
    _refresh_context()
    # ===== 現在HP割合を基本に、少しだけランダム幅を足して行動値を作る =====
    if max_hp <= 0:
        hp_ratio_score = 0
    else:
        hp_ratio_score = (max(0, current_hp) / max_hp) * 100

    random_bonus = random.randint(-10, 10)
    return hp_ratio_score + random_bonus, hp_ratio_score, random_bonus


def build_turn_action_order():
    _refresh_context()
    # ===== 敵味方をまとめて、1ターン内の行動順を決める =====
    # 行動値 = 最大HPに対する現在HP割合 × 100 + ランダム(-10〜10)
    order = []

    online_players()

    for player in alive_players():
        if not player.get("online", True):
            continue

        if player.get("name") not in game_state.get("actions", {}):
            continue

        value, hp_score, random_bonus = calculate_action_order_value(
            int(player.get("hp", 0)),
            int(player.get("max_hp", 1))
        )

        order.append({
            "kind": "player",
            "actor": player,
            "name": player.get("name", "プレイヤー"),
            "value": value,
            "hp_score": hp_score,
            "random_bonus": random_bonus
        })

    for enemy in alive_enemies():
        value, hp_score, random_bonus = calculate_action_order_value(
            int(enemy.get("hp", 0)),
            int(enemy.get("max_hp", 1))
        )

        order.append({
            "kind": "enemy",
            "actor": enemy,
            "name": enemy.get("name", "敵"),
            "value": value,
            "hp_score": hp_score,
            "random_bonus": random_bonus
        })

    order.sort(key=lambda item: item.get("value", 0), reverse=True)
    return order


def make_action_order_text(order):
    _refresh_context()
    # ===== 戦闘ログ用の行動順テキスト =====
    names = []

    for item in order:
        kind_mark = "敵" if item.get("kind") == "enemy" else "味方"
        names.append(f"{item.get('name', '？')}({kind_mark})")

    if not names:
        return "行動順：なし"

    return "行動順：" + " → ".join(names)


def is_all_attack_weapon_local(weapon_id):
    _refresh_context()
    return weapon_id in ["tempest", "laser_blade", "flamethrower", "emp_generator", "homing_missile"]

def resolve_weapon_attack_element(weapon_id, target_enemy=None):
    _refresh_context()

    element = get_weapon_element(weapon_id)

    if element != "auto_weak":
        return element

    if target_enemy is None:
        return "none"

    weaknesses = target_enemy.get("weakness", [])

    if not weaknesses:
        return "none"

    return weaknesses[0]


def get_revenge_sword_multiplier(player):
    _refresh_context()
    # ===== リベンジソード：HPが減るほど攻撃倍率上昇 =====
    if player is None:
        return 1.0

    max_hp = max(1, int(player.get("max_hp", 1)))
    hp = max(0, int(player.get("hp", 0)))
    hp_rate = hp / max_hp

    if hp_rate <= 0.10:
        return 4.0

    if hp_rate <= 0.25:
        return 3.0

    if hp_rate <= 0.50:
        return 2.5

    if hp_rate <= 0.75:
        return 2.0

    return 1.5


def is_magic_charge_active_for_player(player):
    _refresh_context()
    # ===== マジックチャージ：次ターンだけ攻撃魔法を2倍 =====
    if player is None:
        return False

    return int(player.get("magic_charge_turn", -1)) == int(game_state.get("turn", 0))


def consume_magic_charge_if_current_turn(player, events=None, activate_message=False):
    _refresh_context()
    # ===== 現在ターンに有効なマジックチャージを解除する =====
    if not is_magic_charge_active_for_player(player):
        return False

    player.pop("magic_charge_turn", None)

    if activate_message:
        message = "マジックチャージ発動！ 魔法威力2倍！"

        add_log(f"{player.get('name', '魔術師')}のマジックチャージ発動！")

    return True


def expire_unused_magic_charges_after_turn(events):
    _refresh_context()
    # ===== 次ターンに攻撃魔法を使わなかったマジックチャージはターン終了時に消える =====
    current_turn = int(game_state.get("turn", 0))

    for player in players:
        if int(player.get("magic_charge_turn", -1)) != current_turn:
            continue

        player.pop("magic_charge_turn", None)

        message = f"{player.get('name', '魔術師')}のマジックチャージは消えた。"
        events.append({
            "text": message,
            "state": snapshot()
        })
        add_log(message)


def clear_magic_charges():
    _refresh_context()
    # ===== 戦闘終了・再戦時にマジックチャージを解除 =====
    for player in players:
        player.pop("magic_charge_turn", None)


def process_regen_end_of_turn(events):
    _refresh_context()

    regen_users = game_state.get("active_regen_users", {})

    if not regen_users:
        return

    remove_list = []

    for player_name, turns_left in list(regen_users.items()):
        caster = get_player(player_name)

        if caster is None:
            remove_list.append(player_name)
            continue

        heal_amount = max(1, int(get_magic(caster) * 0.5))

        events.append({
            "text": f"{player_name}のリジェネが発動！",
            "state": snapshot()
        })

        add_log(f"{player_name}のリジェネが発動！")

        for target in alive_players():
            old_hp = int(target.get("hp", 0))
            max_hp = int(target.get("max_hp", old_hp))

            target["hp"] = min(max_hp, old_hp + heal_amount)
            actual_heal = target["hp"] - old_hp

            if actual_heal <= 0:
                continue

            events.append({
                "text": f"{target['name']}が{actual_heal}回復！",
                "state": snapshot()
            })

            add_log(f"{target['name']}が{actual_heal}回復！")

        turns_left -= 1

        if turns_left <= 0:
            remove_list.append(player_name)
        else:
            regen_users[player_name] = turns_left

    for player_name in remove_list:
        regen_users.pop(player_name, None)

def finish_with_victory_after_clearing_magic_charge(events):
    _refresh_context()
    clear_magic_charges()
    finish_with_victory(events)


def finish_with_defeat_after_clearing_magic_charge(events):
    _refresh_context()
    clear_magic_charges()
    finish_with_defeat(events)



def execute_player_action_by_order(p, events, turn_effects):
    _refresh_context()
    # ===== 行動順システム用：プレイヤー1人分の行動処理 =====
    if p is None or p.get("hp", 0) <= 0:
        return None

    p.setdefault("combo", 0)

    act = game_state["actions"].get(p["name"])

    if not act:
        return None

    action_type = act.get("type")
    target_name = act.get("target")

    if action_type == "attack":
        target_enemy_id = act.get("enemy_target")
        attack_weapon_id = act.get("weapon_id", "")
        magic_charge_multiplier = 1

        # ===== 魔術師の通常攻撃経路を使う場合も、マジックチャージ対象にする =====
        if p.get("job") == "魔術師" and is_magic_charge_active_for_player(p):
            magic_charge_multiplier = 2
            consume_magic_charge_if_current_turn(p, events, activate_message=True)

        # ===== 特殊武器の防御効果はターン開始時に登録済み =====
        # ここでは攻撃演出とダメージ処理だけを行う。

        # ===== テンペストは全体攻撃なので単体対象を持たせない =====
        if is_all_attack_weapon_local(attack_weapon_id):
            target_enemy = None
        else:
            target_enemy = get_enemy(target_enemy_id)

            if target_enemy is None or target_enemy["hp"] <= 0:
                target_enemy = choose_attack_enemy()

            if target_enemy is None:
                return None
        attack_weapon_name = get_weapon_display_name(attack_weapon_id)

        # ===== 魔術師の攻撃はスキル「アイスアロー」として扱う =====
        if p.get("job") == "魔術師":
            skill = get_skill("ice_arrow")
            skill_name = skill.get("name", "アイスアロー") if skill else "アイスアロー"
            attack_text = f"{p['name']}の{skill_name}！"

        elif attack_weapon_id:
            attack_text = f"{p['name']}は{attack_weapon_name}で攻撃！"

        else:
            attack_text = f"{p['name']}の攻撃！"

        attack_element = resolve_weapon_attack_element(
            attack_weapon_id,
            target_enemy
        )

        if is_all_attack_weapon_local(attack_weapon_id):
            events.append({"text": attack_text, "state": snapshot()})
        else:
            events.append({
                "text": attack_text,
                "state": snapshot(),
                "target_enemy": target_enemy["id"],
                "flash_enemy": True,
                "flash_type": "physical",
                "flash_element": attack_element
            })

        add_log(attack_text)

        # ===== 攻撃威力計算 =====
        # 勇者：
        #   attack × weapon.power_rate
        #
        # タンク：
        #   attack × weapon.power_rate × 0.7
        #
        # 魔術師：
        #   magic × skill倍率（現状5倍）

        if p.get("job") == "魔術師":
            power = int(get_magic(p) * 5 * magic_charge_multiplier)

        else:
            weapon = get_weapon(attack_weapon_id) if attack_weapon_id else None

            if weapon:
                power_rate = weapon.get("power_rate", 1)
            else:
                power_rate = 1

            if attack_weapon_id == "revenge_sword":
                power_rate = get_revenge_sword_multiplier(p)

            if p.get("job") == "タンク":
                if weapon and weapon.get("ignore_tank_penalty", False):
                    power = int(get_attack(p) * power_rate)
                else:
                    power = int(get_attack(p) * power_rate * 0.7)
            else:
                power = int(get_attack(p) * power_rate)

        base_dmg = random.randint(max(1, power - 5), power + 5)

        if p.get("job") == "勇者":
            combo_count = p.get("combo", 0)
            multiplier = 1.0 + (combo_count * 0.3)

            if combo_count > 0:
                percent_text = int(multiplier * 100)
                events.append({"text": f"攻撃力上昇！ 攻撃力{percent_text}%！", "state": snapshot()})
                add_log(f"{p['name']}の攻撃力上昇！ 攻撃力{percent_text}%！")

            dmg = int(base_dmg * multiplier)
            p["combo"] = combo_count + 1
        else:
            dmg = base_dmg
            reset_combo(p)

        # ===== テンペスト：全体攻撃 =====
        if is_all_attack_weapon_local(attack_weapon_id):

            # 攻撃宣言は直前の attack_text で表示済み
            # ここでは全体攻撃の発動説明だけ表示する
            attack_element = get_weapon_element(attack_weapon_id)
            target_enemy_ids = [
                enemy.get("id")
                for enemy in alive_enemies()
                if enemy.get("id")
            ]

            if attack_weapon_id == "laser_blade":
                all_attack_text = "光のレーザーが敵全体を貫く！"
            elif attack_weapon_id == "flamethrower":
                all_attack_text = "火炎放射器が敵全体を焼き払う！"
            elif attack_weapon_id == "emp_generator":
                all_attack_text = "EMPジェネレーターが雷撃を放つ！"
            elif attack_weapon_id == "homing_missile":
                all_attack_text = "自動追尾ミサイルが敵全体に降り注ぐ！"
            else:
                all_attack_text = "風の刃が敵全体を切り裂く！"

            events.append({
                "text": all_attack_text,
                "state": snapshot(),
                "target_enemies": target_enemy_ids,
                "flash_enemy": bool(target_enemy_ids),
                "flash_type": "physical",
                "flash_element": attack_element
            })
            add_log(all_attack_text)

            for enemy in game_state["enemies"]:
                if enemy["hp"] <= 0:
                    continue

                enemy_dmg = dmg

                enemy_dmg, element_result = apply_enemy_element_modifier(
                    enemy_dmg,
                    enemy,
                    attack_element
                )

                if element_result == "weak":
                    element_name = get_element_display_name(attack_element)

                    events.append({
                        "text": f"{enemy['name']}の弱点を突いた！",
                        "state": snapshot(),
                        "target_enemy": enemy["id"]
                    })

                    add_log(f"{enemy['name']}の弱点を突いた！")

                elif element_result == "resist":
                    element_name = get_element_display_name(attack_element)

                    events.append({
                        "text": f"{enemy['name']}は{element_name}属性に耐性がある！",
                        "state": snapshot(),
                        "target_enemy": enemy["id"]
                    })

                    add_log(f"{enemy['name']}は{element_name}属性に耐性がある！")

                damage_enemy(enemy, enemy_dmg)

                events.append({
                    "text": f"{enemy['name']}に{enemy_dmg}ダメージ！",
                    "state": snapshot(),
                    "target_enemy": enemy["id"]
                })

                add_log(f"{enemy['name']}に{enemy_dmg}ダメージ！")

                if enemy["hp"] <= 0:
                    events.append({
                        "text": f"{enemy['name']}を倒した！",
                        "state": snapshot(),
                        "target_enemy": enemy["id"]
                    })
                    add_log(f"{enemy['name']}を倒した！")

        # ===== テンペストで敵をすべて倒した場合 =====
        if is_all_attack_weapon_local(attack_weapon_id) and len(alive_enemies()) == 0:
            finish_with_victory_after_clearing_magic_charge(events)
            return "finished"

        # ===== テンペスト処理はここで完了。通常単体攻撃へ進まない =====
        if is_all_attack_weapon_local(attack_weapon_id):
            return None

        # ===== 通常単体攻撃 =====
        else:

            # ===== 武器属性による弱点・耐性判定 =====
            dmg, element_result = apply_enemy_element_modifier(dmg, target_enemy, attack_element)

            if element_result == "weak":
                element_name = get_element_display_name(attack_element)
                events.append({
                    "text": f"弱点！ {element_name}属性が効いている！",
                    "state": snapshot(),
                    "target_enemy": target_enemy["id"]
                })
                add_log(f"弱点！ {element_name}属性が効いている！")

            elif element_result == "resist":
                element_name = get_element_display_name(attack_element)
                events.append({
                    "text": f"{target_enemy['name']}は{element_name}属性に耐性がある！",
                    "state": snapshot(),
                    "target_enemy": target_enemy["id"]
                })
                add_log(f"{target_enemy['name']}は{element_name}属性に耐性がある！")

            damage_enemy(target_enemy, dmg)

            events.append({
                "text": f"{target_enemy['name']}に{dmg}ダメージ！",
                "state": snapshot(),
                "target_enemy": target_enemy["id"]
            })

            add_log(f"{target_enemy['name']}に{dmg}ダメージ！")

            # ===== ブラッドセイバー吸収 =====
            if is_blood_saver(attack_weapon_id):
                absorb = max(1, int(dmg * 0.3))

                old_hp = p["hp"]
                p["hp"] = min(p["max_hp"], p["hp"] + absorb)
                actual_heal = p["hp"] - old_hp

                if actual_heal > 0:
                    events.append({
                        "text": f"{p['name']}は血を吸収し{actual_heal}回復した！",
                        "state": snapshot()
                    })

                    add_log(f"{p['name']}は血を吸収し{actual_heal}回復した！")

        if (not is_all_attack_weapon_local(attack_weapon_id)) and target_enemy["hp"] <= 0:
            events.append({"text": f"{target_enemy['name']}を倒した！", "state": snapshot(), "target_enemy": target_enemy["id"]})
            add_log(f"{target_enemy['name']}を倒した！")

            if len(alive_enemies()) == 0:
                finish_with_victory_after_clearing_magic_charge(events)
                return "finished"

    elif action_type == "skill":
        reset_combo(p)

        skill_id = act.get("skill_id", "")
        skill = get_skill(skill_id)

        if not skill:
            events.append({"text": f"{p['name']}は魔法を唱えようとしたが、うまく発動しなかった！", "state": snapshot()})
            add_log(f"{p['name']}の魔法は発動しなかった。")
            return None

        skill_name = skill.get("name", "魔法")
        skill_type = skill.get("type", "attack")
        target_type = skill.get("target_type", "single")
        effect_type = skill.get("effect_type", "")

        charge_active = (
            skill_type == "attack"
            and is_magic_charge_active_for_player(p)
        )

        if charge_active:
            skill_text = (
                f"{p['name']}の{skill_name}！ "
                f"マジックチャージ発動！ 魔法威力2倍！"
            )
        else:
            skill_text = f"{p['name']}の{skill_name}！"

        skill_event_index = len(events)
        events.append({
            "text": skill_text,
            "state": snapshot()
        })

        add_log(skill_text)



        if skill_type == "attack":
            element = skill.get("element", "none")
            power_rate = float(skill.get("power_rate", 1.0))
            base_dmg = max(1, int(get_magic(p) * power_rate))

            if is_magic_charge_active_for_player(p):
                base_dmg *= 2
                consume_magic_charge_if_current_turn(p, events, activate_message=True)

            if target_type == "all":
                target_enemy_ids = [
                    enemy.get("id")
                    for enemy in alive_enemies()
                    if enemy.get("id")
                ]

                if target_enemy_ids and 0 <= skill_event_index < len(events):
                    events[skill_event_index]["target_enemies"] = target_enemy_ids
                    events[skill_event_index]["flash_enemy"] = True
                    events[skill_event_index]["flash_type"] = "magic"
                    events[skill_event_index]["flash_element"] = element

                for enemy in list(game_state.get("enemies", [])):
                    if enemy["hp"] <= 0:
                        continue

                    dmg = base_dmg
                    dmg, element_result = apply_enemy_element_modifier(dmg, enemy, element)

                    if element_result == "weak":
                        element_name = get_element_display_name(element)
                        events.append({
                            "text": f"{enemy['name']}の弱点を突いた！ {element_name}属性が効いている！",
                            "state": snapshot(),
                            "target_enemy": enemy["id"]
                        })
                        add_log(f"{enemy['name']}の弱点を突いた！")

                    elif element_result == "resist":
                        element_name = get_element_display_name(element)
                        events.append({
                            "text": f"{enemy['name']}は{element_name}属性に耐性がある！",
                            "state": snapshot(),
                            "target_enemy": enemy["id"]
                        })
                        add_log(f"{enemy['name']}は{element_name}属性に耐性がある！")

                    damage_enemy(enemy, dmg)

                    events.append({
                        "text": f"{enemy['name']}に{dmg}ダメージ！",
                        "state": snapshot(),
                        "target_enemy": enemy["id"]
                    })
                    add_log(f"{enemy['name']}に{dmg}ダメージ！")

                    if enemy["hp"] <= 0:
                        events.append({
                            "text": f"{enemy['name']}を倒した！",
                            "state": snapshot(),
                            "target_enemy": enemy["id"]
                        })
                        add_log(f"{enemy['name']}を倒した！")

                if len(alive_enemies()) == 0:
                    finish_with_victory_after_clearing_magic_charge(events)
                    return "finished"

            else:
                target_enemy_id = act.get("enemy_target", "")
                target_enemy = get_enemy(target_enemy_id)

                if target_enemy is None or target_enemy["hp"] <= 0:
                    target_enemy = choose_attack_enemy()

                if target_enemy is None:
                    return None

                # ===== 単体攻撃魔法は、魔法宣言イベントで敵被弾演出を1回だけ出す =====
                if 0 <= skill_event_index < len(events):
                    events[skill_event_index]["target_enemy"] = target_enemy["id"]
                    events[skill_event_index]["flash_enemy"] = True
                    events[skill_event_index]["flash_type"] = "magic"
                    events[skill_event_index]["flash_element"] = element

                dmg = base_dmg
                dmg, element_result = apply_enemy_element_modifier(dmg, target_enemy, element)

                if element_result == "weak":
                    element_name = get_element_display_name(element)
                    events.append({
                        "text": f"弱点！ {element_name}属性が効いている！",
                        "state": snapshot(),
                        "target_enemy": target_enemy["id"]
                    })
                    add_log(f"弱点！ {element_name}属性が効いている！")

                elif element_result == "resist":
                    element_name = get_element_display_name(element)
                    events.append({
                        "text": f"{target_enemy['name']}は{element_name}属性に耐性がある！",
                        "state": snapshot(),
                        "target_enemy": target_enemy["id"]
                    })
                    add_log(f"{target_enemy['name']}は{element_name}属性に耐性がある！")

                damage_enemy(target_enemy, dmg)

                events.append({
                    "text": f"{target_enemy['name']}に{dmg}ダメージ！",
                    "state": snapshot(),
                    "target_enemy": target_enemy["id"]
                })
                add_log(f"{target_enemy['name']}に{dmg}ダメージ！")

                if target_enemy["hp"] <= 0:
                    events.append({"text": f"{target_enemy['name']}を倒した！", "state": snapshot(), "target_enemy": target_enemy["id"]})
                    add_log(f"{target_enemy['name']}を倒した！")

                    if len(alive_enemies()) == 0:
                        finish_with_victory_after_clearing_magic_charge(events)
                        return "finished"

        elif skill_type == "support":
            # ===== チャージ中の次ターンに支援魔法を使った場合、チャージは消える =====
            consume_magic_charge_if_current_turn(p)

            if effect_type == "magic_defense":
                # ===== 実効果はターン開始時に登録済み。ここでは保険として状態だけ維持 =====
                game_state["active_magic_defense"] = True
                turn_effects["magic_defense_active"] = True

            elif effect_type == "magic_wall":
                game_state["active_magic_wall"] = True
                turn_effects["magic_wall_active"] = True
                events.append({"text": "味方全体に魔法の壁が展開された！", "state": snapshot()})
                add_log("味方全体に魔法の壁が展開された！")

            elif effect_type == "defend":
                set_party_buff("defend", int(skill.get("duration_turns", 3)))
                events.append({"text": "味方全体の物理防御が上がった！", "state": snapshot()})
                add_log("味方全体の物理防御が上がった！")

            elif effect_type == "physical_up":
                set_party_buff("physical_up", int(skill.get("duration_turns", 3)))
                events.append({"text": "味方全体の攻撃力が上がった！", "state": snapshot()})
                add_log("味方全体の攻撃力が上がった！")

            elif effect_type == "magic_boost":
                set_party_buff("magic_boost", int(skill.get("duration_turns", 3)))
                events.append({"text": "味方全体の魔力が上がった！", "state": snapshot()})
                add_log("味方全体の魔力が上がった！")

            elif effect_type == "regen":
                game_state.setdefault("active_regen_users", {})
                game_state["active_regen_users"][p["name"]] = int(skill.get("duration_turns", 3))

                events.append({
                    "text": f"{p['name']}は再生の魔法をかけた！",
                    "state": snapshot()
                })

                add_log(f"{p['name']}はリジェネを発動した！")

            elif effect_type == "reflect":
                reflect_target_name = act.get("target", "") or p.get("name", "")

                events.append({
                    "text": f"{p['name']}はリフレクトを維持している！",
                    "state": snapshot()
                })

                add_log(f"{p['name']}はリフレクトを維持している！")

            elif effect_type == "magic_charge":
                p["magic_charge_turn"] = int(game_state.get("turn", 0)) + 1

                events.append({
                    "text": f"{p['name']}は魔力を集中した！ 次のターンの攻撃魔法が2倍になる！",
                    "state": snapshot()
                })

                add_log(f"{p['name']}はマジックチャージで魔力を集中した！")

    elif action_type == "heal":
        reset_combo(p)
        consume_magic_charge_if_current_turn(p)

        target = get_player(target_name)

        if target is not None and target["hp"] > 0:
            base_heal = get_magic(p) + get_magic(target)

            heal_amount = random.randint(
                max(1, base_heal - 5),
                base_heal + 5
            )

            target["hp"] += heal_amount
            target["hp"] = min(target["hp"], target["max_hp"])

            events.append({"text": f"{p['name']}の選択回復！", "state": snapshot()})
            events.append({"text": f"{target['name']}が{heal_amount}回復！", "state": snapshot()})

            add_log(f"{p['name']}の選択回復！ {target['name']}が{heal_amount}回復！")

    elif action_type == "heal_all":
        reset_combo(p)
        consume_magic_charge_if_current_turn(p)

        events.append({"text": f"{p['name']}の全体回復！", "state": snapshot()})
        add_log(f"{p['name']}の全体回復！")

        for target in alive_players():
            base_heal = int((get_magic(p) + get_magic(target)) * 0.7)

            heal_amount = random.randint(
                max(1, base_heal - 5),
                base_heal + 5
            )

            target["hp"] += heal_amount
            target["hp"] = min(target["hp"], target["max_hp"])

            events.append({
                "text": f"{target['name']}が{heal_amount}回復！",
                "state": snapshot()
            })

            add_log(f"{target['name']}が{heal_amount}回復！")

    elif action_type == "shield":
        reset_combo(p)

        turn_effects["shield_users"].add(p["name"])
        turn_effects["taunt_user"] = p["name"]

        shield_id = act.get("shield_id", "")
        shield = get_shield(shield_id)
        shield_name = shield.get("name", "シールド") if shield else "シールド"

        # ===== イージスシールドは戦闘中1回だけ =====
        if shield_id == "aegis_shield" and game_state.get("aegis_used", False):
            events.append({
                "text": "イージスシールドの力は既に失われている！",
                "state": snapshot()
            })
            add_log("イージスシールドの力は既に失われている！")
            return None

        # ===== ガッツシールドは戦闘中1回だけ =====
        if shield_id == "guts_shield" and game_state.get("guts_used", False):
            events.append({
                "text": "ガッツシールドの力は既に失われている！",
                "state": snapshot()
            })
            add_log("ガッツシールドの力は既に失われている！")
            return None



        if shield:
            # ===== 実効果はターン開始時に登録済み。ここは重複しないよう保険だけ行う =====
            already_registered = any(
                info.get("id") == shield_id and info.get("user") == p["name"]
                for info in game_state.get("active_party_shields", [])
            )

        if shield:
            # ===== 実効果はターン開始時に登録済み。ここは重複しないよう保険だけ行う =====
            already_registered = any(
                info.get("id") == shield_id and info.get("user") == p["name"]
                for info in game_state.get("active_party_shields", [])
            )

            if not already_registered:
                game_state["active_party_shields"].append({
                    "id": shield_id,
                    "user": p["name"]
                })

            if shield.get("effect_type") == "physical_counter":
                if p["name"] not in game_state.get("active_attack_shield_users", []):
                    game_state["active_attack_shield_users"].append(p["name"])

        events.append({"text": f"{p['name']}は{shield_name}を構えた！", "state": snapshot()})
        events.append({"text": f"{p['name']}は敵の注意を引きつけた！", "state": snapshot()})

        add_log(f"{p['name']}は{shield_name}を構えた！")
        add_log(f"{p['name']}は敵の注意を引きつけた！")

    elif action_type == "magic_defense":
        reset_combo(p)

        skill = get_skill("magic_defense")
        skill_name = skill.get("name", "魔法障壁") if skill else "魔法障壁"

        # ===== 実効果はターン開始時に登録済み。ここでは行動順が来た時の演出だけ出す =====
        events.append({
            "text": f"{p['name']}の{skill_name}！",
            "state": snapshot()
        })
        add_log(f"{p['name']}の{skill_name}！")

    return None



def register_turn_start_magic_defense_effects(events, turn_effects):
    _refresh_context()
    # ===== 魔法障壁は行動順に関係なく、ターン開始時点から有効 =====
    actions = game_state.get("actions", {})

    for player in alive_players():
        player_name = player.get("name", "")
        action = actions.get(player_name, {})

        skill = None

        if action.get("type") == "magic_defense":
            skill = get_skill("magic_defense")
        elif action.get("type") == "skill":
            skill = get_skill(action.get("skill_id", ""))
            if not skill or skill.get("effect_type") != "magic_defense":
                continue
        else:
            continue

        skill_name = skill.get("name", "魔法障壁") if skill else "魔法障壁"

        turn_effects["magic_defense_active"] = True
        game_state["active_magic_defense"] = True

        events.append({
            "text": f"{player_name}は{skill_name}を構えた！",
            "state": snapshot()
        })
        add_log(f"{player_name}は{skill_name}を構えた！")

def register_turn_start_reflect_effects(events, turn_effects):
    _refresh_context()
    # ===== リフレクトは行動順に関係なく、ターン開始時点から有効 =====
    actions = game_state.get("actions", {})
    game_state.setdefault("active_reflect_targets", [])

    for player in alive_players():
        player_name = player.get("name", "")
        action = actions.get(player_name, {})

        if action.get("type") != "skill":
            continue

        skill = get_skill(action.get("skill_id", ""))

        if not skill or skill.get("effect_type") != "reflect":
            continue

        reflect_target_name = action.get("target", "") or player_name
        reflect_target = get_player(reflect_target_name)

        if reflect_target is None or reflect_target.get("hp", 0) <= 0:
            continue

        if reflect_target_name not in game_state["active_reflect_targets"]:
            game_state["active_reflect_targets"].append(reflect_target_name)

        events.append({
            "text": f"{reflect_target_name}にリフレクトがかかった！",
            "state": snapshot()
        })

        add_log(f"{reflect_target_name}にリフレクトがかかった！")


def execute_enemy_action_by_order(enemy, events, turn_effects):
    _refresh_context()
    # ===== 行動順システム用：敵1体分の行動処理 =====
    if enemy is None or enemy.get("hp", 0) <= 0:
        return None

    targets = online_alive_players()
    if not targets:
        return None

    skill = choose_enemy_skill(enemy)
    skill_name = skill.get("name", "攻撃")
    target_type = skill.get("target", "single")
    attack_category = skill.get("category", "physical")
    element = skill.get("element", "none")

    if attack_category == "heal" or target_type == "ally_heal":
        heal_targets = [e for e in alive_enemies() if e.get("hp", 0) < e.get("max_hp", 1)]
        if not heal_targets:
            events.append({"text": f"{enemy['name']}は様子を見ている。", "state": snapshot()})
            add_log(f"{enemy['name']}は様子を見ている。")
            return None

        heal_target = min(heal_targets, key=lambda e: e.get("hp", 0) / max(1, e.get("max_hp", 1)))
        heal_amount = get_enemy_skill_heal(skill, 10, 20)
        heal_target["hp"] = min(heal_target.get("max_hp", 1), heal_target.get("hp", 0) + heal_amount)
        game_state["boss_hp"] = sum(e["hp"] for e in game_state.get("enemies", []))

        events.append({
            "text": f"{enemy['name']}の{skill_name}！ {heal_target['name']}が{heal_amount}回復！",
            "state": snapshot(),
            "target_enemy": heal_target.get("id")
        })
        add_log(f"{enemy['name']}の{skill_name}！ {heal_target['name']}が{heal_amount}回復！")
        return None

    if target_type == "all":
        events.append({"text": f"{enemy['name']}の{skill_name}！", "state": snapshot()})
        add_log(f"{enemy['name']}の{skill_name}！")

        game_state["guts_all_attack_batch_active"] = True
        game_state["guts_all_attack_batch_triggered"] = False

        for target in list(online_alive_players()):
            base_damage = get_enemy_skill_damage(skill, 1, 1)
            apply_enemy_damage_to_player(enemy, target, base_damage, attack_category, element, "all", events)

            if len(alive_enemies()) == 0:
                game_state["guts_all_attack_batch_active"] = False
                game_state["guts_all_attack_batch_triggered"] = False
                finish_with_victory_after_clearing_magic_charge(events)
                return "finished"

            if len(alive_players()) == 0:
                game_state["guts_all_attack_batch_active"] = False
                game_state["guts_all_attack_batch_triggered"] = False
                finish_with_defeat_after_clearing_magic_charge(events)
                return "finished"

        game_state["guts_all_attack_batch_active"] = False
        game_state["guts_all_attack_batch_triggered"] = False

        return None

    target = choose_enemy_single_target(targets, turn_effects)
    if target is None:
        return None

    base_damage = get_enemy_skill_damage(skill, 1, 1)

    events.append({"text": f"{enemy['name']}の{skill_name}！", "state": snapshot()})
    add_log(f"{enemy['name']}の{skill_name}！")

    apply_enemy_damage_to_player(enemy, target, base_damage, attack_category, element, "single", events)

    if len(alive_enemies()) == 0:
        finish_with_victory_after_clearing_magic_charge(events)
        return "finished"

    if len(alive_players()) == 0:
        finish_with_defeat_after_clearing_magic_charge(events)
        return "finished"

    return None

def process_turn():
    _refresh_context()
    if game_state["phase"] != "choice":
        return

    events = []
    turn_effects = create_turn_effects()

    # ===== このターンに有効な盾・魔法防御情報 =====
    game_state["active_party_shields"] = []
    game_state["active_attack_shield_users"] = []
    game_state["active_counter_shield_hits"] = {}
    game_state["active_counter_shield_damage"] = {}
    game_state["active_aegis_users"] = []
    game_state["active_guts_users"] = []
    game_state["guts_all_attack_batch_active"] = False
    game_state["guts_all_attack_batch_triggered"] = False
    game_state["active_healing_shield_users"] = []
    game_state["healing_shield_damage"] = {}
    game_state["active_magic_wall"] = False
    game_state["active_magic_defense"] = False
    game_state["active_reflect_targets"] = []

    # ===== このターンに有効な特殊武器 =====
    game_state["active_defender_users"] = []
    game_state["active_magic_blade_users"] = []
    game_state["active_bazooka_users"] = []

    events.append({"text": "次ターン開始！", "state": snapshot()})
    add_log(f"--- {game_state['turn']}ターン目 ---")

    # ===== ターン開始時点で、選択済みの盾効果をすべて有効化 =====
    register_turn_start_shield_effects(turn_effects)

    # ===== ターン開始時点で、選択済みの特殊武器効果をすべて有効化 =====
    register_turn_start_weapon_effects(events)

    # ===== ターン開始時点で、魔法障壁を先に有効化 =====
    register_turn_start_magic_defense_effects(events, turn_effects)

    # ===== ターン開始時点で、リフレクトを先に有効化 =====
    register_turn_start_reflect_effects(events, turn_effects)

    # ===== E-1セクション：敵味方混合の行動順処理 =====

    action_order = build_turn_action_order()
    order_text = make_action_order_text(action_order)
    events.append({"text": order_text, "state": snapshot()})
    add_log(order_text)

    for item in action_order:
        if len(alive_enemies()) == 0:
            finish_with_victory_after_clearing_magic_charge(events)
            return

        if len(alive_players()) == 0:
            finish_with_defeat_after_clearing_magic_charge(events)
            return

        if item.get("kind") == "player":
            result = execute_player_action_by_order(item.get("actor"), events, turn_effects)
        else:
            result = execute_enemy_action_by_order(item.get("actor"), events, turn_effects)

        if result == "finished":
            return

    # ===== E-2セクション：勝利・敗北判定 =====

    if len(alive_enemies()) == 0:
        finish_with_victory_after_clearing_magic_charge(events)
        return

    if len(alive_players()) == 0:
        finish_with_defeat_after_clearing_magic_charge(events)
        return

    counter_result = resolve_counter_shield_end_of_turn(events)

    if counter_result == "finished":
        return

    healing_result = resolve_healing_shield_end_of_turn(events)

    if healing_result == "finished":
        return

    # ===== E-3セクション：次ターン準備 =====

    process_regen_end_of_turn(events)
    expire_unused_magic_charges_after_turn(events)
    decrement_party_buffs_after_turn(events)
    game_state["active_magic_wall"] = False
    game_state["active_magic_defense"] = False

    game_state["turn"] += 1
    game_state["actions"] = {}
    finalize_turn_events(events)



def resolve_counter_shield_end_of_turn(events):
    _refresh_context()

    # ===== カウンターシールド：ターン終了時に蓄積ダメージを放出 =====

    damage_pool = game_state.get("active_counter_shield_damage", {})

    if not damage_pool:
        return None

    for player_name, stored_damage in list(damage_pool.items()):
        stored_damage = int(stored_damage)

        if stored_damage <= 0:
            continue

        enemies = alive_enemies()

        if not enemies:
            return "finished"

        target_enemy = random.choice(enemies)

        damage_enemy(target_enemy, stored_damage)

        events.append({
            "text": f"{player_name}のカウンターシールドが蓄積ダメージを放出！",
            "state": snapshot(),
            "target_enemy": target_enemy.get("id"),
            "flash_enemy": True,
            "flash_type": "physical",
            "flash_element": "none"
        })

        events.append({
            "text": f"{target_enemy['name']}に{stored_damage}ダメージ！",
            "state": snapshot(),
            "target_enemy": target_enemy.get("id")
        })

        add_log(f"{player_name}のカウンターシールドが{stored_damage}ダメージを放出！")
        add_log(f"{target_enemy['name']}に{stored_damage}ダメージ！")

        if target_enemy.get("hp", 0) <= 0:
            events.append({
                "text": f"{target_enemy['name']}を倒した！",
                "state": snapshot(),
                "target_enemy": target_enemy.get("id")
            })

            add_log(f"{target_enemy['name']}を倒した！")

            if len(alive_enemies()) == 0:
                finish_with_victory_after_clearing_magic_charge(events)
                return "finished"

    game_state["active_counter_shield_damage"] = {}
    return None



def resolve_healing_shield_end_of_turn(events):
    _refresh_context()

    damage_pool = game_state.get("healing_shield_damage", {})

    if not damage_pool:
        return None

    for player_name, heal_amount in list(damage_pool.items()):
        heal_amount = int(heal_amount)

        if heal_amount <= 0:
            continue

        user = get_player(player_name)
        shield_name = "ヒーリングシールド"

        if user is not None:
            action = game_state.get("actions", {}).get(player_name, {})
            shield_id = action.get("shield_id", "")
            shield = get_shield(shield_id)

            if shield:
                shield_name = shield.get("name", shield_name)

        events.append({
            "text": f"{player_name}の{shield_name}が蓄積した力を解放した！",
            "state": snapshot()
        })
        add_log(f"{player_name}の{shield_name}が蓄積した力を解放した！")

        for target in alive_players():
            old_hp = int(target.get("hp", 0))
            max_hp = int(target.get("max_hp", old_hp))

            target["hp"] = min(max_hp, old_hp + heal_amount)
            actual_heal = target["hp"] - old_hp

            if actual_heal <= 0:
                continue

            events.append({
                "text": f"{target['name']}が{actual_heal}回復！",
                "state": snapshot()
            })
            add_log(f"{target['name']}が{actual_heal}回復！")

    game_state["healing_shield_damage"] = {}
    return None


# ===== E-7セクション：敵AI呼び出し =====

def build_enemy_ai_context():
    _refresh_context()
    # ===== enemy_ai.pyへ渡す状態・共通関数 =====
    return {
        "game_state": game_state,
        "players": players,
        "snapshot": snapshot,
        "add_log": add_log,
        "get_player": get_player,
        "alive_enemies": alive_enemies,
        "online_alive_players": online_alive_players,
        "choose_attack_enemy": choose_attack_enemy,
        "damage_enemy": damage_enemy,
        "physical_damage": physical_damage,
        "magic_damage": magic_damage,
        "get_attack": get_attack,
        "get_magic": get_magic,
        "get_party_buffs": get_party_buffs,
        "reset_combo": reset_combo,
        "reset_combo_if_unprotected_damage": reset_combo_if_unprotected_damage,
        "get_active_party_shield_effects": get_active_party_shield_effects,
        "apply_shield_effects_to_damage": apply_shield_effects_to_damage,
        "is_attack_shield_active": is_attack_shield_active,
        "get_selected_shield_name": get_selected_shield_name,
        "is_tank_basic_shield_physical_avoid_active": is_tank_basic_shield_physical_avoid_active,
        "get_shield": get_shield,
        "apply_used_weapon_resist": apply_used_weapon_resist,
        "is_defender_active": is_defender_active,
        "apply_magic_blade_reduction": apply_magic_blade_reduction,
        "choose_enemy_skill": choose_enemy_skill,
        "get_enemy_skill_damage": get_enemy_skill_damage,
        "get_enemy_skill_heal": get_enemy_skill_heal,
    }


def process_volcano_dragon_action(events, targets, turn_effects):
    _refresh_context()
    # ===== enemy_ai.pyへ一時効果をまとめて渡す =====
    return enemy_ai_process_volcano_dragon_action(
        build_enemy_ai_context(),
        events,
        targets,
        turn_effects
    )


def process_training_golem_action(events, targets, turn_effects):
    _refresh_context()
    # ===== enemy_ai.pyへ一時効果をまとめて渡す =====
    return enemy_ai_process_training_golem_action(
        build_enemy_ai_context(),
        events,
        targets,
        turn_effects
    )


def process_goblin_action(events, turn_effects):
    _refresh_context()
    # ===== enemy_ai.pyへ一時効果をまとめて渡す =====
    return enemy_ai_process_goblin_action(
        build_enemy_ai_context(),
        events,
        turn_effects
    )
