# Asset Guide

The profile uses a Dense ASCII animated GIF nameplate, native README content, and the existing scientific animations. All displayed image assets are local to this repository.

## Included assets

- `brain-candidates/Head-mri-animation.gif`
  Approved source MRI animation used for the primary clinical imaging panel.
- `brain-candidates/Brainanim-FreeSurfer.gif`
  Approved source cortical surface animation used for the secondary research panel.
- `davide-stefanelli-dense-ascii.gif`
  Active nameplate at the top of the profile README. The first frame shows the complete name, followed by the letter-drop loop.
- `terminal-intro.gif`
  Animated terminal introduction below the nameplate. Its first frame shows the full role and location text.
- `profile-nameplate.svg`
  Previous SVG nameplate, retained for reference.
- `brain-turntable.png`
  Historical ImageGen 4×4 sheet, retained for reference; no longer used by the banner.
- `brain-turntable-stable.png`, `brain-turntable-stable.json`
  Active 12×10 sheet and playback metadata: 120 deterministic surface renders, each 80×80 pixels.
- `brain-turntable-stable.gif`
  Standalone 320×320 nearest-neighbor GIF export of the same animation for review and reuse.
- `brain-turntable-ascii-blue.gif`, `brain-turntable-ascii-palette.gif`
  Two 480×481 ASCII GIF derivatives of the 120-frame brain turntable. The blue version preserves the approved first ASCII result; the second uses the green, orange, coral, violet, and gold colors of the Dense ASCII nameplate and is displayed beside the contact links in the README.
- `ascii-links/linkedin.gif`, `ascii-links/email.gif`, `ascii-links/projects.gif`
  Three independent animated ASCII link cards, displayed to the right of the brain in the README. The entire image of each card is a link.
- `head-mri-panel.gif`
  Optimized display derivative for the primary MRI panel in the README hero.
- `freesurfer-panel.gif`
  Optimized display derivative for the secondary FreeSurfer panel in the README hero.
- `signal-divider.svg`
  Active section separator above and below Selected projects. Uses the banner's decorative waveform on a transparent background and the same 9-second light-pulse loop, with slightly stronger strokes for standalone readability.
- `signal-divider.gif`
  Historical GIF separator, retained as a source asset but no longer displayed in the README.
- `signal-divider-eeg-alpha.gif`
  Optional alternate-seed variant using the same hero EEG divider renderer.
- `signal-divider-eeg-clinical.gif`
  Optional alternate-seed variant using the same hero EEG divider renderer.
- `signal-divider-eeg-evoked.gif`
  Optional alternate-seed variant using the same hero EEG divider renderer.
- `console-band.svg`
  Static SVG band summarizing the main technical directions of the profile.

## Provenance

- `projects/eeg-erp-topomaps.png`, `projects/eeg-time-frequency.png`
  Unmodified copies of `outputs/figures/group/stage03/04_stage03_ga_topomaps.png` and `outputs/figures/group/stage04/01_stage04_ga_tf_focus_channels.png` from the local MATLAB-EEG-Processing-Pipeline repository (HEAD at selection: `64ba7e2a58f96d54dd72f515dad6e50c4b880bdf`). These are project outputs, showing grand-average ERP scalp maps and Morlet time–frequency maps. The full-resolution figures remain clickable; the second figure is inside a README details panel.
- `projects/imaging-ventricle-evolution.gif`, `projects/imaging-atrium-slices.gif`
  Unmodified copies of `results/seg_ventricles/evolution_lv.gif` and `results/seg_left_atrium_3d/segmentation_slices.gif` from the local Medical-Imaging-Analysis checkout, named `Smart Medical Imaging` (HEAD at selection: `f3ba850c391af33f913fee97da81297d46d9270f`). These are project outputs: left-ventricle level-set evolution and a traversal of segmented left atrium MRI slices. Original frames, timing, palettes and loop settings are preserved. The second animation shows slice progression, not optimization iterations.
- `brain-candidates/Head-mri-animation.gif`
  Downloaded from Wikimedia Commons file `Head mri animation.gif`.
  Source page: `https://commons.wikimedia.org/wiki/File:Head_mri_animation.gif`
  License note: public domain, released by the author.
- `brain-candidates/Brainanim-FreeSurfer.gif`
  Downloaded from Wikimedia Commons file `Brainanim.gif`, described there as a rotating view of a left hemisphere pial surface with Desikan-Killiany atlas parcellation constructed in FreeSurfer and rendered in FreeView.
  Source page: `https://commons.wikimedia.org/wiki/File:Brainanim.gif`
  License note: CC BY-SA 4.0. Keep attribution and share-alike requirements attached to the source file and to derivatives.
- `davide-stefanelli-dense-ascii.gif`, `scripts/davide-stefanelli-dense-ascii.html`
  The GIF was exported from the approved local HTML preview at 20 fps using `scripts/export_dense_ascii_gif.py` and `scripts/export_dense_frames.js`. The preview adapts [ASCII Magic's Bouncing Letters piece](https://github.com/kailashsr38/ascii-magic-art/blob/main/pieces/bouncing-letters.js) with the text “DAVIDE STEFANELLI” and uses its [Dense ASCII glyph renderer](https://github.com/kailashsr38/ascii-magic-art/blob/main/runtime/glyphs.js). Copyright (c) 2026 ASCII Magic (ascii-magic.com); [MIT license](../scripts/ASCII_MAGIC_LICENSE). The preview source is retained so the export can be regenerated.
- `profile-nameplate.svg`
  Authored in `scripts/generate_nameplate.py`: pixel typography, cyan/lavender gradient, stepped light sweep, rotating pixel-art brain, and a decorative signal trace. `scripts/pixel_lettering.py` defines the name as custom 5×7 glyphs, drawn with 12-unit square pixels, top-edge highlights and a lavender offset shadow. The name is SVG path geometry, with no font dependency; the accessible SVG title preserves the full name. Supporting labels use Segoe UI / Helvetica / Arial and monospace fallbacks. `scripts/brain_sprite.py` embeds the active PNG sheet as a data URL and reads its dimensions and timing from the accompanying JSON: 120 cells in a 4.8-second CSS loop (25 fps). No external fonts, JavaScript, or runtime image services.
- `brain-turntable-stable.png`, `brain-turntable-stable.gif`
  Rendered by `scripts/render_brain_turntable.py` from the left/right pial surfaces and sulcal maps of the standard FreeSurfer fsaverage template distributed by MNE. Source: [MNE fsaverage dataset](https://mne.tools/stable/generated/mne.datasets.fetch_fsaverage.html), [FreeSurfer](https://surfer.nmr.mgh.harvard.edu/). The local template previously downloaded for NeuroScope supplies the geometry; no individual participant data or ImageGen frames are used. The renderer applies a stylized blue/cyan palette; this is decorative anatomical visualization, not a result from a featured project.
- `brain-turntable-ascii-blue.gif`, `brain-turntable-ascii-palette.gif`
  Rendered by `scripts/render_ascii_brain.py` from `brain-turntable-stable.gif`. Each source frame is sampled into a 60×37 character grid; glyph density follows the original shading. The palette version recolors those glyphs with the nameplate colors while retaining the source luminance for cortical relief. Both are decorative derivatives of the fsaverage rendering described above.
- `ascii-links/linkedin.gif`, `ascii-links/email.gif`, `ascii-links/projects.gif`
  Generated locally by `scripts/generate_ascii_link_cards.py` with Pillow and Windows Consolas. Each card has a 4.8-second ASCII border pulse, matching the brain GIF loop. No external art assets are used.
- `terminal-intro.gif`
  Generated locally by `scripts/generate_terminal_intro.py` with Pillow and Windows Consolas. It types the existing role, location, and education details as colored terminal output, inspired by the presentation of [Infra Plan and Apply](https://www.ascii-magic.com/ascii/infra-plan-diff); its code and frames are authored for this profile.
- `brain-turntable.png`
  Created for this profile with the built-in ImageGen tool. Decorative stylized artwork, not an anatomical reference or project output. No Wikimedia source material was used for this new asset. The generation brief is saved in `assets/brain-turntable-prompt.txt`. The original PNG is preserved unchanged; the SVG crops frames at display time.
- `head-mri-panel.gif`
  Generated locally from `brain-candidates/Head-mri-animation.gif` by `scripts/generate_assets.py`.
- `freesurfer-panel.gif`
  Generated locally from `brain-candidates/Brainanim-FreeSurfer.gif` by `scripts/generate_assets.py`.
- `signal-divider.svg`
  Generated by `scripts/generate_signal_divider.py` from the same `scripts/signal_art.py` waveform function used by the banner. Decorative signal, not measured EEG. No external assets; respects reduced-motion settings.
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

Generate the existing scientific and divider motion assets with:

```bash
python scripts/generate_assets.py
```

To regenerate the Dense ASCII nameplate, install Node.js and Pillow, then run `python scripts/export_dense_ascii_gif.py scripts/davide-stefanelli-dense-ascii.html` on Windows. The export takes its characters, colors, and motion directly from the approved preview. The rendering font is Windows Consolas.

To regenerate either ASCII brain variant on Windows with Pillow installed, run `python scripts/render_ascii_brain.py --variant blue` or `python scripts/render_ascii_brain.py --variant palette`. These exports use the checked-in brain GIF and Windows Consolas; they do not need the FreeSurfer mesh files.

To regenerate the contact cards, run `python scripts/generate_ascii_link_cards.py` on Windows with Pillow installed.

To regenerate the terminal introduction, run `python scripts/generate_terminal_intro.py` on Windows with Pillow installed.

The existing asset pipeline uses Pillow; the historical SVG nameplate is emitted with Python string generation only. No network access is required. To regenerate that SVG alone, run `python scripts/generate_nameplate.py`. The full generator delegates to the same implementation.

To regenerate only the section separator, run `python scripts/generate_signal_divider.py`. It is also included in the full asset build.

To rebuild the stable brain sequence, install NumPy, Numba and Pillow and run:

```bash
python scripts/render_brain_turntable.py --subjects-dir PATH_TO_FSAVERAGE_PARENT
python scripts/generate_nameplate.py
```

The supplied directory must contain `fsaverage/surf/lh.pial`, `rh.pial`, `lh.sulc`, and `rh.sulc`. Source mesh files are not bundled. Ordinary banner regeneration uses the checked-in PNG/JSON and requires only the Python standard library.

The scientific renderer uses one fixed 3D pivot, orthographic scale, camera and light for all 120 equally spaced angles. It never crops, rescales or centers individual views. Pixelation comes from an 80×80 render grid and nearest-neighbor display. `output/brain-animation-qa.json` records clipping checks and adjacent-frame differences, including the loop seam; `output/brain-stable-contact-sheet.png` shows eight views.

## GitHub rendering and motion

- GitHub removes scripts and page styles from README HTML. The Dense ASCII animation is an ordinary linked GIF image; the README itself uses supported HTML. See [GitHub's rendering pipeline](https://github.com/github/markup).
- The contact table has one HTML row containing the brain and three linked images. Keeping all cards in the same cell avoids GitHub's alternating table-row background behind the Email card.
- The GIF loops in 9.5 seconds. Its first frame shows the complete name. As with the other GIFs in the README, it cannot respond to `prefers-reduced-motion`.
- The historical SVG nameplate uses a raster sprite sheet inside an SVG. SVG images cannot fetch external image resources in image context, but can use embedded data URLs: [MDN SVG as an image](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image).
- MRI and cortical-surface GIFs are illustrative source material, not outputs produced by the featured repositories. Their source credits above remain applicable.
- Unused historical assets are retained for future iterations.

## Local preview

Run `python scripts/preview_readme.py` (requires `markdown-it-py`), then `python -m http.server 8765 --bind 127.0.0.1` and open `http://127.0.0.1:8765/output/profile-preview.html`.

The preview offers light/dark and narrow-width controls. Its CSS approximates GitHub; it does not reproduce GitHub's sanitizer or image proxy. Generated preview files are ignored by Git.
