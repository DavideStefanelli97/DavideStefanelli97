from __future__ import annotations

from math import cos, pi, sin
from pathlib import Path
from random import Random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"

WIDTH = 1200
HERO_HEIGHT = 420
DIVIDER_HEIGHT = 84
HERO_FRAMES = 20
DIVIDER_FRAMES = 16

COLORS = {
    "bg0": (4, 8, 18),
    "bg1": (6, 16, 34),
    "bg2": (8, 28, 54),
    "cyan": (54, 242, 255),
    "cyan_soft": (106, 232, 255),
    "blue": (43, 120, 255),
    "green": (124, 255, 178),
    "green_soft": (154, 255, 211),
    "line": (18, 60, 102),
    "text": (200, 245, 255),
}


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/bahnschrift.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


FONT_HERO = load_font(48, bold=True)
FONT_PANEL = load_font(20, bold=True)
FONT_SMALL = load_font(16)


def vertical_gradient(width: int, height: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGBA", (width, height))
    pixels = image.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(width):
            pixels[x, y] = color + (255,)
    return image


def alpha(color: tuple[int, int, int], value: int) -> tuple[int, int, int, int]:
    return color + (value,)


def draw_glow_line(
    base: Image.Image,
    points: list[tuple[float, float]],
    color: tuple[int, int, int],
    *,
    width: int = 2,
    glow_radius: int = 9,
    glow_alpha: int = 140,
    core_alpha: int = 230,
) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.line(points, fill=alpha(color, glow_alpha), width=width + 5)
    glow = glow.filter(ImageFilter.GaussianBlur(glow_radius))
    base.alpha_composite(glow)
    crisp = ImageDraw.Draw(base)
    crisp.line(points, fill=alpha(color, core_alpha), width=width)


def draw_glow_circle(
    base: Image.Image,
    bbox: tuple[int, int, int, int],
    color: tuple[int, int, int],
    *,
    width: int = 2,
    glow_radius: int = 10,
    glow_alpha: int = 120,
    core_alpha: int = 210,
) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(bbox, outline=alpha(color, glow_alpha), width=width + 4)
    glow = glow.filter(ImageFilter.GaussianBlur(glow_radius))
    base.alpha_composite(glow)
    crisp = ImageDraw.Draw(base)
    crisp.ellipse(bbox, outline=alpha(color, core_alpha), width=width)


def draw_glow_rect(
    base: Image.Image,
    bbox: tuple[int, int, int, int],
    color: tuple[int, int, int],
    *,
    width: int = 2,
    radius: int = 18,
    glow_radius: int = 8,
    glow_alpha: int = 110,
    core_alpha: int = 200,
) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle(bbox, radius=radius, outline=alpha(color, glow_alpha), width=width + 4)
    glow = glow.filter(ImageFilter.GaussianBlur(glow_radius))
    base.alpha_composite(glow)
    crisp = ImageDraw.Draw(base)
    crisp.rounded_rectangle(bbox, radius=radius, outline=alpha(color, core_alpha), width=width)


def add_grid(base: Image.Image, spacing: int, x_shift: float = 0.0) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = base.size
    x_offset = int(x_shift % spacing)
    for x in range(-spacing + x_offset, width + spacing, spacing):
        draw.line([(x, 0), (x, height)], fill=alpha(COLORS["line"], 48), width=1)
    for y in range(0, height + spacing, spacing):
        draw.line([(0, y), (width, y)], fill=alpha(COLORS["line"], 36), width=1)
    base.alpha_composite(overlay)


def add_scanlines(base: Image.Image, step: int, opacity: int) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = base.size
    for y in range(0, height, step):
        draw.line([(0, y), (width, y)], fill=(255, 255, 255, opacity), width=1)
    base.alpha_composite(overlay)


def add_noise(base: Image.Image, seed: int, count: int, opacity: int) -> None:
    rng = Random(seed)
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    pixels = overlay.load()
    width, height = base.size
    for _ in range(count):
        x = rng.randrange(width)
        y = rng.randrange(height)
        c = COLORS["cyan"] if rng.random() > 0.72 else COLORS["green"]
        pixels[x, y] = c + (opacity,)
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.25))
    base.alpha_composite(overlay)


def render_hero_frame(frame_index: int) -> Image.Image:
    t = frame_index / HERO_FRAMES
    image = vertical_gradient(WIDTH, HERO_HEIGHT, COLORS["bg0"], COLORS["bg2"])
    add_grid(image, 42, x_shift=t * 22)

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    beam_x = int(160 + (WIDTH - 320) * t)
    draw.rectangle([(beam_x - 34, 0), (beam_x + 34, HERO_HEIGHT)], fill=alpha(COLORS["cyan"], 16))
    draw.rectangle([(beam_x - 8, 0), (beam_x + 8, HERO_HEIGHT)], fill=alpha(COLORS["green"], 28))

    pulse_radius = 40 + int(18 * sin(t * 2 * pi))
    for offset in (0, 74, 148):
        cx = 180 + offset
        cy = 220 + int(8 * sin((t * 2 * pi) + offset / 30))
        bbox = (cx - pulse_radius, cy - pulse_radius, cx + pulse_radius, cy + pulse_radius)
        draw_glow_circle(overlay, bbox, COLORS["cyan"], width=2, glow_radius=12, glow_alpha=95, core_alpha=120)

    waveform_points: list[tuple[float, float]] = []
    for x in range(0, WIDTH, 12):
        wave = sin((x / 85.0) + (t * 2 * pi * 1.8))
        ripple = 0.45 * sin((x / 28.0) - (t * 2 * pi * 3.0))
        y = 292 + (wave + ripple) * 24
        waveform_points.append((x, y))
    draw_glow_line(overlay, waveform_points, COLORS["cyan"], width=3, glow_radius=8, glow_alpha=125)

    orbit_center = (930, 175)
    for radius in (44, 76, 110):
        bbox = (
            orbit_center[0] - radius,
            orbit_center[1] - radius,
            orbit_center[0] + radius,
            orbit_center[1] + radius,
        )
        draw_glow_circle(overlay, bbox, COLORS["green"], width=1, glow_radius=6, glow_alpha=70, core_alpha=105)
    for phase, radius, color in ((0.0, 44, COLORS["cyan"]), (0.33, 76, COLORS["green"]), (0.66, 110, COLORS["cyan_soft"])):
        angle = (t + phase) * 2 * pi
        px = orbit_center[0] + cos(angle) * radius
        py = orbit_center[1] + sin(angle) * radius
        draw.ellipse([(px - 6, py - 6), (px + 6, py + 6)], fill=alpha(color, 220))

    draw_glow_rect(overlay, (56, 44, 428, 120), COLORS["cyan"], width=2, radius=22)
    draw_glow_rect(overlay, (780, 44, 1144, 120), COLORS["green"], width=2, radius=22)
    draw_glow_rect(overlay, (60, 332, 442, 390), COLORS["green"], width=1, radius=18)
    draw_glow_rect(overlay, (756, 312, 1144, 390), COLORS["cyan"], width=1, radius=18)

    image.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(1.2)))
    image.alpha_composite(overlay)

    draw = ImageDraw.Draw(image)
    draw.text((88, 61), "NEURAL INTERFACE", font=FONT_HERO, fill=alpha(COLORS["cyan"], 245))
    draw.text((90, 120), "BIOELECTRIC SIGNAL MAP // PROFILE LAYER", font=FONT_PANEL, fill=alpha(COLORS["text"], 195))

    draw.text((810, 60), "HUD STATE", font=FONT_PANEL, fill=alpha(COLORS["green"], 225))
    draw.text((810, 92), "LINK STABILITY  .  99.84%", font=FONT_SMALL, fill=alpha(COLORS["text"], 205))
    draw.text((810, 116), "SPECTRAL NOISE  .  LOW", font=FONT_SMALL, fill=alpha(COLORS["text"], 205))

    draw.text((78, 343), "SCAN BUS  /  CORTEX LAYER  /  LIVE TELEMETRY", font=FONT_SMALL, fill=alpha(COLORS["green_soft"], 205))
    draw.text((776, 324), "NODE CLUSTER", font=FONT_PANEL, fill=alpha(COLORS["cyan"], 205))
    draw.text((776, 350), "systems  intelligence  interface  deployment", font=FONT_SMALL, fill=alpha(COLORS["text"], 190))

    for i in range(9):
        vx = 768 + i * 40
        bar_h = 16 + int(18 * (0.5 + 0.5 * sin((i * 0.7) + t * 2 * pi * 2.2)))
        draw.rounded_rectangle(
            [(vx, 370 - bar_h), (vx + 14, 370)],
            radius=4,
            fill=alpha(COLORS["green"] if i % 2 else COLORS["cyan"], 170),
        )

    add_scanlines(image, 4, 18)
    add_noise(image, seed=frame_index * 13 + 7, count=900, opacity=44)
    vignette = Image.new("L", image.size, 255)
    vignette_draw = ImageDraw.Draw(vignette)
    vignette_draw.rectangle((0, 0, WIDTH, HERO_HEIGHT), fill=210)
    vignette = vignette.filter(ImageFilter.GaussianBlur(40))
    vignette_rgba = Image.merge("RGBA", (vignette, vignette, vignette, vignette))
    image = ImageChops.multiply(image, vignette_rgba)
    return image


def render_divider_frame(frame_index: int) -> Image.Image:
    t = frame_index / DIVIDER_FRAMES
    image = vertical_gradient(WIDTH, DIVIDER_HEIGHT, COLORS["bg0"], COLORS["bg1"])
    add_grid(image, 36, x_shift=t * 14)

    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    points: list[tuple[float, float]] = []
    for x in range(0, WIDTH, 8):
        y = DIVIDER_HEIGHT / 2 + sin((x / 38.0) - (t * 2 * pi * 2.0)) * 10 + sin((x / 13.0) + (t * 2 * pi * 3.4)) * 3
        points.append((x, y))
    draw_glow_line(overlay, points, COLORS["cyan"], width=2, glow_radius=5, glow_alpha=110)

    pulse_x = int((WIDTH - 120) * t) + 60
    draw.ellipse([(pulse_x - 8, DIVIDER_HEIGHT / 2 - 8), (pulse_x + 8, DIVIDER_HEIGHT / 2 + 8)], fill=alpha(COLORS["green"], 230))
    draw.rectangle([(0, DIVIDER_HEIGHT / 2 - 1), (WIDTH, DIVIDER_HEIGHT / 2 + 1)], fill=alpha(COLORS["line"], 80))
    image.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(0.8)))
    image.alpha_composite(overlay)

    draw = ImageDraw.Draw(image)
    draw.text((36, 18), "SIGNAL BUS", font=FONT_PANEL, fill=alpha(COLORS["cyan"], 220))
    draw.text((WIDTH - 290, 18), "neural spine // section transition", font=FONT_SMALL, fill=alpha(COLORS["text"], 175))

    add_scanlines(image, 4, 15)
    add_noise(image, seed=frame_index * 19 + 3, count=250, opacity=38)
    return image


def save_gif(path: Path, frames: list[Image.Image], duration_ms: int) -> None:
    quantized = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=96) for frame in frames]
    quantized[0].save(
        path,
        save_all=True,
        append_images=quantized[1:],
        loop=0,
        duration=duration_ms,
        optimize=False,
        disposal=2,
    )


def build() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    hero_frames = [render_hero_frame(index) for index in range(HERO_FRAMES)]
    divider_frames = [render_divider_frame(index) for index in range(DIVIDER_FRAMES)]
    save_gif(ASSETS_DIR / "hero-neural.gif", hero_frames, duration_ms=85)
    save_gif(ASSETS_DIR / "divider-signal.gif", divider_frames, duration_ms=75)


if __name__ == "__main__":
    build()
