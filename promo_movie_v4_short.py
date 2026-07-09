"""
YouTube Shorts layout adapter for promo_movie_v4.py.

Run:
    pip install moviepy pillow numpy
    python promo_movie_v4_short.py

Output:
    promo_movie_v4_short.mp4
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

try:
    from moviepy import VideoClip
except ImportError:
    from moviepy.editor import VideoClip

import promo_movie_v4 as base


WIDTH = 1080
HEIGHT = 1920
FPS = base.FPS
DURATION = base.DURATION
OUTPUT_PATH = Path(__file__).resolve().parent / "promo_movie_v4_short.mp4"
URL = "https://co-op-battle.onrender.com/login"

FONT_INTRO = base.load_font(58, True)
FONT_TITLE = base.load_font(72, True)
FONT_TITLE_SMALL = base.load_font(52, True)
FONT_END_TITLE = base.load_font(68, True)
FONT_END_SUB = base.load_font(46, True)
FONT_URL = base.load_font(32, False)
FONT_FOOTER = base.load_font(38, True)


def clamp(v: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def cover_crop(img: Image.Image, box: tuple[int, int, int, int], w: int, h: int) -> Image.Image:
    cropped = img.crop(box).convert("RGBA")
    scale = max(w / cropped.width, h / cropped.height)
    resized = cropped.resize((max(1, int(cropped.width * scale)), max(1, int(cropped.height * scale))), Image.Resampling.LANCZOS)
    left = (resized.width - w) // 2
    top = (resized.height - h) // 2
    return resized.crop((left, top, left + w, top + h))


def fit_crop(img: Image.Image, box: tuple[int, int, int, int], max_w: int, max_h: int) -> Image.Image:
    cropped = img.crop(box).convert("RGBA")
    scale = min(max_w / cropped.width, max_h / cropped.height)
    resized = cropped.resize((max(1, int(cropped.width * scale)), max(1, int(cropped.height * scale))), Image.Resampling.LANCZOS)
    return resized


def paste_alpha(base_img: Image.Image, layer: Image.Image, xy: tuple[int, int], alpha: float = 1.0) -> None:
    alpha = clamp(alpha)
    if alpha <= 0:
        return
    layer = layer.convert("RGBA")
    if alpha < 1:
        layer = layer.copy()
        layer.putalpha(layer.getchannel("A").point(lambda p: int(p * alpha)))
    base_img.alpha_composite(layer, xy)


def make_vertical_bg(src: Image.Image) -> Image.Image:
    bg = cover_crop(src, (0, 0, base.WIDTH, base.HEIGHT), WIDTH, HEIGHT)
    bg = bg.filter(ImageFilter.GaussianBlur(18))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (3, 5, 12, 130))
    bg.alpha_composite(overlay)
    return bg


def draw_shadow_panel(frame: Image.Image, box: tuple[int, int, int, int]) -> None:
    d = ImageDraw.Draw(frame)
    x1, y1, x2, y2 = box
    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle((x1 + 10, y1 + 14, x2 + 10, y2 + 14), radius=28, fill=(0, 0, 0, 128))
    frame.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(10)))
    d.rounded_rectangle(box, radius=28, outline=(255, 218, 90, 210), width=4)


def text_size(draw: ImageDraw.ImageDraw, text: str, font) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=font)
    return box[2] - box[0], box[3] - box[1]


def draw_centered_line(
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


def draw_centered_multiline(
    draw: ImageDraw.ImageDraw,
    text: str,
    center_y: int,
    font,
    fill,
    line_gap: int = 18,
    stroke_width: int = 0,
    stroke_fill=(0, 0, 0, 255),
) -> None:
    lines = text.split("\n")
    heights = [text_size(draw, line or " ", font)[1] for line in lines]
    total_h = sum(heights) + line_gap * (len(lines) - 1)
    y = center_y - total_h // 2
    for line, h in zip(lines, heights):
        draw_centered_line(draw, line, y, font, fill, stroke_width, stroke_fill)
        y += h + line_gap


def vertical_intro(t: float) -> Image.Image:
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    d = ImageDraw.Draw(frame)
    fade = 1.0 if t < 9 else clamp(1 - (t - 9) / .65)
    captions = [
        ("ターン制バトルで", 410, 0),
        ("メンバー一人ひとりを\n操作しているのが", 760, 3),
        ("別々の人間だったら\n面白くないですか？", 1130, 6),
    ]
    for text, y, start in captions:
        alpha = int(255 * fade * clamp((t - start) / 1.0))
        if alpha > 0:
            draw_centered_multiline(d, text, y, FONT_INTRO, (255, 255, 255, alpha), line_gap=24)
    return frame


def vertical_title(t: float, src: Image.Image) -> Image.Image:
    local = t - 10
    frame = cover_crop(src, (0, 0, base.WIDTH, base.HEIGHT), WIDTH, HEIGHT)
    frame = frame.filter(ImageFilter.GaussianBlur(1))
    frame.alpha_composite(Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 95)))
    d = ImageDraw.Draw(frame)
    if local < 3:
        a = int(255 * clamp(local / .35) * clamp((3.15 - local) / .45))
        draw_centered_multiline(
            d,
            "そんなブラウザゲームを\n作りました！！",
            910,
            FONT_TITLE,
            (255, 35, 35, a),
            line_gap=28,
            stroke_width=5,
            stroke_fill=(70, 0, 0, int(240 * a / 255)),
        )
    else:
        a = clamp((local - 3) / .6)
        logo = base.fit_image(base.LOGO, 900, 250)
        paste_alpha(frame, logo, ((WIDTH - logo.width) // 2, 610), a)
        draw_centered_multiline(
            d,
            "その名も\n『協力バトルONLINE』",
            940,
            FONT_TITLE_SMALL,
            (255, 236, 145, int(255 * a)),
            line_gap=22,
            stroke_width=4,
            stroke_fill=(65, 18, 4, int(240 * a)),
        )
        draw_centered_multiline(
            d,
            "無料ですぐ遊べる\nブラウザゲーム",
            1140,
            base.load_font(34, True),
            (245, 250, 255, int(235 * a)),
            line_gap=12,
            stroke_width=2,
            stroke_fill=(0, 0, 0, int(220 * a)),
        )
    return frame


def vertical_cover(src: Image.Image) -> Image.Image:
    return cover_crop(src, (0, 0, base.WIDTH, base.HEIGHT), WIDTH, HEIGHT)


def split_battle_and_text(src: Image.Image) -> Image.Image:
    frame = make_vertical_bg(src)
    top_box = (40, 40, 1040, 930)
    bottom_box = (40, 990, 1040, 1870)

    battle = fit_crop(src, (48, 34, 990, 990), 1000, 890)
    text = fit_crop(src, (1000, 110, 1865, 950), 1000, 880)

    paste_alpha(frame, battle, (top_box[0] + (1000 - battle.width) // 2, top_box[1] + (890 - battle.height) // 2), 1)
    paste_alpha(frame, text, (bottom_box[0] + (1000 - text.width) // 2, bottom_box[1] + (880 - text.height) // 2), 1)

    draw_shadow_panel(frame, top_box)
    draw_shadow_panel(frame, bottom_box)
    return frame


def vertical_chat(src: Image.Image) -> Image.Image:
    frame = make_vertical_bg(src)
    chat = fit_crop(src, (150, 100, 1770, 955), 1040, 1450)
    paste_alpha(frame, chat, ((WIDTH - chat.width) // 2, 225), 1)
    draw_shadow_panel(frame, (30, 210, 1050, 1700))
    return frame


def vertical_ending() -> Image.Image:
    frame = Image.new("RGBA", (WIDTH, HEIGHT), (7, 10, 20, 255))
    d = ImageDraw.Draw(frame)
    for y in range(HEIGHT):
        r = y / HEIGHT
        d.line((0, y, WIDTH, y), fill=(int(8 + 18 * r), int(10 + 18 * r), int(22 + 42 * r), 255))
    d.rectangle((0, 0, WIDTH, HEIGHT), fill=(0, 0, 0, 35))

    logo = base.fit_image(base.LOGO, 860, 250)
    paste_alpha(frame, logo, ((WIDTH - logo.width) // 2, 170), 1)
    draw_centered_line(d, "協力バトルONLINE", 455, FONT_END_TITLE, (255, 236, 145, 255), 4, (64, 18, 4, 240))
    draw_centered_line(d, "今すぐ仲間と冒険に出よう！", 570, FONT_END_SUB, (255, 255, 255, 245), 2, (0, 0, 0, 220))

    d.rounded_rectangle((74, 710, 1006, 800), radius=22, fill=(246, 247, 250, 255), outline=(255, 204, 96, 255), width=4)
    draw_centered_line(d, URL, 735, FONT_URL, (18, 22, 32, 255))

    d.rounded_rectangle((205, 875, 875, 1545), radius=30, fill=(246, 247, 250, 255), outline=(255, 204, 96, 255), width=5)
    qr = base.fit_image(base.QR, 590, 590)
    paste_alpha(frame, qr, ((WIDTH - qr.width) // 2, 915), 1)
    draw_centered_line(d, "QRコード", 1485, base.load_font(30, True), (18, 22, 32, 255))

    draw_centered_line(d, "概要欄にもURLがあります！", 1650, FONT_FOOTER, (230, 238, 255, 245), 2, (0, 0, 0, 220))
    return frame


def render_frame(t: float) -> np.ndarray:
    if t < 10:
        frame = vertical_intro(t)
    elif t >= 75:
        frame = vertical_ending()
    else:
        src = Image.fromarray(base.render_frame(t)).convert("RGBA")
        if t < 16:
            frame = vertical_title(t, src)
        elif 17 <= t < 65:
            frame = split_battle_and_text(src)
        elif 65 <= t < 75:
            frame = vertical_chat(src)
        else:
            frame = vertical_cover(src)

    return np.array(frame.convert("RGB"))


def set_audio(video: VideoClip, audio):
    return video.with_audio(audio) if hasattr(video, "with_audio") else video.set_audio(audio)


def main() -> None:
    clip = VideoClip(render_frame, duration=DURATION)
    audio, extra_clips = base.build_audio()
    if audio:
        clip = set_audio(clip, audio)
    clip.write_videofile(str(OUTPUT_PATH), fps=FPS, codec="libx264", audio_codec="aac" if audio else None, preset="ultrafast", threads=4)
    clip.close()
    if audio:
        audio.close()
    for c in extra_clips:
        c.close()
    print(f"動画を出力しました: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
