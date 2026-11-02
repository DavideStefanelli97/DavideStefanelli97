"""Render the existing brain turntable as colored ASCII art."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "brain-turntable-stable.gif"
COLS, ROWS = 60, 37
CW, CH = 8, 13
FONT = ImageFont.truetype(r"C:\Windows\Fonts\consola.ttf", 14)
BACKGROUND = (13, 17, 23)
RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
NAME_COLORS = ((126, 231, 135), (255, 166, 87), (255, 123, 114),
               (210, 168, 255), (255, 209, 102))


def sorted_glyphs():
    coverage = []
    for glyph in dict.fromkeys(RAMP):
        if glyph == " ":
            continue
        tile = Image.new("L", (CW, CH))
        ImageDraw.Draw(tile).text((0, CH / 2), glyph, font=FONT, fill=255, anchor="lm")
        coverage.append((sum(tile.getdata()), glyph))
    return [glyph for _, glyph in sorted(coverage)]


GLYPHS = sorted_glyphs()


def name_color(x, y, light):
    position = max(0.0, min(1.0, (x - 5 + y * 0.07) / (COLS - 10)))
    scaled = position * (len(NAME_COLORS) - 1)
    index = min(len(NAME_COLORS) - 2, int(scaled))
    fraction = scaled - index
    base = tuple(NAME_COLORS[index][i] * (1 - fraction) +
                 NAME_COLORS[index + 1][i] * fraction for i in range(3))
    shade = max(0.32, min(1.0, (light - 0.06) / 0.64))
    return tuple(round(channel * shade) for channel in base)


def draw_frame(source, variant):
    reduced = source.convert("RGBA").resize((COLS, ROWS), Image.Resampling.BOX)
    canvas = Image.new("RGB", (COLS * CW, ROWS * CH), BACKGROUND)
    draw = ImageDraw.Draw(canvas)
    for y in range(ROWS):
        for x in range(COLS):
            r, g, b, alpha = reduced.getpixel((x, y))
            opacity = alpha / 255
            if opacity < 0.08:
                continue
            light = (0.18 * r + 0.66 * g + 0.16 * b) / 255
            density = max(0, min(1, ((light - 0.07) / 0.66) ** 0.85))
            density *= min(1, opacity * 2.2)
            index = min(len(GLYPHS) - 1, int(density * (len(GLYPHS) - 1)))
            glyph = GLYPHS[index]
            if variant == "blue":
                boost = 1.32
                color = tuple(min(255, round(channel * boost)) for channel in (r, g, b))
            else:
                color = name_color(x, y, light)
            draw.text((x * CW, (y + 0.5) * CH), glyph, font=FONT, fill=color, anchor="lm")
    return canvas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", choices=("blue", "palette"), default="palette")
    args = parser.parse_args()
    destination = ROOT / "assets" / f"brain-turntable-ascii-{args.variant}.gif"
    gif = Image.open(SOURCE)
    frames = []
    for index in range(gif.n_frames):
        gif.seek(index)
        frames.append(draw_frame(gif.copy(), args.variant))
    frames[30].save(ROOT / "output" / f"brain-turntable-ascii-{args.variant}-preview.png")
    palette = frames[30].quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    indexed = [frame.quantize(palette=palette, dither=Image.Dither.NONE) for frame in frames]
    indexed[0].save(destination, save_all=True, append_images=indexed[1:], duration=40,
                    loop=0, disposal=2, optimize=True)
    print(f"{destination}: {len(indexed)} frames at {COLS * CW}x{ROWS * CH}")


if __name__ == "__main__":
    main()
