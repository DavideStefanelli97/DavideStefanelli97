# Asset Guide

This README now uses an SVG nameplate plus an MRI-led dashboard assembled directly in `README.md`, rather than a single raster hero banner.

## Included assets

- `brain-candidates/Head-mri-animation.gif`
  Approved source MRI animation used for the primary clinical imaging panel.
- `brain-candidates/Brainanim-FreeSurfer.gif`
  Approved source cortical surface animation used for the secondary research panel.
- `profile-nameplate.svg`
  Animated SVG nameplate used at the very top of the profile README.
- `head-mri-panel.gif`
  Optimized display derivative for the primary MRI panel in the README hero.
- `freesurfer-panel.gif`
  Optimized display derivative for the secondary FreeSurfer panel in the README hero.
- `signal-divider.gif`
  Reusable divider used between major README sections.
- `signal-divider-eeg-alpha.gif`
  Optional divider variant with a smoother alpha-rhythm style EEG trace.
- `signal-divider-eeg-clinical.gif`
  Optional divider variant with stacked multi-trace clinical EEG styling.
- `signal-divider-eeg-evoked.gif`
  Optional divider variant with evoked-response style spikes and event markers.
- `console-band.svg`
  Static SVG band summarizing the main technical directions of the profile.

## Provenance

- `brain-candidates/Head-mri-animation.gif`
  Downloaded from Wikimedia Commons file `Head mri animation.gif`.
  Source page: `https://commons.wikimedia.org/wiki/File:Head_mri_animation.gif`
  License note: public domain, released by the author.
- `brain-candidates/Brainanim-FreeSurfer.gif`
  Downloaded from Wikimedia Commons file `Brainanim.gif`, described there as a rotating view of a left hemisphere pial surface with Desikan-Killiany atlas parcellation constructed in FreeSurfer and rendered in FreeView.
  Source page: `https://commons.wikimedia.org/wiki/File:Brainanim.gif`
  License note: CC BY-SA 4.0. Keep attribution and share-alike requirements attached to the source file and to derivatives.
- `profile-nameplate.svg`
  Generated locally by `scripts/generate_assets.py` from a repository-defined bitmap glyph map and inline SVG animation layers.
- `head-mri-panel.gif`
  Generated locally from `brain-candidates/Head-mri-animation.gif` by `scripts/generate_assets.py`.
- `freesurfer-panel.gif`
  Generated locally from `brain-candidates/Brainanim-FreeSurfer.gif` by `scripts/generate_assets.py`.
- `signal-divider.gif`
  Generated locally by `scripts/generate_assets.py`.
- `signal-divider-eeg-alpha.gif`
  Generated locally by `scripts/generate_assets.py`.
- `signal-divider-eeg-clinical.gif`
  Generated locally by `scripts/generate_assets.py`.
- `signal-divider-eeg-evoked.gif`
  Generated locally by `scripts/generate_assets.py`.
- `console-band.svg`
  Custom SVG authored in this repository. The circuit-trace visual language was informed by BGJar's circuit-board generator as a reference direction, but the final asset is local and authored here.

## Regeneration

Generate the current motion assets with:

```bash
python scripts/generate_assets.py
```

The GIF pipeline uses Pillow; the SVG nameplate is emitted with Python string generation only. No network access is required.

## Notes

- The hero is now built directly in `README.md` using a generated SVG nameplate plus HTML tables and generated panel GIFs.
- `scripts/generate_assets.py` now emits the top SVG nameplate alongside the reusable support GIF assets and optimized panel derivatives.
- Multiple EEG-style divider variants are generated so the README can switch visual tone without reworking the page structure.
- If the MRI panel still feels too heavy on the live profile page, reduce the frame count or panel width in the generator rather than swapping out the approved source asset.
