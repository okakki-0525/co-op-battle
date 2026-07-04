"""
協力バトル プロモーション動画テスト Ver.2

実行方法:
    pip install moviepy pillow numpy
    python promo_movie_v2.py

QRコードを自動生成したい場合:
    pip install qrcode[pil]

出力:
    promo_movie_v2.mp4

BGM:
    BGM_PATH を任意の音声ファイルに変更してください。
    ファイルが存在しない場合は無音で出力します。
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

try:
    from moviepy import AudioFileClip, VideoClip
except ImportError:  # MoviePy 1.x
    from moviepy.editor import AudioFileClip, VideoClip


WIDTH = 1280
HEIGHT = 720
FPS = 30
DURATION = 25.0

ROOT = Path(__file__).resolve().parent
IMAGE_DIR = ROOT / "static" / "images"
SOUND_DIR = ROOT / "static" / "sounds"
OUTPUT_PATH = ROOT / "promo_movie_v2.mp4"
BGM_PATH = SOUND_DIR / "battle_bgm.mp3"
URL = "https://co-op-battle.onrender.com/login"

ASSETS = {
    "background": IMAGE_DIR / "login_bg.png",
    "logo": IMAGE_DIR / "title.png",
    "hero": IMAGE_DIR / "yusya.png",
    "tank": IMAGE_DIR / "tanc.png",
    "mage": IMAGE_DIR / "majyutu.png",
}

ENEMY_CANDIDATES = [
    "slime.png",
    "orc.png",
    "skeleton_knight.png",
    "fire_lizard.png",
    "flame_witch.png",
    "minotaur.png",
    "death_knight.png",
    "lich.png",
    "tempest_dragon.png",
    "demon_lord.png",
]


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
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


FONT_HUGE = load_font(78, True)
FONT_BIG = load_font(58, True)
FONT_MID = load_font(38, True)
FONT_SMALL = load_font(24, True)
FONT_TINY = load_font(19, False)
FONT_URL = load_font(30, False)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def ease_out(x: float) -> float:
    x = clamp(x)
    return 1.0 - (1.0 - x) * (1.0 - x)


def ease_in_out(x: float) -> float:
    x = clamp(x)
    return x * x * (3.0 - 2.0 * x)


def text_size(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_center_text(
    image: Image.Image,
    text: str,
    y: int,
    font: ImageFont.ImageFont,
    fill: tuple[int, int, int, int],
    stroke_width: int = 0,
    stroke_fill: tuple[int, int, int, int] = (0, 0, 0, 255),
) -> None:
    draw = ImageDraw.Draw(image)
    w, _ = text_size(draw, text, font)
    draw.text(
        ((WIDTH - w) // 2, y),
        text,
        font=font,
        fill=fill,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )


def load_image(path: Path) -> Image.Image | None:
    if not path.exists():
        return None
    try:
        return Image.open(path).convert("RGBA")
    except OSError:
        return None


def fit_image(image: Image.Image, max_w: int, max_h: int) -> Image.Image:
    image = image.convert("RGBA")
    scale = min(max_w / image.width, max_h / image.height)
    size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    return image.resize(size, Image.Resampling.LANCZOS)


def center_crop(image: Image.Image, width: int, height: int) -> Image.Image:
    image = image.convert("RGBA")
    scale = max(width / image.width, height / image.height)
    size = (max(1, int(image.width * scale)), max(1, int(image.height * scale)))
    resized = image.resize(size, Image.Resampling.LANCZOS)
    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))


def paste_alpha(base: Image.Image, layer: Image.Image, xy: tuple[int, int], alpha: float = 1.0) -> None:
    alpha = clamp(alpha)
    if alpha <= 0:
        return
    layer = layer.convert("RGBA")
    if alpha < 1:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda p: int(p * alpha)))
    base.alpha_composite(layer, xy)


def rotate_layer(layer: Image.Image, angle: float, scale: float = 1.0) -> Image.Image:
    if scale != 1.0:
        layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.Resampling.LANCZOS)
    return layer.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)


def make_placeholder(label: str, color: tuple[int, int, int], size: tuple[int, int]) -> Image.Image:
    w, h = size
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((18, 18, w - 18, h - 18), radius=30, fill=(*color, 232), outline=(255, 231, 150, 230), width=4)
    draw.ellipse((int(w * 0.30), int(h * 0.14), int(w * 0.70), int(h * 0.43)), fill=(255, 245, 214, 215))
    draw.rounded_rectangle((int(w * 0.20), int(h * 0.41), int(w * 0.80), int(h * 0.78)), radius=42, fill=(255, 245, 214, 185))
    tw, th = text_size(draw, label, FONT_MID)
    draw.text(((w - tw) // 2, h - th - 32), label, font=FONT_MID, fill=(24, 20, 18, 255))
    return image


def make_logo() -> Image.Image:
    logo = load_image(ASSETS["logo"])
    if logo:
        return fit_image(logo, 420, 145)
    layer = Image.new("RGBA", (470, 142), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle((8, 18, 462, 126), radius=24, fill=(14, 17, 28, 230), outline=(255, 219, 102, 255), width=4)
    text = "協力バトル"
    tw, th = text_size(draw, text, FONT_BIG)
    draw.text(((470 - tw) // 2, (142 - th) // 2 - 5), text, font=FONT_BIG, fill=(255, 236, 148, 255), stroke_width=3, stroke_fill=(80, 28, 6, 255))
    return layer


def make_background() -> Image.Image:
    source = load_image(ASSETS["background"])
    if source:
        base = center_crop(source, WIDTH, HEIGHT)
    else:
        base = Image.new("RGBA", (WIDTH, HEIGHT), (12, 16, 30, 255))
        draw = ImageDraw.Draw(base)
        for y in range(HEIGHT):
            r = int(10 + y / HEIGHT * 24)
            g = int(13 + y / HEIGHT * 22)
            b = int(26 + y / HEIGHT * 48)
            draw.line((0, y, WIDTH, y), fill=(r, g, b, 255))

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (2, 4, 10, 112))
    draw = ImageDraw.Draw(overlay)
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(2, 4, 10, 78))
    draw.polygon([(0, 448), (WIDTH, 324), (WIDTH, HEIGHT), (0, HEIGHT)], fill=(2, 3, 7, 132))
    for i in range(8):
        x = -120 + i * 190
        draw.line((x, 0, x + 340, HEIGHT), fill=(255, 190, 80, 12), width=3)
    return Image.alpha_composite(base, overlay)


def make_battle_background() -> Image.Image:
    bg = make_background()
    draw = ImageDraw.Draw(bg)
    draw.rectangle((0, 424, WIDTH, HEIGHT), fill=(4, 7, 13, 150))
    for y in range(454, HEIGHT, 42):
        draw.line((0, y, WIDTH, y - 92), fill=(255, 133, 40, 22), width=2)
    for x in range(-100, WIDTH, 170):
        draw.line((x, HEIGHT, x + 230, 430), fill=(255, 217, 128, 12), width=2)
    draw.ellipse((84, 556, 560, 694), fill=(0, 0, 0, 110))
    draw.ellipse((744, 510, 1202, 682), fill=(0, 0, 0, 125))
    return bg


def make_enemy_card(enemy: Image.Image, label: str) -> Image.Image:
    card = Image.new("RGBA", (420, 500), (0, 0, 0, 0))
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(shadow)
    sdraw.rounded_rectangle((34, 34, 386, 470), radius=28, fill=(0, 0, 0, 172))
    card.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)))

    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((22, 18, 398, 464), radius=28, fill=(15, 17, 27, 244), outline=(255, 194, 76, 235), width=5)
    draw.rounded_rectangle((44, 42, 376, 360), radius=20, fill=(36, 20, 28, 236), outline=(255, 87, 40, 155), width=3)
    fitted = fit_image(enemy, 300, 292)
    card.alpha_composite(fitted, ((420 - fitted.width) // 2, 76 + (292 - fitted.height) // 2))
    tw, _ = text_size(draw, label, FONT_MID)
    draw.text(((420 - tw) // 2, 386), label, font=FONT_MID, fill=(255, 232, 142, 255), stroke_width=2, stroke_fill=(61, 18, 5, 255))
    return card


def make_qr_image() -> Image.Image:
    existing = load_image(ROOT / "qr_code.png")
    if existing:
        return fit_image(existing, 250, 250)

    try:
        import qrcode

        qr = qrcode.QRCode(border=2, box_size=10)
        qr.add_data(URL)
        qr.make(fit=True)
        image = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
        return fit_image(image, 250, 250)
    except Exception:
        image = Image.new("RGBA", (250, 250), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 0, 249, 249), outline=(0, 0, 0, 255), width=8)
        for ox, oy in [(24, 24), (164, 24), (24, 164)]:
            draw.rectangle((ox, oy, ox + 58, oy + 58), outline=(0, 0, 0, 255), width=10)
            draw.rectangle((ox + 20, oy + 20, ox + 38, oy + 38), fill=(0, 0, 0, 255))
        for y in range(108, 220, 22):
            for x in range(106, 222, 22):
                if (x + y) // 22 % 2 == 0:
                    draw.rectangle((x, y, x + 12, y + 12), fill=(0, 0, 0, 255))
        tw, _ = text_size(draw, "QR", FONT_MID)
        draw.text(((250 - tw) // 2, 102), "QR", font=FONT_MID, fill=(0, 0, 0, 255))
        return image


def make_enemy_images() -> list[Image.Image]:
    images = []
    for name in ENEMY_CANDIDATES:
        img = load_image(IMAGE_DIR / name)
        if img:
            images.append(img)
    while len(images) < 8:
        index = len(images) + 1
        images.append(make_placeholder(f"敵{index}", (90 + index * 18 % 120, 38, 58 + index * 23 % 140), (310, 360)))
    return images


def make_character(key: str, label: str, color: tuple[int, int, int], max_size: tuple[int, int]) -> Image.Image:
    source = load_image(ASSETS[key])
    if not source:
        source = make_placeholder(label, color, (300, 380))
    return fit_image(source, *max_size)


BG = make_background()
BATTLE_BG = make_battle_background()
LOGO = make_logo()
QR_IMAGE = make_qr_image()
HERO = make_character("hero", "勇者", (220, 74, 58), (205, 270))
TANK = make_character("tank", "タンク", (64, 133, 222), (224, 292))
MAGE = make_character("mage", "魔術師", (143, 86, 220), (205, 270))
ENEMIES = make_enemy_images()
ENEMY_CARDS = [make_enemy_card(img, f"ENEMY {i + 1}") for i, img in enumerate(ENEMIES)]
SELECTED_ENEMY = fit_image(ENEMIES[-1], 365, 365)


def draw_speed_lines(image: Image.Image, t: float, alpha: int = 32) -> None:
    draw = ImageDraw.Draw(image)
    for i in range(14):
        x = int((t * 770 + i * 128) % (WIDTH + 420)) - 260
        draw.line((x, 66, x + 400, 638), fill=(255, 208, 102, alpha), width=5)


def draw_log_panel(draw: ImageDraw.ImageDraw, logs: list[str]) -> None:
    draw.rounded_rectangle((28, 566, 720, 704), radius=16, fill=(4, 7, 13, 218), outline=(255, 183, 80, 138), width=2)
    draw.text((52, 582), "BATTLE LOG", font=FONT_TINY, fill=(255, 208, 112, 235))
    y = 610
    for log in logs[-3:]:
        draw.text((54, y), log, font=FONT_SMALL, fill=(244, 248, 255, 240))
        y += 30


def draw_hp_panel(draw: ImageDraw.ImageDraw, local: float) -> None:
    draw.rounded_rectangle((26, 28, 386, 184), radius=16, fill=(5, 8, 15, 202), outline=(255, 178, 72, 142), width=2)
    members = [
        ("勇者", 1280, 1.0, (255, 214, 86)),
        ("タンク", 1850, 1.0, (106, 194, 255)),
        ("魔術師", 960, 1.0, (215, 160, 255)),
    ]
    if local > 5.7:
        members = [
            ("勇者", 1058, 0.82, (255, 214, 86)),
            ("タンク", 1732, 0.94, (106, 194, 255)),
            ("魔術師", 798, 0.83, (215, 160, 255)),
        ]
    for i, (name, hp, ratio, color) in enumerate(members):
        y = 50 + i * 42
        draw.text((48, y), name, font=FONT_SMALL, fill=(*color, 255))
        draw.rounded_rectangle((146, y + 7, 314, y + 25), radius=9, fill=(34, 45, 58, 255))
        draw.rounded_rectangle((146, y + 7, 146 + int(168 * ratio), y + 25), radius=9, fill=(*color, 235))
        draw.text((324, y), str(hp), font=FONT_SMALL, fill=(245, 248, 255, 235))


def draw_command_ui(draw: ImageDraw.ImageDraw, active: str) -> None:
    draw.rounded_rectangle((778, 564, 1238, 704), radius=16, fill=(5, 8, 15, 218), outline=(255, 183, 80, 138), width=2)
    commands = ["攻撃", "スキル", "防御", "アイテム"]
    for i, command in enumerate(commands):
        x = 804 + (i % 2) * 206
        y = 588 + (i // 2) * 52
        is_active = command == active
        fill = (78, 28, 14, 235) if is_active else (18, 24, 38, 235)
        outline = (255, 168, 62, 245) if is_active else (88, 104, 132, 170)
        draw.rounded_rectangle((x, y, x + 174, y + 38), radius=10, fill=fill, outline=outline, width=2)
        draw.text((x + 48, y + 6), command, font=FONT_SMALL, fill=(255, 243, 210, 255))


def draw_boss_ui(draw: ImageDraw.ImageDraw, local: float) -> None:
    draw.rounded_rectangle((760, 38, 1224, 112), radius=18, fill=(8, 7, 14, 202), outline=(255, 91, 48, 180), width=3)
    draw.text((788, 52), "BOSS", font=FONT_MID, fill=(255, 224, 130, 255), stroke_width=2, stroke_fill=(70, 17, 4, 255))
    draw.rounded_rectangle((928, 64, 1186, 94), radius=14, fill=(47, 19, 23, 255))
    loss = 0.0
    if local > 3.05:
        loss += 0.18 * clamp((local - 3.05) / 0.5)
    if local > 9.6:
        loss += 0.20 * clamp((local - 9.6) / 0.6)
    if local > 12.1:
        loss += 0.28 * clamp((local - 12.1) / 0.7)
    hp_w = int(258 * max(0.18, 1.0 - loss))
    draw.rounded_rectangle((928, 64, 928 + hp_w, 94), radius=14, fill=(235, 60, 42, 255))


def hp_color(hp: int, max_hp: int) -> tuple[int, int, int]:
    ratio = hp / max_hp if max_hp else 0
    if ratio < 0.3:
        return (255, 82, 82)
    if ratio < 0.6:
        return (255, 179, 0)
    return (61, 220, 132)


def draw_html_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    draw.rounded_rectangle(box, radius=8, fill=(43, 49, 66, 246), outline=(30, 36, 52, 230), width=1)


def draw_html_hp_bar(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], hp: int, max_hp: int) -> None:
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=(y2 - y1) // 2, fill=(85, 85, 85, 255))
    width = max(0, int((x2 - x1) * clamp(hp / max_hp if max_hp else 0)))
    if width > 0:
        draw.rounded_rectangle((x1, y1, x1 + width, y2), radius=(y2 - y1) // 2, fill=hp_color(hp, max_hp))


def draw_enemy_html_card(
    frame: Image.Image,
    x: int,
    y: int,
    w: int,
    h: int,
    enemy: Image.Image,
    name: str,
    hp: int,
    max_hp: int,
    flash: float = 0.0,
) -> tuple[int, int]:
    draw = ImageDraw.Draw(frame)
    fill = (23, 29, 43, 255)
    outline = (255, 23, 68, 235) if flash > 0 else (45, 53, 72, 255)
    draw.rounded_rectangle((x, y, x + w, y + h), radius=8, fill=fill, outline=outline, width=2 if flash > 0 else 1)
    if flash > 0:
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.rounded_rectangle((x - 7, y - 7, x + w + 7, y + h + 7), radius=12, outline=(255, 23, 68, int(190 * flash)), width=5)
        frame.alpha_composite(glow.filter(ImageFilter.GaussianBlur(5)))

    title_w, _ = text_size(draw, name, FONT_TINY)
    draw.text((x + (w - title_w) // 2, y + 7), name, font=FONT_TINY, fill=(255, 255, 255, 245))
    fitted = fit_image(enemy, w - 32, 96)
    image_x = x + (w - fitted.width) // 2
    image_y = y + 36 + (96 - fitted.height) // 2
    paste_alpha(frame, fitted, (image_x, image_y), 1.0)
    draw.text((x + 12, y + h - 34), f"HP:{hp}/{max_hp}", font=FONT_TINY, fill=(230, 230, 230, 245))
    draw_html_hp_bar(draw, (x + 12, y + h - 14, x + w - 12, y + h - 8), hp, max_hp)
    return (x + w // 2, image_y + fitted.height // 2)


def draw_player_html_card(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    w: int,
    name: str,
    job: str,
    hp: int,
    max_hp: int,
    attack: int,
    heal: int,
    weapon: str,
    me: bool = False,
    damaged: bool = False,
    guarded: bool = False,
) -> tuple[int, int]:
    fill = (90, 74, 31, 255) if me else (57, 64, 86, 255)
    outline = (255, 213, 79, 255) if me else (57, 64, 86, 255)
    if damaged:
        fill = (210, 35, 58, 245)
        outline = (255, 80, 96, 255)
    if guarded:
        outline = (66, 165, 245, 255)
    draw.rounded_rectangle((x, y, x + w, y + 38), radius=7, fill=fill, outline=outline, width=2 if me or damaged or guarded else 1)
    draw.text((x + 10, y + 6), f"{name}({job})", font=FONT_TINY, fill=(255, 255, 255, 255))
    draw.text((x + 10, y + 21), f"HP:{hp}/{max_hp} ATK:{attack} HEAL:{heal}", font=FONT_TINY, fill=(222, 222, 222, 245))
    draw.text((x + 258, y + 21), f"持込:{weapon}", font=FONT_TINY, fill=(255, 204, 128, 245))
    draw_html_hp_bar(draw, (x + 446, y + 15, x + w - 12, y + 24), hp, max_hp)
    return (x + w // 2, y + 19)


def draw_battle_html_screen(frame: Image.Image, local: float, ox: int, oy: int) -> dict[str, tuple[int, int]]:
    screen_x = (WIDTH - 700) // 2 + ox
    screen_y = oy
    draw = ImageDraw.Draw(frame)

    draw.rounded_rectangle((screen_x - 10, screen_y, screen_x + 710, screen_y + HEIGHT), radius=14, fill=(27, 31, 42, 246), outline=(10, 12, 18, 230), width=2)

    # Header panel: battle.html's centered title and turn.
    draw_html_panel(draw, (screen_x + 8, screen_y + 8, screen_x + 692, screen_y + 66))
    title = "協力バトル"
    tw, _ = text_size(draw, title, FONT_SMALL)
    draw.text((screen_x + 350 - tw // 2, screen_y + 16), title, font=FONT_SMALL, fill=(255, 255, 255, 255))
    turn = "ターン 1"
    turn_w, _ = text_size(draw, turn, FONT_TINY)
    draw.text((screen_x + 350 - turn_w // 2, screen_y + 42), turn, font=FONT_TINY, fill=(235, 235, 235, 245))

    # Enemy panel: enemies-grid / enemy-card look.
    draw_html_panel(draw, (screen_x + 8, screen_y + 74, screen_x + 692, screen_y + 306))
    enemy_title = "敵"
    ew, _ = text_size(draw, enemy_title, FONT_SMALL)
    draw.text((screen_x + 350 - ew // 2, screen_y + 84), enemy_title, font=FONT_SMALL, fill=(255, 255, 255, 255))

    boss_hp = 7800
    if local > 2.7:
        boss_hp -= int(2480 * clamp((local - 2.7) / 0.5))
    if local > 9.35:
        boss_hp -= int(1680 * clamp((local - 9.35) / 0.5))
    if local > 12.05:
        boss_hp -= int(2600 * clamp((local - 12.05) / 0.55))
    boss_hp = max(820, boss_hp)

    enemy_flash = max(
        clamp(1.0 - abs(local - 2.67) / 0.32),
        clamp(1.0 - abs(local - 9.35) / 0.35),
        clamp(1.0 - abs(local - 12.05) / 0.45),
    )
    card_y = screen_y + 118
    card_w = 160
    start_x = screen_x + 110
    draw_enemy_html_card(frame, start_x, card_y, card_w, 166, ENEMIES[2 % len(ENEMIES)], "護衛A", 2100, 2800)
    boss_center = draw_enemy_html_card(frame, start_x + 172, card_y, card_w, 166, ENEMIES[-1], "BOSS", boss_hp, 7800, enemy_flash)
    draw_enemy_html_card(frame, start_x + 344, card_y, card_w, 166, ENEMIES[4 % len(ENEMIES)], "護衛B", 1850, 2600)

    # Players panel: players-grid / player-card look.
    draw_html_panel(draw, (screen_x + 8, screen_y + 314, screen_x + 692, screen_y + 468))
    draw.text((screen_x + 22, screen_y + 323), "パーティー", font=FONT_SMALL, fill=(255, 255, 255, 255))
    after_aoe = local > 6.75
    guarded = 4.45 <= local <= 6.95
    hero_pos = draw_player_html_card(draw, screen_x + 22, screen_y + 352, 652, "勇者", "勇者", 1058 if after_aoe else 1280, 1280, 260, 40, "炎剣", True, 6.6 <= local <= 7.4, guarded)
    tank_pos = draw_player_html_card(draw, screen_x + 22, screen_y + 394, 652, "タンク", "タンク", 1732 if after_aoe else 1850, 1850, 150, 30, "大盾", False, 6.7 <= local <= 7.45, guarded)
    mage_pos = draw_player_html_card(draw, screen_x + 22, screen_y + 436, 652, "魔術師", "魔術師", 798 if after_aoe else 960, 960, 95, 220, "魔導書", False, 6.76 <= local <= 7.5, guarded)

    # Main panel: battle.html's message/action area.
    draw_html_panel(draw, (screen_x + 8, screen_y + 476, screen_x + 692, screen_y + 558))
    draw.rounded_rectangle((screen_x + 22, screen_y + 488, screen_x + 678, screen_y + 540), radius=8, fill=(17, 23, 34, 255))
    main_text = "全員の行動を待っています"
    if 1.1 <= local < 3.8:
        main_text = "勇者の炎剣！"
    elif 4.4 <= local < 6.2:
        main_text = "タンクのフォートレス！"
    elif 6.2 <= local < 7.6:
        main_text = "敵の全体攻撃！"
    elif 8.1 <= local < 10.2:
        main_text = "魔術師のマジックブースト！"
    elif local >= 10.45:
        main_text = "協力攻撃！"
    mw, _ = text_size(draw, main_text, FONT_SMALL)
    draw.text((screen_x + 350 - mw // 2, screen_y + 503), main_text, font=FONT_SMALL, fill=(255, 255, 255, 255))
    draw.text((screen_x + 24, screen_y + 542), "行動済み", font=FONT_TINY, fill=(221, 221, 221, 235))

    # Actions row, matching battle.html button colors.
    button_y = screen_y + 566
    actions = [("攻撃", (229, 57, 53)), ("回復", (67, 160, 71)), ("盾", (30, 136, 229)), ("魔法", (142, 36, 170))]
    for i, (label, color) in enumerate(actions):
        bx = screen_x + 8 + i * 174
        draw.rounded_rectangle((bx, button_y, bx + 166, button_y + 42), radius=8, fill=(*color, 255))
        bw, _ = text_size(draw, label, FONT_SMALL)
        draw.text((bx + 83 - bw // 2, button_y + 8), label, font=FONT_SMALL, fill=(255, 255, 255, 255))

    # Chat and log panels are visible in the real battle page, so keep them compressed but readable.
    draw_html_panel(draw, (screen_x + 8, screen_y + 616, screen_x + 342, screen_y + 710))
    draw.text((screen_x + 22, screen_y + 625), "チャット", font=FONT_SMALL, fill=(255, 255, 255, 255))
    draw.rounded_rectangle((screen_x + 22, screen_y + 650, screen_x + 328, screen_y + 694), radius=10, fill=(17, 23, 34, 255))
    draw.text((screen_x + 34, screen_y + 660), "勇者: いくぞ！", font=FONT_TINY, fill=(255, 213, 79, 245))
    draw.text((screen_x + 34, screen_y + 678), "魔術師: 合わせます", font=FONT_TINY, fill=(220, 225, 240, 235))

    draw_html_panel(draw, (screen_x + 350, screen_y + 616, screen_x + 692, screen_y + 710))
    draw.text((screen_x + 364, screen_y + 625), "ログ", font=FONT_SMALL, fill=(255, 255, 255, 255))
    draw.rounded_rectangle((screen_x + 364, screen_y + 650, screen_x + 678, screen_y + 694), radius=10, fill=(17, 23, 34, 255))
    logs = battle_logs(local)[-2:]
    for i, log in enumerate(logs):
        draw.text((screen_x + 376, screen_y + 658 + i * 18), log, font=FONT_TINY, fill=(235, 238, 248, 235))

    return {
        "boss": boss_center,
        "hero": hero_pos,
        "tank": tank_pos,
        "mage": mage_pos,
        "screen": (screen_x + 350, screen_y + 360),
    }


def damage_text(image: Image.Image, text: str, xy: tuple[int, int], t: float, start: float, color: tuple[int, int, int]) -> None:
    p = clamp((t - start) / 0.9)
    alpha = clamp((t - start) / 0.12) * clamp((start + 0.9 - t) / 0.28)
    if alpha <= 0:
        return
    x, y = xy
    draw = ImageDraw.Draw(image)
    draw.text((x, y - int(52 * ease_out(p))), text, font=FONT_BIG, fill=(*color, int(255 * alpha)), stroke_width=4, stroke_fill=(60, 10, 3, int(235 * alpha)))


def draw_fire_slash(image: Image.Image, local: float, start_time: float, start: tuple[int, int], end: tuple[int, int]) -> float:
    progress = clamp((local - start_time) / 0.85)
    impact = clamp(1.0 - abs(local - (start_time + 0.82)) / 0.32)
    if progress <= 0 and impact <= 0:
        return 0.0

    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    p = ease_out(progress)
    tip = (start[0] + (end[0] - start[0]) * p, start[1] + (end[1] - start[1]) * p)
    for i in range(12):
        trail = max(0.0, p - i * 0.052)
        sx = start[0] + (end[0] - start[0]) * trail
        sy = start[1] + (end[1] - start[1]) * trail
        draw.line((sx, sy, tip[0], tip[1]), fill=(255, 58 + i * 15, 12, int(218 * (1 - i / 13))), width=max(4, 40 - i * 3))
    draw.line((start[0], start[1], tip[0], tip[1]), fill=(255, 246, 190, 245), width=11)
    for i in range(24):
        ember_p = max(0.0, p - i * 0.022)
        ex = start[0] + (end[0] - start[0]) * ember_p + math.sin(i * 2.1 + local) * 38
        ey = start[1] + (end[1] - start[1]) * ember_p + math.cos(i * 1.7) * 25
        r = 2 + (i % 4)
        draw.ellipse((ex - r, ey - r, ex + r, ey + r), fill=(255, 148, 34, 185))
    if impact > 0:
        cx, cy = end
        for i in range(24):
            a = i / 24 * math.tau
            length = 34 + 112 * impact * (0.45 + (i % 5) / 6)
            draw.line((cx, cy, cx + math.cos(a) * length, cy + math.sin(a) * length), fill=(255, 222, 92, int(232 * impact)), width=4)
        draw.ellipse((cx - 120 * impact, cy - 86 * impact, cx + 120 * impact, cy + 86 * impact), fill=(255, 94, 24, int(104 * impact)))
        draw.ellipse((cx - 58 * impact, cy - 42 * impact, cx + 58 * impact, cy + 42 * impact), fill=(255, 247, 190, int(204 * impact)))
    image.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(2)))
    image.alpha_composite(overlay)
    return impact


def draw_shield(image: Image.Image, local: float, box: tuple[int, int, int, int] = (112, 274, 536, 686)) -> None:
    p = clamp((local - 4.55) / 0.8) * clamp((6.6 - local) / 0.7)
    if p <= 0:
        return
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    alpha = int(170 * p)
    x1, y1, x2, y2 = box
    draw.rounded_rectangle(box, radius=26, outline=(106, 194, 255, alpha), width=10)
    draw.rounded_rectangle((x1 + 18, y1 + 14, x2 - 18, y2 - 14), radius=22, outline=(255, 255, 255, int(80 * p)), width=4)
    for i in range(10):
        x = x1 + 28 + i * max(1, (x2 - x1 - 56) // 10)
        draw.line((x, y1 + 12, x + 52, y2 - 12), fill=(112, 204, 255, int(42 * p)), width=3)
    image.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(5)))
    image.alpha_composite(overlay)


def draw_enemy_aoe(image: Image.Image, local: float, center: tuple[int, int] = (904, 330)) -> float:
    p = clamp((local - 5.85) / 0.75)
    impact = clamp(1.0 - abs(local - 6.62) / 0.28)
    if p <= 0 and impact <= 0:
        return 0.0
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    cx, cy = center
    radius = 40 + 660 * ease_out(p)
    draw.ellipse((cx - radius, cy - radius * 0.55, cx + radius, cy + radius * 0.55), outline=(210, 58, 255, int(180 * (1 - p * 0.55))), width=14)
    for i in range(18):
        a = -math.pi + i / 17 * math.pi * 1.25
        ex = cx + math.cos(a) * radius
        ey = cy + math.sin(a) * radius * 0.55
        draw.line((cx, cy, ex, ey), fill=(182, 70, 255, int(80 * (1 - p * 0.4))), width=4)
    if impact > 0:
        draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(140, 58, 255, int(58 * impact)))
    image.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(3)))
    image.alpha_composite(overlay)
    return impact


def draw_magic(
    image: Image.Image,
    local: float,
    start: tuple[int, int] = (224, 424),
    end: tuple[int, int] = (922, 304),
) -> float:
    p = clamp((local - 8.15) / 1.1)
    impact = clamp(1.0 - abs(local - 9.35) / 0.35)
    if p <= 0 and impact <= 0:
        return 0.0
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    sx, sy = start
    ex, ey = end
    tip = (sx + (ex - sx) * ease_out(p), sy + (ey - sy) * ease_out(p))
    for i in range(7):
        offset = math.sin(local * 8 + i) * 22
        draw.line((sx, sy + offset, tip[0], tip[1] - offset), fill=(160, 95, 255, int(70 + i * 16)), width=8)
    for i in range(16):
        angle = i / 16 * math.tau + local * 5
        r = 38 + i * 4
        x = tip[0] + math.cos(angle) * r
        y = tip[1] + math.sin(angle) * r
        draw.ellipse((x - 5, y - 5, x + 5, y + 5), fill=(222, 174, 255, 190))
    if impact > 0:
        draw.ellipse((ex - 124 * impact, ey - 100 * impact, ex + 124 * impact, ey + 100 * impact), fill=(190, 100, 255, int(110 * impact)))
        draw.ellipse((ex - 52 * impact, ey - 52 * impact, ex + 52 * impact, ey + 52 * impact), fill=(255, 246, 255, int(205 * impact)))
    image.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(3)))
    image.alpha_composite(overlay)
    return impact


def draw_coop_finish(
    image: Image.Image,
    local: float,
    center: tuple[int, int] = (916, 298),
    origins: list[tuple[int, int]] | None = None,
) -> float:
    p = clamp((local - 10.45) / 1.55)
    impact = clamp(1.0 - abs(local - 12.05) / 0.45)
    if p <= 0 and impact <= 0:
        return 0.0
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    if origins is None:
        origins = [(270, 432), (386, 410), (186, 450)]
    colors = [(255, 78, 32), (92, 202, 255), (207, 116, 255)]
    for origin, color in zip(origins, colors):
        tip = (origin[0] + (center[0] - origin[0]) * ease_out(p), origin[1] + (center[1] - origin[1]) * ease_out(p))
        draw.line((origin[0], origin[1], tip[0], tip[1]), fill=(*color, 210), width=18)
        draw.line((origin[0], origin[1], tip[0], tip[1]), fill=(255, 247, 210, 190), width=6)
    ring = 30 + 220 * p
    draw.ellipse((center[0] - ring, center[1] - ring, center[0] + ring, center[1] + ring), outline=(255, 224, 108, int(180 * (1 - p * 0.45))), width=10)
    if impact > 0:
        draw.ellipse((center[0] - 180 * impact, center[1] - 130 * impact, center[0] + 180 * impact, center[1] + 130 * impact), fill=(255, 231, 128, int(150 * impact)))
        draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(255, 246, 190, int(58 * impact)))
    image.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(4)))
    image.alpha_composite(overlay)
    return impact


def shake_offset(t: float, amount: float) -> tuple[int, int]:
    return int(math.sin(t * 91) * amount), int(math.cos(t * 77) * amount)


def intro_enemy_index(t: float) -> int:
    elapsed = clamp(t / 5.0)
    wave = math.sin(elapsed * math.pi)
    flips = int(1.2 + elapsed * 16.0 + wave * 12.0)
    return flips % len(ENEMY_CARDS)


def render_intro(t: float) -> Image.Image:
    frame = BG.copy()
    draw_speed_lines(frame, t, 30)
    draw_center_text(frame, "敵紹介", 46, FONT_BIG, (255, 232, 150, 238), 3, (60, 18, 4, 230))

    final_phase = t >= 4.35
    card = make_enemy_card(ENEMIES[-1], "BOSS") if final_phase else ENEMY_CARDS[intro_enemy_index(t)]
    speed = 0.25 + 0.78 * math.sin(clamp(t / 5.0) * math.pi)
    angle = math.sin(t * (7.0 + speed * 12.0)) * (2.5 + speed * 8.0)
    scale = 1.12 if final_phase else 0.92 + 0.10 * math.sin(t * (6.0 + speed * 10.0))
    if final_phase:
        angle = math.sin(t * 13.0) * 1.8
        scale += 0.04 * math.sin(t * 18.0)

    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    pulse = 0.45 + 0.55 * math.sin(t * 7.5) ** 2
    gdraw.ellipse((360, 104, 920, 654), fill=(255, 92, 28, int(46 + pulse * 54)))
    frame.alpha_composite(glow.filter(ImageFilter.GaussianBlur(30)))

    for i in range(3):
        ghost = rotate_layer(card, angle - 12 + i * 8, scale * (0.92 - i * 0.03))
        paste_alpha(frame, ghost, ((WIDTH - ghost.width) // 2 + (i - 1) * 32, (HEIGHT - ghost.height) // 2 + 14 + (i - 1) * 10), 0.12)

    layer = rotate_layer(card, angle, scale)
    paste_alpha(frame, layer, ((WIDTH - layer.width) // 2, (HEIGHT - layer.height) // 2 + 16), 1.0)

    if t >= 4.25:
        a = clamp((t - 4.25) / 0.35)
        draw_center_text(frame, "強敵出現！", 574, FONT_BIG, (255, 235, 130, int(255 * a)), 4, (86, 19, 4, int(245 * a)))
    return frame


def render_transition(t: float) -> Image.Image:
    local = t - 5.0
    amount = 10 + 24 * clamp(local / 1.0)
    ox, oy = shake_offset(t, amount)
    frame = BG.copy()
    enemy = rotate_layer(fit_image(ENEMIES[-1], 430, 430), math.sin(t * 18) * 2.0, 1.0 + 0.25 * ease_in_out(local))
    paste_alpha(frame, enemy, ((WIDTH - enemy.width) // 2 + ox, 162 + oy), 1.0)
    draw_speed_lines(frame, t, 58)
    frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, int(190 * ease_in_out(local)))))
    frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (255, 224, 150, int(78 * math.sin(clamp(local) * math.pi)))))
    draw_center_text(frame, "BATTLE START", 318 + oy, FONT_HUGE, (255, 235, 150, 240), 4, (74, 16, 4, 230))
    return frame


def battle_logs(local: float) -> list[str]:
    logs = ["強敵が現れた！"]
    if local >= 1.25:
        logs.append("勇者の炎剣！")
    if local >= 3.1:
        logs.append("2480 ダメージ！")
    if local >= 4.45:
        logs.append("タンクのフォートレス！")
    if local >= 6.2:
        logs.append("敵の全体攻撃！")
    if local >= 6.75:
        logs.append("フォートレスがダメージを軽減した！")
    if local >= 8.2:
        logs.append("魔術師のマジックブースト！")
    if local >= 10.45:
        logs.append("協力攻撃！")
    return logs


def render_battle(t: float) -> Image.Image:
    local = t - 6.0
    hero_impact = clamp(1.0 - abs(local - 2.67) / 0.32)
    aoe_impact = clamp(1.0 - abs(local - 6.62) / 0.28)
    magic_impact = clamp(1.0 - abs(local - 9.35) / 0.35)
    coop_impact = clamp(1.0 - abs(local - 12.05) / 0.45)
    ox, oy = shake_offset(t, 12 * max(hero_impact, aoe_impact, magic_impact, coop_impact))

    frame = BG.copy()
    frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 94)))
    draw_speed_lines(frame, t, 16)
    positions = draw_battle_html_screen(frame, local, ox, oy)

    # battle.htmlの敵カード上に、実ゲームのslash-effect / magic-burst風エフェクトを重ねます。
    boss_x, boss_y = positions["boss"]
    hero_x, hero_y = positions["hero"]
    tank_x, tank_y = positions["tank"]
    mage_x, mage_y = positions["mage"]

    shield_box = (min(hero_x, tank_x, mage_x) - 330, hero_y - 30, max(hero_x, tank_x, mage_x) + 330, mage_y + 44)
    draw_shield(frame, local, shield_box)
    aoe = draw_enemy_aoe(frame, local, (boss_x, boss_y))
    hero_hit = draw_fire_slash(frame, local, 1.85, (hero_x + 110, hero_y + 36), (boss_x, boss_y))
    magic_hit = draw_magic(frame, local, (mage_x + 70, mage_y - 8), (boss_x, boss_y))
    coop_hit = draw_coop_finish(frame, local, (boss_x, boss_y), [(hero_x + 80, hero_y), (tank_x + 60, tank_y), (mage_x + 70, mage_y)])

    draw = ImageDraw.Draw(frame)
    if 1.12 <= local <= 3.8:
        a = clamp((local - 1.12) / 0.22) * clamp((3.8 - local) / 0.55)
        draw_center_text(frame, "炎剣！", 132, FONT_BIG, (255, 237, 142, int(255 * a)), 4, (88, 20, 4, int(245 * a)))
    if 4.42 <= local <= 6.8:
        a = clamp((local - 4.42) / 0.25) * clamp((6.8 - local) / 0.55)
        draw_center_text(frame, "フォートレス！", 132, FONT_BIG, (168, 226, 255, int(255 * a)), 4, (8, 32, 74, int(245 * a)))
    if 8.15 <= local <= 10.2:
        a = clamp((local - 8.15) / 0.25) * clamp((10.2 - local) / 0.55)
        draw_center_text(frame, "マジックブースト！", 132, FONT_BIG, (222, 176, 255, int(255 * a)), 4, (42, 13, 80, int(245 * a)))
    if 10.45 <= local <= 13.4:
        a = clamp((local - 10.45) / 0.28) * clamp((13.4 - local) / 0.7)
        draw_center_text(frame, "協力攻撃！", 126, FONT_HUGE, (255, 236, 132, int(255 * a)), 5, (82, 20, 4, int(245 * a)))

    damage_text(frame, "2480", (boss_x - 48, boss_y - 62), local, 2.72, (255, 238, 136))
    damage_text(frame, "1680", (boss_x - 38, boss_y - 72), local, 9.38, (231, 176, 255))
    damage_text(frame, "5200", (boss_x - 50, boss_y - 92), local, 12.05, (255, 242, 142))
    damage_text(frame, "222", (hero_x - 220, hero_y - 56), local, 6.64, (255, 166, 116))
    damage_text(frame, "118", (tank_x - 220, tank_y - 52), local, 6.70, (255, 166, 116))
    damage_text(frame, "162", (mage_x - 220, mage_y - 48), local, 6.76, (255, 166, 116))

    flash = max(hero_hit, aoe, magic_hit, coop_hit)
    if flash > 0:
        frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (255, 232, 156, int(58 * flash))))
    if local >= 13.25:
        fade = clamp((local - 13.25) / 0.75)
        frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, int(170 * fade))))
    return frame


def render_ending(t: float) -> Image.Image:
    local = t - 20.0
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (9, 12, 22, 255))
    draw = ImageDraw.Draw(frame)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        draw.line((0, y, WIDTH, y), fill=(int(10 + ratio * 16), int(12 + ratio * 14), int(24 + ratio * 32), 255))
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 42))

    a = clamp(local / 0.7)
    paste_alpha(frame, LOGO, (92, 62), a)
    draw.text((92, 216), "協力バトルONLINE", font=FONT_HUGE, fill=(255, 236, 148, int(255 * a)), stroke_width=4, stroke_fill=(68, 19, 4, int(230 * a)))
    draw.text((96, 324), "最大6人で協力バトル！", font=FONT_BIG, fill=(255, 255, 255, int(242 * a)), stroke_width=3, stroke_fill=(0, 0, 0, int(215 * a)))
    draw.text((96, 394), "仲間と連携して強敵を倒せ！", font=FONT_MID, fill=(230, 238, 255, int(232 * a)), stroke_width=2, stroke_fill=(0, 0, 0, int(190 * a)))

    draw.rounded_rectangle((88, 530, 820, 598), radius=16, fill=(3, 6, 12, int(205 * a)), outline=(255, 184, 82, int(190 * a)), width=2)
    draw.text((116, 546), URL, font=FONT_URL, fill=(255, 250, 230, int(255 * a)))

    qr_box_alpha = int(255 * a)
    draw.rounded_rectangle((898, 118, 1196, 552), radius=22, fill=(245, 246, 248, qr_box_alpha), outline=(255, 205, 96, qr_box_alpha), width=4)
    paste_alpha(frame, QR_IMAGE, (922, 150), a)
    label = "QRコード"
    tw, _ = text_size(draw, label, FONT_MID)
    draw.text((1047 - tw // 2, 426), label, font=FONT_MID, fill=(18, 22, 32, qr_box_alpha))
    sub = "スマホでアクセス"
    sw, _ = text_size(draw, sub, FONT_SMALL)
    draw.text((1047 - sw // 2, 474), sub, font=FONT_SMALL, fill=(42, 48, 60, qr_box_alpha))

    return frame


def render_frame(t: float) -> np.ndarray:
    if t < 5.0:
        frame = render_intro(t)
    elif t < 6.0:
        frame = render_transition(t)
    elif t < 20.0:
        frame = render_battle(t)
    else:
        frame = render_ending(t)
    return np.array(frame.convert("RGB"))


def set_audio_compat(video: VideoClip, audio: AudioFileClip) -> VideoClip:
    if hasattr(video, "with_audio"):
        return video.with_audio(audio)
    return video.set_audio(audio)


def main() -> None:
    clip = VideoClip(render_frame, duration=DURATION)
    audio = None
    if BGM_PATH and Path(BGM_PATH).exists():
        audio = AudioFileClip(str(BGM_PATH))
        end = min(DURATION, audio.duration)
        audio = audio.subclipped(0, end) if hasattr(audio, "subclipped") else audio.subclip(0, end)
        audio = audio.with_duration(DURATION) if hasattr(audio, "with_duration") else audio.set_duration(DURATION)
        clip = set_audio_compat(clip, audio)

    clip.write_videofile(
        str(OUTPUT_PATH),
        fps=FPS,
        codec="libx264",
        audio_codec="aac" if audio else None,
        preset="medium",
        threads=4,
    )

    clip.close()
    if audio:
        audio.close()
    print(f"動画を出力しました: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
