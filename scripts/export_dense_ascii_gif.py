"""Export the approved ASCII Magic canvas piece as a GitHub-compatible GIF.

Requires Node.js and Pillow. The source HTML is the approved local preview.
"""

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONT = Path(r"C:\Windows\Fonts\consola.ttf")
CELL_WIDTH = 10
CELL_HEIGHT = CELL_WIDTH / 0.602
BACKGROUND = "#0d1117"
INK = "#e6edf3"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="Approved Dense ASCII HTML preview")
    parser.add_argument(
        "--output", type=Path, default=ROOT / "assets" / "davide-stefanelli-bouncing-dense-ascii.gif"
    )
    args = parser.parse_args()

    result = subprocess.run(
        ["node", str(ROOT / "scripts" / "export_dense_frames.js"), str(args.source)],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    frames = []
    font = ImageFont.truetype(str(FONT), round(CELL_HEIGHT))
    for line in result.stdout.splitlines():
        frame = json.loads(line)
        rows = frame["text"].split("\n")
        colors = frame["color"].split("\n")
        image = Image.new("RGB", (len(rows[0]) * CELL_WIDTH, round(len(rows) * CELL_HEIGHT)), BACKGROUND)
        draw = ImageDraw.Draw(image)
        palette = frame["palette"]
        for y, row in enumerate(rows):
            for x, glyph in enumerate(row):
                if glyph == " ":
                    continue
                key = colors[y][x]
                fill = palette.get(key, INK) if key != " " else INK
                draw.text((x * CELL_WIDTH, (y + 0.5) * CELL_HEIGHT), glyph, font=font, fill=fill, anchor="lm")
        frames.append(image)

    reference_palette = frames[0].quantize(colors=256, method=Image.Quantize.FASTOCTREE)
    indexed = [frame.quantize(palette=reference_palette, dither=Image.Dither.NONE) for frame in frames]
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
    print(f"{args.output}: {len(indexed)} frames, {indexed[0].width}x{indexed[0].height}")


if __name__ == "__main__":
    main()
