"""Generate the banner-style SVG separator with no runtime dependencies."""
from pathlib import Path

if __package__:
    from .signal_art import SIGNAL_CSS, signal_path
else:
    from signal_art import SIGNAL_CSS, signal_path


def build_signal_divider(destination: Path) -> None:
    wave = signal_path(36)
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="72" viewBox="0 0 1200 72" role="img" aria-labelledby="title">
<title id="title">Decorative signal separator</title>
<style>{SIGNAL_CSS}</style>
<path d="{wave}" fill="none" stroke="#72dce7" stroke-opacity=".35" stroke-width="2"/>
<path d="{wave}" fill="none" stroke="#a1f4ff" stroke-opacity=".85" stroke-width="2.6" class="pulse"/>
</svg>
'''
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(svg, encoding='utf-8')


if __name__ == '__main__':
    build_signal_divider(Path(__file__).resolve().parents[1] / 'assets' / 'signal-divider.svg')
