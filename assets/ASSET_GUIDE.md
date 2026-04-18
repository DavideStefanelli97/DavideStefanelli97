# Asset Guide

This README now uses an MRI-led dashboard assembled directly in `README.md`, rather than a single generated hero banner.

## Included assets

- `brain-candidates/Head-mri-animation.gif`
  Approved source MRI animation used for the primary clinical imaging panel.
- `brain-candidates/Brainanim-FreeSurfer.gif`
  Approved source cortical surface animation used for the secondary research panel.
- `head-mri-panel.gif`
  Optimized display derivative for the primary MRI panel in the README hero.
- `freesurfer-panel.gif`
  Optimized display derivative for the secondary FreeSurfer panel in the README hero.
- `signal-divider.gif`
  Reusable divider used between major README sections.
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
- `head-mri-panel.gif`
  Generated locally from `brain-candidates/Head-mri-animation.gif` by `scripts/generate_assets.py`.
- `freesurfer-panel.gif`
  Generated locally from `brain-candidates/Brainanim-FreeSurfer.gif` by `scripts/generate_assets.py`.
- `signal-divider.gif`
  Generated locally by `scripts/generate_assets.py`.
- `console-band.svg`
  Custom SVG authored in this repository. The circuit-trace visual language was informed by BGJar's circuit-board generator as a reference direction, but the final asset is local and authored here.

## Regeneration

Generate the current motion assets with:

```bash
python scripts/generate_assets.py
```

The script uses Pillow only and does not require network access.

## Notes

- The hero is now built directly in `README.md` using HTML tables and the generated panel GIFs.
- `scripts/generate_assets.py` no longer composes a full hero banner. It only prepares reusable support assets and optimized panel derivatives.
- If the MRI panel still feels too heavy on the live profile page, reduce the frame count or panel width in the generator rather than swapping out the approved source asset.
