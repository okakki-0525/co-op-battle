"""
協力バトルの戦闘PVテスト動画を生成するスクリプトです。

実行方法:
    pip install moviepy pillow numpy
    python promo_battle_scene_test.py

出力:
    promo_battle_scene_test.mp4

BGM設定:
    BGM_PATH に音声ファイルを指定してください。
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
except ImportError:  # MoviePy 1.x fallback
    from moviepy.editor import AudioFileClip, VideoClip


WIDTH = 1280
HEIGHT = 720
FPS = 30
DURATION = 15.0

ROOT = Path(__file__).resolve().parent
IMAGE_DIR = ROOT / "static" / "images"
SOUND_DIR = ROOT / "static" / "sounds"
OUTPUT_PATH = ROOT / "promo_battle_scene_test.mp4"
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


FONT_HUGE = load_font(82, True)
FONT_BIG = load_font(62, True)
FONT_MID = load_font(42, True)
FONT_SMALL = load_font(26, True)
FONT_URL = load_font(28, False)


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


def load_image(path: Path) -> Image.Image | None:
    if not path.exists():
        return None
    try:
        return Image.open(path).convert("RGBA")
    except OSError:
        return None


def make_placeholder(label: str, color: tuple[int, int, int], size: tuple[int, int]) -> Image.Image:
    w, h = size
    image = Image.new("RGBA", size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((18, 18, w - 18, h - 18), radius=34, fill=(*color, 230), outline=(255, 236, 170, 230), width=4)
    draw.ellipse((w * 0.31, h * 0.15, w * 0.69, h * 0.44), fill=(255, 245, 210, 220))
    draw.rounded_rectangle((w * 0.20, h * 0.43, w * 0.80, h * 0.78), radius=48, fill=(255, 245, 210, 190))
    tw, th = text_size(draw, label, FONT_MID)
    draw.text(((w - tw) // 2, h - th - 38), label, font=FONT_MID, fill=(25, 20, 18, 255))
    return image


def make_enemy_card(enemy: Image.Image, label: str = "ENEMY") -> Image.Image:
    card = Image.new("RGBA", (430, 520), (0, 0, 0, 0))
    shadow = Image.new("RGBA", card.size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle((34, 34, 396, 486), radius=28, fill=(0, 0, 0, 170))
    card.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(14)))
    draw = ImageDraw.Draw(card)
    draw.rounded_rectangle((24, 20, 406, 480), radius=28, fill=(16, 18, 28, 242), outline=(255, 194, 75, 235), width=5)
    draw.rounded_rectangle((44, 40, 386, 380), radius=22, fill=(34, 22, 31, 235), outline=(255, 95, 42, 160), width=3)
    fitted = fit_image(enemy, 300, 300)
    card.alpha_composite(fitted, ((430 - fitted.width) // 2, 84 + (300 - fitted.height) // 2))
    tw, _ = text_size(draw, label, FONT_MID)
    draw.text(((430 - tw) // 2, 400), label, font=FONT_MID, fill=(255, 231, 140, 255), stroke_width=2, stroke_fill=(58, 20, 8, 255))
    return card


def make_background() -> Image.Image:
    source = load_image(ASSETS["background"])
    if source:
        base = center_crop(source, WIDTH, HEIGHT)
    else:
        base = Image.new("RGBA", (WIDTH, HEIGHT), (14, 18, 30, 255))
        draw = ImageDraw.Draw(base)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            draw.line((0, y, WIDTH, y), fill=(int(12 + ratio * 28), int(15 + ratio * 20), int(30 + ratio * 45), 255))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (4, 6, 12, 112))
    draw = ImageDraw.Draw(overlay)
    draw.polygon([(0, 474), (WIDTH, 326), (WIDTH, HEIGHT), (0, HEIGHT)], fill=(3, 5, 9, 126))
    for i in range(9):
        x = -160 + i * 190
        draw.line((x, 0, x + 360, HEIGHT), fill=(255, 255, 255, 14), width=3)
    return Image.alpha_composite(base, overlay)


def make_battle_floor() -> Image.Image:
    bg = make_background()
    draw = ImageDraw.Draw(bg)
    draw.rectangle((0, 430, WIDTH, HEIGHT), fill=(5, 8, 14, 132))
    for y in range(450, HEIGHT, 42):
        draw.line((0, y, WIDTH, y - 95), fill=(255, 137, 42, 22), width=2)
    draw.ellipse((90, 560, 520, 690), fill=(0, 0, 0, 95))
    draw.ellipse((760, 520, 1190, 680), fill=(0, 0, 0, 110))
    return bg


def make_logo() -> Image.Image:
    logo = load_image(ASSETS["logo"])
    if logo:
        return fit_image(logo, 420, 145)
    layer = Image.new("RGBA", (460, 140), (0, 0, 0, 0))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle((8, 18, 452, 124), radius=24, fill=(15, 18, 29, 228), outline=(255, 218, 95, 255), width=4)
    text = "協力バトル"
    tw, th = text_size(draw, text, FONT_BIG)
    draw.text(((460 - tw) // 2, (140 - th) // 2 - 6), text, font=FONT_BIG, fill=(255, 232, 138, 255), stroke_width=3, stroke_fill=(78, 30, 8, 255))
    return layer


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
        layer = layer.resize((int(layer.width * scale), int(layer.height * scale)), Image.Resampling.LANCZOS)
    return layer.rotate(angle, resample=Image.Resampling.BICUBIC, expand=True)


def flash_layer(color: tuple[int, int, int], alpha: int) -> Image.Image:
    return Image.new("RGBA", (WIDTH, HEIGHT), (*color, alpha))


def draw_motion_lines(image: Image.Image, t: float, alpha: int = 34) -> None:
    draw = ImageDraw.Draw(image)
    for i in range(13):
        x = int((t * 760 + i * 132) % (WIDTH + 360)) - 220
        draw.line((x, 80, x + 380, 620), fill=(255, 211, 115, alpha), width=5)


def draw_slash(image: Image.Image, progress: float, impact: float) -> None:
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    start = (408, 514)
    end = (930, 266)
    p = ease_out(progress)
    tip = (start[0] + (end[0] - start[0]) * p, start[1] + (end[1] - start[1]) * p)
    for i in range(11):
        trail = max(0.0, p - i * 0.055)
        sx = start[0] + (end[0] - start[0]) * trail
        sy = start[1] + (end[1] - start[1]) * trail
        width = 38 - i * 2
        alpha = int(210 * (1 - i / 12))
        draw.line((sx, sy, tip[0], tip[1]), fill=(255, 68 + i * 14, 14, alpha), width=width)
    draw.line((start[0], start[1], tip[0], tip[1]), fill=(255, 246, 190, 245), width=12)
    for i in range(18):
        ember_p = max(0.0, p - i * 0.025)
        ex = start[0] + (end[0] - start[0]) * ember_p + math.sin(i * 1.9) * 36
        ey = start[1] + (end[1] - start[1]) * ember_p + math.cos(i * 2.4) * 28
        r = 3 + (i % 4)
        draw.ellipse((ex - r, ey - r, ex + r, ey + r), fill=(255, 148, 36, 190))
    if impact > 0:
        cx, cy = end
        for i in range(22):
            a = i / 22 * math.tau
            length = 32 + 90 * impact * (0.5 + (i % 5) / 5)
            draw.line((cx, cy, cx + math.cos(a) * length, cy + math.sin(a) * length), fill=(255, 214, 82, int(230 * impact)), width=4)
        draw.ellipse((cx - 110 * impact, cy - 80 * impact, cx + 110 * impact, cy + 80 * impact), fill=(255, 106, 24, int(95 * impact)))
        draw.ellipse((cx - 62 * impact, cy - 44 * impact, cx + 62 * impact, cy + 44 * impact), fill=(255, 245, 184, int(190 * impact)))
    image.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(2)))
    image.alpha_composite(overlay)


def shake_offset(t: float, amount: float) -> tuple[int, int]:
    return (int(math.sin(t * 95.0) * amount), int(math.cos(t * 73.0) * amount))


def make_character(key: str, label: str, color: tuple[int, int, int], max_size: tuple[int, int]) -> Image.Image:
    source = load_image(ASSETS[key])
    if not source:
        source = make_placeholder(label, color, (300, 390))
    return fit_image(source, *max_size)


def make_enemy_images() -> list[Image.Image]:
    images: list[Image.Image] = []
    for name in ENEMY_CANDIDATES:
        source = load_image(IMAGE_DIR / name)
        if source:
            images.append(source)
    while len(images) < 8:
        idx = len(images) + 1
        images.append(make_placeholder(f"敵{idx}", (110 + idx * 13 % 100, 38, 46 + idx * 17 % 120), (330, 380)))
    return images


BG = make_background()
BATTLE_BG = make_battle_floor()
LOGO = make_logo()
HERO = make_character("hero", "勇者", (214, 70, 58), (210, 280))
TANK = make_character("tank", "タンク", (62, 132, 218), (230, 300))
MAGE = make_character("mage", "魔術師", (142, 86, 220), (210, 280))
ENEMIES = make_enemy_images()
ENEMY_CARDS = [make_enemy_card(img, f"ENEMY {i + 1}") for i, img in enumerate(ENEMIES)]
SELECTED_ENEMY = fit_image(ENEMIES[-1], 350, 360)


def enemy_index_for_time(t: float) -> int:
    elapsed = clamp(t / 4.0)
    speed_wave = math.sin(elapsed * math.pi)
    flips = int(1.7 + elapsed * 14.0 + speed_wave * 8.0)
    return flips % len(ENEMY_CARDS)


def render_intro(t: float) -> Image.Image:
    frame = BG.copy()
    draw_motion_lines(frame, t, 28)
    draw_center_text(frame, "敵影接近", 52, FONT_BIG, (255, 230, 145, 230), 3, (52, 16, 8, 220))

    if t >= 3.58:
        card = make_enemy_card(ENEMIES[-1], "BOSS")
        scale = 1.08 + 0.07 * math.sin(t * 18)
        angle = math.sin(t * 10) * 2
        alpha = 1.0
    else:
        idx = enemy_index_for_time(t)
        card = ENEMY_CARDS[idx]
        speed = 0.25 + 0.75 * math.sin(clamp(t / 4) * math.pi)
        scale = 0.92 + 0.10 * math.sin(t * (7 + speed * 10))
        angle = math.sin(t * (8 + speed * 12)) * (3 + speed * 8)
        alpha = 0.94

    for ghost_i in range(3):
        ghost = rotate_layer(card, angle - 10 + ghost_i * 8, scale * (0.94 - ghost_i * 0.035))
        gx = (WIDTH - ghost.width) // 2 + (ghost_i - 1) * 28
        gy = (HEIGHT - ghost.height) // 2 + (ghost_i - 1) * 12
        paste_alpha(frame, ghost, (gx, gy), 0.12)

    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    pulse = 0.45 + 0.55 * math.sin(t * 9) ** 2
    gdraw.ellipse((385, 120, 895, 640), fill=(255, 93, 28, int(42 + pulse * 42)))
    frame.alpha_composite(glow.filter(ImageFilter.GaussianBlur(26)))

    card_layer = rotate_layer(card, angle, scale)
    paste_alpha(frame, card_layer, ((WIDTH - card_layer.width) // 2, (HEIGHT - card_layer.height) // 2 + 16), alpha)
    return frame


def render_transition(t: float) -> Image.Image:
    local = t - 4.0
    shake = 8 + 16 * clamp(local / 1.5)
    ox, oy = shake_offset(t, shake)
    frame = BATTLE_BG.copy()
    enemy = fit_image(ENEMIES[-1], 430, 430)
    scale = 1.0 + 0.30 * math.sin(clamp(local / 2.0) * math.pi)
    enemy = rotate_layer(enemy, math.sin(t * 18) * 1.2, scale)
    paste_alpha(frame, enemy, ((WIDTH - enemy.width) // 2 + ox, 176 + oy), 1.0)

    dark = int(160 * ease_in_out(clamp((local - 0.85) / 1.1)))
    if dark:
        frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, dark)))

    draw_motion_lines(frame, t, 52)
    draw_center_text(frame, "強敵出現！", 88 + oy, FONT_HUGE, (255, 233, 140, 255), 5, (91, 20, 5, 255))
    if local > 1.0:
        frame.alpha_composite(flash_layer((255, 226, 157), int(80 * math.sin(clamp(local - 1.0, 0, 1) * math.pi))))
    return frame


def render_battle(t: float) -> Image.Image:
    local = t - 6.0
    impact = clamp(1.0 - abs(local - 3.05) / 0.36)
    ox, oy = shake_offset(t, 11 * impact)
    frame = BATTLE_BG.copy()
    draw = ImageDraw.Draw(frame)

    draw.rounded_rectangle((26, 28, 362, 180), radius=16, fill=(7, 10, 18, 185), outline=(255, 174, 65, 135), width=2)
    for i, (name, hp, color) in enumerate([("勇者", "HP 1280", (255, 210, 90)), ("タンク", "HP 1850", (106, 192, 255)), ("魔術師", "HP 960", (214, 157, 255))]):
        y = 48 + i * 42
        draw.text((48, y), name, font=FONT_SMALL, fill=(*color, 255))
        draw.rounded_rectangle((148, y + 7, 322, y + 25), radius=9, fill=(35, 48, 62, 255))
        draw.rounded_rectangle((148, y + 7, 300 - i * 18, y + 25), radius=9, fill=(*color, 230))
        draw.text((332, y), hp, font=FONT_SMALL, fill=(245, 248, 255, 235))

    for layer, x, y in [(HERO, 154, 368), (TANK, 282, 350), (MAGE, 68, 384)]:
        paste_alpha(frame, layer, (x + ox, y + oy), 1.0)

    enemy_float = int(math.sin(t * 3.5) * 5)
    paste_alpha(frame, SELECTED_ENEMY, (842 + ox, 230 + oy + enemy_float), 1.0)

    draw.rounded_rectangle((764, 46, 1218, 112), radius=18, fill=(10, 8, 15, 190), outline=(255, 89, 48, 175), width=3)
    draw.text((790, 58), "BOSS", font=FONT_MID, fill=(255, 222, 130, 255), stroke_width=2, stroke_fill=(70, 18, 4, 255))
    draw.rounded_rectangle((928, 70, 1184, 94), radius=12, fill=(45, 20, 22, 255))
    hp_w = int(256 * max(0.36, 1.0 - 0.13 * clamp((local - 3.05) / 0.6)))
    draw.rounded_rectangle((928, 70, 928 + hp_w, 94), radius=12, fill=(235, 62, 43, 255))

    attack_p = clamp((local - 2.15) / 1.0)
    if 0 < attack_p < 1 or impact > 0:
        draw_slash(frame, attack_p, impact)

    if local > 1.15:
        telop_alpha = clamp((local - 1.15) / 0.35) * clamp((5.35 - local) / 0.8)
        draw.rounded_rectangle((420, 36, 860, 108), radius=20, fill=(85, 21, 8, int(180 * telop_alpha)), outline=(255, 180, 72, int(230 * telop_alpha)), width=3)
        draw_center_text(frame, "協力攻撃！ 炎剣！", 48, FONT_MID, (255, 239, 164, int(255 * telop_alpha)), 3, (52, 12, 4, int(230 * telop_alpha)))

    if impact > 0:
        draw_center_text(frame, "2480", 224 - int(48 * impact), FONT_BIG, (255, 237, 136, int(255 * impact)), 4, (98, 14, 2, int(235 * impact)))
        frame.alpha_composite(flash_layer((255, 222, 134), int(70 * impact)))

    return frame


def render_ending(t: float) -> Image.Image:
    local = t - 12.0
    frame = BG.copy()
    frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 78)))
    draw_motion_lines(frame, t, 34)
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    gdraw.ellipse((310, 110, 970, 600), fill=(255, 110, 32, int(55 + 35 * math.sin(t * 5) ** 2)))
    frame.alpha_composite(glow.filter(ImageFilter.GaussianBlur(34)))

    alpha = clamp(local / 0.55)
    draw_center_text(frame, "最大6人で協力バトル！", 178, FONT_HUGE, (255, 236, 142, int(255 * alpha)), 5, (84, 22, 4, int(245 * alpha)))
    draw_center_text(frame, "仲間と連携して、強敵を倒せ！", 300, FONT_MID, (255, 255, 255, int(238 * alpha)), 3, (0, 0, 0, int(210 * alpha)))

    logo_alpha = clamp((local - 0.55) / 0.7)
    paste_alpha(frame, LOGO, ((WIDTH - LOGO.width) // 2, 385), logo_alpha)

    draw = ImageDraw.Draw(frame)
    url_alpha = clamp((local - 1.05) / 0.5)
    draw.rounded_rectangle((296, 560, 984, 614), radius=16, fill=(4, 7, 12, int(185 * url_alpha)), outline=(255, 178, 74, int(180 * url_alpha)), width=2)
    uw, _ = text_size(draw, URL, FONT_URL)
    draw.text(((WIDTH - uw) // 2, 572), URL, font=FONT_URL, fill=(255, 250, 230, int(255 * url_alpha)))

    fade = clamp((DURATION - t) / 0.7)
    if fade < 1:
        frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, int(255 * (1 - fade)))))
    return frame


def render_frame(t: float) -> np.ndarray:
    if t < 4.0:
        frame = render_intro(t)
    elif t < 6.0:
        frame = render_transition(t)
    elif t < 12.0:
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
