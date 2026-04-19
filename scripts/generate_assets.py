from __future__ import annotations

from collections import defaultdict
from math import exp, pi, sin
from pathlib import Path
from random import Random

from PIL import Image, ImageDraw, ImageFilter, ImageOps, ImageSequence


ROOT = Path(__file__).resolve().parents[1]
ASSETS_DIR = ROOT / "assets"
BRAIN_DIR = ASSETS_DIR / "brain-candidates"

DIVIDER_WIDTH = 1200
DIVIDER_HEIGHT = 72
DIVIDER_FRAMES = 16
NAMEPLATE_WIDTH = 1200
NAMEPLATE_HEIGHT = 360
NAMEPLATE_TITLE = "Davide Stefanelli"
NAMEPLATE_TAGLINE = "From brain signals to intelligent systems"
NAMEPLATE_DESCRIPTOR = "AI / Computer Vision / Neuro-engineering / Neuro-imaging / NeuroScience"

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
    panel_x = 24
    panel_y = 20
    panel_width = NAMEPLATE_WIDTH - panel_x * 2
    panel_height = NAMEPLATE_HEIGHT - panel_y * 2
    panel_radius = 28

    cell = 10
    pixel_inset = 0.9
    total_columns = bitmap_text_columns(NAMEPLATE_TITLE, gap=1)
    title_x = (NAMEPLATE_WIDTH - total_columns * cell) // 2
    title_y = 72
    title_pixels, _, title_height = build_bitmap_pixels(
        NAMEPLATE_TITLE,
        origin_x=title_x,
        origin_y=title_y,
        cell=cell,
        gap=1,
    )
    title_width = total_columns * cell
    title_right = title_x + title_width
    title_bottom = title_y + title_height

    title_markup = build_bitmap_group_markup(title_pixels, cell=cell, inset=pixel_inset)
    ignition_markup = build_ignition_groups_markup(
        title_pixels,
        cell=cell,
        inset=pixel_inset,
        total_columns=total_columns,
    )

    signal_view_x = title_x - 34
    signal_view_y = 264
    signal_view_width = title_width + 68
    signal_view_height = 58
    signal_baseline = 30
    signal_loop_width = 1800
    signal_sample_step = 3
    signal_sample_count = signal_loop_width // signal_sample_step + 1
    eeg_series = build_eeg_series(signal_sample_count, seed=211)
    eeg_path = series_to_path(eeg_series, x_start=0, x_step=signal_sample_step, baseline=signal_baseline)
    signal_beam_width = 208

    left_trace_paths = [
        [(86, 228), (144, 228), (174, 244), (228, 244)],
        [(94, 270), (152, 270), (186, 286), (236, 286)],
    ]
    right_trace_paths = [mirror_points(path, NAMEPLATE_WIDTH) for path in left_trace_paths]

    left_nodes = [(86, 228), (174, 244), (152, 270), (186, 286)]
    right_nodes = mirror_points(left_nodes, NAMEPLATE_WIDTH)

    grid_lines = []
    for x in range(panel_x + 78, panel_x + panel_width - 20, 108):
        grid_lines.append(
            f'<line x1="{x}" y1="{panel_y + 14}" x2="{x}" y2="{panel_y + panel_height - 14}" class="grid"/>'
        )
    for y in range(panel_y + 40, panel_y + panel_height - 24, 78):
        grid_lines.append(
            f'<line x1="{panel_x + 14}" y1="{y}" x2="{panel_x + panel_width - 14}" y2="{y}" class="grid"/>'
        )

    scanlines = []
    for y in range(panel_y + 10, panel_y + panel_height - 4, 6):
        scanlines.append(
            f'<line x1="{panel_x + 6}" y1="{y}" x2="{panel_x + panel_width - 6}" y2="{y}" class="scanline"/>'
        )

    trace_paths_markup = "".join(
        f'<path d="{points_to_path(path)}" class="trace-path"/>' for path in left_trace_paths + right_trace_paths
    )
    trace_nodes_markup = "".join(
        f'<circle cx="{x}" cy="{y}" r="4.2" class="trace-node"/>' for x, y in left_nodes + right_nodes
    )

    title_shadow_y = 4
    tagline_y = 198
    descriptor_y = 236
    tagline_capsule_width = 492
    tagline_capsule_height = 36
    tagline_capsule_x = (NAMEPLATE_WIDTH - tagline_capsule_width) // 2
    tagline_capsule_y = tagline_y - 24
    descriptor_divider_y = descriptor_y + 22
    nameplate_desc = f"{NAMEPLATE_TAGLINE}. {NAMEPLATE_DESCRIPTOR}"

    svg = f"""<svg width="{NAMEPLATE_WIDTH}" height="{NAMEPLATE_HEIGHT}" viewBox="0 0 {NAMEPLATE_WIDTH} {NAMEPLATE_HEIGHT}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="hero-title hero-desc">
<title id="hero-title">{NAMEPLATE_TITLE}</title>
<desc id="hero-desc">{nameplate_desc}</desc>
<defs>
  <linearGradient id="panelBg" x1="0" y1="{panel_y}" x2="0" y2="{panel_y + panel_height}" gradientUnits="userSpaceOnUse">
    <stop stop-color="{hex_color(COLORS["bg_top"])}"/>
    <stop offset="1" stop-color="{hex_color(COLORS["bg_bottom"])}"/>
  </linearGradient>
  <linearGradient id="panelBorder" x1="{panel_x}" y1="{panel_y}" x2="{panel_x + panel_width}" y2="{panel_y + panel_height}" gradientUnits="userSpaceOnUse">
    <stop stop-color="{hex_color(COLORS["cyan"])}" stop-opacity="0.86"/>
    <stop offset="1" stop-color="{hex_color(COLORS["teal"])}" stop-opacity="0.76"/>
  </linearGradient>
  <linearGradient id="titleFill" x1="{title_x}" y1="{title_y}" x2="{title_right}" y2="{title_bottom}" gradientUnits="userSpaceOnUse">
    <stop stop-color="{hex_color(COLORS["cyan"])}"/>
    <stop offset="0.52" stop-color="#D5E7F4"/>
    <stop offset="1" stop-color="{hex_color(COLORS["teal"])}"/>
  </linearGradient>
  <linearGradient id="taglineFill" x1="{tagline_capsule_x}" y1="{tagline_capsule_y}" x2="{tagline_capsule_x + tagline_capsule_width}" y2="{tagline_capsule_y}" gradientUnits="userSpaceOnUse">
    <stop stop-color="#D5E7F4"/>
    <stop offset="1" stop-color="#A7D5E1"/>
  </linearGradient>
  <linearGradient id="scanBeamGradient" x1="0" y1="0" x2="180" y2="0" gradientUnits="userSpaceOnUse">
    <stop stop-color="#FFFFFF" stop-opacity="0"/>
    <stop offset="0.35" stop-color="{hex_color(COLORS["cyan"])}" stop-opacity="0.08"/>
    <stop offset="0.52" stop-color="#FFFFFF" stop-opacity="0.85"/>
    <stop offset="0.7" stop-color="{hex_color(COLORS["teal"])}" stop-opacity="0.12"/>
    <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
  </linearGradient>
  <filter id="titleGlow" x="-24%" y="-40%" width="148%" height="180%">
    <feGaussianBlur stdDeviation="7.5" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
  <filter id="softGlow" x="-18%" y="-30%" width="136%" height="160%">
    <feGaussianBlur stdDeviation="3.4" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
  <filter id="panelGlow" x="-6%" y="-10%" width="112%" height="130%">
    <feGaussianBlur stdDeviation="6" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>
  <g id="titlePixels">{title_markup}</g>
  <clipPath id="panelClip">
    <rect x="{panel_x}" y="{panel_y}" width="{panel_width}" height="{panel_height}" rx="{panel_radius}"/>
  </clipPath>
  <clipPath id="titleClip">
    <use href="#titlePixels"/>
  </clipPath>
  <clipPath id="glitchSliceA">
    <rect x="{title_x - 8}" y="{title_y + 10}" width="{title_width + 16}" height="16" rx="5"/>
  </clipPath>
  <clipPath id="glitchSliceB">
    <rect x="{title_x - 10}" y="{title_y + 33}" width="{title_width + 20}" height="15" rx="5"/>
  </clipPath>
  <clipPath id="glitchSliceC">
    <rect x="{title_x - 6}" y="{title_y + 54}" width="{title_width + 12}" height="15" rx="5"/>
  </clipPath>
  <clipPath id="signalClip">
    <rect x="{signal_view_x}" y="{signal_view_y}" width="{signal_view_width}" height="{signal_view_height}" rx="16"/>
  </clipPath>
  <linearGradient id="signalBeamGradient" x1="0" y1="0" x2="{signal_beam_width}" y2="0" gradientUnits="userSpaceOnUse">
    <stop stop-color="#FFFFFF" stop-opacity="0"/>
    <stop offset="0.18" stop-color="{hex_color(COLORS["cyan"])}" stop-opacity="0.14"/>
    <stop offset="0.48" stop-color="#FFFFFF" stop-opacity="0.48"/>
    <stop offset="0.72" stop-color="{hex_color(COLORS["teal"])}" stop-opacity="0.2"/>
    <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="signalFocusGradient" x1="0" y1="0" x2="{signal_beam_width}" y2="0" gradientUnits="userSpaceOnUse">
    <stop stop-color="#000000" stop-opacity="0"/>
    <stop offset="0.24" stop-color="#7F7F7F" stop-opacity="0.72"/>
    <stop offset="0.5" stop-color="#FFFFFF" stop-opacity="1"/>
    <stop offset="0.76" stop-color="#7F7F7F" stop-opacity="0.72"/>
    <stop offset="1" stop-color="#000000" stop-opacity="0"/>
  </linearGradient>
  <mask id="signalFocusMask" maskUnits="userSpaceOnUse">
    <rect x="{signal_view_x}" y="{signal_view_y}" width="{signal_view_width}" height="{signal_view_height}" fill="black"/>
    <g class="signal-sweep">
      <rect x="{signal_view_x - signal_beam_width}" y="{signal_view_y}" width="{signal_beam_width}" height="{signal_view_height}" fill="url(#signalFocusGradient)"/>
    </g>
  </mask>
  <path id="eegSegment" d="{eeg_path}"/>
</defs>
<style>
  .grid {{
    stroke: {hex_color(COLORS["line"])};
    stroke-opacity: 0.12;
    stroke-width: 1;
  }}
  .scanline {{
    stroke: #FFFFFF;
    stroke-opacity: 0.026;
    stroke-width: 1;
  }}
  .trace-path {{
    fill: none;
    stroke: url(#panelBorder);
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
    opacity: 0.46;
    filter: url(#softGlow);
  }}
  .trace-node {{
    fill: {hex_color(COLORS["cyan"])};
    opacity: 0.88;
    filter: url(#titleGlow);
    transform-origin: center;
    transform-box: fill-box;
    animation: nodePulse 2.8s ease-in-out infinite;
  }}
  .title-glow {{
    opacity: 0.58;
    animation: glowPulse 3.2s ease-in-out infinite;
  }}
  .ignite {{
    opacity: 0;
    transform-origin: center;
    transform-box: fill-box;
    animation: pixelIgnite 0.56s ease-out 1 both;
  }}
  .scan-beam {{
    animation: scanSweep 4.5s linear infinite;
  }}
  .glitch-a {{
    animation: glitchA 8s steps(1, end) infinite;
  }}
  .glitch-b {{
    animation: glitchB 8s steps(1, end) infinite;
  }}
  .glitch-c {{
    animation: glitchC 8s steps(1, end) infinite;
  }}
  .tagline {{
    font-family: Consolas, Monaco, monospace;
    font-size: 20px;
    font-weight: 700;
    letter-spacing: 0.7px;
    fill: url(#taglineFill);
    text-anchor: middle;
    animation: taglinePulse 2.8s ease-in-out infinite;
  }}
  .descriptor {{
    font-family: Consolas, Monaco, monospace;
    font-size: 13px;
    font-weight: 700;
    letter-spacing: 0.45px;
    fill: #7AA0B8;
    text-anchor: middle;
    opacity: 0.96;
  }}
  .wave-stream {{
    animation: waveScroll 7.2s linear infinite;
  }}
  .wave-base {{
    fill: none;
    stroke: {hex_color(COLORS["line"])};
    stroke-width: 1.9;
    stroke-linecap: round;
    stroke-linejoin: round;
    opacity: 0.72;
  }}
  .wave-glow {{
    fill: none;
    stroke: {hex_color(COLORS["cyan"])};
    stroke-width: 4.4;
    stroke-linecap: round;
    stroke-linejoin: round;
    opacity: 0.42;
    filter: url(#softGlow);
  }}
  .wave-core {{
    fill: none;
    stroke: #DDF7FF;
    stroke-width: 1.8;
    stroke-linecap: round;
    stroke-linejoin: round;
    opacity: 0.94;
  }}
  .wave-focus {{
    fill: none;
    stroke: #FFFFFF;
    stroke-width: 3.1;
    stroke-linecap: round;
    stroke-linejoin: round;
    opacity: 0.98;
    filter: url(#titleGlow);
  }}
  .signal-sweep {{
    animation: signalSweep 4.8s linear infinite;
  }}
  .signal-beam {{
    opacity: 0.58;
  }}
  .panel-border {{
    animation: borderPulse 6s ease-in-out infinite;
  }}
  .scanlines {{
    animation: scanlineFlicker 3.6s linear infinite;
  }}
  @keyframes glowPulse {{
    0%, 100% {{ opacity: 0.38; }}
    50% {{ opacity: 0.82; }}
  }}
  @keyframes pixelIgnite {{
    0% {{ opacity: 0; transform: translateY(7px) scale(0.86); }}
    38% {{ opacity: 1; transform: translateY(0) scale(1.08); }}
    100% {{ opacity: 0; transform: translateY(0) scale(1); }}
  }}
  @keyframes scanSweep {{
    0% {{ transform: translateX(-360px); opacity: 0; }}
    12% {{ opacity: 0.75; }}
    70% {{ opacity: 0.46; }}
    100% {{ transform: translateX(1320px); opacity: 0; }}
  }}
  @keyframes glitchA {{
    0%, 92%, 100% {{ opacity: 0; transform: translateX(0); }}
    93% {{ opacity: 0.58; transform: translateX(-12px); }}
    93.8% {{ opacity: 0.32; transform: translateX(8px); }}
    94.5% {{ opacity: 0; transform: translateX(0); }}
  }}
  @keyframes glitchB {{
    0%, 92.4%, 100% {{ opacity: 0; transform: translateX(0); }}
    93.2% {{ opacity: 0.54; transform: translateX(11px); }}
    94% {{ opacity: 0.22; transform: translateX(-6px); }}
    94.6% {{ opacity: 0; transform: translateX(0); }}
  }}
  @keyframes glitchC {{
    0%, 91.7%, 100% {{ opacity: 0; transform: translateX(0); }}
    92.7% {{ opacity: 0.42; transform: translateX(-8px); }}
    93.5% {{ opacity: 0.26; transform: translateX(5px); }}
    94.2% {{ opacity: 0; transform: translateX(0); }}
  }}
  @keyframes taglinePulse {{
    0%, 100% {{ opacity: 0.84; }}
    50% {{ opacity: 1; }}
  }}
  @keyframes nodePulse {{
    0%, 100% {{ opacity: 0.52; transform: scale(0.92); }}
    50% {{ opacity: 0.95; transform: scale(1.12); }}
  }}
  @keyframes waveScroll {{
    from {{ transform: translateX(0); }}
    to {{ transform: translateX(-{signal_loop_width}px); }}
  }}
  @keyframes signalSweep {{
    0% {{ transform: translateX(0); opacity: 0; }}
    8% {{ opacity: 0.52; }}
    62% {{ opacity: 0.48; }}
    100% {{ transform: translateX({signal_view_width + signal_beam_width * 2}px); opacity: 0; }}
  }}
  @keyframes borderPulse {{
    0%, 100% {{ opacity: 0.56; }}
    50% {{ opacity: 0.92; }}
  }}
  @keyframes scanlineFlicker {{
    0%, 100% {{ opacity: 0.52; }}
    48% {{ opacity: 0.68; }}
    52% {{ opacity: 0.36; }}
  }}
  @media (prefers-reduced-motion: reduce) {{
    .trace-node,
    .title-glow,
    .ignite,
    .scan-beam,
    .glitch-a,
    .glitch-b,
    .glitch-c,
    .tagline,
    .wave-stream,
    .signal-sweep,
    .panel-border,
    .scanlines {{
      animation: none !important;
    }}
    .ignite,
    .glitch-a,
    .glitch-b,
    .glitch-c {{
      opacity: 0 !important;
    }}
    .title-glow {{
      opacity: 0.5 !important;
    }}
    .signal-beam,
    .wave-focus {{
      opacity: 0 !important;
    }}
  }}
</style>
<rect width="{NAMEPLATE_WIDTH}" height="{NAMEPLATE_HEIGHT}" rx="{panel_radius + 8}" fill="transparent"/>
<rect x="{panel_x}" y="{panel_y}" width="{panel_width}" height="{panel_height}" rx="{panel_radius}" fill="url(#panelBg)"/>
<g clip-path="url(#panelClip)">
  {''.join(grid_lines)}
  <g class="scanlines">{''.join(scanlines)}</g>
  <path d="M{panel_x + 1} {descriptor_divider_y} H{panel_x + panel_width - 1}" stroke="{hex_color(COLORS["line"])}" stroke-opacity="0.22"/>
  {trace_paths_markup}
  {trace_nodes_markup}
  <path d="M{tagline_capsule_x - 54} {descriptor_divider_y} H{tagline_capsule_x - 18}" stroke="{hex_color(COLORS["teal"])}" stroke-opacity="0.32"/>
  <path d="M{tagline_capsule_x + tagline_capsule_width + 18} {descriptor_divider_y} H{tagline_capsule_x + tagline_capsule_width + 54}" stroke="{hex_color(COLORS["cyan"])}" stroke-opacity="0.32"/>
  <g clip-path="url(#signalClip)">
    <path d="M{signal_view_x} {signal_view_y + signal_baseline} H{signal_view_x + signal_view_width}" stroke="{hex_color(COLORS["line"])}" stroke-opacity="0.2"/>
    <g class="signal-sweep signal-beam">
      <rect x="{signal_view_x - signal_beam_width}" y="{signal_view_y}" width="{signal_beam_width}" height="{signal_view_height}" fill="url(#signalBeamGradient)"/>
    </g>
    <g class="wave-stream">
      <use href="#eegSegment" x="{signal_view_x}" y="{signal_view_y}" class="wave-base"/>
      <use href="#eegSegment" x="{signal_view_x}" y="{signal_view_y}" class="wave-glow"/>
      <use href="#eegSegment" x="{signal_view_x}" y="{signal_view_y}" class="wave-core"/>
      <use href="#eegSegment" x="{signal_view_x + signal_loop_width}" y="{signal_view_y}" class="wave-base"/>
      <use href="#eegSegment" x="{signal_view_x + signal_loop_width}" y="{signal_view_y}" class="wave-glow"/>
      <use href="#eegSegment" x="{signal_view_x + signal_loop_width}" y="{signal_view_y}" class="wave-core"/>
    </g>
    <g class="wave-stream" mask="url(#signalFocusMask)">
      <use href="#eegSegment" x="{signal_view_x}" y="{signal_view_y}" class="wave-focus"/>
      <use href="#eegSegment" x="{signal_view_x + signal_loop_width}" y="{signal_view_y}" class="wave-focus"/>
    </g>
  </g>
  <rect x="{tagline_capsule_x}" y="{tagline_capsule_y}" width="{tagline_capsule_width}" height="{tagline_capsule_height}" rx="17" fill="#0D1F2F" fill-opacity="0.72" stroke="{hex_color(COLORS["line"])}" stroke-opacity="0.55"/>
  <use href="#titlePixels" x="0" y="{title_shadow_y}" fill="#06101A" opacity="0.84"/>
  <use href="#titlePixels" fill="url(#titleFill)"/>
  <g class="title-glow" filter="url(#titleGlow)">
    <use href="#titlePixels" fill="{hex_color(COLORS["cyan"])}"/>
  </g>
  <g fill="#FFFFFF" opacity="0.92">
    {ignition_markup}
  </g>
  <g clip-path="url(#titleClip)" opacity="0.72">
    <g transform="rotate(-12 {NAMEPLATE_WIDTH / 2} {title_y + title_height / 2})">
      <rect x="-180" y="{title_y - 24}" width="180" height="{title_height + 54}" fill="url(#scanBeamGradient)" class="scan-beam"/>
    </g>
  </g>
  <g class="glitch-a" clip-path="url(#glitchSliceA)" filter="url(#softGlow)">
    <use href="#titlePixels" fill="{hex_color(COLORS["cyan"])}"/>
  </g>
  <g class="glitch-b" clip-path="url(#glitchSliceB)" filter="url(#softGlow)">
    <use href="#titlePixels" fill="{hex_color(COLORS["teal"])}"/>
  </g>
  <g class="glitch-c" clip-path="url(#glitchSliceC)" filter="url(#softGlow)">
    <use href="#titlePixels" fill="#D5E7F4"/>
  </g>
  <text x="{NAMEPLATE_WIDTH / 2}" y="{tagline_y}" class="tagline">{NAMEPLATE_TAGLINE}</text>
  <text x="{NAMEPLATE_WIDTH / 2}" y="{descriptor_y}" class="descriptor">{NAMEPLATE_DESCRIPTOR}</text>
</g>
<rect x="{panel_x}" y="{panel_y}" width="{panel_width}" height="{panel_height}" rx="{panel_radius}" stroke="url(#panelBorder)" stroke-width="2.2" class="panel-border" filter="url(#panelGlow)"/>
</svg>
"""
    destination.write_text(svg, encoding="utf-8")


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


def render_eeg_alpha_divider_frame(frame_index: int) -> Image.Image:
    phase = frame_index / DIVIDER_FRAMES
    image = vertical_gradient(DIVIDER_WIDTH, DIVIDER_HEIGHT, COLORS["bg_top"], COLORS["bg_bottom"])
    add_grid(image, 30, x_shift=phase * 12)

    points = []
    for x in range(0, DIVIDER_WIDTH + 6, 6):
        envelope = 0.68 + 0.32 * sin((x / 220.0) - phase * 2 * pi * 0.8)
        signal = sin((x / 20.0) - phase * 2 * pi * 1.55) * 6.4 * envelope
        signal += sin((x / 8.0) + phase * 2 * pi * 2.1) * 1.2
        points.append((x, DIVIDER_HEIGHT / 2 + signal))

    draw_glow_line(image, points, COLORS["cyan"], width=2, glow_radius=5, glow_alpha=92, core_alpha=220)
    ImageDraw.Draw(image).line((0, DIVIDER_HEIGHT / 2, DIVIDER_WIDTH, DIVIDER_HEIGHT / 2), fill=rgba(COLORS["line"], 55), width=1)
    add_scanlines(image, opacity=8)
    add_noise(image, seed=frame_index * 31 + 11, count=180, opacity=18)
    return image


def render_eeg_clinical_divider_frame(frame_index: int) -> Image.Image:
    phase = frame_index / DIVIDER_FRAMES
    image = vertical_gradient(DIVIDER_WIDTH, DIVIDER_HEIGHT, COLORS["bg_top"], COLORS["bg_bottom"])
    add_grid(image, 32, x_shift=phase * 10)
    draw = ImageDraw.Draw(image)

    baselines = [18, DIVIDER_HEIGHT / 2, DIVIDER_HEIGHT - 18]
    configs = [
        (COLORS["teal"], 10.5, 0.0, 0.7),
        (COLORS["cyan"], 13.5, 0.9, 1.0),
        (COLORS["teal"], 8.5, 1.7, 0.55),
    ]
    for baseline, (color, period, offset, amp) in zip(baselines, configs):
        points = []
        for x in range(0, DIVIDER_WIDTH + 8, 8):
            signal = sin((x / (period * 2.0)) - phase * 2 * pi * 1.4 + offset) * (4.2 * amp)
            signal += sin((x / 7.5) + phase * 2 * pi * 2.3 - offset) * (0.9 * amp)
            spike = 0.0
            for center in (210, 590, 970):
                local = ((x - center) / 22.0) + sin(phase * 2 * pi + offset) * 0.3
                spike += exp(-(local * local)) * (5.3 * amp)
            points.append((x, baseline + signal - spike))
        draw_glow_line(image, points, color, width=2, glow_radius=4, glow_alpha=78, core_alpha=195)
        draw.line((0, baseline, DIVIDER_WIDTH, baseline), fill=rgba(COLORS["line"], 34), width=1)

    add_scanlines(image, opacity=7)
    add_noise(image, seed=frame_index * 29 + 13, count=180, opacity=16)
    return image


def render_eeg_evoked_divider_frame(frame_index: int) -> Image.Image:
    phase = frame_index / DIVIDER_FRAMES
    image = vertical_gradient(DIVIDER_WIDTH, DIVIDER_HEIGHT, COLORS["bg_top"], COLORS["bg_bottom"])
    add_grid(image, 28, x_shift=phase * 9)
    draw = ImageDraw.Draw(image)

    points = []
    for x in range(0, DIVIDER_WIDTH + 6, 6):
        baseline = sin((x / 36.0) - phase * 2 * pi * 0.7) * 1.4
        signal = baseline
        for center, scale in ((260, 1.0), (600, 0.85), (940, 1.1)):
            shift = sin(phase * 2 * pi * (1.1 + scale * 0.2)) * 20
            local = (x - center - shift) / 18.0
            positive = exp(-((local - 0.55) ** 2)) * 9.5 * scale
            negative = exp(-((local + 0.28) ** 2)) * 6.8 * scale
            signal += positive - negative
        points.append((x, DIVIDER_HEIGHT / 2 - signal))

    draw_glow_line(image, points, COLORS["cyan"], width=2, glow_radius=5, glow_alpha=96, core_alpha=225)
    for center in (260, 600, 940):
        x = int(center + sin(phase * 2 * pi * 1.15) * 20)
        draw.line((x, 10, x, DIVIDER_HEIGHT - 10), fill=rgba(COLORS["teal"], 50), width=1)
    draw.line((0, DIVIDER_HEIGHT / 2, DIVIDER_WIDTH, DIVIDER_HEIGHT / 2), fill=rgba(COLORS["line"], 42), width=1)

    add_scanlines(image, opacity=8)
    add_noise(image, seed=frame_index * 37 + 17, count=190, opacity=17)
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
