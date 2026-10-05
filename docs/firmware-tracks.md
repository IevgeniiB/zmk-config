# Stable and experimental firmware

The two tracks share typing layers, combos, home-row modifiers, timing and the
Urchin shield definitions. They differ in firmware and Zephyr sources. The
experiment is **Urchin only**; Glove80 remains stable until its vendor status
features and hardware behavior have been reviewed separately.

| | Stable | Experimental |
| --- | --- | --- |
| ZMK source | MoErgo v26.09 (`ce69e85f…`) | Official main snapshot (`5b51501f…`, 2026-10-05) |
| Zephyr | `dacab487…`, 3.5 fork | `10ba6d0c…`, 4.1 fork |
| Manifest | `config/west.yml` | `experimental/west.yml` |
| Matrix | `build.yaml` (five targets) | `build-experimental.yaml` (two Urchin halves) |
| Workflow source | Official ZMK v0.3.0 | Pinned official ZMK main snapshot |
| Download archive | `stable-firmware` | `experimental-urchin-firmware` |
| UF2 filename prefix | `stable-` | `experimental-` |
| Hardware status | Unverified in this maintenance work | Untested; opt-in experiment |

Full commit hashes are in the manifests. Both source sets are pinned; neither
track silently follows a moving branch. Official-main changes can affect typing
behavior even though the layout source is shared. Build success is not hardware
validation. **Do not promote experimental firmware to stable without user
hardware feedback.** No workflow automatically flashes, promotes, or publishes a
final firmware release.

## Portable keymap

`config/base.keymap` contains the common behavior and layout. The Glove80 adapter
opts into `config/glove80-behaviors.dtsi`; that file contains the existing MoErgo
RGB-status/Magic and Bluetooth helper behaviors, moved without modification.
Urchin never loads those unused vendor declarations, so official ZMK does not
need MoErgo's `RGB_STATUS` extension. No replacement typing layout is introduced.

The experimental adapter includes the normal Urchin keymap. Its `.conf` and
shield directory are symlinks to the stable source, avoiding copies that drift.
The newer nice!nano board identifier is `nice_nano@2.0.0//zmk`; the hardware is
unchanged. Diagrams remain the shared source layout and do not promise identical
runtime behavior across ZMK versions or reflect saved Studio edits.

## Build separately

Follow `docs/stable-builds.md` for the stable workspace. Initialize the experiment
in a **different** workspace; never update the stable workspace from the
experimental manifest:

```sh
mkdir -p /path/to/experimental-workspace/experimental
cp /path/to/zmk-config/experimental/west.yml /path/to/experimental-workspace/experimental/west.yml
# Unset any environment variables pointing to the stable Zephyr before init:
unset ZEPHYR_BASE Zephyr_DIR
west init -l /path/to/experimental-workspace/experimental
cd /path/to/experimental-workspace
west update
west zephyr-export
python -m pip install -r zephyr/scripts/requirements.txt
```

With the appropriate SDK/toolchain activated:

```sh
python scripts/build-all.py --track stable \
  --workspace /path/to/stable-workspace --output /path/to/builds/stable
python scripts/build-all.py --track experimental \
  --workspace /path/to/experimental-workspace --output /path/to/builds/experimental
python scripts/validate-keymaps.py --track stable \
  --workspace /path/to/stable-workspace --build-root /path/to/builds/stable
python scripts/validate-keymaps.py --track experimental \
  --workspace /path/to/experimental-workspace --build-root /path/to/builds/experimental
```

The runner rejects a workspace whose direct dependency commits do not match the
selected track. It explicitly selects that workspace's Zephyr, even when a shell
previously activated another workspace. Keep outputs separate; JSON summaries
include the track, actual command, pass/fail outcome and UF2 checksums.

## Downloads, feedback and rollback

Download artifacts from the corresponding GitHub Actions run. Keep a copy of a
known working stable left/right pair before trying experimental firmware; Actions
artifacts expire. Test both halves from the same track/build. Never mix stable and
experimental halves. No cross-version preservation of saved Bluetooth/Studio
settings is assumed. Stable settings-reset firmware is a separate destructive
utility, not a normal update or a routine rollback step.

For rollback, use the saved stable pair or rebuild the recorded stable commit
with its pinned manifest. If an experiment is rejected, the stable manifest and
workflow remain available; no source migration back is necessary. Report the
track, repository commit, hardware halves, host OS, pairing state and observed
behavior when testing. Check typing/combos/home-row mods, split reconnection,
Bluetooth, nice!view, sleep/wake and any saved settings before recommending
promotion. Reset/re-pair only when troubleshooting establishes it is needed.

Future dependency bumps should be separate PRs. Update one track's manifest,
run every target in that track, verify the shared diagrams and keymap equivalence,
and compare results before merging. Hardware feedback governs promotion.
