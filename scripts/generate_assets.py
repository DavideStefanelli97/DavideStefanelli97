from __future__ import annotations

from collections import defaultdict
from math import exp, pi, sin
from pathlib import Path
from random import Random

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageOps, ImageSequence


ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
BRAIN_DIR = ASSETS_DIR / "brain-candidates"

DIVIDER_WIDTH = 1200
DIVIDER_HEIGHT = 72
DIVIDER_FRAMES = 16
DIVIDER_EEG_LOOP_WIDTH = 1800
DIVIDER_EEG_STEP = 3

COLORS = {
    "bg_top": (7, 15, 26),
    "bg_bottom": (11, 27, 41),
    "panel_top": (9, 18, 30),
    "panel_bottom": (13, 31, 47),
    "line": (24, 63, 86),
    "cyan": (110, 231, 249),
    "teal": (88, 199, 177),
}

BITMAP_FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01111", "10000", "10000", "10000", "10000", "10000", "01111"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01111", "10000", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("11111", "00100", "00100", "00100", "00100", "00100", "11111"),
    "J": ("00111", "00010", "00010", "00010", "10010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "a": ("00000", "00000", "01110", "00001", "01111", "10001", "01111"),
    "d": ("00001", "00001", "01111", "10001", "10001", "10001", "01111"),
    "e": ("00000", "00000", "01110", "10001", "11111", "10000", "01110"),
    "f": ("00110", "01001", "01000", "11100", "01000", "01000", "01000"),
    "i": ("00100", "00000", "01100", "00100", "00100", "00100", "01110"),
    "l": ("01100", "00100", "00100", "00100", "00100", "00100", "01110"),
    "n": ("00000", "00000", "11110", "10001", "10001", "10001", "10001"),
    "t": ("00100", "00100", "11111", "00100", "00100", "00101", "00010"),
    "v": ("00000", "00000", "10001", "10001", "10001", "01010", "00100"),
    " ": ("000", "000", "000", "000", "000", "000", "000"),
}


def format_svg_number(value: float) -> str:
    rounded = round(value, 2)
    if abs(rounded - int(rounded)) < 0.01:
        return str(int(rounded))
    return f"{rounded:.2f}".rstrip("0").rstrip(".")


def hex_color(color: tuple[int, int, int]) -> str:
    return f"#{color[0]:02X}{color[1]:02X}{color[2]:02X}"


def points_to_path(points: list[tuple[float, float]]) -> str:
    if not points:
        raise ValueError("Cannot build a path without points")
    start_x, start_y = points[0]
    segments = [f"M{format_svg_number(start_x)} {format_svg_number(start_y)}"]
    segments.extend(f"L{format_svg_number(x)} {format_svg_number(y)}" for x, y in points[1:])
    return " ".join(segments)


def mirror_points(points: list[tuple[float, float]], width: float) -> list[tuple[float, float]]:
    return [(width - x, y) for x, y in points]


def bitmap_text_columns(text: str, *, gap: int = 1) -> int:
    total = 0
    for index, char in enumerate(text):
        if char not in BITMAP_FONT:
            raise ValueError(f"Unsupported bitmap glyph: {char!r}")
        total += len(BITMAP_FONT[char][0])
        if index < len(text) - 1:
            total += gap
    return total


def build_bitmap_pixels(
    text: str,
    *,
    origin_x: int,
    origin_y: int,
    cell: int,
    gap: int = 1,
) -> tuple[list[tuple[int, int, int]], int, int]:
    pixels: list[tuple[int, int, int]] = []
    cursor = 0
    for index, char in enumerate(text):
        glyph = BITMAP_FONT[char]
        glyph_width = len(glyph[0])
        for row_index, row in enumerate(glyph):
            for col_index, bit in enumerate(row):
                if bit != "1":
                    continue
                global_column = cursor + col_index
                pixels.append((origin_x + global_column * cell, origin_y + row_index * cell, global_column))
        cursor += glyph_width
        if index < len(text) - 1:
            cursor += gap
    return pixels, cursor, len(next(iter(BITMAP_FONT.values()))) * cell


def pixel_rect_markup(x: int, y: int, *, cell: int, inset: float) -> str:
    size = cell - inset * 2
    radius = max(size * 0.18, 1.2)
    return (
        f'<rect x="{format_svg_number(x + inset)}" y="{format_svg_number(y + inset)}" '
        f'width="{format_svg_number(size)}" height="{format_svg_number(size)}" '
        f'rx="{format_svg_number(radius)}"/>'
    )


def build_bitmap_group_markup(pixels: list[tuple[int, int, int]], *, cell: int, inset: float) -> str:
    return "".join(pixel_rect_markup(x, y, cell=cell, inset=inset) for x, y, _ in pixels)


def build_ignition_groups_markup(
    pixels: list[tuple[int, int, int]],
    *,
    cell: int,
    inset: float,
    total_columns: int,
) -> str:
    columns: dict[int, list[str]] = defaultdict(list)
    for x, y, column in pixels:
        columns[column].append(pixel_rect_markup(x, y, cell=cell, inset=inset))

    groups = []
    for column in sorted(columns):
        delay = (column / max(total_columns - 1, 1)) * 1.05
        groups.append(
            f'<g class="ignite" style="animation-delay:{delay:.3f}s">{"".join(columns[column])}</g>'
        )
    return "".join(groups)


def build_noise_track(sample_count: int, *, rng: Random, anchor_step: int, amplitude: float) -> list[float]:
    anchor_count = (sample_count - 1) // anchor_step + 3
    anchors = [rng.uniform(-1.0, 1.0) for _ in range(anchor_count)]
    values: list[float] = []
    for index in range(sample_count):
        anchor_index = index // anchor_step
        blend = (index % anchor_step) / anchor_step
        smooth = blend * blend * (3.0 - 2.0 * blend)
        left = anchors[anchor_index]
        right = anchors[anchor_index + 1]
        values.append(((1.0 - smooth) * left + smooth * right) * amplitude)
    return values


def inject_mixed_waking_transients(series: list[float], *, seed: int) -> None:
    rng = Random(seed)
    zones = (
        (0.08, 0.11),
        (0.2, 0.27),
        (0.38, 0.44),
        (0.56, 0.63),
        (0.74, 0.81),
        (0.87, 0.92),
    )
    last_index = len(series) - 1
    for low, high in zones:
        center = int(rng.uniform(low, high) * last_index)
        polarity = 1.0 if rng.random() > 0.34 else -1.0
        sharp_amp = rng.uniform(8.8, 12.8)
        lead_amp = sharp_amp * rng.uniform(0.12, 0.2)
        slow_amp = sharp_amp * rng.uniform(0.34, 0.46)
        settle_amp = sharp_amp * rng.uniform(0.12, 0.22)
        ripple_amp = sharp_amp * rng.uniform(0.08, 0.14)
        for index in range(max(0, center - 34), min(len(series), center + 56)):
            dx = index - center
            series[index] -= polarity * lead_amp * exp(-((dx + 8.5) / 5.8) ** 2)
            series[index] += polarity * sharp_amp * exp(-(dx / 1.75) ** 2)
            series[index] -= polarity * slow_amp * exp(-((dx - 5.5) / 4.2) ** 2)
            series[index] += polarity * settle_amp * exp(-((dx - 16.0) / 7.0) ** 2)
            series[index] += polarity * ripple_amp * exp(-((dx - 6.5) / 12.5) ** 2) * sin((dx - 6.5) * 0.9)


def build_eeg_series(sample_count: int, *, seed: int) -> list[float]:
    rng = Random(seed)
    phases = [rng.random() * 2 * pi for _ in range(10)]
    slow_noise = build_noise_track(sample_count, rng=rng, anchor_step=44, amplitude=0.62)
    contour_noise = build_noise_track(sample_count, rng=rng, anchor_step=15, amplitude=0.34)
    micro_noise = build_noise_track(sample_count, rng=rng, anchor_step=6, amplitude=0.14)
    series: list[float] = []
    last_index = max(sample_count - 1, 1)
    for index in range(sample_count):
        t = index / last_index
        drift = 0.82 * sin(2 * pi * 1.2 * t + phases[0])
        drift += 0.46 * sin(2 * pi * 2.6 * t + phases[1])
        drift += 0.2 * slow_noise[index]

        alpha_envelope = 0.76 + 0.24 * sin(2 * pi * 1.6 * t + phases[2])
        alpha_envelope += 0.12 * sin(2 * pi * 3.8 * t + phases[3])
        alpha_envelope += 0.08 * slow_noise[index]
        alpha = alpha_envelope * 1.95 * sin(2 * pi * 18.5 * t + phases[4] + contour_noise[index] * 0.75)

        beta_envelope = 0.34 + 0.14 * sin(2 * pi * 2.9 * t + phases[5])
        beta = beta_envelope * 1.18 * sin(2 * pi * 34.0 * t + phases[6] + contour_noise[index] * 1.05)

        texture = 0.38 * sin(2 * pi * 51.0 * t + phases[7] + micro_noise[index] * 1.8)
        texture += 0.22 * sin(2 * pi * 63.0 * t + phases[8])
        texture += micro_noise[index]

        series.append(drift + alpha + beta + texture + contour_noise[index] * 0.55)

    burst_specs = (
        (0.15, 20.0, 1.35, 0.9),
        (0.43, 24.0, 1.18, 0.72),
        (0.69, 18.0, 1.08, 0.84),
        (0.83, 15.0, 0.94, 0.94),
    )
    for center_ratio, width, amplitude, frequency in burst_specs:
        center = center_ratio * last_index
        for index in range(sample_count):
            dx = index - center
            envelope = exp(-((dx / width) ** 2))
            phase = (dx / width) * 2 * pi * frequency
            series[index] += envelope * amplitude * sin(phase)

    inject_mixed_waking_transients(series, seed=seed + 17)

    mean = sum(series) / len(series)
    centered = [value - mean for value in series]
    peak = max(abs(value) for value in centered) or 1.0
    scale = 18.8 / peak
    return [value * scale for value in centered]


def series_to_path(series: list[float], *, x_start: float, x_step: float, baseline: float) -> str:
    points = [(x_start + index * x_step, baseline - value) for index, value in enumerate(series)]
    return points_to_path(points)


def build_nameplate_svg(destination: Path) -> None:
    # Keep the full asset build aligned with the standalone banner generator.
    if __package__:
        from .generate_nameplate import build_nameplate_svg as generate
    else:
        from generate_nameplate import build_nameplate_svg as generate

    generate(destination)


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


def draw_masked_glow_line(
    base: Image.Image,
    points: list[tuple[float, float]],
    color: tuple[int, int, int],
    mask: Image.Image,
    *,
    width: int = 2,
    glow_radius: int = 6,
    glow_alpha: int = 90,
    core_alpha: int = 210,
) -> None:
    layer = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw_glow_line(
        layer,
        points,
        color,
        width=width,
        glow_radius=glow_radius,
        glow_alpha=glow_alpha,
        core_alpha=core_alpha,
    )
    layer.putalpha(ImageChops.multiply(layer.getchannel("A"), mask))
    base.alpha_composite(layer)


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


def close_eeg_loop(series: list[float]) -> list[float]:
    if len(series) < 2:
        return series
    drift = series[-1] - series[0]
    last_index = len(series) - 1
    looped = [value - drift * (index / last_index) for index, value in enumerate(series)]
    looped[-1] = looped[0]
    return looped


def sample_looped_eeg(series: list[float], sample_position: float) -> float:
    period = len(series) - 1
    base_index = int(sample_position) % period
    blend = sample_position - int(sample_position)
    next_index = (base_index + 1) % period
    return series[base_index] * (1.0 - blend) + series[next_index] * blend


def build_divider_eeg_points(
    frame_index: int,
    *,
    seed: int,
    amplitude_scale: float = 0.92,
    y_offset: float = 0.0,
) -> list[tuple[float, float]]:
    sample_count = DIVIDER_EEG_LOOP_WIDTH // DIVIDER_EEG_STEP + 1
    series = close_eeg_loop(build_eeg_series(sample_count, seed=seed))
    phase = (frame_index % DIVIDER_FRAMES) / DIVIDER_FRAMES
    stream_offset = phase * DIVIDER_EEG_LOOP_WIDTH
    baseline = DIVIDER_HEIGHT / 2 + y_offset
    points: list[tuple[float, float]] = []
    for x in range(0, DIVIDER_WIDTH + DIVIDER_EEG_STEP, DIVIDER_EEG_STEP):
        sample_position = ((x + stream_offset) % DIVIDER_EEG_LOOP_WIDTH) / DIVIDER_EEG_STEP
        value = sample_looped_eeg(series, sample_position)
        points.append((x, baseline - value * amplitude_scale))
    return points


def build_beam_mask(center_x: float, *, beam_width: int, max_alpha: int) -> Image.Image:
    mask = Image.new("L", (DIVIDER_WIDTH, DIVIDER_HEIGHT), 0)
    draw = ImageDraw.Draw(mask)
    half_width = beam_width / 2
    left = max(0, int(center_x - half_width) - 2)
    right = min(DIVIDER_WIDTH, int(center_x + half_width) + 3)
    for x in range(left, right):
        distance = abs(x - center_x) / half_width
        if distance <= 1.0:
            strength = int(max_alpha * (1.0 - distance) ** 2)
            draw.line((x, 6, x, DIVIDER_HEIGHT - 6), fill=strength, width=1)
    return mask.filter(ImageFilter.GaussianBlur(3))


def draw_signal_beam(base: Image.Image, mask: Image.Image) -> None:
    cyan_layer = Image.new("RGBA", base.size, rgba(COLORS["cyan"], 0))
    cyan_layer.putalpha(mask.point(lambda value: int(value * 0.42)))
    base.alpha_composite(cyan_layer)

    hot_layer = Image.new("RGBA", base.size, (255, 255, 255, 0))
    hot_layer.putalpha(mask.point(lambda value: int(value * 0.18)))
    base.alpha_composite(hot_layer)


def render_hero_eeg_divider_frame(
    frame_index: int,
    *,
    seed: int,
    accent_color: tuple[int, int, int] = COLORS["cyan"],
) -> Image.Image:
    phase = (frame_index % DIVIDER_FRAMES) / DIVIDER_FRAMES
    image = vertical_gradient(DIVIDER_WIDTH, DIVIDER_HEIGHT, COLORS["bg_top"], COLORS["bg_bottom"])
    add_grid(image, 30, x_shift=phase * 22)

    draw = ImageDraw.Draw(image)
    baseline = DIVIDER_HEIGHT / 2
    draw.line((0, baseline, DIVIDER_WIDTH, baseline), fill=rgba(COLORS["line"], 78), width=1)
    draw.line((0, 10, DIVIDER_WIDTH, 10), fill=rgba(COLORS["line"], 34), width=1)
    draw.line((0, DIVIDER_HEIGHT - 10, DIVIDER_WIDTH, DIVIDER_HEIGHT - 10), fill=rgba(COLORS["line"], 34), width=1)

    trail_points = build_divider_eeg_points(frame_index - 1, seed=seed, amplitude_scale=0.78)
    draw_glow_line(image, trail_points, COLORS["teal"], width=1, glow_radius=5, glow_alpha=34, core_alpha=74)

    points = build_divider_eeg_points(frame_index, seed=seed, amplitude_scale=0.94)
    draw_glow_line(image, points, accent_color, width=2, glow_radius=7, glow_alpha=118, core_alpha=236)
    ImageDraw.Draw(image).line(points, fill=(221, 247, 255, 236), width=1)

    beam_center = -120 + (DIVIDER_WIDTH + 240) * phase
    beam_mask = build_beam_mask(beam_center, beam_width=218, max_alpha=235)
    draw_signal_beam(image, beam_mask)
    draw_masked_glow_line(
        image,
        points,
        (255, 255, 255),
        beam_mask,
        width=3,
        glow_radius=7,
        glow_alpha=170,
        core_alpha=248,
    )

    add_scanlines(image, opacity=9)
    add_noise(image, seed=frame_index * 41 + seed, count=220, opacity=18)
    return image


def render_divider_frame(frame_index: int) -> Image.Image:
    return render_hero_eeg_divider_frame(frame_index, seed=211, accent_color=COLORS["cyan"])


def render_eeg_alpha_divider_frame(frame_index: int) -> Image.Image:
    return render_hero_eeg_divider_frame(frame_index, seed=263, accent_color=COLORS["cyan"])


def render_eeg_clinical_divider_frame(frame_index: int) -> Image.Image:
    return render_hero_eeg_divider_frame(frame_index, seed=307, accent_color=COLORS["teal"])


def render_eeg_evoked_divider_frame(frame_index: int) -> Image.Image:
    return render_hero_eeg_divider_frame(frame_index, seed=359, accent_color=COLORS["cyan"])


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

    build_nameplate_svg(ASSETS_DIR / "profile-nameplate.svg")

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
    eeg_alpha_frames = [render_eeg_alpha_divider_frame(index) for index in range(DIVIDER_FRAMES)]
    save_gif(ASSETS_DIR / "signal-divider-eeg-alpha.gif", eeg_alpha_frames, 80)
    eeg_clinical_frames = [render_eeg_clinical_divider_frame(index) for index in range(DIVIDER_FRAMES)]
    save_gif(ASSETS_DIR / "signal-divider-eeg-clinical.gif", eeg_clinical_frames, 85)
    eeg_evoked_frames = [render_eeg_evoked_divider_frame(index) for index in range(DIVIDER_FRAMES)]
    save_gif(ASSETS_DIR / "signal-divider-eeg-evoked.gif", eeg_evoked_frames, 85)


if __name__ == "__main__":
    build()
