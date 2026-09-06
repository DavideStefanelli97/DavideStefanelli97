"""Generate the profile SVG: python scripts/generate_nameplate.py.

Self-contained vector art: no external fonts, JavaScript or dependencies.
"""
from pathlib import Path


def build_nameplate_svg(destination: Path) -> None:
    if __package__:
        from .brain_sprite import brain_sprite
        from .pixel_lettering import lettering_paths
        from .signal_art import signal_path
    else:
        from brain_sprite import brain_sprite
        from pixel_lettering import lettering_paths
        from signal_art import signal_path
    wave = signal_path()
    brain_css, brain_markup = brain_sprite()
    letter_path, highlight_path = lettering_paths()
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="420" viewBox="0 0 1200 420" role="img" aria-labelledby="title desc">
<title id="title">Davide Stefanelli</title>
<desc id="desc">Computer Vision, Machine Learning and Biomedical Engineering. Cyan and lavender pixel lettering with a stepped light sweep, signal trace, and a rotating pixel-art brain.</desc>
<defs>
  <linearGradient id="bg" x2="1" y2="1"><stop stop-color="#080f1c"/><stop offset="1" stop-color="#102638"/></linearGradient>
  <radialGradient id="halo"><stop stop-color="#237785" stop-opacity=".25"/><stop offset="1" stop-color="#237785" stop-opacity="0"/></radialGradient>
  <linearGradient id="ink" x1="0" x2="1" y2=".25"><stop stop-color="#f0f8ff"/><stop offset=".42" stop-color="#8aeaff"/><stop offset="1" stop-color="#b9a4ff"/></linearGradient>
  <linearGradient id="shine"><stop stop-color="white" stop-opacity="0"/><stop offset=".5" stop-color="white" stop-opacity=".85"/><stop offset="1" stop-color="white" stop-opacity="0"/></linearGradient>
  <pattern id="grid" width="32" height="32" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="#a1cfdf" opacity=".10"/></pattern>
  <filter id="glow" x="-30%" y="-50%" width="160%" height="200%"><feGaussianBlur stdDeviation="4"/></filter>
  <path id="name" d="__LETTER_PATH__"/>
  <clipPath id="letters"><use href="#name"/></clipPath>
  <clipPath id="panel"><rect x="1" y="1" width="1198" height="418" rx="22"/></clipPath>
</defs>
<style>
  .sweep { animation:sweep 7s steps(48,end) infinite; }
  __BRAIN_CSS__
  .pulse { stroke-dasharray:90 1800; animation:signal 9s linear infinite; }
  @keyframes sweep { 0%,18% { transform:translateX(-260px); } 64%,100% { transform:translateX(1100px); } }
  @keyframes signal { from { stroke-dashoffset:1890; } to { stroke-dashoffset:0; } }
  @media (prefers-reduced-motion: reduce) {
    .sweep { display:none; }
    .pulse { animation:none; }
  }
</style>
<g clip-path="url(#panel)">
  <rect width="1200" height="420" fill="url(#bg)"/>
  <rect width="1200" height="420" fill="url(#grid)"/>
  <ellipse cx="986" cy="208" rx="370" ry="270" fill="url(#halo)"/>
  <path d="M62 52H91" stroke="#79e6ee" stroke-width="3"/>
  <text x="106" y="58" fill="#aec4d8" font-family="Consolas, monospace" font-size="17" letter-spacing="3">VISION / LEARNING / NEUROSCIENCE</text>
  __BRAIN_MARKUP__
  <circle cx="972" cy="194" r="132" stroke="#94cbdf" stroke-opacity=".09" fill="none"/>
  <circle cx="972" cy="194" r="167" stroke="#94cbdf" stroke-opacity=".06" fill="none"/>
  <use href="#name" fill="#6fdde9" opacity=".12" filter="url(#glow)"/>
  <use href="#name" fill="#7563c2" opacity=".4" transform="translate(4 4)" shape-rendering="crispEdges"/>
  <use href="#name" fill="url(#ink)" shape-rendering="crispEdges"/>
  <path d="__HIGHLIGHT_PATH__" fill="#e4ffff" opacity=".28" shape-rendering="crispEdges"/>
  <g clip-path="url(#letters)"><path d="M-160 84h96v48h24v48h24v48h24v72h-96v-48h-24v-48h-24v-48h-24z" fill="url(#shine)" class="sweep"/></g>
  <path d="__WAVE__" fill="none" stroke="#72dce7" stroke-opacity=".19" stroke-width="1.5"/>
  <path d="__WAVE__" fill="none" stroke="#a1f4ff" stroke-opacity=".7" stroke-width="2" class="pulse"/>
  <text x="62" y="392" fill="#a8c3d8" font-family="Segoe UI, Helvetica, Arial, sans-serif" font-size="20">From brain signals to intelligent systems.</text>
  <text x="1138" y="392" text-anchor="end" fill="#829caf" font-family="Consolas, monospace" font-size="15" letter-spacing="2">DS / RESEARCH + ENGINEERING</text>
</g>
<rect x="1" y="1" width="1198" height="418" rx="22" fill="none" stroke="#284555"/>
</svg>
'''
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(svg.replace("__BRAIN_CSS__", brain_css).replace("__BRAIN_MARKUP__", brain_markup).replace("__WAVE__", wave).replace("__LETTER_PATH__", letter_path).replace("__HIGHLIGHT_PATH__", highlight_path), encoding="utf-8")


if __name__ == "__main__":
    build_nameplate_svg(Path(__file__).resolve().parents[1] / "assets" / "profile-nameplate.svg")
