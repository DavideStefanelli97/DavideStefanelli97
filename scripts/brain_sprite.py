"""Embed the deterministic 3D turntable sheet in a self-contained SVG image.

Animation is performed by SVG clipping and CSS, without editing the source PNG.
"""
import base64
import json
from pathlib import Path


SPRITE_PATH = Path(__file__).resolve().parents[1] / "assets" / "brain-turntable-stable.png"
CELL_SIZE = 336


def brain_sprite() -> tuple[str, str]:
    data = base64.b64encode(SPRITE_PATH.read_bytes()).decode("ascii")
    metadata = json.loads(SPRITE_PATH.with_suffix('.json').read_text(encoding='utf-8'))
    frame_count = metadata['frames']
    columns, rows = metadata['columns'], metadata['rows']
    assert frame_count == columns * rows
    keyframes = []
    for frame in range(frame_count):
        x = -(frame % columns) * CELL_SIZE
        y = -(frame // columns) * CELL_SIZE
        keyframes.append(f"{frame * 100 / frame_count:.8f}% {{ transform:translate({x}px,{y}px); }}")
    keyframes.append("100% { transform:translate(0,0); }")
    css = (
        f".brain-turn {{ animation:brain-turn {metadata['duration_seconds']}s steps(1,end) infinite; }}\n"
        "@keyframes brain-turn {" + " ".join(keyframes) + "}\n"
        "@media (prefers-reduced-motion: reduce) { .brain-turn { animation:none; } }"
    )
    markup = (
        '<svg x="800" y="26" width="336" height="336" viewBox="0 0 336 336" overflow="hidden">'
        f'<image class="brain-turn" width="{columns*CELL_SIZE}" height="{rows*CELL_SIZE}" '
        'style="image-rendering:pixelated" '
        f'href="data:image/png;base64,{data}"/>'
        '</svg>'
    )
    return css, markup
