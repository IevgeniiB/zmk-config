#!/usr/bin/env python3
"""Package exactly the matrix's UF2s, source pins, diagrams and checksums."""
import argparse
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--artifacts', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    matrix = yaml.safe_load((ROOT / 'build.yaml').read_text())['include']
    expected = {}
    for target in matrix:
        shield = target.get('shield', '')
        original = target.get('artifact-name', (shield + '-' if shield else '') + target['board'] + '-zmk') + '.uf2'
        name = target['board'].replace('/', '_') + '-' + (shield.split() or ['firmware'])[0] + '.uf2'
        if original in expected or name in expected.values():
            raise SystemExit('Duplicate firmware artifact names')
        expected[original] = name
    found = {p.name for p in args.artifacts.iterdir() if p.is_file()}
    if found != set(expected):
        raise SystemExit(f'Unexpected artifact set: missing={set(expected)-found}, extra={found-set(expected)}')
    args.output.mkdir(parents=True, exist_ok=False)
    for original, name in expected.items():
        source = args.artifacts / original
        data = source.read_bytes()
        if len(data) < 512 or len(data) % 512 or data[:8] != bytes.fromhex('5546320a57515d9e'):
            raise SystemExit(f'Invalid UF2 header/length: {original}')
        shutil.copyfile(source, args.output / name)
    for svg in (ROOT / 'draw').glob('*.svg'):
        shutil.copyfile(svg, args.output / svg.name)
    shutil.copyfile(ROOT / 'config/west.yml', args.output / 'source-manifest.yml')
    sums = ''.join(f'{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n' for p in sorted(args.output.iterdir()))
    (args.output / 'SHA256SUMS').write_text(sums)
    sha = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    tag = os.environ.get('RELEASE_TAG', 'local-validation')
    notes = f'''Firmware built from `{sha}` for `{tag}`. All five cloud build targets must succeed before publication.

Source baseline: MoErgo ZMK v26.09, with exact ZMK, helpers and Zephyr commits in `source-manifest.yml`. Key behavior is unchanged by the initial maintenance work. Layer and combo diagrams are included; Urchin geometry is a matrix-order schematic.

**Hardware validation has not been performed.** Bluetooth, displays, sleep, Studio runtime edits and typing behavior have not been tested on a keyboard. Build success does not establish those properties.

Choose the UF2 matching your board and half. `nice_nano_v2-settings_reset.uf2` is a **settings-reset utility**, not typing firmware; it clears persistent settings. Do not flash it as a normal keyboard update. Existing upstream settings-reset array warnings are documented in `docs/maintenance.md`.

`SHA256SUMS` covers all firmware, diagrams and the source manifest. The cloud toolchain uses the MoErgo reusable workflow and its mutable `stable` container; bit-for-bit identity with local builds is not claimed. Nothing is flashed automatically.
'''
    (ROOT / 'release-notes.md').write_text(notes)
    print(f'Prepared {len(expected)} UF2s and checksummed supporting assets for {sha}')


if __name__ == '__main__':
    main()
