from __future__ import annotations

from math import pi, sin
from pathlib import Path
from random import Random

from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageSequence


ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
BRAIN_DIR = ASSETS_DIR / "brain-candidates"

DIVIDER_WIDTH = 1200
DIVIDER_HEIGHT = 72
DIVIDER_FRAMES = 16

COLORS = {
    "bg_top": (7, 15, 26),
    "bg_bottom": (11, 27, 41),
    "panel_top": (9, 18, 30),
    "panel_bottom": (13, 31, 47),
    "line": (24, 63, 86),
    "cyan": (110, 231, 249),
    "teal": (88, 199, 177),
}


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
    glow_radius: int = 6,
    glow_alpha: int = 90,
    core_alpha: int = 210,
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
    radius: int = 16,
    glow_radius: int = 7,
    glow_alpha: int = 70,
    core_alpha: int = 150,
    fill: tuple[int, int, int, int] | None = None,
) -> None:
    glow = Image.new("RGBA", base.size, (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    glow_draw.rounded_rectangle(bbox, radius=radius, outline=rgba(color, glow_alpha), width=width + 4, fill=fill)
    glow = glow.filter(ImageFilter.GaussianBlur(glow_radius))
    base.alpha_composite(glow)
    ImageDraw.Draw(base).rounded_rectangle(bbox, radius=radius, outline=rgba(color, core_alpha), width=width, fill=fill)


def add_grid(base: Image.Image, spacing: int, x_shift: float = 0.0) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = base.size
    x_offset = int(x_shift % spacing)
    for x in range(-spacing + x_offset, width + spacing, spacing):
        draw.line([(x, 0), (x, height)], fill=rgba(COLORS["line"], 32), width=1)
    for y in range(0, height + spacing, spacing):
        draw.line([(0, y), (width, y)], fill=rgba(COLORS["line"], 22), width=1)
    base.alpha_composite(overlay)


def add_scanlines(base: Image.Image, *, opacity: int = 10, step: int = 4) -> None:
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    width, height = base.size
    for y in range(0, height, step):
        draw.line([(0, y), (width, y)], fill=(255, 255, 255, opacity), width=1)
    base.alpha_composite(overlay)


def add_noise(base: Image.Image, *, seed: int, count: int, opacity: int = 22) -> None:
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


def sample_frames(path: Path, *, step: int = 1, max_frames: int | None = None) -> list[Image.Image]:
    frames: list[Image.Image] = []
    with Image.open(path) as image:
        for index, frame in enumerate(ImageSequence.Iterator(image)):
            if index % step != 0:
                continue
            frames.append(frame.convert("RGBA"))
            if max_frames is not None and len(frames) >= max_frames:
                break
    if not frames:
        raise ValueError(f"No frames decoded from {path}")
    return frames


def rotate_frames(frames: list[Image.Image], start_index: int) -> list[Image.Image]:
    if not frames:
        return frames
    offset = start_index % len(frames)
    return frames[offset:] + frames[:offset]


def render_panel_frame(
    source_frame: Image.Image,
    *,
    frame_index: int,
    total_frames: int,
    canvas_size: tuple[int, int],
    content_size: tuple[int, int],
    border_color: tuple[int, int, int],
) -> Image.Image:
    width, height = canvas_size
    phase = frame_index / max(total_frames, 1)

    panel = vertical_gradient(width, height, COLORS["panel_top"], COLORS["panel_bottom"])
    add_grid(panel, 28, x_shift=phase * 8)
    draw_glow_rect(
        panel,
        (10, 10, width - 10, height - 10),
        border_color,
        width=2,
        radius=18,
        glow_alpha=44,
        core_alpha=114,
        fill=rgba(COLORS["bg_top"], 38),
    )

    thumb = ImageOps.contain(source_frame, content_size)
    layer = Image.new("RGBA", panel.size, (0, 0, 0, 0))
    x = (width - thumb.width) // 2
    y = (height - thumb.height) // 2
    layer.paste(thumb, (x, y), thumb)
    panel.alpha_composite(layer)

    draw_glow_rect(
        panel,
        (24, 24, width - 24, height - 24),
        COLORS["line"],
        width=1,
        radius=14,
        glow_radius=4,
        glow_alpha=10,
        core_alpha=84,
    )
    add_scanlines(panel)
    add_noise(panel, seed=frame_index * 19 + 7, count=110)
    return panel


def build_panel_gif(
    source_path: Path,
    destination: Path,
    *,
    frame_step: int,
    max_frames: int | None,
    canvas_size: tuple[int, int],
    content_size: tuple[int, int],
    border_color: tuple[int, int, int],
    duration_ms: int,
    start_offset: int = 0,
) -> None:
    frames = sample_frames(source_path, step=frame_step, max_frames=max_frames)
    frames = rotate_frames(frames, start_offset)
    rendered = [
        render_panel_frame(
            frame,
            frame_index=index,
            total_frames=len(frames),
            canvas_size=canvas_size,
            content_size=content_size,
            border_color=border_color,
        )
        for index, frame in enumerate(frames)
    ]
    save_gif(destination, rendered, duration_ms)


def render_divider_frame(frame_index: int) -> Image.Image:
    phase = frame_index / DIVIDER_FRAMES
    image = vertical_gradient(DIVIDER_WIDTH, DIVIDER_HEIGHT, COLORS["bg_top"], COLORS["bg_bottom"])
    add_grid(image, 34, x_shift=phase * 10)

    points = []
    for x in range(0, DIVIDER_WIDTH + 8, 8):
        y = DIVIDER_HEIGHT / 2 + sin((x / 44.0) - phase * 2 * pi * 1.7) * 7 + sin((x / 13.0) + phase * 2 * pi * 2.8) * 2.2
        points.append((x, y))
    draw_glow_line(image, points, COLORS["cyan"], width=2, glow_radius=4, glow_alpha=84, core_alpha=210)

    pulse_x = int(40 + (DIVIDER_WIDTH - 80) * phase)
    pulse_overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    pulse_draw = ImageDraw.Draw(pulse_overlay)
    pulse_draw.ellipse((pulse_x - 10, 26, pulse_x + 10, 46), outline=rgba(COLORS["teal"], 180), width=2)
    pulse_overlay = pulse_overlay.filter(ImageFilter.GaussianBlur(2))
    image.alpha_composite(pulse_overlay)
    ImageDraw.Draw(image).line((0, DIVIDER_HEIGHT / 2, DIVIDER_WIDTH, DIVIDER_HEIGHT / 2), fill=rgba(COLORS["line"], 80), width=1)

    add_scanlines(image, opacity=8)
    add_noise(image, seed=frame_index * 23 + 3, count=220, opacity=20)
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

    build_panel_gif(
        BRAIN_DIR / "Head-mri-animation.gif",
        ASSETS_DIR / "head-mri-panel.gif",
        frame_step=2,
        max_frames=72,
        canvas_size=(560, 320),
        content_size=(500, 252),
        border_color=COLORS["cyan"],
        duration_ms=95,
        start_offset=40,
    )
    build_panel_gif(
        BRAIN_DIR / "Brainanim-FreeSurfer.gif",
        ASSETS_DIR / "freesurfer-panel.gif",
        frame_step=1,
        max_frames=None,
        canvas_size=(420, 300),
        content_size=(360, 240),
        border_color=COLORS["teal"],
        duration_ms=110,
    )

    divider_frames = [render_divider_frame(index) for index in range(DIVIDER_FRAMES)]
    save_gif(ASSETS_DIR / "signal-divider.gif", divider_frames, 80)


if __name__ == "__main__":
    build()
