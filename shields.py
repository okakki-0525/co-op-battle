# ===== Aセクション：盾データ =====
# 盾の追加はこの SHIELDS に追加する。
#
# effect_type:
#   element_guard = 属性軽減
#   magic_guard = 魔法軽減
#   physical_counter = 物理反撃
#   physical_avoid = 物理回避
#   magic_counter = 魔法反撃
#   hit_counter = 被弾回数反撃
#
# trigger:
#   element_magic = 対応属性の魔法・属性攻撃
#   all_magic = すべての魔法攻撃
#   single_physical = 単体物理攻撃
#   magic = 魔法攻撃
#   all_damage = 物理・魔法を問わず被弾
#
# target_scope:
#   party = パーティ全体に効果
#   self = 使用者本人だけに効果

SHIELDS = {

    # ===== 初期盾 =====

    "iron_shield": {
        "image": "/static/images/shields/iron_shield.png",
        "name": "アイアンシールド",
        "element": "none",
        "effect_type": "basic_guard",
        "trigger": "single_physical",
        "target_scope": "self",
        "description": "タンクの初期盾。シールド行動中、タンク本人への物理攻撃を防ぐ。",
        "obtain_type": "initial"
    },

    # ===== 属性軽減盾 =====

    "flame_shield": {
        "image": "/static/images/shields/flame_shield.png",
        "name": "フレイムシールド",
        "element": "fire",
        "effect_type": "element_guard",
        "trigger": "element_magic",
        "target_scope": "party",
        "cut_rate": 0.80,
        "description": "使用ターン中、パーティ全員への火属性ダメージを8割軽減する盾。",
        "obtain_type": "raid_drop"
    },

    "ice_shield": {
        "image": "/static/images/shields/ice_shield.png",
        "name": "アイスシールド",
        "element": "ice",
        "effect_type": "element_guard",
        "trigger": "element_magic",
        "target_scope": "party",
        "cut_rate": 0.80,
        "description": "使用ターン中、パーティ全員への氷属性ダメージを8割軽減する盾。",
        "obtain_type": "raid_drop"
    },

    "thunder_shield": {
        "image": "/static/images/shields/thunder_shield.png",
        "name": "サンダーシールド",
        "element": "thunder",
        "effect_type": "element_guard",
        "trigger": "element_magic",
        "target_scope": "party",
        "cut_rate": 0.80,
        "description": "使用ターン中、パーティ全員への雷属性ダメージを8割軽減する盾。",
        "obtain_type": "raid_drop"
    },

    "holy_shield": {
        "image": "/static/images/shields/holy_shield.png",
        "name": "ホーリーシールド",
        "element": "light",
        "effect_type": "element_guard",
        "trigger": "element_magic",
        "target_scope": "party",
        "cut_rate": 0.80,
        "description": "使用ターン中、パーティ全員への光属性ダメージを8割軽減する盾。",
        "obtain_type": "raid_drop"
    },

    "dark_shield": {
        "image": "/static/images/shields/dark_shield.png",
        "name": "ダークシールド",
        "element": "dark",
        "effect_type": "element_guard",
        "trigger": "element_magic",
        "target_scope": "party",
        "cut_rate": 0.80,
        "description": "使用ターン中、パーティ全員への闇属性ダメージを8割軽減する盾。",
        "obtain_type": "raid_drop"
    },

    # ===== 特殊盾 =====

    "attack_shield": {
        "image": "/static/images/shields/attack_shield.png",
        "name": "アタックシールド",
        "element": "none",
        "effect_type": "physical_counter",
        "trigger": "single_physical",
        "target_scope": "self",
        "counter_type": "physical",
        "counter_stat": "attack",
        "counter_rate": 5.00,
        "counter_target": "attacker",
        "description": "物理攻撃に対して、タンクのATK×5.0で反撃する盾。",
        "obtain_type": "raid_drop"
    },

    "magic_shield": {
        "image": "/static/images/shields/magic_shield.png",
        "name": "マジックシールド",
        "element": "all_magic",
        "effect_type": "magic_guard",
        "trigger": "all_magic",
        "target_scope": "party",
        "cut_rate": 0.50,
        "description": "使用ターン中、全属性魔法ダメージを半減する盾。",
        "obtain_type": "raid_drop"
    },

    "auto_shield": {
        "image": "/static/images/shields/auto_shield.png",
        "name": "オートシールド",
        "element": "none",
        "effect_type": "physical_avoid",
        "trigger": "single_physical",
        "target_scope": "party",
        "avoid_rate": 1.00,
        "description": "使用ターン中、パーティの誰かに対する単体物理攻撃を100％回避する盾。",
        "obtain_type": "raid_drop"
    },

    "guardian_shield": {
        "image": "/static/images/shields/guardian_shield.png",
        "name": "ガーディアンシールド",
        "element": "none",
        "effect_type": "magic_counter",
        "trigger": "magic",
        "target_scope": "party",
        "counter_type": "magic",
        "counter_stat": "magic",
        "counter_rate": 5.00,
        "counter_target": "attacker_or_all",
        "description": "魔法攻撃に対して、タンクのMAGIC×5.0で反撃する盾。全体魔法には全体反撃する。",
        "obtain_type": "raid_drop"
    },

    "counter_shield": {
        "image": "/static/images/shields/counter_shield.png",
        "name": "カウンターシールド",
        "element": "none",
        "effect_type": "hit_counter",
        "trigger": "all_damage",
        "target_scope": "self",
        "counter_stat": "attack",
        "counter_rate": 0.50,
        "counter_target": "random_enemy",
        "description": "物理・魔法を問わず被弾回数を蓄積し、ターン終了時にランダムな敵へ放出する盾。",
        "obtain_type": "raid_drop"
    },

    "fortress_shield": {
        "image": "/static/images/shields/fortress_shield.png",
        "name": "フォートレスシールド",
        "element": "none",
        "effect_type": "all_attack_guard",
        "trigger": "all_damage",
        "target_scope": "party",
        "cut_rate": 0.30,
        "description": "使用ターン中、パーティ全員への全体攻撃ダメージを3割軽減する盾。",
        "obtain_type": "normal_drop"
    },

    "aegis_shield": {
        "image": "/static/images/shields/aegis_shield.png",
        "name": "イージスシールド",
        "element": "none",
        "effect_type": "first_hit_nullify",
        "trigger": "first_damage",
        "target_scope": "party",
        "description": "使用ターン中、パーティ全員がそれぞれ最初に受ける攻撃を1回だけ無効化する盾。",
        "obtain_type": "normal_drop"
    },

    "guts_shield": {
        "image": "/static/images/shields/guts_shield.png",
        "name": "ガッツシールド",
        "element": "none",
        "effect_type": "fatal_survive",
        "trigger": "fatal_damage",
        "target_scope": "party",
        "description": "使用ターン中、パーティの誰かが残りHP以上のダメージを受けた時、HP1で踏みとどまる。戦闘中1回だけ発動する。",
        "obtain_type": "normal_drop"
    },

    "healing_shield": {
        "image": "/static/images/shields/healing_shield.png",
        "name": "ヒーリングシールド",
        "element": "none",
        "effect_type": "healing_guard",
        "trigger": "damage_taken",
        "target_scope": "party",
        "description": "使用ターン中、タンクが本来受けるはずだったダメージを蓄積し、ターン終了時にパーティ全員をその分回復する盾。",
        "obtain_type": "normal_drop"
    },

    "reflect_shield": {
        "image": "/static/images/shields/reflect_shield.png",
        "name": "リフレクトシールド",
        "element": "none",
        "effect_type": "single_magic_reflect",
        "trigger": "single_magic",
        "target_scope": "party",
        "description": "使用ターン中、パーティの誰かが受ける単体魔法攻撃を反射し、術者に跳ね返す盾。",
        "obtain_type": "normal_drop"
    },
}


# ===== Bセクション：盾取得補助 =====

def get_shield(shield_id):
    return SHIELDS.get(shield_id)


def get_shields_for_job(job):
    # 現時点ではタンクだけ盾を使用可能
    if job != "タンク":
        return {}

    return SHIELDS


def get_shield_display_name(shield_id):
    shield = get_shield(shield_id)

    if shield:
        return shield.get("name", "盾")

    return "盾"
