# Asset Guide

The profile uses a self-contained SVG nameplate, native README content, and the existing scientific animations. All displayed image assets are local to this repository.

## Included assets

- `brain-candidates/Head-mri-animation.gif`
  Approved source MRI animation used for the primary clinical imaging panel.
- `brain-candidates/Brainanim-FreeSurfer.gif`
  Approved source cortical surface animation used for the secondary research panel.
- `profile-nameplate.svg`
  Animated SVG nameplate used at the very top of the profile README.
- `brain-turntable.png`
  Historical ImageGen 4×4 sheet, retained for reference; no longer used by the banner.
- `brain-turntable-stable.png`, `brain-turntable-stable.json`
  Active 12×10 sheet and playback metadata: 120 deterministic surface renders, each 80×80 pixels.
- `brain-turntable-stable.gif`
  Standalone 320×320 nearest-neighbor GIF export of the same animation for review and reuse.
- `head-mri-panel.gif`
  Optimized display derivative for the primary MRI panel in the README hero.
- `freesurfer-panel.gif`
  Optimized display derivative for the secondary FreeSurfer panel in the README hero.
- `signal-divider.gif`
  Reusable hero EEG divider used between major README sections.
- `signal-divider-eeg-alpha.gif`
  Optional alternate-seed variant using the same hero EEG divider renderer.
- `signal-divider-eeg-clinical.gif`
  Optional alternate-seed variant using the same hero EEG divider renderer.
- `signal-divider-eeg-evoked.gif`
  Optional alternate-seed variant using the same hero EEG divider renderer.
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
  Authored in `scripts/generate_nameplate.py`: pixel typography, cyan/lavender gradient, stepped light sweep, rotating pixel-art brain, and a decorative signal trace. `scripts/pixel_lettering.py` defines the name as custom 5×7 glyphs, drawn with 12-unit square pixels, top-edge highlights and a lavender offset shadow. The name is SVG path geometry, with no font dependency; the accessible SVG title preserves the full name. Supporting labels use Segoe UI / Helvetica / Arial and monospace fallbacks. `scripts/brain_sprite.py` embeds the active PNG sheet as a data URL and reads its dimensions and timing from the accompanying JSON: 120 cells in a 4.8-second CSS loop (25 fps). No external fonts, JavaScript, or runtime image services.
- `brain-turntable-stable.png`, `brain-turntable-stable.gif`
  Rendered by `scripts/render_brain_turntable.py` from the left/right pial surfaces and sulcal maps of the standard FreeSurfer fsaverage template distributed by MNE. Source: [MNE fsaverage dataset](https://mne.tools/stable/generated/mne.datasets.fetch_fsaverage.html), [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/). The local template previously downloaded for NeuroScope supplies the geometry; no individual participant data or ImageGen frames are used. The renderer applies a stylized blue/cyan palette; this is decorative anatomical visualization, not a result from a featured project.
- `brain-turntable.png`
  Created for this profile with the built-in ImageGen tool. Decorative stylized artwork, not an anatomical reference or project output. No Wikimedia source material was used for this new asset. The generation brief is saved in `assets/brain-turntable-prompt.txt`. The original PNG is preserved unchanged; the SVG crops frames at display time.
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

The GIF pipeline uses Pillow; the SVG nameplate is emitted with Python string generation only. No network access is required. To regenerate only the nameplate, run `python scripts/generate_nameplate.py`. The full generator delegates to the same implementation.

To rebuild the stable brain sequence, install NumPy, Numba and Pillow and run:

```bash
python scripts/render_brain_turntable.py --subjects-dir PATH_TO_FSAVERAGE_PARENT
python scripts/generate_nameplate.py
```

The supplied directory must contain `fsaverage/surf/lh.pial`, `rh.pial`, `lh.sulc`, and `rh.sulc`. Source mesh files are not bundled. Ordinary banner regeneration uses the checked-in PNG/JSON and requires only the Python standard library.

The scientific renderer uses one fixed 3D pivot, orthographic scale, camera and light for all 120 equally spaced angles. It never crops, rescales or centers individual views. Pixelation comes from an 80×80 render grid and nearest-neighbor display. `output/brain-animation-qa.json` records clipping checks and adjacent-frame differences, including the loop seam; `output/brain-stable-contact-sheet.png` shows eight views.

## GitHub rendering and motion

- The public README pins the banner URL to the commit containing the approved image, avoiding stale images served for the mutable `main` URL. After publishing a new banner asset, update this commit reference. The local preview maps it back to the working-copy SVG so design changes remain immediately visible.

- GitHub removes scripts and page styles from README HTML. Animation lives inside the linked SVG image; the README itself uses ordinary Markdown and supported HTML. See [GitHub's rendering pipeline](https://github.com/github/markup).
- The name stays visible throughout the animation. The SVG disables motion for `prefers-reduced-motion: reduce`; the existing GIFs do not respond to that preference.
- The rotating brain uses a raster sprite sheet inside an SVG, not an embedded external GIF. SVG images cannot fetch external image resources in image context, but can use embedded data URLs: [MDN SVG as an image](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image). The complete banner is approximately 245 KB, versus 2.5 MB with the historical generated sheet; it keeps the existing animated vector lettering and avoids external requests.
- MRI and cortical-surface GIFs are illustrative source material, not outputs produced by the featured repositories. Their source credits above remain applicable.
- Unused historical assets are retained for future iterations.

## Local preview

Run `python scripts/preview_readme.py` (requires `markdown-it-py`), then `python -m http.server 8765 --bind 127.0.0.1` and open `http://127.0.0.1:8765/output/profile-preview.html`.

The preview offers light/dark and narrow-width controls. Its CSS approximates GitHub; it does not reproduce GitHub's sanitizer or image proxy. Generated preview files are ignored by Git.
