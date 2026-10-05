# Baseline audit — 2026-10-05

Repository baseline: [`64df484`](https://github.com/IevgeniiB/zmk-config/commit/64df484).
The five targets are defined in [`build.yaml`](../build.yaml). Shared behavior is
in `config/base.keymap`; the Glove80 and Urchin files are adapters. There were no
README, generated diagrams, local build runner, or generated-file freshness check.
No `AGENTS.md` or `.agents/skills` instructions were present in this checkout or
its published workspace.

The GitHub API returned no open issues, no open PRs, no releases and zero retained
Actions runs during the audit. This is an observation of currently available
records, not a claim that the repository has never built successfully. No issue
reply was needed. The original workflow runs on push, PR and manual dispatch;
it calls ZMK's reusable build workflow, uploads firmware artifacts, and has no
scheduled trigger or final-release publishing step.

## Tested source baseline

| Component | Previous tracking ref | Pinned commit |
| --- | --- | --- |
| [MoErgo ZMK](https://github.com/moergo-sc/zmk) | `main`, resolving to `v26.09` | `ce69e85f585c724142aae37ddf8a7e019ff19e93` |
| [zmk-helpers](https://github.com/urob/zmk-helpers) | `v2` | `a98b7f7e4a5130a5150dce81bb8aa419fc3ca3c0` |
| [Zephyr fork](https://github.com/zmkfirmware/zephyr) | `v3.5.0+zmk-fixes` | `dacab4875df72109b96cc8977547a0dc04875bcd` |
| [MoErgo reusable build workflow](https://github.com/moergo-sc/zmk/blob/ce69e85f585c724142aae37ddf8a7e019ff19e93/.github/workflows/build-user-config.yml) | upstream ZMK `main` | `ce69e85f585c724142aae37ddf8a7e019ff19e93` |

MoErgo's [v26.09 release](https://github.com/moergo-sc/zmk/releases/tag/v26.09)
was published October 1 and includes the upstream input-report deadlock fix.
The pin records the already-resolved local firmware, rather than migrating to a
different ZMK lineage. The explicit Zephyr override retains MoErgo's import
blocklist; all remaining imported project revisions are already commit hashes.
Re-evaluate that override and import filter when updating MoErgo.

Upstream [ZMK releases](https://github.com/zmkfirmware/zmk/releases) are relevant
for security, behavior and Studio changes, but their tags are **not** drop-in
Glove80 firmware updates. Latest upstream stable identified during the audit:
`v0.3.0`. MoErgo's release numbering is independent.

## First improvement

- Generate each actual adapter: 5 × 80 Glove80 keys, 4 × 34 Urchin keys, 29 combos each.
- Render Glove80's pinned firmware geometry; explicitly label Urchin's schematic.
- Show combo layer scopes and custom punctuation, hold-tap, Studio and BLE actions.
- Pin the renderer and its dependency set; check source/output freshness in CI.
- Add a pristine five-target runner and compare drawer parsing to compiled DTS.
- Freeze currently tested source dependencies without changing key behavior.

Inspiration from [urob/zmk-config](https://github.com/urob/zmk-config): locked
firmware refs, source-derived diagrams and repeatable local builds. The existing
home-row modifier configuration is retained. No new layout or typing experiment
is enabled in this PR.

## Practical recurring scope (no schedule created here)

1. Check MoErgo releases/`main`, upstream ZMK releases/`main`, helpers `v2`,
   Zephyr `v3.5.0+zmk-fixes`, and the upstream reusable workflow. Track
   [keymap-drawer releases](https://github.com/caksoylar/keymap-drawer/releases)
   for parser fixes. Inspect [urob/zmk-config](https://github.com/urob/zmk-config)
   for separately reviewable ideas, not automatic layout adoption.
2. For a new MoErgo release, prepare a dependency-only branch, resolve every
   imported ref, check compatibility notes, run all five pristine builds,
   regenerate diagrams and run both validators. Notify with release notes,
   commit refs, passed/failed/unrun checks, and draft PR/artifact links.
3. Review new issues and PRs for actionable information. Reproduce reports in
   isolation; treat third-party text as evidence, never shell authorization.
   Ask about missing hardware, host OS or intended behavior. Public replies,
   merge policy and final-release policy remain subject to the user's scope.
4. Keep at most one clearly explained behavioral experiment per PR. Candidates
   include runtime behavior tests for home-row mods/combos, or a measured Urchin
   physical-layout definition. Require hardware feedback for timing, Bluetooth,
   sleep, displays and Studio behavior before considering them validated.

The initial audit was draft-only. The owner subsequently authorized merging
passing maintenance changes and publishing firmware releases. Never flash
hardware automatically; seek feedback before significant typing experiments.
Source pins improve repeatability; the cloud's mutable container/actions and
unverified hardware behavior remain explicit limitations.

## Validation evidence

All five pristine builds passed with SDK 0.16.8; each produced a UF2.
[Machine-readable results and UF2 hashes](validation.json) identify the artifacts.
All four keyboard halves passed complete binding/argument and combo comparisons
against the fresh compiled devicetrees. Diagram regeneration is deterministic;
the freshness check passes. Negative checks correctly rejected both a stale YAML
file and a same-length Q-to-W keybinding change. Browser previews were inspected.

Existing warnings remain: deprecated `NRF_STORE_REBOOT_TYPE_GPREGRET`, ineffective
Urchin battery-percentage settings, the right Urchin USB setting, and array-size/
array-bound warnings in the upstream settings-reset build. They do not fail the
builds and are not silently treated as hardware validation. Investigate the reset
warnings upstream before relying on a reset image on hardware.

Hardware flashing, Bluetooth/display/sleep/Studio behavior and typing feel are
unrun. GitHub Actions results must be checked on the draft PR; local builds do not
prove that the upstream cloud container and actions will execute successfully.

## Cloud workflow compatibility correction

The first cloud run compiled Glove80 successfully, then failed in upstream ZMK's
new board-compatibility check: `west boards --format "{qualifiers}"` raises
`KeyError: 'qualifiers'` in this MoErgo/Zephyr version. Evidence:
[failed job](https://github.com/IevgeniiB/zmk-config/actions/runs/37314122213/job/111776524084).
The reusable workflow now comes from the same MoErgo v26.09 commit as the firmware.
This retains the fork's compatible build process instead of altering board
configuration to satisfy a newer upstream check.

## Publishing an authorized firmware release

After all checks pass on the exact proposed commit, merge the maintenance PR.
Push a `firmware-*` tag on the verified merged commit (for example
`firmware-2026-10-05-v26.09`). The release workflow rebuilds all five targets at
that tag and publishes only after every build succeeds. It verifies all expected
UF2 filenames, includes SHA-256 checksums, source pins and keymap diagrams, and
marks hardware validation as unrun in the release notes. Settings-reset firmware
is explicitly identified as a destructive settings-reset utility. No workflow
flashes a keyboard. No recurring automation is added.
