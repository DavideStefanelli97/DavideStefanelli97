# Asset Guide

This profile package uses a hybrid asset model:

- Local static SVGs provide the dark HUD shells that keep the README visually consistent on GitHub light and dark themes.
- Local GIFs carry the high-motion pieces because GitHub does not reliably support local SVG animation.
- External SVG endpoints provide live telemetry cards and typing effects.

## Included assets

- `hero-neural.gif`
  The main cinematic banner used in the hero section.
- `divider-signal.gif`
  The animated waveform divider used between major sections.
- `boot-panel.svg`
  A static system-boot panel with terminal framing and telemetry copy.
- `radar-panel.svg`
  A static capability radar visual for the interface section.
- `footer-standby.svg`
  The closing transmission panel.

## Generation

The GIFs are generated locally from `scripts/generate_assets.py`.

```bash
python scripts/generate_assets.py
```

The script uses Pillow only. No network access or external media downloads are required.

## If you want to iterate later

- Change palette values and frame counts in `scripts/generate_assets.py`.
- Replace the static SVG text directly in the `.svg` files if you want different panel language.
- If the public stats endpoints become unreliable, self-host `github-readme-stats` or render cards into this repo with GitHub Actions.
