"""Recolor the profile's ASCII brain GIF while preserving its animation data."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "ascii-profile-panels" / "brain.gif"
DESTINATION = ROOT / "previews" / "ascii-profile-brain-phosphor-green.gif"
DEPTH_DESTINATION = ROOT / "previews" / "ascii-profile-brain-phosphor-green-depth.gif"


def phosphor_green(red: int, green: int, blue: int,
                   depth: bool = False) -> tuple[int, int, int]:
    # The terminal frame is neutral gray; recolor only the blue/cyan cortex.
    if blue - red < 6 or blue < green - 8:
        return red, green, blue

    # A monotonic lightness map keeps the source's sulcal shadow ordering.
    luminance = 0.2126 * red + 0.7152 * green + 0.0722 * blue
    level = min(1.0, luminance / 220.0)
    if depth:
        # Separate the darker sulci from illuminated gyri without clipping
        # their character shapes or changing the underlying animation.
        level = max(0.03, min(1.0, 0.5 + (level - 0.5) * 1.7))
    phosphor = min(255, round((16 if depth else 22) + (239 if depth else 233) * level ** 0.95))
    tint = level ** 1.7
    return (
        round(phosphor * (0.10 + 0.55 * tint)),
        phosphor,
        round(phosphor * (0.20 + 0.45 * tint)),
    )


def recolor_table(data: bytearray, start: int, entries: int, depth: bool) -> int:
    end = start + entries * 3
    if end > len(data):
        raise ValueError("Truncated GIF color table")
    for offset in range(start, end, 3):
        data[offset:offset + 3] = bytes(phosphor_green(*data[offset:offset + 3], depth=depth))
    return end


def skip_subblocks(data: bytearray, position: int) -> int:
    while True:
        if position >= len(data):
            raise ValueError("Truncated GIF sub-block")
        length = data[position]
        position += 1
        if length == 0:
            return position
        position += length
        if position > len(data):
            raise ValueError("Truncated GIF sub-block payload")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--variant", choices=("green", "depth"), default="green")
    args = parser.parse_args()
    depth = args.variant == "depth"
    destination = DEPTH_DESTINATION if depth else DESTINATION
    data = bytearray(SOURCE.read_bytes())
    if data[:6] not in (b"GIF87a", b"GIF89a"):
        raise ValueError("The source is not a GIF")
    packed = data[10]
    position = 13
    tables = 0
    if packed & 0x80:
        position = recolor_table(data, position, 1 << ((packed & 7) + 1), depth)
        tables += 1

    frames = 0
    while position < len(data):
        marker = data[position]
        if marker == 0x3B:
            break
        if marker == 0x21:
            position = skip_subblocks(data, position + 2)
        elif marker == 0x2C:
            if position + 10 > len(data):
                raise ValueError("Truncated GIF image descriptor")
            packed = data[position + 9]
            position += 10
            if packed & 0x80:
                position = recolor_table(data, position, 1 << ((packed & 7) + 1), depth)
                tables += 1
            position = skip_subblocks(data, position + 1)  # LZW code size
            frames += 1
        else:
            raise ValueError(f"Unexpected GIF block 0x{marker:02x}")
    if frames != 120 or tables == 0:
        raise ValueError(f"Unexpected GIF structure: {frames} frames, {tables} palettes")

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    with Image.open(destination) as output:
        if output.n_frames != frames:
            raise ValueError("The recolored GIF has an incorrect frame count")
        print(f"{destination}: {frames} frames, {output.width}x{output.height}, {tables} palettes")


if __name__ == "__main__":
    main()
