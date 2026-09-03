"""Build the profile's schematic hero and verified, project-derived previews.

Default: regenerate the self-contained SVG and check the committed previews.
Optional --refresh-evidence: recreate previews from pinned, read-only source
checkouts. Source files are hashed before use; no network access is performed.
"""
from __future__ import annotations

import argparse
import hashlib
from math import pi, sin
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
NAMEPLATE_FILENAME = "profile-nameplate-clean.svg"
PREVIEWS = (
    "work-neuroscope.webp",
    "work-eeg-pipeline.webp",
    "work-medical-imaging.webp",
)
# Paths are relative to --sources-root. Never write to these checkouts.
SOURCES = {
    "topoplot": (
        "NEURO-SCOPE_public_release/docs/assets/topoplot-window.png",
        "491b8037cc9ccf9cdfbdee9254d379c87045c751e0a686ed1d7bea2972a4c954",
    ),
    "spectrum": (
        "NEURO-SCOPE_public_release/docs/assets/filter-compare.png",
        "85b3068b952de773d20c416ed936f26bed1fbd7d6a2d0fc86dee54c8555474a2",
    ),
    "wavelets": (
        "MATLAB-EEG-Processing-Pipeline/outputs/figures/sub-035/stage04/"
        "01_stage04_subject_tf_focus_channels.png",
        "769fbf3b5ee5d616a696b4da8c8e5d6358644f4e835855cb6938a9ae8a85e53a",
    ),
    "rotation": (
        "Smart Medical Imaging/results/reg_rotation/metric_trends.jpg",
        "e551be1b48917a41aeb24cec38e934d43f992e1444ae8f27fdc92310dd68758b",
    ),
}


def signal_path(x0: int, x1: int, baseline: int, phase: float) -> str:
    """A deliberately synthetic trace: no participant data or measured result."""
    points = []
    for x in range(x0, x1 + 1, 2):
        t = (x - x0) / (x1 - x0)
        envelope = max(0.0, sin(pi * t)) ** 0.7
        y = baseline + envelope * (
            10 * sin(2 * pi * (6.5 * t + phase))
            + 5 * sin(2 * pi * (13 * t + 0.3))
            + 7 * sin(2 * pi * (2 * t + phase))
        )
        points.append(f"{'M' if not points else 'L'}{x},{y:.2f}")
    return " ".join(points)


def hero_svg() -> str:
    grid = "".join(
        f'<path d="M{x} 88V248" />' for x in range(64, 1153, 32)
    ) + "".join(
        f'<path d="M48 {y}H1152" />' for y in range(88, 249, 32)
    )
    clusters = [
        ([(426, 134), (448, 112), (466, 145), (442, 164), (482, 124)], "#6EE7F9"),
        ([(545, 191), (564, 211), (587, 179), (610, 204), (575, 231)], "#58C7B1"),
        ([(633, 102), (653, 127), (674, 91), (693, 118), (670, 151)], "#D5E7F4"),
    ]
    points = []
    for coordinates, colour in clusters:
        for i, (x, y) in enumerate(coordinates):
            nx, ny = coordinates[(i + 1) % len(coordinates)]
            points.append(
                f'<path d="M{x} {y}L{nx} {ny}" stroke="{colour}" opacity=".23" />'
                f'<circle cx="{x}" cy="{y}" r="4" fill="{colour}" />'
            )
    signals = "\n".join(
        f'<path d="{signal_path(x0, x1, y, phase)}" stroke="{colour}" />'
        for x0, x1, y, phase, colour in [
            (740, 996, 126, 0.1, "#D5E7F4"),
            (724, 1010, 169, 0.45, "#6EE7F9"),
            (740, 996, 212, 0.8, "#58C7B1"),
        ]
    )
    contours = "".join(
        f'<ellipse cx="1089" cy="161" rx="{r}" ry="{r * 0.62:.1f}" '
        f'transform="rotate(-24 1089 161)" />'
        for r in [13, 24, 35, 46, 57, 68]
    )
    electrodes = "".join(
        f'<circle cx="{x}" cy="{y}" r="2.3" />'
        for x, y in [
            (1054, 127), (1081, 117), (1108, 127), (1037, 165),
            (1081, 169), (1125, 165), (1054, 205), (1081, 219), (1108, 205),
        ]
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="320" viewBox="0 0 1200 320" role="img" aria-labelledby="title desc">
  <title id="title">Davide Stefanelli — research engineering across visual and neural data</title>
  <desc id="desc">An original schematic, not an experimental result. A visual crop connects to embedding neighbourhoods and then to EEG traces and a scalp contour. A single pulse travels along this path for 4.5 seconds, then stops. All information remains visible without motion.</desc>
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, Consolas, "Liberation Mono", monospace; }}
    @media (prefers-reduced-motion: reduce) {{ .motion {{ display: none; }} }}
    @media (max-width: 600px) {{ text {{ font-size: 32px; letter-spacing: 1px; }} .micro {{ display: none; }} }}
  </style>
  <defs>
    <clipPath id="scalp"><circle cx="1081" cy="169" r="67" /></clipPath>
  </defs>
  <rect x="1" y="1" width="1198" height="318" rx="16" fill="#0B1320" stroke="#263D50" stroke-width="2" />
  <g stroke="#243C50" stroke-width="1" opacity=".35" fill="none">{grid}</g>
  <path d="M32 55H1168M32 274H1168" stroke="#263D50" />
  <g font-size="18" fill="#D5E7F4" letter-spacing="1.8">
    <text x="48" y="35">DS / RESEARCH ENGINEERING</text>
    <text class="micro" x="1152" y="35" text-anchor="end" fill="#8FAABD">BUILD · EVALUATE · REPRODUCE</text>
  </g>
  <g fill="none">
    <rect x="76" y="91" width="238" height="148" rx="4" fill="#101F2E" stroke="#36566F" />
    <path d="M77 205L113 174L147 184L187 143L229 183L267 160L313 189V238H77Z" fill="#1D3548" />
    <path d="M78 223L133 197L168 212L203 191L242 213L276 191L313 209" stroke="#496A80" />
    <circle cx="278" cy="119" r="9" stroke="#496A80" />
    <path d="M134 135V116H153M215 116H234V135M234 202V221H215M153 221H134V202" stroke="#6EE7F9" stroke-width="3" />
    <path d="M169 169H199M184 154V184" stroke="#6EE7F9" stroke-width="1.5" opacity=".6" />
    <path d="M234 169H330C368 169 380 157 411 157" stroke="#58C7B1" stroke-width="1.5" />
    <path d="M400 153L411 157L400 161" stroke="#58C7B1" stroke-width="1.5" />
  </g>
  <g stroke-width="1.3">{''.join(points)}</g>
  <g fill="none">
    <path d="M482 124L518 157L545 191M466 145L518 157L587 179" stroke="#6EE7F9" opacity=".48" />
    <circle cx="518" cy="157" r="30" stroke="#6EE7F9" stroke-dasharray="3 7" opacity=".5" />
    <circle cx="518" cy="157" r="12" fill="#0B1320" stroke="#6EE7F9" stroke-width="2" />
    <path d="M697 169H719M710 165L721 169L710 173" stroke="#58C7B1" stroke-width="1.5" />
    <g stroke-width="1.5" stroke-linejoin="round">{signals}</g>
    <circle cx="1081" cy="169" r="68" fill="#102633" stroke="#58C7B1" stroke-width="1.5" />
    <g clip-path="url(#scalp)" stroke="#58C7B1" opacity=".65">{contours}</g>
    <path d="M1074 101L1081 93L1088 101M1012 155Q1002 155 1002 169Q1002 183 1012 183M1150 155Q1160 155 1160 169Q1160 183 1150 183" stroke="#58C7B1" />
  </g>
  <g fill="#D5E7F4">{electrodes}</g>
  <g class="motion">
    <circle r="10" fill="#6EE7F9" opacity=".12" />
    <circle r="3.5" fill="#D5E7F4" />
    <animateMotion dur="4.5s" repeatCount="1" fill="freeze" path="M184 169H330C371 169 380 157 415 157H518C559 157 560 169 604 169H1011C1036 169 1055 169 1081 169" />
  </g>
  <g font-size="16" fill="#D5E7F4" letter-spacing="2">
    <text x="48" y="302">VISUAL DATA</text>
    <text class="micro" x="600" y="302" text-anchor="middle" font-size="12" fill="#8FAABD">SHARED METHODS. DIFFERENT MODALITIES.</text>
    <text x="1152" y="302" text-anchor="end">NEURAL DATA</text>
  </g>
</svg>
'''


def verified_source(sources_root: Path, key: str) -> Path:
    relative, expected = SOURCES[key]
    path = sources_root / relative
    if not path.is_file():
        raise FileNotFoundError(f"Source missing: {path}. See assets/ASSET_GUIDE.md.")
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(f"Unverified source: {path}\nExpected {expected}\nActual   {actual}")
    return path


def refresh_previews(sources_root: Path) -> None:
    from PIL import Image, ImageOps

    # Validate every input before writing any output.
    paths = {key: verified_source(sources_root, key) for key in SOURCES}
    resample = Image.Resampling.LANCZOS

    def rgb(key: str):
        with Image.open(paths[key]) as image:
            return image.convert("RGB")

    def save(image, name: str) -> None:
        # Fresh canvases/conversion deliberately exclude source EXIF and metadata.
        image.save(ASSETS / name, "WEBP", quality=86, method=6, exact=True)

    canvas = Image.new("RGB", (1200, 350), "#292929")
    topoplot = ImageOps.contain(rgb("topoplot"), (330, 326), resample)
    spectrum = ImageOps.contain(
        rgb("spectrum").crop((322, 28, 1854, 605)), (828, 326), resample
    )
    canvas.paste(topoplot, (12 + (330 - topoplot.width) // 2, (350 - topoplot.height) // 2))
    canvas.paste(spectrum, (360, (350 - spectrum.height) // 2))
    save(canvas, PREVIEWS[0])

    # Pz column only: standard, target, distractor. Retain labels, axes, colourbars.
    wavelets = rgb("wavelets")
    canvas = Image.new("RGB", (1200, 310), "white")
    for i, (top, bottom) in enumerate([(300, 1285), (1303, 2288), (2306, 3291)]):
        tile = ImageOps.contain(
            wavelets.crop((3890, top, 5480, bottom)), (392, 300), resample
        )
        canvas.paste(tile, (i * 400 + (400 - tile.width) // 2, (310 - tile.height) // 2))
    save(canvas, PREVIEWS[1])

    save(ImageOps.contain(rgb("rotation"), (1200, 500), resample), PREVIEWS[2])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh-evidence", action="store_true")
    parser.add_argument("--sources-root", type=Path, default=ROOT.parent)
    args = parser.parse_args()
    ASSETS.mkdir(exist_ok=True)
    if args.refresh_evidence:
        refresh_previews(args.sources_root.resolve())
    missing = [name for name in PREVIEWS if not (ASSETS / name).is_file()]
    if missing:
        raise FileNotFoundError(
            f"Missing committed previews: {', '.join(missing)}. "
            "Use --refresh-evidence with the documented source checkouts."
        )
    (ASSETS / NAMEPLATE_FILENAME).write_text(hero_svg(), encoding="utf-8", newline="\n")
    for name in (NAMEPLATE_FILENAME, *PREVIEWS):
        print(f"{name}: {(ASSETS / name).stat().st_size:,} bytes")


if __name__ == "__main__":
    main()
