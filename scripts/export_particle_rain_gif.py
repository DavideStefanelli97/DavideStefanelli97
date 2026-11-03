"""Render the particle-rain name animation as a profile-ready Dense ASCII GIF."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "particle_rain_name.mjs"
MASK_GENERATOR = ROOT / "scripts" / "generate_particle_rain_mask.py"
DEFAULT_OUTPUT = ROOT / "assets" / "davide-stefanelli-dense-ascii.gif"
FONT = Path(r"C:\Windows\Fonts\consola.ttf")
CELL_WIDTH = 12
CELL_HEIGHT = 20
BACKGROUND = "#000000"
BEZEL_X = 60
BEZEL_TOP = 65
BEZEL_BOTTOM = 95


def render(frame: dict, font: ImageFont.FreeTypeFont) -> Image.Image:
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
                point = (x * CELL_WIDTH, y * CELL_HEIGHT + CELL_HEIGHT / 2)
                if glyph in "@#%&WM8*":
                    glow_draw.text(point, glyph, font=font, fill=(*bytes.fromhex(color[1:]), 100), anchor="lm")
    # Keep the characters crisp while allowing a restrained CRT phosphor halo.
    halo = glow.filter(ImageFilter.GaussianBlur(radius=4))
    image.paste(halo, mask=halo.getchannel("A"))
    draw = ImageDraw.Draw(image)
    for y, (row, color_row) in enumerate(zip(rows, colors)):
        for x, (glyph, key) in enumerate(zip(row, color_row)):
            if glyph != " ":
                draw.text(
                    (x * CELL_WIDTH, y * CELL_HEIGHT + CELL_HEIGHT / 2),
                    glyph,
                    font=font,
                    fill=frame["palette"].get(key, "#e6edf3"),
                    anchor="lm",
                )
    # Fine scanlines sit over the glow and crisp characters.
    overlay = Image.new("RGBA", size)
    scanlines = ImageDraw.Draw(overlay)
    for y in range(4, size[1], 5):
        scanlines.line((0, y, size[0], y), fill=(0, 0, 0, 28))
    image = Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB")

    outer_size = (size[0] + 2 * BEZEL_X, size[1] + BEZEL_TOP + BEZEL_BOTTOM)
    device = Image.new("RGB", outer_size, "#080b0e")
    casing = ImageDraw.Draw(device)
    w, h = outer_size
    casing.rounded_rectangle((5, 5, w - 6, h - 6), radius=42,
                            fill="#171e24", outline="#5b6a72", width=4)
    casing.rounded_rectangle((18, 18, w - 19, h - 19), radius=34,
                            outline="#303d46", width=3)
    casing.rounded_rectangle((BEZEL_X - 13, BEZEL_TOP - 13,
                             BEZEL_X + size[0] + 12, BEZEL_TOP + size[1] + 12),
                            radius=15, fill="#020506", outline="#405660", width=3)
    device.paste(image, (BEZEL_X, BEZEL_TOP))
    casing = ImageDraw.Draw(device)
    for x in (32, w - 33):
        for y in (32, h - 33):
            casing.ellipse((x - 5, y - 5, x + 5, y + 5),
                           fill="#0b1115", outline="#59656b", width=2)
    label_font = ImageFont.truetype(str(FONT), 21)
    casing.text((BEZEL_X + 8, h - 56), "DS-97  /  VISUAL TERMINAL",
                font=label_font, fill="#81929c")
    casing.text((w - 220, h - 56), "POWER", font=label_font, fill="#81929c")
    casing.ellipse((w - 80, h - 64, w - 54, h - 38), fill="#103d4a")
    casing.ellipse((w - 75, h - 59, w - 59, h - 43), fill="#6bd9ef")
    return device


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    subprocess.run([sys.executable, str(MASK_GENERATOR)], check=True, capture_output=True)
    process = subprocess.run(
        ["node", str(SOURCE)],
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
    samples = [render(source_frames[round(i * (len(source_frames) - 1) / 7)], font)
               for i in range(8)]
    sw, sh = samples[0].size
    reference = Image.new("RGB", (sw, sh * len(samples)), BACKGROUND)
    for i, sample in enumerate(samples):
        reference.paste(sample, (0, i * sh))
    palette = reference.quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    del reference, samples
    indexed = [render(frame, font).quantize(palette=palette, dither=Image.Dither.NONE)
               for frame in source_frames]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    indexed[0].save(
        args.output,
        save_all=True,
        append_images=indexed[1:],
        duration=50,
        loop=0,
        optimize=True,
        disposal=1,
    )
    print(f"{args.output}: {len(indexed)} frames, {sw}x{sh}")


if __name__ == "__main__":
    main()
