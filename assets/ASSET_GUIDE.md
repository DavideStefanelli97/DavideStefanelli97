# Asset Guide

This README uses a smaller and more technical asset set than the previous version.

## Included assets

- `hero-console.gif`
  Locally generated hero banner for the top of the profile. It blends AI, EEG, and medical imaging cues into a restrained engineering-console visual.
- `signal-divider.gif`
  Locally generated section divider used to separate major blocks with a single reusable telemetry line.
- `console-band.svg`
  Static SVG band used to summarize the three main research directions: representation learning, EEG/BCI signals, and medical imaging/computer vision.
- `telemetry-gauge.gif`
  Small telemetry indicator used near the hero badges.

## Provenance

- `hero-console.gif`
  Custom asset generated in this repository from `scripts/generate_assets.py`.
- `signal-divider.gif`
  Custom asset generated in this repository from `scripts/generate_assets.py`.
- `console-band.svg`
  Custom SVG authored in this repository. The circuit-trace visual language was informed by BGJar's circuit-board generator as a reference direction, but the final asset is local and authored here.
- `telemetry-gauge.gif`
  Downloaded from Loading.io's free `gauge` spinner sample and palette-adjusted locally to match the README color system.
  Source sample URL: `https://loading.io/assets/mod/spinner/gauge/sample.gif`
  License note: Loading.io's free license states that free-license items can be used without attribution.

## Regeneration

Generate the local motion assets with:

```bash
python scripts/generate_assets.py
```

The script uses Pillow only and does not require network access.

## Notes

- The README intentionally avoids large decorative panel assets. Most of the visual identity now comes from layout, restrained motion, and real repository content.
- If the Loading.io telemetry asset is replaced later, record the new source and license here.
