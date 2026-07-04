"""
通常YouTube向け 協力バトルONLINE 紹介PV Ver.4

Run:
    pip install moviepy pillow numpy
    python promo_movie_v4.py

Output:
    promo_movie_v4.mp4
"""

from __future__ import annotations

import math
import os
import random
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

try:
    from moviepy import AudioFileClip, CompositeAudioClip, VideoClip, concatenate_audioclips
except ImportError:
    from moviepy.editor import AudioFileClip, CompositeAudioClip, VideoClip, concatenate_audioclips

WIDTH = 1920
HEIGHT = 1080
FPS = 30
DURATION = 80.0
URL = "https://co-op-battle.onrender.com/login"

ROOT = Path(__file__).resolve().parent
IMAGE_DIR = ROOT / "static" / "images"
SOUND_DIR = ROOT / "static" / "sounds"
OUTPUT_PATH = ROOT / "promo_movie_v4.mp4"
BGM_PATH = SOUND_DIR / "tabidachi.mp3"
IMPACT_SFX_PATH = SOUND_DIR / "boss_attack.mp3"
QR_PATH = ROOT / "co_op_battle_qr.png"

TEXT = {
    'doc_title': '通常YouTube向け 協力バトルONLINE 紹介PV Ver.4',
    'intro1': 'ターン制バトルで',
    'intro2': 'メンバー一人ひとりを操作しているのが',
    'intro3': '別々の人間だったら面白くないですか？',
    'made': 'そんなブラウザゲームを作りました！！',
    'name_intro': 'その名も『協力バトルONLINE』',
    'battle_title': '協力バトルONLINE',
    'turn': 'ターン 1',
    'enemy': '敵',
    'party': 'パーティ',
    'command': 'コマンド',
    'log': 'ログ',
    'main_wait': '全員の行動を待っています',
    'hero': '勇者',
    'tank': 'タンク',
    'mage': '魔術師',
    'attack': '攻撃',
    'weapon': '武器',
    'shield': '盾',
    'magic': '魔法',
    'heal': '回復',
    'fire_sword': '炎剣',
    'fortress': 'フォートレス',
    'magic_boost': 'マジックブースト',
    'boss1': 'シャドウウルフ',
    'boss2': 'フレイムリザード',
    'boss3': 'デスナイト',
    'boss4': '魔王',
    'hero_title': '勇者の特徴',
    'hero_text': '勇者は攻撃すればするほど\n攻撃力が上がっていきます。\n\nただし\n防御スキルを持たないため\n仲間の援護が欠かせません。',
    'tank_title': 'タンクの特徴',
    'tank_text': 'タンクは仲間を守る専門職。\n\nダメージ軽減\n\n攻撃無効\n\nカウンターなど\n\n多彩な盾で仲間を支えます。',
    'mage_title': '魔術師の特徴',
    'mage_text': '魔術師は強力な攻撃魔法だけでなく\n\n回復\n\n能力強化\n\n補助魔法で\n\n戦況を大きく変えることができます。',
    'growth_title': '戦闘後にキャラが成長！',
    'growth_text': '戦闘が終わると\n一定の確率でキャラが成長します。\n\nHP\n\n攻撃力\n\n魔力\n\n少しずつ能力が上がっていきます。\n\nさらに\n\n強力な武器や盾、\n魔法を手に入れることもあります。',
    'hp_up': 'HP +1',
    'atk_up': '攻撃力 +1',
    'mag_up': '魔力 +1',
    'reward1': '炎剣を手に入れた！',
    'reward2': 'フォートレスを手に入れた！',
    'reward3': 'マジックブーストを手に入れた！',
    'chat_title': 'チャットで作戦会議',
    'chat1_name': '勇者',
    'chat1_msg': '次フォートレスお願い！',
    'chat2_name': 'タンク',
    'chat2_msg': '了解！',
    'chat3_name': '魔術師',
    'chat3_msg': '次のターンで強化します！',
    'chat4_name': '勇者',
    'chat4_msg': 'ナイス！',
    'ending_title': '協力バトルONLINE',
    'ending_sub': '今すぐ仲間と冒険に出よう！',
    'url_label': 'URL',
    'footer': '概要欄にもURLがあります！',
    'free': '無料ですぐ遊べるブラウザゲーム',
    'log1': '強敵が4体現れた！',
    'log2': '勇者が炎剣を構えた！',
    'log3': 'タンクが仲間を守る準備をした！',
    'log4': '魔術師が魔力を集中している！',
    'result': '勝利！ 報酬を確認しよう',
}
ASSETS = {
    "background": IMAGE_DIR / "login_bg.png",
    "logo": IMAGE_DIR / "title.png",
    "hero": IMAGE_DIR / "yusya.png",
    "tank": IMAGE_DIR / "tanc.png",
    "mage": IMAGE_DIR / "majyutu.png",
}

ENEMY_FILES = ["gray_wolf.png", "fire_lizard.png", "death_knight.png", "demon_lord.png"]
ENEMY_LABELS = [TEXT["boss1"], TEXT["boss2"], TEXT["boss3"], TEXT["boss4"]]
REWARD_TEXT = random.Random(7).choice([TEXT["reward1"], TEXT["reward2"], TEXT["reward3"]])


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

FONT_HUGE = load_font(76, True)
FONT_XXL = load_font(66, True)
FONT_XL = load_font(52, True)
FONT_L = load_font(40, True)
FONT_M = load_font(30, True)
FONT_S = load_font(24, True)
FONT_XS = load_font(19, False)
FONT_URL = load_font(30, False)


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def ease_out(x: float) -> float:
    x = clamp(x)
    return 1 - (1 - x) * (1 - x)


def text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_center(draw: ImageDraw.ImageDraw, text: str, y: int, font, fill, stroke=0, stroke_fill=(0, 0, 0, 255)):
    w, _ = text_size(draw, text, font)
    draw.text(((WIDTH - w) // 2, y), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


def draw_center_in_box(draw: ImageDraw.ImageDraw, text: str, box: tuple[int, int, int, int], font, fill, stroke=0, stroke_fill=(0, 0, 0, 255)):
    x1, y1, x2, y2 = box
    w, h = text_size(draw, text, font)
    draw.text((x1 + (x2 - x1 - w) // 2, y1 + (y2 - y1 - h) // 2), text, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)


def load_image(path: Path) -> Image.Image | None:
    if not path.exists():
        return None
    try:
        return Image.open(path).convert("RGBA")
    except Exception:
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


def make_placeholder(label: str, color=(120, 70, 120), size=(360, 320)) -> Image.Image:
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w, h = size
    d.rounded_rectangle((16, 16, w - 16, h - 16), radius=26, fill=(*color, 236), outline=(255, 220, 110, 230), width=4)
    d.ellipse((w // 2 - 58, 52, w // 2 + 58, 168), fill=(255, 246, 210, 210))
    d.rounded_rectangle((w // 2 - 92, 170, w // 2 + 92, 260), radius=38, fill=(255, 246, 210, 180))
    tw, th = text_size(d, label, FONT_M)
    d.text(((w - tw) // 2, h - th - 28), label, font=FONT_M, fill=(20, 18, 18, 255))
    return img


def make_background() -> Image.Image:
    src = load_image(ASSETS["background"])
    if src:
        bg = cover_image(src, WIDTH, HEIGHT)
    else:
        bg = Image.new("RGBA", (WIDTH, HEIGHT), (12, 16, 30, 255))
        d = ImageDraw.Draw(bg)
        for y in range(HEIGHT):
            r = y / HEIGHT
            d.line((0, y, WIDTH, y), fill=(int(10 + 24 * r), int(13 + 20 * r), int(30 + 54 * r), 255))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle((0, 0, WIDTH, HEIGHT), fill=(3, 5, 12, 126))
    d.ellipse((-180, 210, 860, 1030), fill=(255, 70, 28, 28))
    d.ellipse((1000, -250, 2220, 740), fill=(80, 180, 255, 22))
    for i in range(14):
        x = -260 + i * 170
        d.line((x, 0, x + 620, HEIGHT), fill=(255, 185, 80, 16), width=3)
    return Image.alpha_composite(bg, overlay)


def make_logo() -> Image.Image:
    logo = load_image(ASSETS["logo"])
    if logo:
        return fit_image(logo, 760, 210)
    img = Image.new("RGBA", (760, 180), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((10, 22, 750, 158), radius=24, fill=(16, 20, 33, 238), outline=(255, 218, 90, 255), width=5)
    w, _ = text_size(d, TEXT["battle_title"], FONT_XL)
    d.text(((760 - w) // 2, 54), TEXT["battle_title"], font=FONT_XL, fill=(255, 236, 145, 255), stroke_width=4, stroke_fill=(70, 18, 4, 255))
    return img


def make_qr() -> Image.Image:
    qr = load_image(QR_PATH)
    if qr:
        return fit_image(qr, 360, 360)
    img = Image.new("RGBA", (360, 360), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 359, 359), outline=(0, 0, 0, 255), width=10)
    for ox, oy in [(36, 36), (248, 36), (36, 248)]:
        d.rectangle((ox, oy, ox + 72, oy + 72), outline=(0, 0, 0, 255), width=12)
        d.rectangle((ox + 24, oy + 24, ox + 48, oy + 48), fill=(0, 0, 0, 255))
    for y in range(130, 302, 24):
        for x in range(130, 302, 24):
            if (x + y) // 24 % 2 == 0:
                d.rectangle((x, y, x + 13, y + 13), fill=(0, 0, 0, 255))
    return img

BG = make_background()
LOGO = make_logo()
QR = make_qr()
HERO_IMG = fit_image(load_image(ASSETS["hero"]) or make_placeholder(TEXT["hero"], (220, 74, 58)), 190, 230)
TANK_IMG = fit_image(load_image(ASSETS["tank"]) or make_placeholder(TEXT["tank"], (64, 133, 222)), 205, 245)
MAGE_IMG = fit_image(load_image(ASSETS["mage"]) or make_placeholder(TEXT["mage"], (143, 86, 220)), 190, 230)
ENEMY_IMAGES = []
for idx, name in enumerate(ENEMY_FILES):
    ENEMY_IMAGES.append(fit_image(load_image(IMAGE_DIR / name) or make_placeholder(ENEMY_LABELS[idx], (105, 40 + idx * 20, 90 + idx * 25)), 170, 135))


def rounded_panel(d, box, fill=(24, 29, 42, 238), outline=(66, 76, 105, 240), radius=18, width=2):
    d.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def typewriter_text(text: str, local: float, duration: float) -> str:
    count = int(len(text) * clamp(local / duration))
    return text[:count]


def draw_multiline(draw, text: str, x: int, y: int, font, fill, line_gap=12, stroke=0, stroke_fill=(0, 0, 0, 255)):
    yy = y
    for line in text.split("\n"):
        draw.text((x, yy), line, font=font, fill=fill, stroke_width=stroke, stroke_fill=stroke_fill)
        yy += text_size(draw, line or " ", font)[1] + line_gap
    return yy


def draw_caption_panel(frame: Image.Image, title: str, body: str, local: float, type_duration: float = 5.5, portrait: Image.Image | None = None):
    d = ImageDraw.Draw(frame)
    rounded_panel(d, (1040, 145, 1835, 905), fill=(12, 17, 30, 234), outline=(255, 210, 96, 210), radius=24, width=3)
    if portrait is not None:
        large = fit_image(portrait, 360, 430)
        paste_alpha(frame, large, (1460 - large.width // 2, 520), .20)
    d.text((1085, 190), title, font=FONT_XL, fill=(255, 236, 145, 255), stroke_width=2, stroke_fill=(60, 18, 4, 240))
    d.rounded_rectangle((1085, 266, 1790, 270), radius=2, fill=(255, 78, 42, 220))
    visible = typewriter_text(body, local, type_duration)
    draw_multiline(d, visible, 1090, 320, FONT_L, (243, 247, 255, 245), line_gap=16, stroke=1, stroke_fill=(0, 0, 0, 210))


def draw_button(d, box, label, color):
    d.rounded_rectangle(box, radius=12, fill=(*color, 255), outline=(255, 255, 255, 110), width=2)
    draw_center_in_box(d, label, box, FONT_M, (255, 255, 255, 255), 1, (0, 0, 0, 200))


def draw_battle_ui(frame: Image.Image, highlight: str | None = None, message: str | None = None, show_result=False):
    d = ImageDraw.Draw(frame)
    rounded_panel(d, (70, 52, 970, 965), fill=(20, 25, 38, 245), outline=(8, 10, 18, 240), radius=22, width=4)
    d.rounded_rectangle((92, 72, 948, 128), radius=10, fill=(43, 49, 66, 255))
    draw_center_in_box(d, TEXT["battle_title"], (92, 72, 948, 128), FONT_M, (255, 255, 255, 255))
    d.text((835, 90), TEXT["turn"], font=FONT_XS, fill=(220, 226, 240, 240))
    rounded_panel(d, (92, 145, 948, 390), fill=(43, 49, 66, 255), outline=(54, 62, 84, 255), radius=12, width=2)
    d.text((118, 162), TEXT["enemy"], font=FONT_S, fill=(255, 255, 255, 255))
    for i, (img, label) in enumerate(zip(ENEMY_IMAGES, ENEMY_LABELS)):
        x = 118 + i * 205
        d.rounded_rectangle((x, 200, x + 180, 358), radius=10, fill=(17, 23, 34, 255), outline=(70, 78, 102, 255), width=2)
        paste_alpha(frame, img, (x + 90 - img.width // 2, 214), 1)
        lw, _ = text_size(d, label, FONT_XS)
        d.text((x + 90 - lw // 2, 334), label, font=FONT_XS, fill=(255, 236, 145, 255))
        hp = 0.92 - i * 0.13
        d.rounded_rectangle((x + 22, 362, x + 158, 371), radius=5, fill=(82, 82, 82, 255))
        d.rounded_rectangle((x + 22, 362, x + 22 + int(136 * hp), 371), radius=5, fill=(229, 57, 53, 255))
    rounded_panel(d, (92, 410, 948, 502), fill=(17, 23, 34, 255), outline=(54, 62, 84, 255), radius=12, width=2)
    draw_center_in_box(d, message or TEXT["main_wait"], (92, 410, 948, 502), FONT_L, (255, 255, 255, 255), 1, (0, 0, 0, 220))
    rounded_panel(d, (92, 520, 948, 710), fill=(43, 49, 66, 255), outline=(54, 62, 84, 255), radius=12, width=2)
    d.text((118, 540), TEXT["party"], font=FONT_S, fill=(255, 255, 255, 255))
    party = [(TEXT["hero"], 1280, 1280, (255, 92, 42)), (TEXT["tank"], 1850, 1850, (118, 208, 255)), (TEXT["mage"], 960, 960, (222, 154, 255))]
    for i, (name, hp, maxhp, color) in enumerate(party):
        y = 576 + i * 42
        d.rounded_rectangle((118, y, 922, y + 34), radius=8, fill=(55, 64, 88, 255), outline=(*color, 200), width=2)
        d.text((136, y + 5), name, font=FONT_XS, fill=(255, 255, 255, 255))
        d.text((280, y + 5), f"HP:{hp}/{maxhp}", font=FONT_XS, fill=(230, 235, 245, 255))
        d.rounded_rectangle((548, y + 11, 880, y + 22), radius=5, fill=(82, 82, 82, 255))
        d.rounded_rectangle((548, y + 11, 548 + int(332 * hp / maxhp), y + 22), radius=5, fill=(61, 220, 132, 255))
    rounded_panel(d, (92, 730, 948, 875), fill=(43, 49, 66, 255), outline=(54, 62, 84, 255), radius=12, width=2)
    d.text((118, 748), TEXT["command"], font=FONT_S, fill=(255, 255, 255, 255))
    labels = [(TEXT["attack"], (229, 57, 53)), (TEXT["weapon"], (244, 128, 36)), (TEXT["shield"], (30, 136, 229)), (TEXT["magic"], (142, 36, 170)), (TEXT["heal"], (67, 160, 71))]
    for i, (label, color) in enumerate(labels):
        draw_button(d, (118 + i * 160, 795, 258 + i * 160, 852), label, color)
    rounded_panel(d, (92, 890, 948, 945), fill=(17, 23, 34, 255), outline=(54, 62, 84, 255), radius=12, width=2)
    logs = [TEXT["log1"], TEXT["log2"], TEXT["log3"], TEXT["log4"]]
    if show_result:
        logs = [TEXT["result"], TEXT["hp_up"], TEXT["atk_up"], TEXT["mag_up"]]
    d.text((118, 904), " / ".join(logs[:2]), font=FONT_XS, fill=(235, 238, 248, 245))
    d.text((118, 928), " / ".join(logs[2:4]), font=FONT_XS, fill=(235, 238, 248, 245))
    if highlight:
        overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        box = (102, 776, 428, 870) if highlight == "hero" else ((416, 776, 610, 870) if highlight == "tank" else (576, 776, 930, 870))
        od.ellipse(box, outline=(255, 24, 24, 255), width=9)
        od.ellipse((box[0]-9, box[1]-9, box[2]+9, box[3]+9), outline=(255, 210, 210, 110), width=5)
        frame.alpha_composite(overlay)


def mosaic_reveal(frame: Image.Image, local: float, duration: float = .75) -> Image.Image:
    p = clamp(local / duration)
    if p >= 1:
        return frame
    block = max(1, int(58 * (1 - ease_out(p)) + 2))
    small = frame.resize((max(1, WIDTH // block), max(1, HEIGHT // block)), Image.Resampling.BILINEAR)
    pix = small.resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)
    pix.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, int(170 * (1 - p)))))
    return pix


def scene_intro(t: float) -> Image.Image:
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    d = ImageDraw.Draw(frame)
    fade = 1.0 if t < 9 else clamp(1 - (t - 9) / .65)
    for text, y, start in [(TEXT["intro1"], 278, 0), (TEXT["intro2"], 430, 3), (TEXT["intro3"], 582, 6)]:
        alpha = int(255 * fade * clamp((t - start) / 1.0))
        if alpha > 0:
            draw_center(d, text, y, FONT_XL, (255, 255, 255, alpha), 0)
    return frame


def zoom_background(local: float) -> Image.Image:
    src = load_image(ASSETS["background"])
    bg = cover_image(src, WIDTH, HEIGHT) if src else BG.copy()
    scale = 1.0 + .42 * ease_out(clamp(local / 3.0))
    big = bg.resize((int(WIDTH * scale), int(HEIGHT * scale)), Image.Resampling.LANCZOS)
    left = (big.width - WIDTH) // 2
    top = (big.height - HEIGHT) // 2
    frame = big.crop((left, top, left + WIDTH, top + HEIGHT))
    frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 92)))
    return frame


def scene_title(t: float) -> Image.Image:
    local = t - 10
    frame = zoom_background(local)
    d = ImageDraw.Draw(frame)
    if local < 3:
        a = int(255 * clamp(local / .35) * clamp((3.15 - local) / .45))
        draw_center(d, TEXT["made"], 450, FONT_HUGE, (255, 35, 35, a), 5, (70, 0, 0, int(240 * a / 255)))
    else:
        a = clamp((local - 3) / .6)
        paste_alpha(frame, LOGO, ((WIDTH - LOGO.width) // 2, 270), a)
        draw_center(d, TEXT["name_intro"], 565, FONT_XXL, (255, 236, 145, int(255 * a)), 4, (65, 18, 4, int(240 * a)))
        draw_center(d, TEXT["free"], 660, FONT_L, (245, 250, 255, int(235 * a)), 2, (0, 0, 0, int(220 * a)))
    return frame


def scene_battle_static(t: float) -> Image.Image:
    local = t - 16
    frame = BG.copy()
    draw_battle_ui(frame)
    return mosaic_reveal(frame, local)


def scene_role(t: float, start: float, highlight: str, title: str, body: str, message: str) -> Image.Image:
    local = t - start
    frame = BG.copy()
    draw_battle_ui(frame, highlight=highlight, message=message)
    portrait = {"hero": HERO_IMG, "tank": TANK_IMG, "mage": MAGE_IMG}.get(highlight)
    draw_caption_panel(frame, title, body, local, type_duration=max(4.8, (len(body) / 16)), portrait=portrait)
    return mosaic_reveal(frame, local) if local < .75 else frame


def scene_growth(t: float) -> Image.Image:
    local = t - 51
    frame = BG.copy()
    d = ImageDraw.Draw(frame)
    draw_battle_ui(frame, show_result=True, message=TEXT["result"])
    rounded_panel(d, (1040, 145, 1835, 905), fill=(12, 17, 30, 236), outline=(255, 210, 96, 210), radius=24, width=3)
    d.text((1085, 188), TEXT["growth_title"], font=FONT_XL, fill=(255, 236, 145, 255), stroke_width=2, stroke_fill=(60, 18, 4, 240))
    visible = typewriter_text(TEXT["growth_text"], local, 7.8)
    draw_multiline(d, visible, 1090, 278, FONT_M, (243, 247, 255, 245), line_gap=9, stroke=1, stroke_fill=(0, 0, 0, 210))
    if local > 7.9:
        p = clamp((local - 7.9) / .5)
        for i, txt in enumerate([TEXT["hp_up"], TEXT["atk_up"], TEXT["mag_up"], REWARD_TEXT]):
            yy = 650 + i * 54
            d.rounded_rectangle((1090, yy, 1786, yy + 42), radius=12, fill=(34, 42, 58, int(235 * p)), outline=(255, 218, 90, int(220 * p)), width=2)
            d.text((1122, yy + 7), txt, font=FONT_S, fill=(255, 252, 218, int(255 * p)))
    return mosaic_reveal(frame, local) if local < .75 else frame


def scene_chat(t: float) -> Image.Image:
    local = t - 65
    frame = BG.copy()
    d = ImageDraw.Draw(frame)
    rounded_panel(d, (190, 120, 1730, 930), fill=(17, 22, 34, 242), outline=(84, 96, 130, 245), radius=28, width=4)
    d.text((250, 170), TEXT["chat_title"], font=FONT_XXL, fill=(255, 236, 145, 255), stroke_width=3, stroke_fill=(55, 16, 4, 230))
    messages = [(TEXT["chat1_name"], TEXT["chat1_msg"], .5), (TEXT["chat2_name"], TEXT["chat2_msg"], 1.5), (TEXT["chat3_name"], TEXT["chat3_msg"], 2.5), (TEXT["chat4_name"], TEXT["chat4_msg"], 3.5)]
    for i, (name, msg, start) in enumerate(messages):
        p = ease_out(clamp((local - start) / .35))
        if p <= 0:
            continue
        left = i % 2 == 0
        x1 = 270 if left else 820
        x2 = 1120 if left else 1640
        y1 = 290 + i * 132
        color = (48, 58, 82, int(235 * p)) if left else (38, 85, 78, int(235 * p))
        d.rounded_rectangle((x1, y1, x2, y1 + 92), radius=22, fill=color, outline=(255, 255, 255, int(70 * p)), width=2)
        d.text((x1 + 28, y1 + 14), name, font=FONT_S, fill=(255, 236, 145, int(255 * p)))
        d.text((x1 + 28, y1 + 48), msg, font=FONT_M, fill=(255, 255, 255, int(255 * p)))
    return mosaic_reveal(frame, local) if local < .75 else frame


def scene_ending(t: float) -> Image.Image:
    local = t - 75
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (7, 10, 20, 255))
    d = ImageDraw.Draw(frame)
    for y in range(HEIGHT):
        r = y / HEIGHT
        d.line((0, y, WIDTH, y), fill=(int(8 + 18 * r), int(10 + 18 * r), int(22 + 42 * r), 255))
    a = clamp(local / .6)
    paste_alpha(frame, LOGO, (250, 178), a)
    d.text((260, 420), TEXT["ending_title"], font=FONT_HUGE, fill=(255, 236, 145, int(255 * a)), stroke_width=4, stroke_fill=(64, 18, 4, int(240 * a)))
    d.text((265, 528), TEXT["ending_sub"], font=FONT_XL, fill=(255, 255, 255, int(242 * a)), stroke_width=2, stroke_fill=(0, 0, 0, int(210 * a)))
    d.rounded_rectangle((250, 660, 1165, 750), radius=20, fill=(246, 247, 250, int(255 * a)), outline=(255, 204, 96, int(255 * a)), width=4)
    d.text((282, 688), URL, font=FONT_URL, fill=(18, 22, 32, int(255 * a)))
    d.text((267, 800), TEXT["footer"], font=FONT_L, fill=(230, 238, 255, int(245 * a)), stroke_width=2, stroke_fill=(0, 0, 0, int(220 * a)))
    d.rounded_rectangle((1265, 160, 1725, 700), radius=26, fill=(246, 247, 250, int(255 * a)), outline=(255, 204, 96, int(255 * a)), width=5)
    paste_alpha(frame, QR, (1315, 210), a)
    draw_center_in_box(d, TEXT["url_label"], (1265, 620, 1725, 680), FONT_M, (18, 22, 32, int(255 * a)))
    if local > 4.2:
        fade = clamp((local - 4.2) / .8)
        frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, int(210 * fade))))
    return frame


def render_frame(t: float) -> np.ndarray:
    if t < 10:
        frame = scene_intro(t)
    elif t < 16:
        frame = scene_title(t)
    elif t < 17:
        frame = scene_battle_static(t)
    elif t < 27:
        frame = scene_role(t, 17, "hero", TEXT["hero_title"], TEXT["hero_text"], TEXT["hero"] + "：" + TEXT["fire_sword"])
    elif t < 39:
        frame = scene_role(t, 27, "tank", TEXT["tank_title"], TEXT["tank_text"], TEXT["tank"] + "：" + TEXT["fortress"])
    elif t < 51:
        frame = scene_role(t, 39, "mage", TEXT["mage_title"], TEXT["mage_text"], TEXT["mage"] + "：" + TEXT["magic_boost"])
    elif t < 65:
        frame = scene_growth(t)
    elif t < 75:
        frame = scene_chat(t)
    else:
        frame = scene_ending(t)
    return np.array(frame.convert("RGB"))


def set_audio(video: VideoClip, audio):
    return video.with_audio(audio) if hasattr(video, "with_audio") else video.set_audio(audio)


def set_duration(clip, duration: float):
    return clip.with_duration(duration) if hasattr(clip, "with_duration") else clip.set_duration(duration)


def set_start(clip, start: float):
    return clip.with_start(start) if hasattr(clip, "with_start") else clip.set_start(start)


def set_volume(clip, volume: float):
    if hasattr(clip, "with_volume_scaled"):
        return clip.with_volume_scaled(volume)
    return clip.volumex(volume)


def build_audio():
    tracks = []
    bgm = None
    if BGM_PATH.exists():
        bgm = AudioFileClip(str(BGM_PATH))
        loops = max(1, math.ceil(DURATION / max(.1, bgm.duration)))
        bgm_loop = concatenate_audioclips([bgm] * loops)
        bgm_loop = set_duration(bgm_loop, DURATION)
        tracks.append(set_volume(bgm_loop, .28))
    if IMPACT_SFX_PATH.exists():
        sfx = AudioFileClip(str(IMPACT_SFX_PATH))
        sfx = set_start(set_volume(sfx, .75), 9.05)
        tracks.append(sfx)
    if not tracks:
        return None, []
    return CompositeAudioClip(tracks), [bgm] if bgm else []


def main() -> None:
    clip = VideoClip(render_frame, duration=DURATION)
    audio, extra_clips = build_audio()
    if audio:
        clip = set_audio(clip, audio)
    clip.write_videofile(str(OUTPUT_PATH), fps=FPS, codec="libx264", audio_codec="aac" if audio else None, preset="medium", threads=4)
    clip.close()
    if audio:
        audio.close()
    for c in extra_clips:
        c.close()
    print(f"動画を出力しました: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
