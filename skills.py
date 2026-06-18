# ===== Aセクション：スキルデータ =====
# 新しいスキルは SKILLS に追加する。
#
# type:
#   attack = 攻撃
#   heal = 回復
#   support = 支援
#
# target_type:
#   single = 単体
#   all = 全体
#
# power_stat:
#   attack = 攻撃力依存
#   magic = 魔力依存
#
# duration_turns:
#   使用ターンを含めた持続ターン数

SKILLS = {

    # ===== 魔術師：初期魔法 =====

    "light_bolt": {
        "name": "ライトボルト",
        "job": "魔術師",
        "type": "attack",
        "element": "light",
        "target_type": "single",
        "power_stat": "magic",
        "power_rate": 1.0,
        "battle_text": "ライトボルト！",
        "description": "光属性の単体攻撃。魔力×1のダメージ。",
        "obtain_type": "initial"
    },

    "magic_defense": {
        "name": "魔法障壁",
        "job": "魔術師",
        "type": "support",
        "effect_type": "magic_defense",
        "target_type": "all",
        "cut_rate": 0.20,
        "duration_turns": 1,
        "battle_text": "魔法障壁！",
        "description": "使用ターン中、味方全体の魔法ダメージを20％軽減。",
        "obtain_type": "initial"
    },

    # ===== 魔術師：攻撃魔法 =====

    "dragon_breath": {
        "name": "ドラゴンブレス",
        "job": "魔術師",
        "type": "attack",
        "element": "fire",
        "target_type": "all",
        "power_stat": "magic",
        "power_rate": 7.0,
        "battle_text": "ドラゴンブレス！",
        "description": "炎属性の全体攻撃。魔力×7のダメージ。",
        "obtain_type": "raid_drop"
    },

    "inferno": {
        "name": "インフェルノ",
        "job": "魔術師",
        "type": "attack",
        "element": "fire",
        "target_type": "single",
        "power_stat": "magic",
        "power_rate": 10.0,
        "battle_text": "インフェルノ！",
        "description": "炎属性の単体攻撃。魔力×10のダメージ。",
        "obtain_type": "raid_drop"
    },

    "thunder": {
        "name": "雷撃",
        "job": "魔術師",
        "type": "attack",
        "element": "thunder",
        "target_type": "all",
        "power_stat": "magic",
        "power_rate": 7.0,
        "battle_text": "雷撃！",
        "description": "雷属性の全体攻撃。魔力×7のダメージ。",
        "obtain_type": "raid_drop"
    },

    "holy_break": {
        "name": "ホーリーブレイク",
        "job": "魔術師",
        "type": "attack",
        "element": "light",
        "target_type": "all",
        "power_stat": "magic",
        "power_rate": 7.0,
        "battle_text": "ホーリーブレイク！",
        "description": "光属性の全体攻撃。魔力×7のダメージ。",
        "obtain_type": "raid_drop"
    },

    "ice_tempest": {
        "name": "アイステンペスト",
        "job": "魔術師",
        "type": "attack",
        "element": "ice",
        "target_type": "all",
        "power_stat": "magic",
        "power_rate": 7.0,
        "battle_text": "アイステンペスト！",
        "description": "氷属性の全体攻撃。魔力×7のダメージ。",
        "obtain_type": "raid_drop"
    },

    "tempest": {
        "name": "テンペスト",
        "job": "魔術師",
        "type": "attack",
        "element": "wind",
        "target_type": "all",
        "power_stat": "magic",
        "power_rate": 7.0,
        "battle_text": "テンペスト！",
        "description": "風属性の全体攻撃。魔力×7のダメージ。",
        "obtain_type": "raid_drop"
    },

    # ===== 魔術師：支援魔法 =====

    "magic_wall": {
        "name": "マジックウォール",
        "job": "魔術師",
        "type": "support",
        "effect_type": "magic_wall",
        "target_type": "all",
        "cut_rate": 0.70,
        "duration_turns": 1,
        "battle_text": "マジックウォール！",
        "description": "使用ターン中、全属性魔法ダメージを70％軽減。軽減系は加算され、上限は90％。",
        "obtain_type": "raid_drop"
    },

    "defend": {
        "name": "ディフェンド",
        "job": "魔術師",
        "type": "support",
        "effect_type": "defend",
        "target_type": "all",
        "cut_rate": 0.50,
        "duration_turns": 3,
        "battle_text": "ディフェンド！",
        "description": "使用ターンを含む3ターン、味方全体の物理ダメージを50％軽減。",
        "obtain_type": "raid_drop"
    },

    "physical_up": {
        "name": "フィジカルアップ",
        "job": "魔術師",
        "type": "support",
        "effect_type": "physical_up",
        "target_type": "all",
        "buff_rate": 0.50,
        "duration_turns": 3,
        "battle_text": "フィジカルアップ！",
        "description": "使用ターンを含む3ターン、味方全体のATKを50％上昇。",
        "obtain_type": "raid_drop"
    },

    "magic_boost": {
        "name": "マジックブースト",
        "job": "魔術師",
        "type": "support",
        "effect_type": "magic_boost",
        "target_type": "all",
        "buff_rate": 0.50,
        "duration_turns": 3,
        "battle_text": "マジックブースト！",
        "description": "使用ターンを含む3ターン、味方全体のMAGICを50％上昇。",
        "obtain_type": "raid_drop"
    },

    "magic_charge": {
        "name": "マジックチャージ",
        "job": "魔術師",
        "type": "support",
        "effect_type": "magic_charge",
        "target_type": "single",
        "duration_turns": 1,
        "battle_text": "マジックチャージ！",
        "description": "次のターンに使用する攻撃魔法の威力を2倍にする。攻撃魔法を使わなかった場合は効果消滅。",
        "obtain_type": "normal_drop"
    },

    "regen": {
        "name": "リジェネ",
        "job": "魔術師",
        "type": "support",
        "effect_type": "regen",
        "target_type": "all",
        "duration_turns": 3,
        "power_stat": "magic",
        "power_rate": 1.0,
        "battle_text": "リジェネ！",
        "description": "使用ターンを含む3ターン、ターン終了時に味方全体のHPを回復する。",
        "obtain_type": "normal_drop"
    },

    "reflect": {
        "name": "リフレクト",
        "job": "魔術師",
        "type": "support",
        "effect_type": "reflect",
        "target_type": "single",
        "duration_turns": 1,
        "battle_text": "リフレクト！",
        "description": "選んだ味方1人が、使用ターン中の単体魔法攻撃を何度でも反射する。",
        "obtain_type": "normal_drop"
    },

    "void": {
        "name": "ヴォイド",
        "job": "魔術師",
        "type": "attack",
        "element": "none",
        "target_type": "single",
        "power_rate": 3.0,
        "battle_text": "ヴォイド！",
        "description": "無属性の単体攻撃（魔力×3.0）",
        "obtain_type": "normal_drop"
    },

    "meteor_strike": {
        "name": "メテオストライク",
        "job": "魔術師",
        "type": "attack",
        "element": "none",
        "target_type": "all",
        "power_rate": 2.0,
        "battle_text": "メテオストライク！",
        "description": "無属性の全体攻撃（魔力×2.0）",
        "obtain_type": "normal_drop"
    }
}


# ===== Bセクション：スキル取得補助 =====

def get_skill(skill_id):
    return SKILLS.get(skill_id)


def get_skills_for_job(job):
    result = {}

    for skill_id, skill in SKILLS.items():
        if skill.get("job") == job:
            result[skill_id] = skill

    return result


def get_skill_display_name(skill_id):
    skill = get_skill(skill_id)

    if skill:
        return skill.get("name", "スキル")

    return "スキル"
