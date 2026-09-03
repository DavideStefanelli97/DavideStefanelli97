# README visual system

The profile is an editorial research portfolio, not a metrics dashboard. Its visual idea is a **cross-domain instrument trace**: a visual crop, an embedding neighbourhood and neural signals, connected by one measured movement.

The README uses only local images, in a vertical flow. Important claims, results, contacts and project names remain selectable Markdown text. No external widget, font, script or image-generation service is needed to read it.

## Current assets

| File | Dimensions | Purpose |
| --- | --- | --- |
| [profile-nameplate-clean.svg](profile-nameplate-clean.svg) | 1200 × 320 | Original schematic hero; one 4.5-second pulse |
| [work-neuroscope.webp](work-neuroscope.webp) | 1200 × 350 | Synthetic-demo topography and filter spectrum |
| [work-eeg-pipeline.webp](work-eeg-pipeline.webp) | 1200 × 310 | Three Pz time–frequency panels from the public pipeline |
| [work-medical-imaging.webp](work-medical-imaging.webp) | 1200 × 491 | Public rotation-search metric curves |

The combined image payload is under **90 KiB**, including the animation. Run the generator to print exact byte sizes. Each WebP contains one static frame, without EXIF metadata. The SVG uses vector motion rather than raster frames.

The palette is graphite `#0B1320`, cold white `#D5E7F4`, cyan `#6EE7F9` and teal `#58C7B1`, with muted blue-grey for secondary marks. Scientific plots retain their original colour scales: they are evidence, not brand decoration.

### Hero and accessibility

The hero is authored deterministically in [generate_assets.py](../scripts/generate_assets.py). It is **not a model output, measured embedding space, patient recording or anatomical reconstruction**. The crop, points, traces and contour are deliberately schematic.

The pulse plays once for 4.5 seconds and stops. The complete diagram is visible from the first frame, and `prefers-reduced-motion: reduce` hides the moving element. There is no flashing, looping GIF, external font, JavaScript or remote resource. At narrow image widths, primary labels enlarge and secondary labels disappear; all essential meaning is also in the README text and image alt description.

The existing user-selected filename `profile-nameplate-clean.svg` is preserved. The former pixel nameplate, multiple GIF panels and widget wall are no longer part of the page.

## Evidence provenance

### NEURO-SCOPE

- Source: [NEURO-SCOPE](https://github.com/DavideStefanelli97/NEURO-SCOPE), commit `ddc57706053a4f502ad7f44d7a1a360fec00ae5b`.
- Inputs: `docs/assets/topoplot-window.png` and `docs/assets/filter-compare.png`, described in the [interface tour](https://github.com/DavideStefanelli97/NEURO-SCOPE/blob/main/docs/INTERFACE_TOUR.md).
- Author / licence: Davide Stefanelli, 2026; [MIT](https://github.com/DavideStefanelli97/NEURO-SCOPE/blob/main/LICENSE).
- Treatment: retain the topoplot; crop the filter-comparison window to the PSD chart; resize and arrange on a neutral canvas. No scientific values or plot colours are changed.
- Context: the project's synthetic demonstration, not a participant or clinical result.

### MATLAB EEG Processing Pipeline

- Source: [MATLAB EEG Processing Pipeline](https://github.com/DavideStefanelli97/MATLAB-EEG-Processing-Pipeline), commit `64ba7e2a58f96d54dd72f515dad6e50c4b880bdf`.
- Input: [public stage-four figure](https://github.com/DavideStefanelli97/MATLAB-EEG-Processing-Pipeline/blob/main/outputs/figures/sub-035/stage04/01_stage04_subject_tf_focus_channels.png).
- Author / licence: DavideStefanelli97, 2025; [MIT](https://github.com/DavideStefanelli97/MATLAB-EEG-Processing-Pipeline/blob/main/LICENSE).
- Treatment: crop the Pz column into standard, target and distractor panels, align and resize. Original titles, axes and colour bars are retained. The colour scale is −6 to +6 dB, as specified by the source figure.
- Context: an already-public, pseudonymised subject-level diagnostic. No raw EEG, participant identifiers, acquisition files or new experimental result are included. Full reproduction needs the [documented external inputs](https://github.com/DavideStefanelli97/MATLAB-EEG-Processing-Pipeline/blob/main/docs/data_manifest.md).

### Medical Imaging Analysis

- Source: [Medical Imaging Analysis](https://github.com/DavideStefanelli97/Medical-Imaging-Analysis), commit `f3ba850c391af33f913fee97da81297d46d9270f`.
- Input: [rotation metric trends](https://github.com/DavideStefanelli97/Medical-Imaging-Analysis/blob/master/results/reg_rotation/metric_trends.jpg), with its [case-study report](https://github.com/DavideStefanelli97/Medical-Imaging-Analysis/blob/master/results/reg_rotation/REPORT.md).
- Author / licence: Davide Stefanelli, 2025; [MIT](https://github.com/DavideStefanelli97/Medical-Imaging-Analysis/blob/master/LICENSE).
- Treatment: downsample only. No patient image pixels, DICOM metadata or changed plot values are included.
- Context: a numerical registration case study using a synthetically rotated copy of one MRI slice, not a clinical validation or segmentation benchmark.

The source copyright notices and MIT permission text are retained in [EVIDENCE_LICENSE.txt](EVIDENCE_LICENSE.txt). Source-image SHA-256 hashes are pinned in the generator; a changed or missing source fails validation before previews are written.

## Reproduction

Python 3.10 or newer is sufficient to regenerate the SVG and verify that the committed previews exist:

```sh
python scripts/generate_assets.py
```

To rebuild all evidence previews, install the pinned imaging dependency and provide the read-only source checkouts:

```sh
python -m pip install -r scripts/requirements-assets.txt
python scripts/generate_assets.py --refresh-evidence --sources-root "/path/to/checkouts"
```

The source-root directory must contain:

```text
NEURO-SCOPE_public_release/        # public NEURO-SCOPE repository, pinned commit above
MATLAB-EEG-Processing-Pipeline/    # public pipeline repository, pinned commit above
Smart Medical Imaging/           # public Medical-Imaging-Analysis repository, pinned commit above
```

The local directory names reflect the source workspace; they do not alter public repository URLs. Obtain each public checkout at the listed commit before refreshing. The generator never downloads data and never modifies a source checkout. It writes only the four current profile assets. Raster outputs were verified byte-for-byte across repeated runs with Pillow 12.3.0; different linked libwebp builds may change compression bytes without changing the source or transformation.

## Preserved legacy assets — not displayed

Earlier local graphics remain available as historical material. They are not loaded by the README and are not regenerated by the current script. Their licences and provenance remain attached here.

- **MRI:** `brain-candidates/Head-mri-animation.gif` by **Zutroy81**, [source and public-domain dedication](https://commons.wikimedia.org/wiki/File:Head_mri_animation.gif). `head-mri-panel.gif` is the earlier resized, framed and palette-optimised derivative. It is stock reference material, not Davide's imaging output.
- **FreeSurfer:** `brain-candidates/Brainanim-FreeSurfer.gif` and its identical copy `brain-freesurfer.gif` are **“Brainanim.gif” by LarrabeeMGH**, [source](https://commons.wikimedia.org/wiki/File:Brainanim.gif), licensed **[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)**. The earlier `freesurfer-panel.gif` and `hero-console.gif` adapt that material through resizing, framing, compositing and palette optimisation. Those adaptations are also distributed under **CC BY-SA 4.0**. The original depicts a FreeSurfer / FreeView left-hemisphere pial surface with Desikan–Killiany parcellation; it is not Davide's reconstruction, and no endorsement is implied.
- **Original schematic support graphics:** `signal-divider.gif`, its `eeg-alpha`, `eeg-clinical` and `eeg-evoked` variants, `signal-divider-options-preview.png`, and `telemetry-gauge.gif` were generated in this repository. Their traces are illustrative, not recordings or benchmarks.
- **Console band:** `console-band.svg` was locally authored; the earlier guide names BGJar's circuit-board generator as a visual reference. It is retained but not used.

The earlier temporary computer-vision candidate collection and a tracked Python bytecode cache were removed from the working tree. Their prior versions remain recoverable from Git history. The mixed third-party candidate imagery and identifiable people did not provide suitable provenance for this profile. No company images or private production artefacts are used.

## Validation and local preview

The checks are reproducible with the same pinned Pillow dependency:

```sh
python scripts/verify_profile.py
python scripts/verify_profile.py --links --render
python scripts/verify_profile.py --serve
```

The first command is offline: asset paths, alt text, SVG safety, finite motion, contrast, metadata, image budget, anchors and deterministic generation. The second checks public links and uses GitHub's stateless GFM rendering API, then caches GitHub's public stylesheets. It does not authenticate, publish or mutate remote content. LinkedIn may reject automated requests; the contact URL was independently checked against the definitive CV.

The preview serves only the rendered README, its four images and the cached stylesheets on `127.0.0.1:8765`. Use `?theme=light` or `?theme=dark`. Only a responsive preview shell and heading IDs are added to the API output; the README itself has no custom page CSS. Re-render after editing the Markdown. Stop the server with Ctrl+C and remove its ignored `tmp/readme-qa` cache after inspection.

The redesign was visually checked in light and dark modes at desktop and narrow widths, including 320 px, and refined after the first render. All four images load; no horizontal content overflow was observed. The pulse was inspected in transit and after stopping. Project previews were checked against their source figures, including axes, alignment and crop boundaries. `git diff --check` is part of the final handoff checks.
