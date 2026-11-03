"""Render the particle-rain name animation as a profile-ready Dense ASCII GIF."""

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "particle_rain_name.mjs"
DEFAULT_OUTPUT = ROOT / "assets" / "davide-stefanelli-dense-ascii.gif"
FONT = Path(r"C:\Windows\Fonts\consola.ttf")
CELL_WIDTH = 11
CELL_HEIGHT = 18
BACKGROUND = "#000000"


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
    return image


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

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
    frames = [render(frame, font) for frame in source_frames]

    # A palette sampled from the whole sequence preserves the name's gradient.
    samples = [frames[round(i * (len(frames) - 1) / 7)] for i in range(8)]
    sw, sh = frames[0].size
    reference = Image.new("RGB", (sw, sh * len(samples)), BACKGROUND)
    for i, sample in enumerate(samples):
        reference.paste(sample, (0, i * sh))
    palette = reference.quantize(colors=128, method=Image.Quantize.FASTOCTREE)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]

    args.output.parent.mkdir(parents=True, exist_ok=True)
    indexed[0].save(
        args.output,
        save_all=True,
        append_images=indexed[1:],
        duration=50,
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"{args.output}: {len(indexed)} frames, {sw}x{sh}")


if __name__ == "__main__":
    main()
