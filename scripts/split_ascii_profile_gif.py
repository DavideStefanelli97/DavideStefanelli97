"""Split the approved ASCII profile GIF into clickable README panels.

The original full animation stays in assets/ascii-profile-readme.gif.
Coordinates refer to that 1741x1652 render; adjacent crops share no pixels.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets" / "ascii-profile-readme.gif"
DESTINATION = ROOT / "assets" / "ascii-profile-panels"

# The row and column cuts fall immediately after the ASCII frame strokes.
CROPS = {
    "intro": (0, 0, 1741, 473),
    "brain": (0, 473, 991, 1652),
    "linkedin": (991, 473, 1741, 929),
    "email": (991, 929, 1741, 1301),
    "projects": (991, 1301, 1741, 1652),
}


def main() -> None:
    with Image.open(SOURCE) as source:
        if source.size != (1741, 1652) or source.n_frames != 120:
            raise ValueError("The approved source GIF dimensions or frame count changed")

    DESTINATION.mkdir(parents=True, exist_ok=True)
    for name, (left, top, right, bottom) in CROPS.items():
        width, height = right - left, bottom - top
        output = DESTINATION / f"{name}.gif"
        crop = f"crop={width}:{height}:{left}:{top}"
        filter_graph = (
            f"[0:v]{crop},split=2[frames][palette_frames];"
            "[palette_frames]palettegen=max_colors=256:stats_mode=full[palette];"
            "[frames][palette]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle[out]"
        )
        subprocess.run(
            [
                "ffmpeg", "-v", "error", "-y", "-i", str(SOURCE),
                "-filter_complex", filter_graph, "-map", "[out]", "-loop", "0",
                str(output),
            ],
            check=True,
        )
        with Image.open(output) as result:
            if result.size != (width, height) or result.n_frames != 120:
                raise ValueError(f"Unexpected output geometry or frames: {output}")
        print(f"{name}: {width}x{height}, 120 frames, {output.stat().st_size} bytes")


if __name__ == "__main__":
    main()
