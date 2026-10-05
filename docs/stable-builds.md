# Stable firmware: reproducible source baseline

The stable track retains the existing MoErgo firmware and all current keyboard
behavior. It builds the five existing `build.yaml` targets: Glove80 left/right,
Urchin left/right with nice!view, and the nice!nano settings-reset utility.

| Source | Pin | Tracking source |
| --- | --- | --- |
| MoErgo ZMK | `ce69e85f585c724142aae37ddf8a7e019ff19e93` | `main`, currently `v26.09` |
| urob helpers | `a98b7f7e4a5130a5150dce81bb8aa419fc3ca3c0` | `v2` |
| ZMK Zephyr fork | `dacab4875df72109b96cc8977547a0dc04875bcd` | `v3.5.0+zmk-fixes` |
| Official ZMK build workflow | `edf5c0814fd3ea202e43aad2d68fd32e882a518c` | `v0.3.0` |

The firmware already came from MoErgo before this change; these pins record the
sources resolved on 2026-10-05. The explicit Zephyr override preserves the
import filter from MoErgo. All resolved module revisions are commit hashes.

The **official** ZMK v0.3.0 reusable workflow is byte-for-byte identical to the
workflow bundled with MoErgo v26.09 (SHA-256
`9f5c072677c226c854ab9392ba9699e5dd5d7aae59a66aa7ed3acd5699b0cb7b`).
It avoids the current official main workflow's newer `west boards` check,
which fails with `KeyError: 'qualifiers'` on this stable Zephyr tooling after
successful compilation. Firmware source and workflow source are independent.

## Local builds

Install west, the Zephyr build prerequisites and a compatible SDK. The audited
local toolchain is Python 3.12, west 1.5.0, Zephyr SDK 0.16.8, CMake 3.31.6 and
Ninja 1.13.2. See the [official setup guide](https://zmk.dev/docs/development/local-toolchain/setup/native).

```sh
mkdir -p /path/to/stable-workspace/config
cp /path/to/zmk-config/config/west.yml /path/to/stable-workspace/config/west.yml
west init -l /path/to/stable-workspace/config
cd /path/to/stable-workspace
west update
west zephyr-export
python -m pip install -r zephyr/scripts/requirements.txt
# Activate the SDK/toolchain before building:
python /path/to/zmk-config/scripts/build-all.py \
  --workspace /path/to/stable-workspace --output /path/to/stable-builds
```

The runner reads every explicit matrix entry and makes pristine builds. It
continues after a failed target, fails overall if any target fails or lacks a
UF2, and saves per-target logs plus `results.json` with commands and checksums.
After a manifest update, copy the new manifest into the workspace and run
`west update` before rebuilding.

The initial baseline passed all five local builds. Hardware validation remains
unrun. Existing warnings include deprecated reboot settings, ineffective Urchin
USB/display settings and array-bound warnings in the upstream settings-reset
build. The reset UF2 clears persistent settings and is not normal typing firmware.

Source pinning does not freeze the reusable workflow's mutable action tags or
`stable` container image, so bit-for-bit cloud/local reproducibility is not
claimed. Review firmware dependency changes in a separate PR, rebuild every
stable target, and preserve previous stable artifacts as a rollback.
