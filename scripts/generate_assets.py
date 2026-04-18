from __future__ import annotations

from math import cos, pi, sin
from pathlib import Path
from random import Random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"

WIDTH = 1200
HERO_HEIGHT = 340
DIVIDER_HEIGHT = 72
HERO_FRAMES = 18
DIVIDER_FRAMES = 16

COLORS = {
    "bg_top": (8, 16, 28),
    "bg_bottom": (12, 32, 48),
    "panel": (14, 29, 43),
    "panel_alt": (16, 38, 56),
    "line": (24, 63, 86),
    "cyan": (110, 231, 249),
    "teal": (88, 199, 177),
    "teal_soft": (148, 230, 216),
    "text": (213, 231, 244),
    "muted": (122, 160, 184),
}


def load_font(size: int, *, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/consolab.ttf" if bold else "C:/Windows/Fonts/consola.ttf",
        "C:/Windows/Fonts/segoeuib.ttf" if bold else "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arialbd.ttf" if bold else "C:/Windows/Fonts/arial.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


FONT_TITLE = load_font(38, bold=True)
FONT_PANEL = load_font(18, bold=True)
FONT_SMALL = load_font(15)
FONT_TINY = load_font(13)


def rgba(color: tuple[int, int, int], alpha: int) -> tuple[int, int, int, int]:
    return color + (alpha,)


def vertical_gradient(width: int, height: int, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> Image.Image:
    image = Image.new("RGBA", (width, height))
    pixels = image.load()
    for y in range(height):
        t = y / max(height - 1, 1)
        color = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(width):
            pixels[x, y] = color + (255,)
    return image


def draw_glow_line(
    base: Image.Image,
    points: list[tuple[float, float]],
    color: tuple[int, int, int],
    *,
    width: int = 2,
    glow_radius: int = 7,
    glow_alpha: int = 110,
    core_alpha: int = 220,
) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.line(points, fill=rgba(color, glow_alpha), width=width + 4)
    glow = glow.filter(ImageFilter.GaussianBlur(glow_radius))
    base.alpha_composite(glow)
    ImageDraw.Draw(base).line(points, fill=rgba(color, core_alpha), width=width)


def draw_glow_rect(
    base: Image.Image,
    bbox: tuple[int, int, int, int],
    color: tuple[int, int, int],
    *,
    width: int = 2,
    radius: int = 18,
    glow_radius: int = 8,
    glow_alpha: int = 90,
    core_alpha: int = 170,
    fill: tuple[int, int, int, int] | None = None,
) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle(bbox, radius=radius, outline=rgba(color, glow_alpha), width=width + 4, fill=fill)
    glow = glow.filter(ImageFilter.GaussianBlur(glow_radius))
    base.alpha_composite(glow)
    ImageDraw.Draw(base).rounded_rectangle(bbox, radius=radius, outline=rgba(color, core_alpha), width=width, fill=fill)


def draw_glow_circle(
    base: Image.Image,
    bbox: tuple[int, int, int, int],
    color: tuple[int, int, int],
    *,
    width: int = 2,
    glow_radius: int = 10,
    glow_alpha: int = 90,
    core_alpha: int = 180,
) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.ellipse(bbox, outline=rgba(color, glow_alpha), width=width + 3)
    glow = glow.filter(ImageFilter.GaussianBlur(glow_radius))
    base.alpha_composite(glow)
    ImageDraw.Draw(base).ellipse(bbox, outline=rgba(color, core_alpha), width=width)


def add_grid(base: Image.Image, spacing: int, x_shift: float = 0.0) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = base.size
    x_offset = int(x_shift % spacing)
    for x in range(-spacing + x_offset, width + spacing, spacing):
        draw.line([(x, 0), (x, height)], fill=rgba(COLORS["line"], 42), width=1)
    for y in range(0, height + spacing, spacing):
        draw.line([(0, y), (width, y)], fill=rgba(COLORS["line"], 30), width=1)
    base.alpha_composite(overlay)


def add_scanlines(base: Image.Image, step: int = 4, opacity: int = 13) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = base.size
    for y in range(0, height, step):
        draw.line([(0, y), (width, y)], fill=(255, 255, 255, opacity), width=1)
    base.alpha_composite(overlay)


def add_noise(base: Image.Image, seed: int, count: int, opacity: int = 36) -> None:
    rng = Random(seed)
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    pixels = overlay.load()
    width, height = base.size
    for _ in range(count):
        x = rng.randrange(width)
        y = rng.randrange(height)
        tone = COLORS["cyan"] if rng.random() > 0.55 else COLORS["teal"]
        pixels[x, y] = tone + (opacity,)
    overlay = overlay.filter(ImageFilter.GaussianBlur(0.2))
    base.alpha_composite(overlay)


def waveform_points(start_x: int, width: int, baseline: int, amplitude: float, phase: float, *, step: int = 10) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    for x in range(start_x, start_x + width + step, step):
        offset = x - start_x
        signal = sin((offset / 58.0) + phase) + 0.38 * sin((offset / 17.0) - phase * 1.6)
        y = baseline + signal * amplitude
        points.append((x, y))
    return points


def draw_trace_panel(base: Image.Image, x: int, y: int, width: int, height: int, label: str, points: list[tuple[float, float]]) -> None:
    fill = rgba(COLORS["panel"], 104)
    draw_glow_rect(base, (x, y, x + width, y + height), COLORS["cyan"], width=1, radius=16, glow_alpha=64, core_alpha=120, fill=fill)
    ImageDraw.Draw(base).text((x + 16, y + 12), label, font=FONT_TINY, fill=rgba(COLORS["text"], 170))
    draw_glow_line(base, points, COLORS["cyan"], width=2, glow_radius=5, glow_alpha=80, core_alpha=210)


def draw_imaging_tiles(base: Image.Image, frame_index: int) -> None:
    draw = ImageDraw.Draw(base)
    phase = frame_index / HERO_FRAMES
    tile_boxes = [
        (794, 90, 930, 176),
        (948, 90, 1084, 176),
        (794, 194, 930, 280),
        (948, 194, 1084, 280),
    ]
    for idx, box in enumerate(tile_boxes):
        x1, y1, x2, y2 = box
        fill = rgba(COLORS["panel_alt"], 136)
        draw_glow_rect(base, box, COLORS["teal"], width=1, radius=14, glow_alpha=55, core_alpha=110, fill=fill)
        inner = Image.new("RGBA", base.size, (0, 0, 0, 0))
        inner_draw = ImageDraw.Draw(inner)
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2
        rx = 34 + idx * 2
        ry = 20 + idx
        offset = sin((phase * 2 * pi) + idx * 0.8) * 6
        inner_draw.ellipse((cx - rx, cy - ry + offset, cx + rx, cy + ry + offset), outline=rgba(COLORS["cyan"], 145), width=2)
        inner_draw.ellipse((cx - rx / 2, cy - ry / 2 + offset, cx + rx / 2, cy + ry / 2 + offset), outline=rgba(COLORS["teal"], 170), width=2)
        inner = inner.filter(ImageFilter.GaussianBlur(1.4))
        base.alpha_composite(inner)
        draw.line((x1 + 12, y2 - 16, x2 - 12, y2 - 16), fill=rgba(COLORS["line"], 120), width=2)


def draw_circuit_mesh(base: Image.Image, frame_index: int) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    phase = frame_index / HERO_FRAMES
    segments = [
        [(706, 72), (760, 72), (760, 128), (808, 128)],
        [(706, 268), (760, 268), (760, 222), (808, 222)],
        [(1098, 132), (1148, 132), (1148, 208), (1098, 208)],
        [(436, 110), (512, 110), (512, 78), (618, 78)],
        [(436, 232), (512, 232), (512, 266), (618, 266)],
    ]
    for segment in segments:
        draw_glow_line(overlay, segment, COLORS["teal"], width=2, glow_radius=5, glow_alpha=70, core_alpha=145)
    for idx, (cx, cy) in enumerate(((760, 72), (760, 268), (1148, 132), (1148, 208), (512, 110), (512, 232))):
        pulse = 4 + 2 * sin((phase * 2 * pi * 2.0) + idx)
        draw.ellipse((cx - pulse, cy - pulse, cx + pulse, cy + pulse), fill=rgba(COLORS["cyan"] if idx % 2 == 0 else COLORS["teal"], 210))
    draw = None
    base.alpha_composite(overlay.filter(ImageFilter.GaussianBlur(0.8)))
    base.alpha_composite(overlay)


def render_hero_frame(frame_index: int) -> Image.Image:
    phase = frame_index / HERO_FRAMES
    image = vertical_gradient(WIDTH, HERO_HEIGHT, COLORS["bg_top"], COLORS["bg_bottom"])
    add_grid(image, 40, x_shift=phase * 16)

    scan = Image.new("RGBA", image.size, (0, 0, 0, 0))
    scan_draw = ImageDraw.Draw(scan)
    scan_x = int(126 + (WIDTH - 252) * phase)
    scan_draw.rectangle((scan_x - 22, 0, scan_x + 22, HERO_HEIGHT), fill=rgba(COLORS["cyan"], 10))
    scan_draw.rectangle((scan_x - 6, 0, scan_x + 6, HERO_HEIGHT), fill=rgba(COLORS["teal"], 20))
    image.alpha_composite(scan)

    draw_glow_rect(image, (52, 46, 646, 296), COLORS["cyan"], width=2, radius=22, glow_alpha=70, core_alpha=125, fill=rgba(COLORS["panel"], 112))
    draw_glow_rect(image, (680, 46, 1148, 296), COLORS["teal"], width=2, radius=22, glow_alpha=60, core_alpha=115, fill=rgba(COLORS["panel"], 92))

    ImageDraw.Draw(image).text((82, 70), "DAVIDE STEFANELLI", font=FONT_TITLE, fill=rgba(COLORS["text"], 238))
    ImageDraw.Draw(image).text(
        (84, 116),
        "AI FOR MEDICAL IMAGING  //  EEG ANALYSIS  //  REPRESENTATION LEARNING",
        font=FONT_SMALL,
        fill=rgba(COLORS["cyan"], 205),
    )
    ImageDraw.Draw(image).text(
        (84, 148),
        "Neuroscience and computer vision workflows built for clarity and reproducibility.",
        font=FONT_SMALL,
        fill=rgba(COLORS["text"], 195),
    )

    panels = [
        ("Medical Imaging", waveform_points(84, 520, 214, 12, phase * 2 * pi * 1.3)),
        ("EEG / ERP / CWT", waveform_points(84, 520, 252, 9, phase * 2 * pi * 1.9 + 0.7)),
        ("Representation Learning", waveform_points(84, 520, 290, 7, phase * 2 * pi * 2.4 + 1.4)),
    ]
    for idx, (label, points) in enumerate(panels):
        draw_trace_panel(image, 78, 184 + idx * 34, 540, 44, label, points)

    ImageDraw.Draw(image).text((708, 64), "RESEARCH DOMAINS", font=FONT_PANEL, fill=rgba(COLORS["teal_soft"], 218))
    ImageDraw.Draw(image).text((708, 95), "medical imaging  /  eeg pipelines  /  experiment tracking", font=FONT_SMALL, fill=rgba(COLORS["text"], 182))
    draw_imaging_tiles(image, frame_index)

    ring_center = (1110, 84)
    for radius in (20, 34, 48):
        draw_glow_circle(
            image,
            (ring_center[0] - radius, ring_center[1] - radius, ring_center[0] + radius, ring_center[1] + radius),
            COLORS["cyan"] if radius != 34 else COLORS["teal"],
            width=1,
            glow_radius=7,
            glow_alpha=55,
            core_alpha=95,
        )
    angle = phase * 2 * pi
    dot_x = ring_center[0] + cos(angle) * 48
    dot_y = ring_center[1] + sin(angle) * 48
    ImageDraw.Draw(image).ellipse((dot_x - 4, dot_y - 4, dot_x + 4, dot_y + 4), fill=rgba(COLORS["teal"], 220))

    ImageDraw.Draw(image).text((1018, 58), "LIVE", font=FONT_TINY, fill=rgba(COLORS["teal_soft"], 200))
    ImageDraw.Draw(image).text((1006, 104), "SIGNAL", font=FONT_TINY, fill=rgba(COLORS["muted"], 180))
    draw_circuit_mesh(image, frame_index)

    add_scanlines(image)
    add_noise(image, seed=frame_index * 17 + 5, count=900, opacity=26)
    vignette = Image.new("L", image.size, 255)
    vignette_draw = ImageDraw.Draw(vignette)
    vignette_draw.rectangle((0, 0, WIDTH, HERO_HEIGHT), fill=225)
    vignette = vignette.filter(ImageFilter.GaussianBlur(32))
    mask = Image.merge("RGBA", (vignette, vignette, vignette, vignette))
    return ImageChops.multiply(image, mask)


def render_divider_frame(frame_index: int) -> Image.Image:
    phase = frame_index / DIVIDER_FRAMES
    image = vertical_gradient(WIDTH, DIVIDER_HEIGHT, COLORS["bg_top"], COLORS["bg_bottom"])
    add_grid(image, 34, x_shift=phase * 10)

    points = []
    for x in range(0, WIDTH + 8, 8):
        y = DIVIDER_HEIGHT / 2 + sin((x / 44.0) - phase * 2 * pi * 1.7) * 7 + sin((x / 13.0) + phase * 2 * pi * 2.8) * 2.2
        points.append((x, y))
    draw_glow_line(image, points, COLORS["cyan"], width=2, glow_radius=4, glow_alpha=84, core_alpha=210)

    pulse_x = int(40 + (WIDTH - 80) * phase)
    draw_glow_circle(image, (pulse_x - 10, 26, pulse_x + 10, 46), COLORS["teal"], width=2, glow_radius=6, glow_alpha=85, core_alpha=160)
    ImageDraw.Draw(image).line((0, DIVIDER_HEIGHT / 2, WIDTH, DIVIDER_HEIGHT / 2), fill=rgba(COLORS["line"], 80), width=1)

    add_scanlines(image, opacity=10)
    add_noise(image, seed=frame_index * 23 + 3, count=240, opacity=24)
    return image


def save_gif(path: Path, frames: list[Image.Image], duration_ms: int) -> None:
    palette_frames = [frame.convert("P", palette=Image.Palette.ADAPTIVE, colors=96) for frame in frames]
    palette_frames[0].save(
        path,
        save_all=True,
        append_images=palette_frames[1:],
        loop=0,
        duration=duration_ms,
        optimize=False,
        disposal=2,
    )


def build() -> None:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    hero_frames = [render_hero_frame(i) for i in range(HERO_FRAMES)]
    divider_frames = [render_divider_frame(i) for i in range(DIVIDER_FRAMES)]
    save_gif(ASSETS_DIR / "hero-console.gif", hero_frames, 95)
    save_gif(ASSETS_DIR / "signal-divider.gif", divider_frames, 80)


if __name__ == "__main__":
    build()
