"""Shared decorative waveform for the profile banner and section dividers."""
from math import sin


def signal_path(baseline: float = 342) -> str:
    return ' '.join(
        f"{'M' if x == 0 else 'L'}{x},{baseline + 7*sin(x/19) + 4*sin(x/7) + 15*sin(x/38)*sin(x/13):.2f}"
        for x in range(0, 1201, 3)
    )


SIGNAL_CSS = '''.pulse { stroke-dasharray:90 1800; animation:signal 9s linear infinite; }
@keyframes signal { from { stroke-dashoffset:1890; } to { stroke-dashoffset:0; } }
@media (prefers-reduced-motion: reduce) { .pulse { animation:none; } }'''
