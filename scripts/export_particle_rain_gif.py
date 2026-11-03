"""Render profile-ready particle-rain name animations in several styles."""

import argparse
import json
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "particle_rain_name.mjs"
MASK_GENERATOR = ROOT / "scripts" / "generate_particle_rain_mask.py"
DEFAULT_OUTPUT = ROOT / "assets" / "davide-stefanelli-dense-ascii.gif"
RETRO_OUTPUT = ROOT / "previews" / "davide-stefanelli-retro-code.gif"
CYAN_OUTPUT = ROOT / "previews" / "davide-stefanelli-cyan-pixel.gif"
DOTS_OUTPUT = ROOT / "previews" / "davide-stefanelli-halftone-dots.gif"
DEPTH_OUTPUT = ROOT / "previews" / "davide-stefanelli-halftone-depth.gif"
GREEN_OUTPUT = ROOT / "previews" / "davide-stefanelli-halftone-green.gif"
FONT = Path(r"C:\Windows\Fonts\consola.ttf")
RETRO_CASE_FONT = Path(r"C:\Windows\Fonts\courbd.ttf")
CELL_WIDTH = 12
CELL_HEIGHT = 20
BACKGROUND = "#000000"
BEZEL_X = 60
BEZEL_TOP = 65
BEZEL_BOTTOM = 95


@lru_cache(maxsize=128)
def bitmap_glyph(glyph: str) -> Image.Image:
    tile = Image.new("L", (6, 10))
    ImageDraw.Draw(tile).text((0, -2), glyph, font=ImageFont.load_default(), fill=255)
    scaled = tile.resize((CELL_WIDTH, CELL_HEIGHT), Image.Resampling.NEAREST)
    return scaled.point(lambda value: 255 if value >= 85 else 0)


def paint_glyph(draw: ImageDraw.ImageDraw, glyph: str, x: int, y: int,
                fill: str | tuple[int, ...], font: ImageFont.FreeTypeFont,
                retro: bool, pixel: bool = False, dots: bool = False,
                depth: bool = False) -> None:
    if dots and glyph in ("123456" if depth else "123"):
        radius = ((1.45, 2.0, 2.65, 3.25, 3.9, 4.45) if depth
                  else (1.5, 2.6, 3.7))[int(glyph) - 1]
        cx = x * CELL_WIDTH + CELL_WIDTH / 2
        cy = y * CELL_HEIGHT + CELL_HEIGHT / 2
        color = (tuple(round(channel * (0.34, 0.46, 0.59, 0.72, 0.86, 1.0)[int(glyph) - 1])
                       for channel in bytes.fromhex(fill[1:])) if depth else fill)
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)
    elif pixel and glyph in "123":
        brightness = (0.68, 0.9, 1.0)[int(glyph) - 1]
        color = tuple(round(channel * brightness) for channel in bytes.fromhex(fill[1:]))
        draw.rectangle((x * CELL_WIDTH, y * CELL_HEIGHT,
                        (x + 1) * CELL_WIDTH - 1, (y + 1) * CELL_HEIGHT - 1), fill=color)
    elif retro:
        draw.bitmap((x * CELL_WIDTH, y * CELL_HEIGHT), bitmap_glyph(glyph), fill=fill)
    else:
        draw.text((x * CELL_WIDTH, y * CELL_HEIGHT + CELL_HEIGHT / 2),
                  glyph, font=font, fill=fill, anchor="lm")


def render(frame: dict, font: ImageFont.FreeTypeFont,
           retro: bool = False, pixel: bool = False, dots: bool = False,
           depth: bool = False, green: bool = False) -> Image.Image:
    rows = frame["text"].split("\n")
    colors = frame["color"].split("\n")
    width = len(rows[0])
    if any(len(row) != width for row in rows + colors):
        raise ValueError("The animation produced a non-rectangular frame")
    size = (width * CELL_WIDTH, len(rows) * CELL_HEIGHT)
    image = Image.new("RGB", size, BACKGROUND)
    glow = Image.new("RGBA", size)
    glow_draw = ImageDraw.Draw(glow)
    for y, (row, color_row) in enumerate(zip(rows, colors)):
        for x, (glyph, key) in enumerate(zip(row, color_row)):
            if glyph != " ":
                color = frame["palette"].get(key, "#e6edf3")
                if depth and glyph in "456":
                    cx = x * CELL_WIDTH + CELL_WIDTH / 2
                    cy = y * CELL_HEIGHT + CELL_HEIGHT / 2
                    radius = (3.25, 3.9, 4.45)[int(glyph) - 4]
                    glow_draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius),
                                      fill=(*bytes.fromhex(color[1:]), 110))
                elif not pixel and glyph in "@#%&WM8*":
                    paint_glyph(glow_draw, glyph, x, y,
                                (*bytes.fromhex(color[1:]), 100), font, retro)
    # Keep the characters crisp while allowing a restrained CRT phosphor halo.
    if depth:
        image = Image.alpha_composite(image.convert("RGBA"),
                                      glow.filter(ImageFilter.GaussianBlur(radius=5))).convert("RGB")
    elif not pixel:
        halo = glow.filter(ImageFilter.GaussianBlur(radius=4))
        image.paste(halo, mask=halo.getchannel("A"))
    draw = ImageDraw.Draw(image)
    for y, (row, color_row) in enumerate(zip(rows, colors)):
        for x, (glyph, key) in enumerate(zip(row, color_row)):
            if glyph != " ":
                paint_glyph(draw, glyph, x, y,
                            frame["palette"].get(key, "#e6edf3"), font, retro, pixel, dots, depth)
    # Fine scanlines sit over the glow and crisp characters.
    overlay = Image.new("RGBA", size)
    scanlines = ImageDraw.Draw(overlay)
    for y in range(4, size[1], 5):
        scanlines.line((0, y, size[0], y), fill=(0, 0, 0, 14 if pixel else 36 if retro else 28))
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")
    if pixel:
        # Preserve the retro window at its original physical size while the
        # name itself uses the selected pixel or halftone grid.
        chrome = ImageDraw.Draw(image)
        cw, ch = size
        chrome.rectangle((7, 7, cw - 8, ch - 8),
                         outline="#4d7854" if green else "#77705a", width=2)
        for x in range(12, cw - 12, 18):
            for y in (8, 54, ch - 25):
                chrome.line((x, y, min(x + 10, cw - 12), y),
                            fill="#4d7854" if green else "#77705a", width=2)
        chrome.text((34, 19), "C:\\> RUN IDENTITY.EXE",
                    font=ImageFont.truetype(str(RETRO_CASE_FONT), 21),
                    fill="#a2ffa0" if green else "#f2c878")
        chrome.text((cw - 195, 19), "MEM 640K [X]",
                    font=ImageFont.truetype(str(RETRO_CASE_FONT), 21),
                    fill="#78ad7e" if green else "#a9a080")

    outer_size = (size[0] + 2 * BEZEL_X, size[1] + BEZEL_TOP + BEZEL_BOTTOM)
    device = Image.new("RGB", outer_size, "#14130e" if retro else "#080b0e")
    casing = ImageDraw.Draw(device)
    w, h = outer_size
    casing.rounded_rectangle((5, 5, w - 6, h - 6), radius=42,
                            fill="#47463a" if retro else "#171e24",
                            outline="#a7a087" if retro else "#5b6a72", width=4)
    casing.rounded_rectangle((18, 18, w - 19, h - 19), radius=34,
                            outline="#6c6b58" if retro else "#303d46", width=3)
    casing.rounded_rectangle((BEZEL_X - 13, BEZEL_TOP - 13,
                             BEZEL_X + size[0] + 12, BEZEL_TOP + size[1] + 12),
                            radius=15, fill="#090b06" if retro else "#020506",
                            outline="#8a856b" if retro else "#405660", width=3)
    device.paste(image, (BEZEL_X, BEZEL_TOP))
    casing = ImageDraw.Draw(device)
    for x in (32, w - 33):
        for y in (32, h - 33):
            casing.ellipse((x - 5, y - 5, x + 5, y + 5),
                           fill="#27291e" if retro else "#0b1115",
                           outline="#a29d82" if retro else "#59656b", width=2)
    label_font = ImageFont.truetype(str(RETRO_CASE_FONT if retro else FONT), 21)
    casing.text((BEZEL_X + 8, h - 56),
                "DS-97  /  CODE TERMINAL" if retro else "DS-97  /  VISUAL TERMINAL",
                font=label_font, fill="#9abf91" if green else "#c9c29d" if retro else "#81929c")
    casing.text((w - 220, h - 56), "POWER", font=label_font,
                fill="#9abf91" if green else "#c9c29d" if retro else "#81929c")
    casing.ellipse((w - 80, h - 64, w - 54, h - 38), fill="#354d1f" if retro else "#103d4a")
    casing.ellipse((w - 75, h - 59, w - 59, h - 43), fill="#bbef70" if retro else "#6bd9ef")
    return device


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("current", "retro-code", "cyan-pixel", "halftone-dots", "halftone-depth", "halftone-green"), default="current")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    retro = args.variant != "current"
    green = args.variant == "halftone-green"
    depth = args.variant in ("halftone-depth", "halftone-green")
    pixel = args.variant in ("cyan-pixel", "halftone-dots", "halftone-depth", "halftone-green")
    dots = args.variant in ("halftone-dots", "halftone-depth", "halftone-green")
    global CELL_WIDTH, CELL_HEIGHT
    if pixel:
        CELL_WIDTH, CELL_HEIGHT = (12, 10) if dots else (6, 10)
    destination = args.output or (GREEN_OUTPUT if green else DEPTH_OUTPUT if depth else DOTS_OUTPUT if dots else CYAN_OUTPUT if pixel else
                                  RETRO_OUTPUT if retro else DEFAULT_OUTPUT)

    subprocess.run([sys.executable, str(MASK_GENERATOR), "--variant", "halftone-depth" if green else args.variant],
                   check=True, capture_output=True)
    process = subprocess.run(
        ["node", str(SOURCE), *(["--halftone-green"] if green else
                                ["--halftone-depth"] if depth else
                                ["--halftone-dots"] if dots else
                                ["--cyan-pixel"] if pixel else ["--retro-code"] if retro else [])],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    source_frames = [json.loads(line) for line in process.stdout.splitlines()]
    if not source_frames:
        raise ValueError("The animation produced no frames")
    font = ImageFont.truetype(str(FONT), CELL_HEIGHT)
    # Sample the full sequence, then render one RGB frame at a time to limit memory.
    samples = [render(source_frames[round(i * (len(source_frames) - 1) / 7)], font, retro, pixel, dots, depth, green)
               for i in range(8)]
    sw, sh = samples[0].size
    reference = Image.new("RGB", (sw, sh * len(samples)), BACKGROUND)
    for i, sample in enumerate(samples):
        reference.paste(sample, (0, i * sh))
    palette = reference.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    del reference, samples
    indexed = [render(frame, font, retro, pixel, dots, depth, green).quantize(palette=palette, dither=Image.Dither.NONE)
               for frame in source_frames]

    destination.parent.mkdir(parents=True, exist_ok=True)
    indexed[0].save(
        destination,
        save_all=True,
        append_images=indexed[1:],
        duration=50,
        loop=0,
        optimize=True,
        disposal=1,
    )
    print(f"{destination}: {len(indexed)} frames, {sw}x{sh}")


if __name__ == "__main__":
    main()
