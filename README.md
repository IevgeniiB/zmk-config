# Glove80 and Urchin keymaps

This configuration shares a 34-key layout between Glove80 and Urchin. The
Glove80 adapter adds outer keys and a Magic layer. The firmware definitions,
including behavior and timing, remain authoritative in `config/`.

[Glove80 layers](draw/glove80.svg) · [Glove80 combos](draw/glove80-combos.svg) ·
[Urchin layers](draw/urchin.svg) · [Urchin combos](draw/urchin-combos.svg)

![Urchin layers](draw/urchin.svg)

Glove80 has five layers of 80 keys; Urchin has four layers of 34 keys. Each has
29 combos. These images are generated from the actual board adapters, including
helper macros and extra keys. Glove80 uses the geometry shipped by its firmware;
Urchin is a **matrix-order schematic**, not a measurement of physical stagger.
The adjacent YAML files contain generated, reviewable layer and combo data.

## Reading the diagrams

On a key, the center is the tap action, the bottom is the hold action, and the
top is the shifted action. `▽` is transparent; an empty key is disabled.
On combo cards, the bottom legend lists the active layers.

Special key legends labeled `C+S:` (Ctrl+Shift) or `2x:` describe modifier or
tap-dance actions, not holds. `Gui` is the platform GUI modifier (Command on macOS).
The smart Shift behavior becomes Caps Word when **left Shift** is already held.
BLE profile numbers are zero-based; Magic-layer BLE keys select BLE output and
profile on one tap and disconnect that profile on two taps. Tapping Magic shows
RGB status; holding it enters the Magic layer. Timing and nested behavior details
remain authoritative in `config/base.keymap` and `config/combos.dtsi`.

ZMK Studio can change a keyboard's runtime layout. These diagrams show the
repository configuration, not later Studio edits stored on hardware.

## Regenerating and checking

Use Python 3.12 and the pinned renderer requirements:

```sh
python3.12 -m venv .venv-draw
. .venv-draw/bin/activate
python -m pip install -r scripts/draw-requirements.txt
python scripts/draw-keymaps.py --workspace /path/to/drawing-dependencies
python scripts/draw-keymaps.py --workspace /path/to/drawing-dependencies --check
```

The dependency directory must contain `zmk` and `zmk-helpers` checkouts at the
commits in [`draw/dependencies.yaml`](draw/dependencies.yaml). These are the
geometry and parser-helper snapshots resolved from the existing main firmware
manifest on 2026-10-05; they **do not change firmware dependency selection**.
The `Keymap diagrams` workflow demonstrates sparse checkouts of only the needed
files. Rendering does not download live geometry from QMK or another service.

Edit `config/*.keymap`, `config/combos.dtsi`, or presentation overrides in
`draw/config.yaml`, regenerate, and commit SVG/YAML outputs together. CI fails if
these committed outputs are stale. Review drawing dependency snapshots alongside
future firmware updates so helper expansion and physical geometry stay aligned.

For comparison against an existing firmware build, put `keymap` on PATH and run:

```sh
python scripts/validate-keymaps.py \
  --workspace /path/to/west-workspace --build-root /path/to/builds
```

The validator expects builds named `glove80_lh-firmware`, `glove80_rh-firmware`,
`nice_nano_v2-urchin_left` and `nice_nano_v2-urchin_right`, each containing
`zephyr/zephyr.dts`. It compares every parsed behavior name and numeric argument,
plus every combo's output, positions and layer scope, to the compiled devicetree.
The settings-reset target has no typing keymap to draw.

The initial diagrams passed these comparisons on all four halves against the
unchanged main keymap, plus deterministic regeneration and negative checks for
stale output and a same-length binding change. Browser previews were inspected.
Hardware testing is not implied. This drawings change does not modify firmware
sources, board settings, timing, build targets or the firmware build workflow.

## Firmware tracks

[Stable and experimental firmware](docs/firmware-tracks.md) documents the separate
MoErgo stable and official-ZMK Urchin experiment, their downloads, validation and
rollback paths. Both use this shared layout. The experiment is not promoted to
stable without hardware feedback.
