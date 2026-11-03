"""Rasterize the profile name into fine or retro bitmap ASCII-cell masks."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
FONT = Path(r"C:\Windows\Fonts\consolab.ttf")
OUTPUT = ROOT / "scripts" / "particle_rain_mask.json"
RETRO_OUTPUT = ROOT / "scripts" / "particle_rain_mask_retro_code.json"
CYAN_OUTPUT = ROOT / "scripts" / "particle_rain_mask_cyan_pixel.json"
DOTS_OUTPUT = ROOT / "scripts" / "particle_rain_mask_halftone_dots.json"
DEPTH_OUTPUT = ROOT / "scripts" / "particle_rain_mask_halftone_depth.json"
CYAN_FONT = Path(r"C:\Windows\Fonts\CascadiaMono.ttf")
LINES = ("DAVIDE", "STEFANELLI")
FONT_SIZE = 30


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("current", "retro-code", "cyan-pixel", "halftone-dots", "halftone-depth"), default="current")
    args = parser.parse_args()
    retro = args.variant == "retro-code"
    if retro:
        font = ImageFont.load_default()
    elif args.variant in ("cyan-pixel", "halftone-dots", "halftone-depth"):
        font = ImageFont.truetype(str(CYAN_FONT), FONT_SIZE * (2 if args.variant == "cyan-pixel" else 1))
        font.set_variation_by_name("SemiBold")
    else:
        font = ImageFont.truetype(str(FONT), FONT_SIZE)
    masks = {}
    for line in LINES:
        left, top, right, bottom = font.getbbox(line)
        image = Image.new("L", (right - left, bottom - top))
        ImageDraw.Draw(image).text((-left, -top), line, font=font, fill=255)
        if retro:
            image = image.resize((image.width * 3, image.height * 3), Image.Resampling.NEAREST)
        elif args.variant in ("halftone-dots", "halftone-depth"):
            image = image.resize((image.width, image.height * 2), Image.Resampling.NEAREST)
        if args.variant == "halftone-depth":
            import numpy as np
            from scipy.ndimage import distance_transform_edt

            alpha = np.asarray(image)
            inside = alpha >= 43
            distance = distance_transform_edt(inside)
            # Most vertical strokes are only four cells wide, so their centers
            # must reach a bright level even at a distance of two cells.
            levels = (np.digitize(distance, (1.05, 1.35, 1.7, 1.95, 2.65)) + 1).astype(np.uint8)
            levels[~inside] = 0
            rows = ["".join(map(str, row)) for row in levels]
        else:
            rows = []
            for y in range(image.height):
                row = "".join(str(min(3, (image.getpixel((x, y)) + 42) // 85)) for x in range(image.width))
                rows.append(row)
        masks[line] = {"w": image.width, "h": image.height, "rows": rows}
    destination = (RETRO_OUTPUT if retro else DEPTH_OUTPUT if args.variant == "halftone-depth"
                   else DOTS_OUTPUT if args.variant == "halftone-dots"
                   else CYAN_OUTPUT if args.variant == "cyan-pixel" else OUTPUT)
    destination.write_text(json.dumps(masks, separators=(",", ":")) + "\n", encoding="ascii")
    print(" ".join(f"{line}: {mask['w']}x{mask['h']}" for line, mask in masks.items()))


if __name__ == "__main__":
    main()
