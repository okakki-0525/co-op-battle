# ===== Aセクション：武器データ =====

WEAPONS = {
    # ===== 初期武器 =====

    "long_sword": {
        "name": "ロングソード",
        "description": "勇者の初期武器。",
        "attack_bonus": 0,
        "power_rate": 1.0,
        "element": "none",
        "allowed_jobs": ["勇者"],
        "image": "/static/images/weapons/long_sword.png",
        "resist": {},
        "obtain_type": "initial"
    },

    "great_sword": {
        "name": "大剣",
        "description": "タンクの初期武器。",
        "attack_bonus": 0,
        "power_rate": 1.0,
        "element": "none",
        "allowed_jobs": ["タンク"],
        "image": "/static/images/weapons/great_sword.png",
        "resist": {},
        "obtain_type": "initial"
    },

    # ===== レイド報酬武器 =====

    "flame_sword": {
        "name": "炎剣",
        "description": "火属性攻撃。使用ターン中、火属性魔法ダメージを50%軽減する。",
        "attack_bonus": 0,
        "power_rate": 7.0,
        "element": "fire",
        "allowed_jobs": ["勇者", "タンク"],
        "image": "/static/images/weapons/flame_sword.png",
        "resist": {"fire": {"single": 0.50, "all": 0.50}},
        "obtain_type": "raid_drop"
    },

    "ice_brand": {
        "name": "アイスブランド",
        "description": "氷属性攻撃。使用ターン中、氷属性魔法ダメージを50%軽減する。",
        "attack_bonus": 0,
        "power_rate": 7.0,
        "element": "ice",
        "allowed_jobs": ["勇者", "タンク"],
        "image": "/static/images/weapons/ice_brand.png",
        "resist": {"ice": {"single": 0.50, "all": 0.50}},
        "obtain_type": "raid_drop"
    },

    "thunder_blade": {
        "name": "雷撃ブレード",
        "description": "雷属性攻撃。使用ターン中、雷属性魔法ダメージを50%軽減する。",
        "attack_bonus": 0,
        "power_rate": 7.0,
        "element": "thunder",
        "allowed_jobs": ["勇者", "タンク"],
        "image": "/static/images/weapons/thunder_blade.png",
        "resist": {"thunder": {"single": 0.50, "all": 0.50}},
        "obtain_type": "raid_drop"
    },

    "tempest": {
        "name": "テンペストブレード",
        "description": "風属性の全体攻撃。使用ターン中、風属性魔法ダメージを50%軽減する。",
        "attack_bonus": 0,
        "power_rate": 6.0,
        "element": "wind",
        "allowed_jobs": ["勇者", "タンク"],
        "image": "/static/images/weapons/tempest.png",
        "resist": {"wind": {"single": 0.50, "all": 0.50}},
        "obtain_type": "raid_drop"
    },

    "saint_blade": {
        "name": "セイントブレード",
        "description": "光属性攻撃。使用ターン中、光属性魔法ダメージを50%軽減する。",
        "attack_bonus": 0,
        "power_rate": 7.0,
        "element": "light",
        "allowed_jobs": ["勇者", "タンク"],
        "image": "/static/images/weapons/saint_blade.png",
        "resist": {"light": {"single": 0.50, "all": 0.50}},
        "obtain_type": "raid_drop"
    },

    "shadow_edge": {
        "name": "シャドウエッジ",
        "description": "闇属性攻撃。使用ターン中、闇属性魔法ダメージを50%軽減する。",
        "attack_bonus": 0,
        "power_rate": 7.0,
        "element": "dark",
        "allowed_jobs": ["勇者", "タンク"],
        "image": "/static/images/weapons/shadow_edge.png",
        "resist": {"dark": {"single": 0.50, "all": 0.50}},
        "obtain_type": "raid_drop"
    },

    "defender": {
        "name": "ディフェンダー",
        "description": "使用ターン中、物理攻撃を回避する。",
        "attack_bonus": 0,
        "power_rate": 5.0,
        "element": "none",
        "allowed_jobs": ["勇者", "タンク"],
        "image": "/static/images/weapons/defender.png",
        "resist": {},
        "obtain_type": "raid_drop"
    },

    "magic_blade": {
        "name": "マジックブレード",
        "description": "使用ターン中、全属性魔法ダメージを30%軽減する。",
        "attack_bonus": 0,
        "power_rate": 5.0,
        "element": "none",
        "allowed_jobs": ["勇者", "タンク"],
        "image": "/static/images/weapons/magic_blade.png",
        "resist": {
            "fire": {"single": 0.30, "all": 0.30},
            "ice": {"single": 0.30, "all": 0.30},
            "thunder": {"single": 0.30, "all": 0.30},
            "wind": {"single": 0.30, "all": 0.30},
            "light": {"single": 0.30, "all": 0.30},
            "dark": {"single": 0.30, "all": 0.30}
        },
        "obtain_type": "raid_drop"
    },

    "blood_saver": {
        "name": "ブラッドセイバー",
        "description": "与えたダメージの30%をHPとして吸収する。",
        "attack_bonus": 0,
        "power_rate": 5.0,
        "element": "none",
        "allowed_jobs": ["勇者", "タンク"],
        "image": "/static/images/weapons/blood_saver.png",
        "resist": {},
        "obtain_type": "raid_drop"
    },

    "buster_sword": {
        "name": "バスターソード",
        "description": "超高火力攻撃。",
        "attack_bonus": 0,
        "power_rate": 10.0,
        "element": "none",
        "allowed_jobs": ["勇者", "タンク"],
        "image": "/static/images/weapons/buster_sword.png",
        "resist": {},
        "obtain_type": "raid_drop"
    },

    # ===== 通常戦闘ドロップ武器（勇者専用） =====

    "weakness_blade": {
        "name": "ウィークネスブレード",
        "description": "敵の弱点属性で自動攻撃する。",
        "attack_bonus": 0,
        "power_rate": 3.0,
        "element": "auto_weak",
        "allowed_jobs": ["勇者"],
        "image": "/static/images/weapons/weakness_blade.png",
        "resist": {},
        "special_effect": "auto_weak",
        "obtain_type": "normal_drop"
    },

    "laser_blade": {
        "name": "レーザーブレード",
        "description": "敵全体を攻撃する。",
        "attack_bonus": 0,
        "power_rate": 2.0,
        "element": "light",
        "allowed_jobs": ["勇者"],
        "image": "/static/images/weapons/laser_blade.png",
        "resist": {},
        "special_effect": "all_attack",
        "obtain_type": "normal_drop"
    },

    "mirror_sword": {
        "name": "ミラーソード",
        "description": "使用ターン中、受けた単体魔法を反射する。",
        "attack_bonus": 0,
        "power_rate": 2.0,
        "element": "none",
        "allowed_jobs": ["勇者"],
        "image": "/static/images/weapons/mirror_sword.png",
        "resist": {},
        "special_effect": "magic_reflect",
        "obtain_type": "normal_drop"
    },

    "revenge_sword": {
        "name": "リベンジソード",
        "description": "HPが減るほど攻撃力が上昇する。",
        "attack_bonus": 0,
        "power_rate": 1.5,
        "element": "none",
        "allowed_jobs": ["勇者"],
        "image": "/static/images/weapons/revenge_sword.png",
        "resist": {},
        "special_effect": "revenge",
        "obtain_type": "normal_drop"
    },

    "counter_sword": {
        "name": "カウンターソード",
        "description": "物理攻撃を受けると反撃する。",
        "attack_bonus": 0,
        "power_rate": 2.0,
        "element": "none",
        "allowed_jobs": ["勇者"],
        "image": "/static/images/weapons/counter_sword.png",
        "resist": {},
        "special_effect": "counter",
        "obtain_type": "normal_drop"
    },

    "magnum44": {
        "name": "44マグナム",
        "description": "近代兵器。タンク補正を受けない高威力単体攻撃。",
        "attack_bonus": 0,
        "power_rate": 2.0,
        "element": "none",
        "allowed_jobs": ["タンク"],
        "image": "/static/images/weapons/magnum44.png",
        "resist": {},
        "ignore_tank_penalty": True,
        "obtain_type": "normal_drop"
    },

    "flamethrower": {
        "name": "火炎放射器",
        "description": "近代兵器。タンク補正を受けない火属性の全体攻撃。",
        "attack_bonus": 0,
        "power_rate": 2.0,
        "element": "fire",
        "allowed_jobs": ["タンク"],
        "image": "/static/images/weapons/flamethrower.png",
        "resist": {},
        "special_effect": "all_attack",
        "ignore_tank_penalty": True,
        "obtain_type": "normal_drop"
    },

    "emp_generator": {
        "name": "EMPジェネレーター",
        "description": "近代兵器。タンク補正を受けない雷属性の全体攻撃。",
        "attack_bonus": 0,
        "power_rate": 3.0,
        "element": "thunder",
        "allowed_jobs": ["タンク"],
        "image": "/static/images/weapons/emp_generator.png",
        "resist": {},
        "special_effect": "all_attack",
        "ignore_tank_penalty": True,
        "obtain_type": "normal_drop"
    },

    "homing_missile": {
        "name": "自動追尾ミサイル",
        "description": "近代兵器。敵全体を攻撃する。タンク補正を受けない。",
        "attack_bonus": 0,
        "power_rate": 4.0,
        "element": "none",
        "allowed_jobs": ["タンク"],
        "image": "/static/images/weapons/homing_missile.png",
        "resist": {},
        "special_effect": "all_attack",
        "ignore_tank_penalty": True,
        "obtain_type": "normal_drop"
    },

    "bazooka": {
        "name": "バズーカ",
        "description": "近代兵器。単体へ大ダメージ。使用ターン中は物理攻撃を回避。",
        "attack_bonus": 0,
        "power_rate": 3.0,
        "element": "none",
        "allowed_jobs": ["タンク"],
        "image": "/static/images/weapons/bazooka.png",
        "resist": {},
        "special_effect": "physical_avoid",
        "ignore_tank_penalty": True,
        "obtain_type": "normal_drop"
    },
}

# ===== Bセクション：武器取得処理 =====

def get_weapon(weapon_id):
    return WEAPONS.get(weapon_id)

def get_weapons_for_job(job):
    return {
        weapon_id: weapon
        for weapon_id, weapon in WEAPONS.items()
        if job in weapon.get("allowed_jobs", [])
    }

def get_weapon_display_name(weapon_id):
    weapon = get_weapon(weapon_id)
    if weapon:
        return weapon.get("name", "武器")
    return "武器なし"
