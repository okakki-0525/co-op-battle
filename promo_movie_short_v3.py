"""
YouTube Shorts PV: game intro + player recruitment.

Run:
    pip install moviepy pillow numpy
    py -3.14 promo_movie_short_v3.py

Output:
    promo_movie_short_v3.mp4
"""

from __future__ import annotations

import math
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

try:
    from moviepy import AudioFileClip, VideoClip, concatenate_audioclips
except ImportError:
    from moviepy.editor import AudioFileClip, VideoClip, concatenate_audioclips


WIDTH = 1080
HEIGHT = 1920
FPS = 30
DURATION = 38.5
URL = "https://co-op-battle.onrender.com/login"

ROOT = Path(__file__).resolve().parent
IMAGE_DIR = ROOT / "static" / "images"
SOUND_DIR = ROOT / "static" / "sounds"
OUTPUT_PATH = ROOT / "promo_movie_short_v3.mp4"
BGM_PATH = SOUND_DIR / "tabidachi.mp3"
QR_PATH = ROOT / "co_op_battle_qr.png"


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def ease_out(v: float) -> float:
    v = clamp(v)
    return 1 - (1 - v) * (1 - v)


def ease_in_out(v: float) -> float:
    v = clamp(v)
    return v * v * (3 - 2 * v)


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


FONT_HUGE = load_font(72, True)
FONT_XL = load_font(58, True)
FONT_L = load_font(46, True)
FONT_M = load_font(34, True)
FONT_S = load_font(26, True)
FONT_XS = load_font(22, False)
FONT_URL = load_font(30, False)


def load_image(path: Path) -> Image.Image | None:
    if not path.exists():
        return None
    try:
        return Image.open(path).convert("RGBA")
    except Exception:
        return None


def text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def fit_image(img: Image.Image, max_w: int, max_h: int) -> Image.Image:
    img = img.convert("RGBA")
    scale = min(max_w / img.width, max_h / img.height)
    return img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.Resampling.LANCZOS)


def cover_image(img: Image.Image, w: int, h: int) -> Image.Image:
    img = img.convert("RGBA")
    scale = max(w / img.width, h / img.height)
    resized = img.resize((max(1, int(img.width * scale)), max(1, int(img.height * scale))), Image.Resampling.LANCZOS)
    left = (resized.width - w) // 2
    top = (resized.height - h) // 2
    return resized.crop((left, top, left + w, top + h))


def paste_alpha(base: Image.Image, layer: Image.Image, xy: tuple[int, int], alpha: float = 1.0) -> None:
    alpha = clamp(alpha)
    if alpha <= 0:
        return
    layer = layer.convert("RGBA")
    if alpha < 1:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda p: int(p * alpha)))
    base.alpha_composite(layer, xy)


def center_line(
    draw: ImageDraw.ImageDraw,
    text: str,
    y: int,
    font,
    fill,
    stroke_width: int = 0,
    stroke_fill=(0, 0, 0, 255),
) -> None:
    w, _ = text_size(draw, text, font)
    draw.text(((WIDTH - w) // 2, y), text, font=font, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)


def center_multiline(
    draw: ImageDraw.ImageDraw,
    text: str,
    center_y: int,
    font,
    fill,
    line_gap: int = 16,
    stroke_width: int = 0,
    stroke_fill=(0, 0, 0, 255),
) -> None:
    lines = text.split("\n")
    heights = [text_size(draw, line or " ", font)[1] for line in lines]
    total = sum(heights) + line_gap * (len(lines) - 1)
    y = center_y - total // 2
    for line, h in zip(lines, heights):
        center_line(draw, line, y, font, fill, stroke_width, stroke_fill)
        y += h + line_gap


def draw_multiline(draw, text: str, x: int, y: int, font, fill, line_gap: int = 10, stroke: int = 0):
    yy = y
    for line in text.split("\n"):
        draw.text((x, yy), line, font=font, fill=fill, stroke_width=stroke, stroke_fill=(0, 0, 0, 210))
        yy += text_size(draw, line or " ", font)[1] + line_gap
    return yy


def placeholder(label: str, color: tuple[int, int, int], size=(300, 300)) -> Image.Image:
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    w, h = size
    d.rounded_rectangle((10, 10, w - 10, h - 10), radius=32, fill=(*color, 230), outline=(255, 225, 110, 230), width=4)
    d.ellipse((w // 2 - 58, 52, w // 2 + 58, 168), fill=(255, 245, 210, 220))
    d.rounded_rectangle((w // 2 - 88, 172, w // 2 + 88, 248), radius=34, fill=(255, 245, 210, 170))
    center_line(d, label, h - 58, FONT_S, (20, 18, 18, 255))
    return img


def make_login_bg() -> Image.Image:
    src = load_image(IMAGE_DIR / "login_bg.png")
    if src:
        bg = cover_image(src, WIDTH, HEIGHT)
    else:
        bg = Image.new("RGBA", (WIDTH, HEIGHT), (12, 16, 30, 255))
        d = ImageDraw.Draw(bg)
        for y in range(HEIGHT):
            r = y / HEIGHT
            d.line((0, y, WIDTH, y), fill=(int(12 + 18 * r), int(16 + 25 * r), int(33 + 60 * r), 255))
    bg.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 88)))
    return bg


def make_qr() -> Image.Image:
    src = load_image(QR_PATH)
    if src:
        return fit_image(src, 560, 560)
    img = Image.new("RGBA", (560, 560), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, 559, 559), outline=(0, 0, 0, 255), width=12)
    center_multiline(d, "QRコード\n準備中", 280, FONT_L, (0, 0, 0, 255))
    return img


LOGIN_BG = make_login_bg()
LOGO = fit_image(load_image(IMAGE_DIR / "title.png") or placeholder("協力バトルONLINE", (60, 60, 120), (820, 220)), 780, 220)
QR = make_qr()
HERO = fit_image(load_image(IMAGE_DIR / "yusya.png") or placeholder("勇者", (200, 70, 55)), 210, 250)
TANK = fit_image(load_image(IMAGE_DIR / "tanc.png") or placeholder("タンク", (55, 105, 205)), 220, 260)
MAGE = fit_image(load_image(IMAGE_DIR / "majyutu.png") or placeholder("魔術師", (120, 70, 205)), 210, 250)
ENEMY = fit_image(load_image(IMAGE_DIR / "enemies" / "demon_lord.png") or placeholder("強敵", (95, 40, 120), (360, 320)), 300, 250)
ENEMY_SMALL = fit_image(load_image(IMAGE_DIR / "enemies" / "death_knight.png") or placeholder("敵", (80, 70, 100), (260, 230)), 210, 170)


def dark_fantasy_bg(t: float = 0.0) -> Image.Image:
    frame = LOGIN_BG.copy().filter(ImageFilter.GaussianBlur(7))
    d = ImageDraw.Draw(frame)
    d.rectangle((0, 0, WIDTH, HEIGHT), fill=(3, 6, 16, 130))
    for i in range(9):
        x = int(-220 + i * 180 + 20 * math.sin(t * 1.8 + i))
        d.line((x, 0, x + 620, HEIGHT), fill=(255, 140, 55, 16), width=3)
    d.ellipse((-260, 650, 530, 1640), fill=(255, 85, 40, 28))
    d.ellipse((520, -160, 1320, 760), fill=(80, 185, 255, 22))
    return frame


def panel(draw: ImageDraw.ImageDraw, box, fill=(16, 21, 34, 232), outline=(86, 96, 132, 220), radius=18, width=3):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def draw_hp_bar(draw, x: int, y: int, w: int, label: str, hp: float, color: tuple[int, int, int]):
    panel(draw, (x, y, x + w, y + 54), fill=(12, 16, 26, 232), outline=(80, 90, 122, 220), radius=14, width=2)
    draw.text((x + 16, y + 13), label, font=FONT_XS, fill=(238, 242, 255, 245))
    draw.rounded_rectangle((x + 116, y + 17, x + w - 18, y + 39), radius=9, fill=(47, 54, 70, 255))
    draw.rounded_rectangle((x + 116, y + 17, x + 116 + int((w - 134) * hp), y + 39), radius=9, fill=(*color, 255))


def battle_canvas(t: float, highlight: str | None = None, message: str = "", extra_players: bool = False) -> Image.Image:
    frame = dark_fantasy_bg(t)
    d = ImageDraw.Draw(frame)

    panel(d, (42, 46, 1038, 1035), fill=(7, 11, 22, 216), outline=(255, 210, 96, 170), radius=28, width=4)
    d.text((78, 78), "協力バトルONLINE", font=FONT_M, fill=(255, 235, 145, 255), stroke_width=2, stroke_fill=(50, 16, 4, 220))
    d.text((808, 84), "TURN 1", font=FONT_S, fill=(230, 238, 255, 235))

    paste_alpha(frame, ENEMY, (600, 215 + int(10 * math.sin(t * 2.2))), 1)
    draw_hp_bar(d, 565, 470, 405, "強敵", .72 + .03 * math.sin(t * 2), (210, 54, 65))

    members = [
        ("勇者", HERO, 92, 560, (220, 74, 58), "hero"),
        ("タンク", TANK, 356, 560, (64, 133, 222), "tank"),
        ("魔術師", MAGE, 626, 560, (143, 86, 220), "mage"),
    ]
    if extra_players:
        members += [
            ("仲間A", HERO, 152, 790, (230, 145, 60), "ally1"),
            ("仲間B", TANK, 426, 790, (70, 185, 150), "ally2"),
            ("仲間C", MAGE, 694, 790, (210, 85, 185), "ally3"),
        ]

    for name, img, x, y, color, key in members:
        size = (165, 195) if extra_players else (205, 240)
        char = fit_image(img, size[0], size[1])
        paste_alpha(frame, char, (x, y), 1)
        draw_hp_bar(d, x - 5, y + size[1] + 8, 230, name, .82, color)
        if highlight == key:
            d.ellipse((x - 24, y - 24, x + size[0] + 28, y + size[1] + 76), outline=(255, 48, 42, 255), width=9)

    panel(d, (60, 1110, 1020, 1445), fill=(13, 18, 31, 238), outline=(84, 96, 130, 235), radius=24, width=3)
    d.text((92, 1140), "コマンド", font=FONT_M, fill=(255, 236, 145, 255))
    commands = [("勇者", "炎剣"), ("タンク", "フォートレス"), ("魔術師", "マジックブースト")]
    for i, (name, cmd) in enumerate(commands):
        y = 1202 + i * 72
        d.rounded_rectangle((92, y, 982, y + 54), radius=16, fill=(36, 45, 66, 238), outline=(255, 255, 255, 50), width=2)
        d.text((122, y + 12), name, font=FONT_S, fill=(228, 236, 255, 245))
        d.text((330, y + 12), cmd, font=FONT_S, fill=(255, 246, 190, 255))
        d.text((902, y + 12), "✓", font=FONT_S, fill=(105, 255, 170, 255))
    if message:
        d.rounded_rectangle((92, 1365, 982, 1424), radius=16, fill=(90, 20, 16, 230), outline=(255, 110, 68, 230), width=2)
        center_line(d, message, 1377, FONT_S, (255, 245, 235, 255))

    panel(d, (60, 1480, 1020, 1770), fill=(10, 15, 26, 235), outline=(255, 210, 96, 190), radius=24, width=3)
    d.text((96, 1514), "戦闘ログ", font=FONT_M, fill=(255, 236, 145, 255))
    logs = ["全員のコマンドが揃った！", "ACTION！ 一斉行動開始", "仲間の連携で強敵に挑む！"]
    for i, line in enumerate(logs):
        d.text((100, 1582 + i * 48), line, font=FONT_S, fill=(235, 242, 255, 238))
    return frame


def caption_overlay(frame: Image.Image, text: str, y: int = 1370, font=FONT_L, alpha: float = 1.0):
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.rounded_rectangle((58, y - 50, 1022, y + 250), radius=28, fill=(0, 0, 0, int(170 * alpha)), outline=(255, 218, 90, int(140 * alpha)), width=3)
    center_multiline(d, text, y + 92, font, (255, 255, 255, int(255 * alpha)), line_gap=14, stroke_width=2, stroke_fill=(0, 0, 0, int(230 * alpha)))
    frame.alpha_composite(layer)


def flash(frame: Image.Image, amount: float) -> Image.Image:
    amount = clamp(amount)
    if amount <= 0:
        return frame
    frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (255, 240, 180, int(120 * amount))))
    return frame


def mosaic_transition(frame: Image.Image, local: float, duration: float = .55) -> Image.Image:
    p = clamp(local / duration)
    if p >= 1:
        return frame
    block = int(42 - 34 * p)
    small = frame.resize((max(1, WIDTH // block), max(1, HEIGHT // block)), Image.Resampling.BILINEAR)
    return small.resize((WIDTH, HEIGHT), Image.Resampling.NEAREST)


def scene_intro(t: float) -> Image.Image:
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    d = ImageDraw.Draw(frame)
    if t < 1:
        a = int(255 * clamp(t / .45))
        center_line(d, "このゲームは…", 760, FONT_XL, (255, 255, 255, a))
    else:
        a = int(255 * clamp((t - 1) / .35) * clamp((4.15 - t) / .6))
        pulse = 1 + .035 * math.sin(t * 8)
        font1 = load_font(int(60 * pulse), True)
        center_multiline(d, "最大6人で協力して戦う\nオンラインターン制RPGです！", 895, font1, (255, 246, 198, a), 20, 3, (80, 20, 4, int(240 * a / 255)))
        center_line(d, "ブラウザで無料プレイ", 1135, FONT_M, (210, 232, 255, int(230 * a / 255)), 2, (0, 0, 0, int(220 * a / 255)))
    return frame


def scene_battle_roles(t: float) -> Image.Image:
    local = t - 4.4
    key = None
    if 0.6 <= local < 2.0:
        key = "hero"
    elif 2.0 <= local < 3.4:
        key = "tank"
    elif local >= 3.4:
        key = "mage"
    frame = battle_canvas(t, highlight=key, message="別々の人が操作！")
    caption_overlay(frame, "勇者・タンク・魔術師など\nそれぞれのキャラクターを\n別々の人が操作します！", 1450, FONT_M, clamp(local / .8))
    if local < .6:
        frame = mosaic_transition(frame, local, .6)
    return frame


def chat_screen(t: float, zoom: float = 1.0, recruit: bool = False) -> Image.Image:
    frame = dark_fantasy_bg(t)
    d = ImageDraw.Draw(frame)
    panel(d, (68, 210, 1012, 1260), fill=(13, 18, 31, 242), outline=(255, 218, 90, 205), radius=30, width=4)
    d.text((110, 250), "チャット", font=FONT_L, fill=(255, 236, 145, 255), stroke_width=2, stroke_fill=(50, 15, 4, 230))
    messages = [
        ("勇者", "次、フォートレスお願い！", .25, False),
        ("タンク", "了解！守ります！", 1.05, True),
        ("魔術師", "強化して一気に行きます！", 1.85, False),
        ("勇者", "ナイス連携！", 2.65, True),
    ]
    if recruit:
        messages = [
            ("勇者", "今日も誰か来てるかな？", .2, False),
            ("タンク", "少しずつ増えたら嬉しいね", 1.0, True),
            ("魔術師", "見かけたらぜひ一緒に！", 1.8, False),
        ]
    for i, (name, msg, start, right) in enumerate(messages):
        p = ease_out(clamp((t - start) / .35))
        if p <= 0:
            continue
        x1 = 165 if not right else 300
        x2 = 875 if not right else 930
        y = 390 + i * 145
        fill = (42, 54, 82, int(235 * p)) if not right else (38, 92, 80, int(235 * p))
        d.rounded_rectangle((x1, y, x2, y + 100), radius=24, fill=fill, outline=(255, 255, 255, int(70 * p)), width=2)
        d.text((x1 + 30, y + 15), name, font=FONT_S, fill=(255, 236, 145, int(255 * p)))
        d.text((x1 + 30, y + 52), msg, font=FONT_S, fill=(255, 255, 255, int(255 * p)))
    if zoom != 1.0:
        new_size = (int(WIDTH * zoom), int(HEIGHT * zoom))
        big = frame.resize(new_size, Image.Resampling.LANCZOS)
        left = (big.width - WIDTH) // 2
        top = int((big.height - HEIGHT) * .35)
        frame = big.crop((left, top, left + WIDTH, top + HEIGHT))
    return frame


def scene_chat(t: float) -> Image.Image:
    local = t - 11.0
    frame = chat_screen(local, 1.03)
    caption_overlay(frame, "チャットで相談しながら\n仲間と協力して敵を倒します！", 1380, FONT_M, clamp(local / .7))
    return mosaic_transition(frame, local, .55) if local < .55 else frame


def scene_but(t: float) -> Image.Image:
    local = t - 16.0
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    d = ImageDraw.Draw(frame)
    a = int(255 * clamp(local / .45) * clamp((2.0 - local) / .45))
    center_line(d, "でも…", 880, FONT_HUGE, (255, 255, 255, a))
    return frame


def scene_lobby(t: float) -> Image.Image:
    local = t - 18.0
    zoom = 1.08 - .05 * ease_out(clamp(local / 4))
    bg = LOGIN_BG.resize((int(WIDTH * zoom), int(HEIGHT * zoom)), Image.Resampling.LANCZOS)
    frame = bg.crop(((bg.width - WIDTH) // 2, (bg.height - HEIGHT) // 2, (bg.width + WIDTH) // 2, (bg.height + HEIGHT) // 2))
    d = ImageDraw.Draw(frame)
    frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 80)))
    paste_alpha(frame, LOGO, ((WIDTH - LOGO.width) // 2, 300), clamp(local / .8))
    panel(d, (74, 720, 1006, 1128), fill=(8, 12, 24, 210), outline=(255, 218, 90, 180), radius=30, width=3)
    center_multiline(d, "作りたてなので\nまだプレイヤーが少ないです。", 922, FONT_L, (255, 255, 255, 255), 20, 2)
    center_line(d, "だからこそ、今の参加が力になります。", 1180, FONT_S, (224, 236, 255, 238), 1)
    return mosaic_transition(frame, local, .55) if local < .55 else frame


def scene_more_people(t: float) -> Image.Image:
    local = t - 22.0
    frame = battle_canvas(t, highlight=None, message="6人で一斉行動！", extra_players=True)
    caption_overlay(frame, "このゲームは\n人が集まるほど\n面白くなります！", 1340, FONT_L, clamp(local / .8))
    if 2.1 < local < 2.55:
        frame = flash(frame, 1 - abs(local - 2.32) / .23)
    return mosaic_transition(frame, local, .55) if local < .55 else frame


def scene_login_again(t: float) -> Image.Image:
    local = t - 27.0
    frame = chat_screen(local, 1.12, recruit=True)
    caption_overlay(frame, "興味を持っていただけたら\n時々ログインしてみてください！", 1360, FONT_M, clamp(local / .6))
    return frame


def scene_peak(t: float) -> Image.Image:
    local = t - 31.0
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    d = ImageDraw.Draw(frame)
    a = int(255 * clamp(local / .35))
    center_multiline(d, "4〜6人集まった瞬間\nこのゲームは\n本領を発揮します！", 880, FONT_XL, (255, 245, 190, a), 20, 3, (90, 22, 5, int(240 * a / 255)))
    return flash(frame, .28 * clamp((local - .8) / .4))


def scene_ending(t: float) -> Image.Image:
    local = t - 33.5
    frame = LOGIN_BG.copy().filter(ImageFilter.GaussianBlur(3))
    frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 115)))
    d = ImageDraw.Draw(frame)
    a = clamp(local / .65)
    center_line(d, "最初の仲間を募集中！", 250, FONT_XL, (255, 236, 145, int(255 * a)), 3, (68, 18, 4, int(240 * a)))
    center_line(d, "ログインするだけでも嬉しいです！", 350, FONT_M, (255, 255, 255, int(248 * a)), 2)
    center_line(d, "一緒にこのゲームを育てませんか？", 420, FONT_S, (228, 238, 255, int(238 * a)), 1)

    d.rounded_rectangle((218, 525, 862, 1168), radius=32, fill=(246, 247, 250, int(255 * a)), outline=(255, 204, 96, int(255 * a)), width=5)
    paste_alpha(frame, QR, ((WIDTH - QR.width) // 2, 565), a)

    d.rounded_rectangle((70, 1255, 1010, 1348), radius=24, fill=(246, 247, 250, int(255 * a)), outline=(255, 204, 96, int(255 * a)), width=4)
    center_line(d, URL, 1282, FONT_URL, (18, 22, 32, int(255 * a)))

    paste_alpha(frame, LOGO, ((WIDTH - LOGO.width) // 2, 1450), a)
    center_line(d, "協力バトルONLINE", 1692, FONT_M, (255, 236, 145, int(255 * a)), 2, (50, 15, 4, int(230 * a)))
    return frame


def render_frame(t: float) -> np.ndarray:
    if t < 4.4:
        frame = scene_intro(t)
    elif t < 11.0:
        frame = scene_battle_roles(t)
    elif t < 16.0:
        frame = scene_chat(t)
    elif t < 18.0:
        frame = scene_but(t)
    elif t < 22.0:
        frame = scene_lobby(t)
    elif t < 27.0:
        frame = scene_more_people(t)
    elif t < 31.0:
        frame = scene_login_again(t)
    elif t < 33.5:
        frame = scene_peak(t)
    else:
        frame = scene_ending(t)
    return np.array(frame.convert("RGB"))


def with_audio(video: VideoClip, audio):
    return video.with_audio(audio) if hasattr(video, "with_audio") else video.set_audio(audio)


def with_duration(clip, duration: float):
    return clip.with_duration(duration) if hasattr(clip, "with_duration") else clip.set_duration(duration)


def with_volume(clip, volume: float):
    if hasattr(clip, "with_volume_scaled"):
        return clip.with_volume_scaled(volume)
    return clip.volumex(volume)


def build_audio():
    if not BGM_PATH.exists():
        return None
    bgm = AudioFileClip(str(BGM_PATH))
    if bgm.duration < DURATION:
        loops = max(1, math.ceil(DURATION / max(.1, bgm.duration)))
        bgm = concatenate_audioclips([bgm] * loops)
    bgm = with_duration(bgm, DURATION)
    return with_volume(bgm, .38)


def main() -> None:
    clip = VideoClip(render_frame, duration=DURATION)
    audio = build_audio()
    if audio:
        clip = with_audio(clip, audio)
    clip.write_videofile(str(OUTPUT_PATH), fps=FPS, codec="libx264", audio_codec="aac" if audio else None, preset="ultrafast", threads=4)
    clip.close()
    if audio:
        audio.close()
    print(f"動画を出力しました: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
