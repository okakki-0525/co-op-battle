# ===== Aセクション：敵データ =====

ENEMIES = {
    "training_golem": {
        "name": "訓練用ゴーレム",
        "max_hp": 100,
        "image": "/static/images/training_golem.png",
        "role": "training_golem",
        "weakness": ["thunder"],
        "resist": [],
        "skills": [
            {
                "name": "打撃",
                "rate": 80,
                "target": "single",
                "category": "physical",
                "element": "none",
                "damage": [10, 19]
            },
            {
                "name": "重い一撃",
                "rate": 20,
                "target": "single",
                "category": "physical",
                "element": "none",
                "damage": [20, 35]
            }
        ]
    },

    "volcano_dragon": {
        "name": "炎帝竜 ボルケーノドラゴン",
        "max_hp": 3000,
        "image": "/static/images/vdragon.png",
        "role": "raid_boss",
        "weakness": ["ice"],
        "resist": ["fire"],
        "skills": [
            {
                "name": "ひっかき",
                "rate": 45,
                "target": "single",
                "category": "physical",
                "element": "none",
                "damage": [60, 90]
            },
            {
                "name": "フレイムランス",
                "rate": 35,
                "target": "single",
                "category": "magic",
                "element": "fire",
                "damage": [100, 150]
            },
            {
                "name": "インフェルノブレス",
                "rate": 20,
                "target": "all",
                "category": "magic",
                "element": "fire",
                "damage": [140, 200]
            }
        ]
    },

    "tempest_dragon": {
        "name": "嵐帝竜 テンペストドラゴン",
        "max_hp": 3000,
        "image": "/static/images/tempest_dragon.png",
        "role": "raid_boss",
        "weakness": ["thunder"],
        "resist": ["wind"],
        "skills": [
            {
                "name": "ウインドクロー",
                "rate": 45,
                "target": "single",
                "category": "physical",
                "element": "none",
                "damage": [60, 100]
            },
            {
                "name": "エアカッター",
                "rate": 35,
                "target": "single",
                "category": "magic",
                "element": "wind",
                "damage": [100, 150]
            },
            {
                "name": "テンペストストーム",
                "rate": 20,
                "target": "all",
                "category": "magic",
                "element": "wind",
                "damage": [140, 200]
            }
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
            {
                "name": "斬りつけ",
                "rate": 100,
                "target": "single",
                "category": "physical",
                "element": "none",
                "damage": [20, 35]
            }
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
            {
                "name": "闇魔法",
                "rate": 100,
                "target": "all",
                "category": "magic",
                "element": "dark",
                "damage": [14, 26]
            }
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
            {
                "name": "杖攻撃",
                "rate": 70,
                "target": "single",
                "category": "physical",
                "element": "none",
                "damage": [8, 16]
            },
            {
                "name": "回復",
                "rate": 30,
                "target": "ally_heal",
                "category": "heal",
                "element": "none",
                "heal": [22, 38]
            }
        ]
    },

    "slime": {
        "name": "スライム",
        "max_hp": 80,
        "image": "/static/images/slime.png",
        "role": "small_fry",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "体当たり", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [6, 12]}
        ]
    },

    "goblin": {
        "name": "ゴブリン",
        "max_hp": 120,
        "image": "/static/images/goblin.png",
        "role": "small_fry",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "小さな斬りつけ", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [10, 18]}
        ]
    },

    "orc": {
        "name": "オーク",
        "max_hp": 180,
        "image": "/static/images/orc.png",
        "role": "small_fry",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "こん棒攻撃", "rate": 75, "target": "single", "category": "physical", "element": "none", "damage": [16, 28]},
            {"name": "力任せの一撃", "rate": 25, "target": "single", "category": "physical", "element": "none", "damage": [24, 36]}
        ]
    },

    "ice_wolf": {
        "name": "アイスウルフ",
        "max_hp": 140,
        "image": "/static/images/ice_wolf.png",
        "role": "small_fry",
        "weakness": ["fire"],
        "resist": ["ice"],
        "skills": [
            {"name": "氷の牙", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [14, 24]}
        ]
    },

    "thunder_bird": {
        "name": "サンダーバード",
        "max_hp": 140,
        "image": "/static/images/thunder_bird.png",
        "role": "small_fry",
        "weakness": ["wind"],
        "resist": ["thunder"],
        "skills": [
            {"name": "小さな雷撃", "rate": 100, "target": "single", "category": "magic", "element": "thunder", "damage": [14, 24]}
        ]
    },

    "wind_fairy": {
        "name": "ウインドフェアリー",
        "max_hp": 120,
        "image": "/static/images/wind_fairy.png",
        "role": "small_fry",
        "weakness": ["thunder"],
        "resist": ["wind"],
        "skills": [
            {"name": "風のいたずら", "rate": 100, "target": "single", "category": "magic", "element": "wind", "damage": [12, 22]}
        ]
    },

    "holy_slime": {
        "name": "ホーリースライム",
        "max_hp": 130,
        "image": "/static/images/holy_slime.png",
        "role": "small_fry",
        "weakness": ["dark"],
        "resist": ["light"],
        "skills": [
            {"name": "聖なるしずく", "rate": 100, "target": "single", "category": "magic", "element": "light", "damage": [12, 22]}
        ]
    },

    "shadow_bat": {
        "name": "シャドウバット",
        "max_hp": 130,
        "image": "/static/images/shadow_bat.png",
        "role": "small_fry",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "闇の羽ばたき", "rate": 100, "target": "single", "category": "magic", "element": "dark", "damage": [14, 26]}
        ]
    },

    "fire_lizard": {
        "name": "ファイアリザード",
        "max_hp": 150,
        "image": "/static/images/fire_lizard.png",
        "role": "small_fry",
        "weakness": ["ice"],
        "resist": ["fire"],
        "skills": [
            {"name": "小さな火炎", "rate": 100, "target": "single", "category": "magic", "element": "fire", "damage": [15, 27]}
        ]
    },

    "stone_beetle": {
        "name": "ストーンビートル",
        "max_hp": 220,
        "image": "/static/images/stone_beetle.png",
        "role": "small_fry",
        "weakness": ["thunder"],
        "resist": [],
        "skills": [
            {"name": "硬い体当たり", "rate": 80, "target": "single", "category": "physical", "element": "none", "damage": [10, 18]},
            {"name": "のしかかり", "rate": 20, "target": "single", "category": "physical", "element": "none", "damage": [18, 28]}
        ]
    },

    "kobold": {
        "name": "コボルト",
        "max_hp": 70,
        "image": "/static/images/kobold.png",
        "role": "small_fry",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "ひっかき", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [12, 20]}
        ]
    },

    "kobold_archer": {
        "name": "コボルトアーチャー",
        "max_hp": 60,
        "image": "/static/images/kobold_archer.png",
        "role": "small_fry",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "矢を放つ", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [16, 24]}
        ]
    },

    "harpy": {
        "name": "ハーピー",
        "max_hp": 80,
        "image": "/static/images/harpy.png",
        "role": "small_fry",
        "weakness": ["thunder"],
        "resist": ["wind"],
        "skills": [
            {"name": "ウインドカッター", "rate": 100, "target": "single", "category": "magic", "element": "wind", "damage": [16, 24]}
        ]
    },

    "minotaur": {
        "name": "ミノタウロス",
        "max_hp": 180,
        "image": "/static/images/minotaur.png",
        "role": "fighter",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "戦斧斬り", "rate": 75, "target": "single", "category": "physical", "element": "none", "damage": [26, 40]},
            {"name": "渾身の一撃", "rate": 25, "target": "single", "category": "physical", "element": "none", "damage": [36, 52]}
        ]
    },

    "treant": {
        "name": "トレント",
        "max_hp": 220,
        "image": "/static/images/treant.png",
        "role": "tank",
        "weakness": ["fire"],
        "resist": [],
        "skills": [
            {"name": "枝の一撃", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [18, 30]}
        ]
    },

    "gargoyle": {
        "name": "ガーゴイル",
        "max_hp": 160,
        "image": "/static/images/gargoyle.png",
        "role": "tank",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "石の爪", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [20, 32]}
        ]
    },

    "skeleton": {
        "name": "スケルトン",
        "max_hp": 90,
        "image": "/static/images/skeleton.png",
        "role": "small_fry",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "骨の剣", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [14, 24]}
        ]
    },

    "skeleton_knight": {
        "name": "スケルトンナイト",
        "max_hp": 170,
        "image": "/static/images/skeleton_knight.png",
        "role": "fighter",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "重斬撃", "rate": 80, "target": "single", "category": "physical", "element": "none", "damage": [24, 36]},
            {"name": "騎士の一撃", "rate": 20, "target": "single", "category": "physical", "element": "none", "damage": [32, 46]}
        ]
    },

    "ghost": {
        "name": "ゴースト",
        "max_hp": 80,
        "image": "/static/images/ghost.png",
        "role": "mage",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "シャドウボルト", "rate": 100, "target": "single", "category": "magic", "element": "dark", "damage": [18, 30]}
        ]
    },

    "lich": {
        "name": "リッチ",
        "max_hp": 140,
        "image": "/static/images/lich.png",
        "role": "mage",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "ダークブラスト", "rate": 70, "target": "all", "category": "magic", "element": "dark", "damage": [18, 30]},
            {"name": "ヘルファイア", "rate": 30, "target": "single", "category": "magic", "element": "fire", "damage": [30, 45]}
        ]
    },

    "goblin_archer": {
        "name": "ゴブリンアーチャー",
        "max_hp": 95,
        "image": "/static/images/goblin_archer.png",
        "role": "danger",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "狙い撃ち", "rate": 70, "target": "single", "category": "physical", "element": "none", "damage": [24, 36]},
            {"name": "急所を射る", "rate": 30, "target": "single", "category": "physical", "element": "none", "damage": [34, 46]}
        ]
    },

    "dark_scout": {
        "name": "ダークスカウト",
        "max_hp": 95,
        "image": "/static/images/dark_scout.png",
        "role": "danger",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "奇襲斬り", "rate": 75, "target": "single", "category": "physical", "element": "dark", "damage": [22, 34]},
            {"name": "影縫い", "rate": 25, "target": "single", "category": "physical", "element": "dark", "damage": [30, 42]}
        ]
    },

    "bomb_slime": {
        "name": "ボムスライム",
        "max_hp": 90,
        "image": "/static/images/bomb_slime.png",
        "role": "danger",
        "weakness": ["ice"],
        "resist": ["fire"],
        "skills": [
            {"name": "火花を散らす", "rate": 65, "target": "single", "category": "magic", "element": "fire", "damage": [20, 32]},
            {"name": "小爆発", "rate": 35, "target": "all", "category": "magic", "element": "fire", "damage": [12, 20]}
        ]
    },

    "imp": {
        "name": "インプ",
        "max_hp": 90,
        "image": "/static/images/imp.png",
        "role": "danger",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "いたずら魔法", "rate": 70, "target": "single", "category": "magic", "element": "dark", "damage": [22, 34]},
            {"name": "小悪魔の呪文", "rate": 30, "target": "all", "category": "magic", "element": "dark", "damage": [13, 21]}
        ]
    },

    "skeleton_mage": {
        "name": "スケルトンメイジ",
        "max_hp": 100,
        "image": "/static/images/skeleton_mage.png",
        "role": "danger",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "骨の呪文", "rate": 70, "target": "single", "category": "magic", "element": "dark", "damage": [24, 36]},
            {"name": "ダークミスト", "rate": 30, "target": "all", "category": "magic", "element": "dark", "damage": [14, 23]}
        ]
    },

    "kobold_thief": {
        "name": "コボルトシーフ",
        "max_hp": 90,
        "image": "/static/images/kobold_thief.png",
        "role": "danger",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "素早い一撃", "rate": 75, "target": "single", "category": "physical", "element": "none", "damage": [22, 34]},
            {"name": "背後からの一突き", "rate": 25, "target": "single", "category": "physical", "element": "none", "damage": [34, 48]}
        ]
    },

    "blood_bat": {
        "name": "ブラッドバット",
        "max_hp": 100,
        "image": "/static/images/blood_bat.png",
        "role": "danger",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "吸血噛みつき", "rate": 80, "target": "single", "category": "physical", "element": "dark", "damage": [22, 34]},
            {"name": "血の羽ばたき", "rate": 20, "target": "all", "category": "magic", "element": "dark", "damage": [12, 20]}
        ]
    },

    "shadow": {
        "name": "シャドウ",
        "max_hp": 100,
        "image": "/static/images/shadow.png",
        "role": "danger",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "闇の爪", "rate": 70, "target": "single", "category": "magic", "element": "dark", "damage": [26, 38]},
            {"name": "影の強襲", "rate": 30, "target": "single", "category": "magic", "element": "dark", "damage": [34, 48]}
        ]
    },

    "poison_mushroom": {
        "name": "ポイズンキノコ",
        "max_hp": 105,
        "image": "/static/images/poison_mushroom.png",
        "role": "danger",
        "weakness": ["fire"],
        "resist": [],
        "skills": [
            {"name": "毒胞子", "rate": 70, "target": "all", "category": "magic", "element": "none", "damage": [12, 20]},
            {"name": "胞子爆発", "rate": 30, "target": "single", "category": "magic", "element": "none", "damage": [24, 36]}
        ]
    },

    "curse_doll": {
        "name": "カースドール",
        "max_hp": 100,
        "image": "/static/images/curse_doll.png",
        "role": "danger",
        "weakness": ["fire"],
        "resist": ["dark"],
        "skills": [
            {"name": "呪いの視線", "rate": 70, "target": "single", "category": "magic", "element": "dark", "damage": [24, 36]},
            {"name": "不気味な歌", "rate": 30, "target": "all", "category": "magic", "element": "dark", "damage": [13, 22]}
        ]
    },

    "dark_priest": {
        "name": "ダークプリースト",
        "max_hp": 170,
        "image": "/static/images/dark_priest.png",
        "role": "elite",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "ダークランス", "rate": 70, "target": "single", "category": "magic", "element": "dark", "damage": [35, 45]},
            {"name": "シャドウレイン", "rate": 30, "target": "all", "category": "magic", "element": "dark", "damage": [45, 55]}
        ]
    },

    "flame_witch": {
        "name": "フレイムウィッチ",
        "max_hp": 165,
        "image": "/static/images/flame_witch.png",
        "role": "elite",
        "weakness": ["ice"],
        "resist": ["fire"],
        "skills": [
            {"name": "ファイアランス", "rate": 70, "target": "single", "category": "magic", "element": "fire", "damage": [35, 45]},
            {"name": "フレアストーム", "rate": 30, "target": "all", "category": "magic", "element": "fire", "damage": [45, 55]}
        ]
    },

    "ice_sorcerer": {
        "name": "アイスソーサラー",
        "max_hp": 165,
        "image": "/static/images/ice_sorcerer.png",
        "role": "elite",
        "weakness": ["fire"],
        "resist": ["ice"],
        "skills": [
            {"name": "アイスランス", "rate": 70, "target": "single", "category": "magic", "element": "ice", "damage": [35, 45]},
            {"name": "アイステンペスト", "rate": 30, "target": "all", "category": "magic", "element": "ice", "damage": [45, 55]}
        ]
    },

    "thunder_shaman": {
        "name": "サンダーシャーマン",
        "max_hp": 170,
        "image": "/static/images/thunder_shaman.png",
        "role": "elite",
        "weakness": ["wind"],
        "resist": ["thunder"],
        "skills": [
            {"name": "サンダーボルト", "rate": 70, "target": "single", "category": "magic", "element": "thunder", "damage": [35, 45]},
            {"name": "ライトニングストーム", "rate": 30, "target": "all", "category": "magic", "element": "thunder", "damage": [45, 55]}
        ]
    },

    "wind_oracle": {
        "name": "ウインドオラクル",
        "max_hp": 165,
        "image": "/static/images/wind_oracle.png",
        "role": "elite",
        "weakness": ["thunder"],
        "resist": ["wind"],
        "skills": [
            {"name": "エアスラスト", "rate": 70, "target": "single", "category": "magic", "element": "wind", "damage": [35, 45]},
            {"name": "トルネード", "rate": 30, "target": "all", "category": "magic", "element": "wind", "damage": [45, 55]}
        ]
    },

    "blood_vampire": {
        "name": "ブラッドヴァンパイア",
        "max_hp": 185,
        "image": "/static/images/blood_vampire.png",
        "role": "elite",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "吸血牙", "rate": 70, "target": "single", "category": "physical", "element": "dark", "damage": [40, 50]},
            {"name": "ブラッドウェーブ", "rate": 30, "target": "all", "category": "magic", "element": "dark", "damage": [45, 55]}
        ]
    },

    "hell_hound": {
        "name": "ヘルハウンド",
        "max_hp": 190,
        "image": "/static/images/hell_hound.png",
        "role": "elite",
        "weakness": ["ice"],
        "resist": ["fire"],
        "skills": [
            {"name": "炎牙", "rate": 70, "target": "single", "category": "physical", "element": "fire", "damage": [40, 50]},
            {"name": "ヘルファイアブレス", "rate": 30, "target": "all", "category": "magic", "element": "fire", "damage": [45, 55]}
        ]
    },

    "death_knight": {
        "name": "デスナイト",
        "max_hp": 195,
        "image": "/static/images/death_knight.png",
        "role": "elite",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "呪剣斬り", "rate": 70, "target": "single", "category": "physical", "element": "dark", "damage": [42, 52]},
            {"name": "ダークスラッシュ", "rate": 30, "target": "all", "category": "physical", "element": "dark", "damage": [45, 55]}
        ]
    },

    "chaos_eye": {
        "name": "カオスアイ",
        "max_hp": 170,
        "image": "/static/images/chaos_eye.png",
        "role": "elite",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "カオスビーム", "rate": 70, "target": "single", "category": "magic", "element": "none", "damage": [40, 50]},
            {"name": "カオスバースト", "rate": 30, "target": "all", "category": "magic", "element": "none", "damage": [45, 55]}
        ]
    },

    "demon_lord": {
        "name": "デーモンロード",
        "max_hp": 180,
        "image": "/static/images/demon_lord.png",
        "role": "elite",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "ヘルブラスト", "rate": 70, "target": "single", "category": "magic", "element": "dark", "damage": [45, 55]},
            {"name": "アビスノヴァ", "rate": 30, "target": "all", "category": "magic", "element": "dark", "damage": [50, 60]}
        ]
    },

    "rabbit": {
        "name": "ラビット",
        "max_hp": 55,
        "image": "/static/images/rabbit.png",
        "role": "small_fry",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "体当たり", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [8, 12]}
        ]
    },

    "horn_rabbit": {
        "name": "ホーンラビット",
        "max_hp": 60,
        "image": "/static/images/horn_rabbit.png",
        "role": "small_fry",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "角突き", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [9, 13]}
        ]
    },

    "forest_snake": {
        "name": "フォレストスネーク",
        "max_hp": 60,
        "image": "/static/images/forest_snake.png",
        "role": "small_fry",
        "weakness": ["fire"],
        "resist": [],
        "skills": [
            {"name": "かみつき", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [8, 14]}
        ]
    },

    "cave_bat": {
        "name": "ケイブバット",
        "max_hp": 50,
        "image": "/static/images/cave_bat.png",
        "role": "small_fry",
        "weakness": ["light"],
        "resist": ["dark"],
        "skills": [
            {"name": "羽ばたき", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [8, 12]}
        ]
    },

    "baby_spider": {
        "name": "ベビースパイダー",
        "max_hp": 58,
        "image": "/static/images/baby_spider.png",
        "role": "small_fry",
        "weakness": ["fire"],
        "resist": [],
        "skills": [
            {"name": "小さな牙", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [8, 13]}
        ]
    },

    "mud_frog": {
        "name": "マッドフロッグ",
        "max_hp": 65,
        "image": "/static/images/mud_frog.png",
        "role": "small_fry",
        "weakness": ["thunder"],
        "resist": ["water"],
        "skills": [
            {"name": "ジャンプ", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [9, 13]}
        ]
    },

    "wild_chicken": {
        "name": "ワイルドチキン",
        "max_hp": 55,
        "image": "/static/images/wild_chicken.png",
        "role": "small_fry",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "くちばし", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [8, 12]}
        ]
    },

    "honey_bee": {
        "name": "ハニービー",
        "max_hp": 52,
        "image": "/static/images/honey_bee.png",
        "role": "small_fry",
        "weakness": ["fire"],
        "resist": ["wind"],
        "skills": [
            {"name": "針刺し", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [9, 13]}
        ]
    },

    "baby_treant": {
        "name": "ベビートレント",
        "max_hp": 70,
        "image": "/static/images/baby_treant.png",
        "role": "small_fry",
        "weakness": ["fire"],
        "resist": [],
        "skills": [
            {"name": "小枝パンチ", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [9, 14]}
        ]
    },

    "rock_mole": {
        "name": "ロックモール",
        "max_hp": 68,
        "image": "/static/images/rock_mole.png",
        "role": "small_fry",
        "weakness": ["thunder"],
        "resist": [],
        "skills": [
            {"name": "突進", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [9, 13]}
        ]
    },

    "wild_boar": {
        "name": "ワイルドボア",
        "max_hp": 80,
        "image": "/static/images/wild_boar.png",
        "role": "small_fry",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "突進", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [10, 16]}
        ]
    },

    "gray_wolf": {
        "name": "グレイウルフ",
        "max_hp": 75,
        "image": "/static/images/gray_wolf.png",
        "role": "small_fry",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "かみつき", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [10, 17]}
        ]
    },

    "giant_rat": {
        "name": "ジャイアントラット",
        "max_hp": 65,
        "image": "/static/images/giant_rat.png",
        "role": "small_fry",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "ひっかく", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [9, 14]}
        ]
    },

    "mad_monkey": {
        "name": "マッドモンキー",
        "max_hp": 70,
        "image": "/static/images/mad_monkey.png",
        "role": "small_fry",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "石投げ", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [9, 15]}
        ]
    },

    "hawk": {
        "name": "ホーク",
        "max_hp": 60,
        "image": "/static/images/hawk.png",
        "role": "small_fry",
        "weakness": ["thunder"],
        "resist": ["wind"],
        "skills": [
            {"name": "急降下", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [11, 17]}
        ]
    },

    "sand_scorpion": {
        "name": "サンドスコーピオン",
        "max_hp": 90,
        "image": "/static/images/sand_scorpion.png",
        "role": "small_fry",
        "weakness": ["water"],
        "resist": ["earth"],
        "skills": [
            {"name": "毒針", "rate": 80, "target": "single", "category": "physical", "element": "none", "damage": [10, 16]},
            {"name": "はさみ攻撃", "rate": 20, "target": "single", "category": "physical", "element": "none", "damage": [14, 22]}
        ]
    },

    "lizardman": {
        "name": "リザードマン",
        "max_hp": 120,
        "image": "/static/images/lizardman.png",
        "role": "small_fry",
        "weakness": ["ice"],
        "resist": [],
        "skills": [
            {"name": "槍突き", "rate": 75, "target": "single", "category": "physical", "element": "none", "damage": [14, 22]},
            {"name": "尻尾攻撃", "rate": 25, "target": "single", "category": "physical", "element": "none", "damage": [18, 28]}
        ]
    },

    "needle_boar": {
        "name": "ニードルボア",
        "max_hp": 95,
        "image": "/static/images/needle_boar.png",
        "role": "small_fry",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "体当たり", "rate": 80, "target": "single", "category": "physical", "element": "none", "damage": [11, 18]},
            {"name": "全身突撃", "rate": 20, "target": "single", "category": "physical", "element": "none", "damage": [16, 25]}
        ]
    },

    "raccoon": {
        "name": "ラクーン",
        "max_hp": 72,
        "image": "/static/images/raccoon.png",
        "role": "small_fry",
        "weakness": [],
        "resist": [],
        "skills": [
            {"name": "ひっかき", "rate": 100, "target": "single", "category": "physical", "element": "none", "damage": [9, 15]}
        ]
    },

    "mountain_goat": {
        "name": "マウンテンゴート",
        "max_hp": 100,
        "image": "/static/images/mountain_goat.png",
        "role": "small_fry",
        "weakness": [],
        "resist": ["earth"],
        "skills": [
            {"name": "角突き", "rate": 80, "target": "single", "category": "physical", "element": "none", "damage": [11, 18]},
            {"name": "飛び蹴り", "rate": 20, "target": "single", "category": "physical", "element": "none", "damage": [16, 25]}
        ]
    },

}
