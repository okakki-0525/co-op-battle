"""
YouTube Shorts向け 協力バトルPV Ver.3

実行方法:
    pip install moviepy pillow numpy
    python promo_movie_v3.py

出力:
    promo_movie_v3.mp4

BGM:
    BGM_PATH を変更すると差し替えできます。
    ファイルが存在しない場合は無音で出力します。

QR:
    プロジェクト直下の co_op_battle_qr.png を使用します。
    無い場合は仮のQR枠を表示して停止しません。
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

try:
    from moviepy import AudioFileClip, VideoClip
except ImportError:
    from moviepy.editor import AudioFileClip, VideoClip

WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 30.0

ROOT = Path(__file__).resolve().parent
IMAGE_DIR = ROOT / "static" / "images"
SOUND_DIR = ROOT / "static" / "sounds"
OUTPUT_PATH = ROOT / "promo_movie_v3.mp4"
BGM_PATH = SOUND_DIR / "battle_bgm.mp3"
URL = "https://co-op-battle.onrender.com/login"
QR_PATH = ROOT / "co_op_battle_qr.png"

ASSETS = {
    "background": IMAGE_DIR / "login_bg.png",
    "logo": IMAGE_DIR / "title.png",
    "hero": IMAGE_DIR / "yusya.png",
    "tank": IMAGE_DIR / "tanc.png",
    "mage": IMAGE_DIR / "majyutu.png",
}

ENEMY_NAMES = [
    "slime.png", "goblin.png", "orc.png", "skeleton_knight.png", "fire_lizard.png",
    "flame_witch.png", "minotaur.png", "death_knight.png", "lich.png",
    "tempest_dragon.png", "demon_lord.png",
]


def load_font(size: int, bold: bool = False):
    candidates = [
        r"C:\Windows\Fonts\meiryob.ttc" if bold else r"C:\Windows\Fonts\meiryo.ttc",
        r"C:\Windows\Fonts\YuGothB.ttc" if bold else r"C:\Windows\Fonts\YuGothR.ttc",
        r"C:\Windows\Fonts\msgothic.ttc",
        r"C:\Windows\Fonts\arialbd.ttf" if bold else r"C:\Windows\Fonts\arial.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size=size)
    return ImageFont.load_default()

FONT_XXL = load_font(92, True)
FONT_XL = load_font(74, True)
FONT_L = load_font(58, True)
FONT_M = load_font(42, True)
FONT_S = load_font(30, True)
FONT_XS = load_font(24, False)
FONT_URL = load_font(31, False)


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def ease_out(x: float) -> float:
    x = clamp(x)
    return 1 - (1 - x) * (1 - x)


def ease_in_out(x: float) -> float:
    x = clamp(x)
    return x * x * (3 - 2 * x)


def text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_center(draw: ImageDraw.ImageDraw, text: str, y: int, font, fill, stroke=0, stroke_fill=(0, 0, 0, 255)):
    w, _ = text_size(draw, text, font)
    draw.text(((WIDTH - w) // 2, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


def load_image(path: Path) -> Image.Image | None:
    if not path.exists():
        return None
    try:
        return Image.open(path).convert("RGBA")
    except OSError:
        return None


def fit_image(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    img = img.convert("RGBA")
    scale = min(max_w / img.width, max_h / img.height)
    size = (max(1, int(img.width * scale)), max(1, int(img.height * scale)))
    return img.resize(size, Image.Resampling.LANCZOS)


def cover_image(img: Image.Image, w: int, h: int) -> Image.Image:
    img = img.convert("RGBA")
    scale = max(w / img.width, h / img.height)
    resized = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.Resampling.LANCZOS)
    left = (resized.width - w) // 2
    top = (resized.height - h) // 2
    return resized.crop((left, top, left + w, top + h))


def paste_alpha(base: Image.Image, layer: Image.Image, xy: tuple[int, int], alpha: float = 1.0):
    alpha = clamp(alpha)
    if alpha <= 0:
        return
    layer = layer.convert("RGBA")
    if alpha < 1:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda p: int(p * alpha)))
    base.alpha_composite(layer, xy)


def make_placeholder(label: str, color: tuple[int, int, int], size=(320, 380)) -> Image.Image:
    w, h = size
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle((18, 18, w - 18, h - 18), radius=34, fill=(*color, 235), outline=(255, 230, 150, 230), width=5)
    draw.ellipse((int(w * .30), int(h * .13), int(w * .70), int(h * .42)), fill=(255, 248, 220, 215))
    draw.rounded_rectangle((int(w * .20), int(h * .42), int(w * .80), int(h * .78)), radius=42, fill=(255, 248, 220, 185))
    tw, th = text_size(draw, label, FONT_M)
    draw.text(((w - tw) // 2, h - th - 36), label, font=FONT_M, fill=(20, 18, 18, 255))
    return img


def make_vertical_bg() -> Image.Image:
    src = load_image(ASSETS["background"])
    if src:
        bg = cover_image(src, WIDTH, HEIGHT)
    else:
        bg = Image.new("RGBA", (WIDTH, HEIGHT), (10, 13, 25, 255))
        d = ImageDraw.Draw(bg)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            d.line((0, y, WIDTH, y), fill=(int(8 + 22 * ratio), int(12 + 18 * ratio), int(26 + 48 * ratio), 255))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle((0, 0, WIDTH, HEIGHT), fill=(4, 6, 12, 132))
    for i in range(10):
        x = -180 + i * 155
        d.line((x, 0, x + 620, HEIGHT), fill=(255, 150, 55, 16), width=5)
    d.ellipse((-300, 230, WIDTH + 300, 1280), fill=(255, 80, 25, 24))
    return Image.alpha_composite(bg, overlay)


def make_logo() -> Image.Image:
    logo = load_image(ASSETS["logo"])
    if logo:
        return fit_image(logo, 680, 220)
    img = Image.new("RGBA", (680, 190), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((10, 24, 670, 166), radius=28, fill=(16, 20, 33, 235), outline=(255, 218, 90, 255), width=5)
    label = "協力バトル"
    tw, th = text_size(d, label, FONT_XL)
    d.text(((680 - tw) // 2, (190 - th) // 2 - 8), label, font=FONT_XL, fill=(255, 236, 145, 255), stroke_width=4, stroke_fill=(80, 28, 6, 255))
    return img


def make_qr() -> Image.Image:
    qr = load_image(QR_PATH)
    if qr:
        return fit_image(qr, 330, 330)
    img = Image.new("RGBA", (330, 330), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 329, 329), outline=(0, 0, 0, 255), width=10)
    for ox, oy in [(32, 32), (224, 32), (32, 224)]:
        d.rectangle((ox, oy, ox + 72, oy + 72), outline=(0, 0, 0, 255), width=12)
        d.rectangle((ox + 24, oy + 24, ox + 48, oy + 48), fill=(0, 0, 0, 255))
    for y in range(122, 280, 24):
        for x in range(120, 282, 24):
            if (x + y) // 24 % 2 == 0:
                d.rectangle((x, y, x + 13, y + 13), fill=(0, 0, 0, 255))
    return img


def make_enemy_card(enemy: Image.Image, label: str) -> Image.Image:
    card = Image.new("RGBA", (610, 760), (0, 0, 0, 0))
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((46, 48, 564, 704), radius=38, fill=(0, 0, 0, 180))
    card.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(20)))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle((30, 26, 580, 692), radius=36, fill=(15, 18, 29, 246), outline=(255, 197, 78, 245), width=7)
    d.rounded_rectangle((64, 72, 546, 542), radius=28, fill=(35, 20, 30, 240), outline=(255, 85, 35, 175), width=4)
    fitted = fit_image(enemy, 440, 440)
    paste_alpha(card, fitted, ((610 - fitted.width) // 2, 102 + (400 - fitted.height) // 2), 1)
    tw, _ = text_size(d, label, FONT_L)
    d.text(((610 - tw) // 2, 575), label, font=FONT_L, fill=(255, 236, 145, 255), stroke_width=3, stroke_fill=(70, 18, 4, 255))
    return card


def make_enemies() -> list[Image.Image]:
    enemies = []
    for name in ENEMY_NAMES:
        img = load_image(IMAGE_DIR / name)
        if img:
            enemies.append(img)
    while len(enemies) < 8:
        i = len(enemies) + 1
        enemies.append(make_placeholder(f"敵{i}", (105 + i * 17 % 120, 36, 54 + i * 21 % 140)))
    return enemies


def make_character(key: str, label: str, color: tuple[int, int, int], max_size: tuple[int, int]) -> Image.Image:
    img = load_image(ASSETS[key])
    if img is None:
        img = make_placeholder(label, color)
    return fit_image(img, *max_size)

BG = make_vertical_bg()
LOGO = make_logo()
QR = make_qr()
ENEMIES = make_enemies()
ENEMY_CARDS = [make_enemy_card(e, f"ENEMY {i + 1}") for i, e in enumerate(ENEMIES)]
BOSS = fit_image(ENEMIES[-1], 390, 390)
HERO = make_character("hero", "勇者", (220, 74, 58), (230, 310))
TANK = make_character("tank", "タンク", (64, 133, 222), (250, 330))
MAGE = make_character("mage", "魔術師", (143, 86, 220), (230, 310))


def draw_caption(frame: Image.Image, main: str, sub: str | None, y: int, alpha: float = 1.0, accent=(255, 236, 145)):
    d = ImageDraw.Draw(frame)
    a = int(255 * clamp(alpha))
    pad = 26
    mw, mh = text_size(d, main, FONT_XL)
    box_h = 112 if not sub else 170
    d.rounded_rectangle(((WIDTH - mw) // 2 - pad, y - 16, (WIDTH + mw) // 2 + pad, y + box_h), radius=24, fill=(3, 5, 11, int(178 * alpha)), outline=(*accent, int(185 * alpha)), width=3)
    draw_center(d, main, y, FONT_XL, (*accent, a), 4, (58, 14, 4, int(235 * alpha)))
    if sub:
        sw, _ = text_size(d, sub, FONT_M)
        d.text(((WIDTH - sw) // 2, y + 94), sub, font=FONT_M, fill=(255, 255, 255, int(238 * alpha)), stroke_width=2, stroke_fill=(0, 0, 0, int(190 * alpha)))


def speed_lines(frame: Image.Image, t: float, alpha=42):
    d = ImageDraw.Draw(frame)
    for i in range(16):
        y = int((t * 780 + i * 160) % (HEIGHT + 300)) - 200
        d.line((-80, y, WIDTH + 120, y - 520), fill=(255, 215, 105, alpha), width=6)


def intro_index(t: float) -> int:
    e = clamp(t / 3.5)
    flips = int(1 + e * 13 + math.sin(e * math.pi) * 11)
    return flips % len(ENEMY_CARDS)


def scene_enemy_intro(t: float) -> Image.Image:
    frame = BG.copy()
    speed_lines(frame, t, 34)
    d = ImageDraw.Draw(frame)
    if t < 2.3:
        card = ENEMY_CARDS[intro_index(t)]
        speed = .25 + .85 * math.sin(clamp(t / 3.5) * math.pi)
        scale = .76 + .08 * math.sin(t * (8 + 12 * speed))
        angle = math.sin(t * (7 + 11 * speed)) * (4 + 9 * speed)
    else:
        card = make_enemy_card(ENEMIES[-1], "BOSS")
        scale = .90 + .04 * math.sin(t * 17)
        angle = math.sin(t * 12) * 2
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((110, 385, 970, 1260), fill=(255, 82, 28, 84))
    frame.alpha_composite(glow.filter(ImageFilter.GaussianBlur(34)))
    for i in range(3):
        ghost = card.resize((int(card.width * scale * (.92 - i * .04)), int(card.height * scale * (.92 - i * .04))), Image.Resampling.LANCZOS).rotate(angle + i * 6 - 8, resample=Image.Resampling.BICUBIC, expand=True)
        paste_alpha(frame, ghost, ((WIDTH - ghost.width) // 2 + (i - 1) * 32, 520 + (i - 1) * 18), .12)
    layer = card.resize((int(card.width * scale), int(card.height * scale)), Image.Resampling.LANCZOS).rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)
    paste_alpha(frame, layer, ((WIDTH - layer.width) // 2, 515), 1)
    if t < 1.45:
        draw_caption(frame, "戦闘だけの", "ブラウザ協力RPG", 112, clamp(t / .4))
    elif t < 2.35:
        draw_caption(frame, "無料で", "すぐ遊べる！", 112, clamp((t - 1.45) / .22), (124, 226, 255))
    else:
        draw_caption(frame, "強敵出現！", "仲間を集めろ", 112, clamp((t - 2.35) / .18), (255, 100, 54))
    return frame


def scene_party(t: float) -> Image.Image:
    local = t - 3.5
    frame = BG.copy()
    d = ImageDraw.Draw(frame)
    draw_caption(frame, "オンラインで", "仲間と協力！", 132, clamp(local / .5), (124, 226, 255))
    members = [(HERO, "勇者", "炎剣で攻める", 118), (TANK, "タンク", "仲間を守る", 398), (MAGE, "魔術師", "魔法で支援", 678)]
    for i, (img, name, role, x) in enumerate(members):
        p = ease_out(clamp((local - .35 - i * .22) / .7))
        y = int(760 - (1 - p) * 220 + math.sin(t * 4 + i) * 7)
        shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.ellipse((x - 40, y + img.height - 42, x + img.width + 40, y + img.height + 28), fill=(0, 0, 0, int(120 * p)))
        frame.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(12)))
        paste_alpha(frame, img, (x, y), p)
        d.rounded_rectangle((x - 20, 1250, x + img.width + 20, 1378), radius=20, fill=(8, 12, 22, int(205 * p)), outline=(255, 213, 79, int(170 * p)), width=2)
        nw, _ = text_size(d, name, FONT_M)
        rw, _ = text_size(d, role, FONT_S)
        d.text((x + img.width // 2 - nw // 2, 1264), name, font=FONT_M, fill=(255, 236, 145, int(255 * p)))
        d.text((x + img.width // 2 - rw // 2, 1320), role, font=FONT_S, fill=(240, 248, 255, int(235 * p)))
    return frame


def command_card(frame: Image.Image, x: int, y: int, title: str, skill: str, color, p: float):
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle((x, y, x + 780, y + 150), radius=24, fill=(8, 12, 22, int(220 * p)), outline=(*color, int(220 * p)), width=4)
    d.text((x + 34, y + 26), title, font=FONT_M, fill=(255, 255, 255, int(255 * p)))
    d.text((x + 290, y + 24), skill, font=FONT_L, fill=(*color, int(255 * p)), stroke_width=2, stroke_fill=(0, 0, 0, int(190 * p)))
    d.rounded_rectangle((x + 646, y + 38, x + 740, y + 112), radius=12, fill=(*color, int(225 * p)))
    d.text((x + 670, y + 56), "OK", font=FONT_S, fill=(12, 16, 28, int(255 * p)))


def scene_commands(t: float) -> Image.Image:
    local = t - 6
    frame = BG.copy()
    d = ImageDraw.Draw(frame)
    draw_caption(frame, "全員のコマンドが", "揃ったら一斉行動", 116, 1, (255, 236, 145))
    cards = [("勇者", "炎剣", (255, 92, 42)), ("タンク", "フォートレス", (118, 208, 255)), ("魔術師", "マジックブースト", (222, 154, 255))]
    for i, (title, skill, color) in enumerate(cards):
        p = clamp((local - i * .28) / .35)
        command_card(frame, 150, 520 + i * 190, title, skill, color, p)
    if local > 2.2:
        a = clamp((local - 2.2) / .25)
        d.rectangle((0, 0, WIDTH, HEIGHT), fill=(255, 232, 160, int(50 * math.sin(clamp(local - 2.2) * math.pi))))
        draw_center(d, "ACTION！", HEIGHT // 2 - 64, FONT_XXL, (255, 38, 38, int(255 * a)), 7, (88, 0, 0, int(245 * a)))
    return frame


def draw_battle_screen(frame: Image.Image, local: float, shake=0):
    ox = int(math.sin(local * 92) * shake)
    oy = int(math.cos(local * 77) * shake)
    d = ImageDraw.Draw(frame)
    sx, sy, sw, sh = 70 + ox, 175 + oy, 940, 1390
    d.rounded_rectangle((sx, sy, sx + sw, sy + sh), radius=28, fill=(27, 31, 42, 245), outline=(8, 10, 18, 240), width=4)
    d.rounded_rectangle((sx + 18, sy + 18, sx + sw - 18, sy + 98), radius=10, fill=(43, 49, 66, 255))
    draw_center(d, "協力バトル", sy + 30, FONT_S, (255, 255, 255, 255))
    turn = "ターン 1"
    tw, _ = text_size(d, turn, FONT_XS)
    d.text((sx + sw // 2 - tw // 2, sy + 64), turn, font=FONT_XS, fill=(220, 226, 240, 245))
    d.rounded_rectangle((sx + 18, sy + 114, sx + sw - 18, sy + 520), radius=10, fill=(43, 49, 66, 255))
    draw_center(d, "敵", sy + 130, FONT_S, (255, 255, 255, 255))
    boss_x, boss_y = sx + 320, sy + 172
    d.rounded_rectangle((boss_x, boss_y, boss_x + 300, boss_y + 295), radius=12, fill=(23, 29, 43, 255), outline=(45, 53, 72, 255), width=2)
    fitted = fit_image(ENEMIES[-1], 230, 200)
    paste_alpha(frame, fitted, (boss_x + 150 - fitted.width // 2, boss_y + 56), 1)
    boss_hp = max(1200, 7800 - int(max(0, local - 2.0) * 720))
    d.text((boss_x + 92, boss_y + 12), "BOSS", font=FONT_S, fill=(255, 236, 145, 255))
    d.text((boss_x + 42, boss_y + 238), f"HP:{boss_hp}/7800", font=FONT_XS, fill=(235, 238, 248, 255))
    d.rounded_rectangle((boss_x + 42, boss_y + 270, boss_x + 258, boss_y + 282), radius=6, fill=(85, 85, 85, 255))
    d.rounded_rectangle((boss_x + 42, boss_y + 270, boss_x + 42 + int(216 * boss_hp / 7800), boss_y + 282), radius=6, fill=(229, 57, 53, 255))
    d.rounded_rectangle((sx + 18, sy + 538, sx + sw - 18, sy + 800), radius=10, fill=(43, 49, 66, 255))
    d.text((sx + 44, sy + 556), "パーティ", font=FONT_S, fill=(255, 255, 255, 255))
    party = [("勇者", "勇者", 1280, 1280, "炎剣"), ("タンク", "タンク", 1850, 1850, "大盾"), ("魔術師", "魔術師", 960, 960, "魔導書")]
    if local > 7.2:
        party = [("勇者", "勇者", 1120, 1280, "炎剣"), ("タンク", "タンク", 1780, 1850, "大盾"), ("魔術師", "魔術師", 850, 960, "魔導書")]
    positions = {}
    for i, (name, job, hp, maxhp, item) in enumerate(party):
        y = sy + 610 + i * 56
        fill = (90, 74, 31, 255) if i == 0 else (57, 64, 86, 255)
        if 7.1 < local < 7.8:
            fill = (190, 38, 58, 240)
        d.rounded_rectangle((sx + 44, y, sx + sw - 44, y + 46), radius=8, fill=fill, outline=(255, 213, 79, 255) if i == 0 else fill, width=2)
        d.text((sx + 62, y + 8), f"{name}({job})", font=FONT_XS, fill=(255, 255, 255, 255))
        d.text((sx + 286, y + 8), f"HP:{hp}/{maxhp}", font=FONT_XS, fill=(230, 230, 230, 255))
        d.text((sx + 524, y + 8), f"持込:{item}", font=FONT_XS, fill=(255, 204, 128, 255))
        d.rounded_rectangle((sx + 700, y + 16, sx + 850, y + 28), radius=6, fill=(85, 85, 85, 255))
        d.rounded_rectangle((sx + 700, y + 16, sx + 700 + int(150 * hp / maxhp), y + 28), radius=6, fill=(61, 220, 132, 255))
        positions[name] = (sx + 500, y + 23)
    d.rounded_rectangle((sx + 18, sy + 820, sx + sw - 18, sy + 940), radius=10, fill=(43, 49, 66, 255))
    d.rounded_rectangle((sx + 44, sy + 850, sx + sw - 44, sy + 912), radius=8, fill=(17, 23, 34, 255))
    message = "全員の行動を待っています"
    if 2.0 < local < 4.0:
        message = "勇者の炎剣！"
    elif 5.0 < local < 6.7:
        message = "フォートレスがダメージを軽減した！"
    elif 8.5 < local < 10.5:
        message = "魔術師のマジックブースト！"
    elif local > 11.0:
        message = "協力攻撃！"
    mw, _ = text_size(d, message, FONT_S)
    d.text((sx + sw // 2 - mw // 2, sy + 866), message, font=FONT_S, fill=(255, 255, 255, 255))
    by = sy + 960
    for i, (label, color) in enumerate([("攻撃", (229, 57, 53)), ("回復", (67, 160, 71)), ("盾", (30, 136, 229)), ("魔法", (142, 36, 170))]):
        bx = sx + 24 + i * 224
        d.rounded_rectangle((bx, by, bx + 206, by + 64), radius=10, fill=(*color, 255))
        lw, _ = text_size(d, label, FONT_S)
        d.text((bx + 103 - lw // 2, by + 14), label, font=FONT_S, fill=(255, 255, 255, 255))
    d.rounded_rectangle((sx + 18, sy + 1050, sx + sw - 18, sy + 1355), radius=10, fill=(43, 49, 66, 255))
    d.text((sx + 44, sy + 1070), "ログ", font=FONT_S, fill=(255, 255, 255, 255))
    d.rounded_rectangle((sx + 44, sy + 1112, sx + sw - 44, sy + 1324), radius=10, fill=(17, 23, 34, 255))
    logs = ["強敵が現れた！"]
    if local > 2.2: logs.append("勇者の炎剣！ 520ダメージ！")
    if local > 5.6: logs.append("フォートレスがダメージを軽減した！")
    if local > 8.9: logs.append("魔術師のマジックブースト！")
    if local > 11.2: logs.append("協力攻撃！ 1280ダメージ！")
    for i, log in enumerate(logs[-5:]):
        d.text((sx + 66, sy + 1132 + i * 36), log, font=FONT_XS, fill=(235, 238, 248, 245))
    return {"boss": (boss_x + 150, boss_y + 150), **positions}


def slash(frame, local, start_time, start, end, color=(255, 80, 22)):
    p = clamp((local - start_time) / .75)
    impact = clamp(1 - abs(local - start_time - .72) / .28)
    if p <= 0 and impact <= 0:
        return 0
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    tip = (start[0] + (end[0] - start[0]) * ease_out(p), start[1] + (end[1] - start[1]) * ease_out(p))
    for i in range(10):
        tr = max(0, p - i * .055)
        sx = start[0] + (end[0] - start[0]) * tr
        sy = start[1] + (end[1] - start[1]) * tr
        d.line((sx, sy, tip[0], tip[1]), fill=(255, 55 + i * 18, 12, int(215 * (1 - i / 11))), width=max(5, 42 - i * 3))
    d.line((start[0], start[1], tip[0], tip[1]), fill=(255, 248, 200, 245), width=10)
    if impact > 0:
        cx, cy = end
        for i in range(24):
            a = i / 24 * math.tau
            length = 42 + 120 * impact
            d.line((cx, cy, cx + math.cos(a) * length, cy + math.sin(a) * length), fill=(255, 226, 92, int(220 * impact)), width=4)
        d.ellipse((cx - 120 * impact, cy - 88 * impact, cx + 120 * impact, cy + 88 * impact), fill=(255, 104, 24, int(112 * impact)))
    frame.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(2)))
    frame.alpha_composite(overlay)
    return impact


def damage(frame, txt, x, y, local, start, color=(255, 238, 132)):
    a = clamp((local - start) / .12) * clamp((start + .85 - local) / .25)
    if a <= 0:
        return
    p = ease_out(clamp((local - start) / .85))
    d = ImageDraw.Draw(frame)
    d.text((x, y - int(68 * p)), txt, font=FONT_L, fill=(*color, int(255 * a)), stroke_width=5, stroke_fill=(65, 8, 2, int(240 * a)))


def scene_battle_start(t):
    local = t - 9
    frame = BG.copy()
    p = clamp(local / 1)
    d = ImageDraw.Draw(frame)
    frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, int(110 * p))))
    pos = draw_battle_screen(frame, 0, int(14 * math.sin(local * 18) * clamp(local / .35)))
    if local < .55:
        draw_center(d, "BATTLE START", 820, FONT_XXL, (255, 236, 145, 255), 7, (82, 20, 4, 245))
    return frame


def scene_battle(t):
    local = t - 10
    hit1 = clamp(1 - abs(local - 2.72) / .28)
    hit2 = clamp(1 - abs(local - 6.35) / .32)
    hit3 = clamp(1 - abs(local - 11.55) / .38)
    frame = BG.copy()
    frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 104)))
    pos = draw_battle_screen(frame, local, int(16 * max(hit1, hit2, hit3)))
    boss = pos["boss"]
    hero = pos["勇者"]
    tank = pos["タンク"]
    mage = pos["魔術師"]
    impact = slash(frame, local, 2.0, (hero[0] + 220, hero[1] + 40), boss)
    # fortress shield
    shield_p = clamp((local - 4.8) / .45) * clamp((7.0 - local) / .6)
    if shield_p > 0:
        ov = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        d.rounded_rectangle((120, 700, 960, 1090), radius=42, outline=(110, 204, 255, int(190 * shield_p)), width=13)
        d.rounded_rectangle((154, 735, 926, 1054), radius=36, outline=(255, 255, 255, int(85 * shield_p)), width=5)
        frame.alpha_composite(ov.filter(ImageFilter.GaussianBlur(5)))
        frame.alpha_composite(ov)
        draw_caption(frame, "フォートレス！", "ダメージ軽減", 274, shield_p, (130, 218, 255))
    # enemy aoe
    aoe_p = clamp((local - 5.7) / .8)
    aoe_hit = clamp(1 - abs(local - 6.35) / .32)
    if aoe_p > 0 and local < 7.5:
        ov = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        r = 80 + 950 * ease_out(aoe_p)
        d.ellipse((boss[0] - r, boss[1] - r * .62, boss[0] + r, boss[1] + r * .62), outline=(194, 76, 255, int(170 * (1 - aoe_p * .55))), width=18)
        frame.alpha_composite(ov.filter(ImageFilter.GaussianBlur(3)))
        frame.alpha_composite(ov)
    # magic boost
    magic_p = clamp((local - 8.5) / 1.0)
    magic_hit = clamp(1 - abs(local - 9.55) / .32)
    if magic_p > 0:
        ov = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        tip = (mage[0] + (boss[0] - mage[0]) * ease_out(magic_p), mage[1] + (boss[1] - mage[1]) * ease_out(magic_p))
        for i in range(8):
            off = math.sin(local * 8 + i) * 28
            d.line((mage[0], mage[1] + off, tip[0], tip[1] - off), fill=(178, 102, 255, 105 + i * 14), width=9)
        if magic_hit > 0:
            d.ellipse((boss[0] - 135 * magic_hit, boss[1] - 110 * magic_hit, boss[0] + 135 * magic_hit, boss[1] + 110 * magic_hit), fill=(198, 104, 255, int(125 * magic_hit)))
        frame.alpha_composite(ov.filter(ImageFilter.GaussianBlur(3)))
        frame.alpha_composite(ov)
    # coop finish
    coop_p = clamp((local - 11.0) / 1.1)
    coop_hit = clamp(1 - abs(local - 11.55) / .38)
    if coop_p > 0:
        ov = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        d = ImageDraw.Draw(ov)
        for origin, color in [(hero, (255, 78, 32)), (tank, (92, 202, 255)), (mage, (207, 116, 255))]:
            tip = (origin[0] + (boss[0] - origin[0]) * ease_out(coop_p), origin[1] + (boss[1] - origin[1]) * ease_out(coop_p))
            d.line((origin[0], origin[1], tip[0], tip[1]), fill=(*color, 220), width=20)
            d.line((origin[0], origin[1], tip[0], tip[1]), fill=(255, 248, 210, 200), width=7)
        if coop_hit > 0:
            d.ellipse((boss[0] - 200 * coop_hit, boss[1] - 150 * coop_hit, boss[0] + 200 * coop_hit, boss[1] + 150 * coop_hit), fill=(255, 231, 128, int(150 * coop_hit)))
        frame.alpha_composite(ov.filter(ImageFilter.GaussianBlur(4)))
        frame.alpha_composite(ov)
        draw_caption(frame, "協力攻撃！", "みんなで勝つ", 260, clamp((local - 11) / .25), (255, 236, 145))
    damage(frame, "520", boss[0] - 52, boss[1] - 90, local, 2.72)
    damage(frame, "120", hero[0] - 190, hero[1] - 80, local, 6.38, (255, 170, 116))
    damage(frame, "80", tank[0] - 190, tank[1] - 80, local, 6.45, (255, 170, 116))
    damage(frame, "110", mage[0] - 190, mage[1] - 80, local, 6.52, (255, 170, 116))
    damage(frame, "680", boss[0] - 52, boss[1] - 110, local, 9.55, (226, 176, 255))
    damage(frame, "1280", boss[0] - 74, boss[1] - 130, local, 11.55)
    flash = max(impact, aoe_hit, magic_hit, coop_hit)
    if flash > 0:
        frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (255, 232, 156, int(70 * flash))))
    return frame


def scene_ending(t):
    local = t - 25
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (9, 12, 22, 255))
    d = ImageDraw.Draw(frame)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        d.line((0, y, WIDTH, y), fill=(int(10 + ratio * 18), int(12 + ratio * 16), int(24 + ratio * 36), 255))
    a = clamp(local / .7)
    paste_alpha(frame, LOGO, ((WIDTH - LOGO.width) // 2, 110), a)
    draw_center(d, "協力バトルONLINE", 390, FONT_XL, (255, 236, 145, int(255 * a)), 4, (68, 19, 4, int(230 * a)))
    draw_center(d, "最大6人で協力バトル！", 520, FONT_L, (255, 255, 255, int(242 * a)), 3, (0, 0, 0, int(215 * a)))
    draw_center(d, "仲間と連携して強敵を倒せ！", 610, FONT_M, (230, 238, 255, int(232 * a)), 2, (0, 0, 0, int(190 * a)))
    d.rounded_rectangle((174, 760, 906, 1538), radius=34, fill=(246, 247, 250, int(255 * a)), outline=(255, 204, 96, int(255 * a)), width=5)
    paste_alpha(frame, QR, ((WIDTH - QR.width) // 2, 825), a)
    draw_center(d, "今すぐ無料でプレイ！", 1196, FONT_L, (18, 22, 32, int(255 * a)), 0)
    uw, _ = text_size(d, URL, FONT_URL)
    d.text(((WIDTH - uw) // 2, 1296), URL, font=FONT_URL, fill=(30, 36, 48, int(255 * a)))
    draw_center(d, "概要欄にもURLがあります！", 1710, FONT_M, (255, 255, 255, int(245 * a)), 3, (0, 0, 0, int(225 * a)))
    if local > 4.2:
        fade = clamp((local - 4.2) / .8)
        frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, int(255 * fade))))
    return frame


def render_frame(t: float) -> np.ndarray:
    if t < 3.5:
        frame = scene_enemy_intro(t)
    elif t < 6:
        frame = scene_party(t)
    elif t < 9:
        frame = scene_commands(t)
    elif t < 10:
        frame = scene_battle_start(t)
    elif t < 25:
        frame = scene_battle(t)
    else:
        frame = scene_ending(t)
    return np.array(frame.convert("RGB"))


def set_audio_compat(video: VideoClip, audio: AudioFileClip) -> VideoClip:
    return video.with_audio(audio) if hasattr(video, "with_audio") else video.set_audio(audio)


def main() -> None:
    clip = VideoClip(render_frame, duration=DURATION)
    audio = None
    if BGM_PATH.exists():
        audio = AudioFileClip(str(BGM_PATH))
        end = min(DURATION, audio.duration)
        audio = audio.subclipped(0, end) if hasattr(audio, "subclipped") else audio.subclip(0, end)
        audio = audio.with_duration(DURATION) if hasattr(audio, "with_duration") else audio.set_duration(DURATION)
        clip = set_audio_compat(clip, audio)
    clip.write_videofile(str(OUTPUT_PATH), fps=FPS, codec="libx264", audio_codec="aac" if audio else None, preset="medium", threads=4)
    clip.close()
    if audio:
        audio.close()
    print(f"動画を出力しました: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
