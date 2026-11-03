"""Rasterize the profile name into a fine ASCII-cell mask."""

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONT = Path(r"C:\Windows\Fonts\consolab.ttf")
OUTPUT = ROOT / "scripts" / "particle_rain_mask.json"
LINES = ("DAVIDE", "STEFANELLI")
FONT_SIZE = 30


def main() -> None:
    font = ImageFont.truetype(str(FONT), FONT_SIZE)
    masks = {}
    for line in LINES:
        left, top, right, bottom = font.getbbox(line)
        image = Image.new("L", (right - left, bottom - top))
        ImageDraw.Draw(image).text((-left, -top), line, font=font, fill=255)
        rows = []
        for y in range(image.height):
            row = "".join(str(min(3, (image.getpixel((x, y)) + 42) // 85)) for x in range(image.width))
            rows.append(row)
        masks[line] = {"w": image.width, "h": image.height, "rows": rows}
    OUTPUT.write_text(json.dumps(masks, separators=(",", ":")) + "\n", encoding="ascii")
    print(" ".join(f"{line}: {mask['w']}x{mask['h']}" for line, mask in masks.items()))


if __name__ == "__main__":
    main()
