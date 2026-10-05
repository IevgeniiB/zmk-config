#!/usr/bin/env python3
"""Pristine-build the selected firmware track; retain logs, UF2s and a JSON summary."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import shlex
import subprocess
import yaml

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--track', choices=['stable', 'experimental'], default='stable')
    parser.add_argument('--workspace', type=Path, required=True, help='initialized west workspace')
    parser.add_argument('--output', type=Path, default=ROOT / 'build')
    args = parser.parse_args()
    ws, output = args.workspace.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    config = ROOT / ('config' if args.track == 'stable' else 'experimental')
    matrix_file = ROOT / ('build.yaml' if args.track == 'stable' else 'build-experimental.yaml')
    manifest = yaml.safe_load((config / 'west.yml').read_text())['manifest']
    for project in manifest['projects']:
        observed = subprocess.check_output(['git', '-C', str(ws / project['name']), 'rev-parse', 'HEAD'], text=True).strip()
        if observed != project['revision']:
            raise SystemExit(f"{args.track}: workspace {project['name']} is {observed}, expected {project['revision']}; run west update in the correct workspace")
    env = dict(os.environ, ZEPHYR_BASE=str(ws / 'zephyr'), Zephyr_DIR=str(ws / 'zephyr/share/zephyr-package/cmake'))
    matrix = yaml.safe_load(matrix_file.read_text())
    if set(matrix) != {'include'}:
        raise SystemExit('Only the explicit include matrix is supported; update this runner for matrix axes.')
    results = []
    for target in matrix['include']:
        name = target['board'].replace('/', '_') + '-' + (target.get('shield', '').split() or ['firmware'])[0]
        build = output / name
        cmd = ['west', 'build', '-p', 'always', '-s', str(ws / 'zmk/app'), '-d', str(build), '-b', target['board']]
        if target.get('snippet'):
            cmd += ['-S', target['snippet']]
        cmd += ['--', f'-DZMK_CONFIG={config}']
        if target.get('shield'):
            cmd += [f'-DSHIELD={target["shield"]}']
        cmd += shlex.split(target.get('cmake-args', ''))
        with (output / f'{name}.log').open('w') as log:
            result = subprocess.run(cmd, cwd=ws, env=env, stdout=log, stderr=subprocess.STDOUT)
        uf2 = build / 'zephyr/zmk.uf2'
        passed = result.returncode == 0 and uf2.is_file()
        row = {'track': args.track, 'target': name, 'passed': passed, 'exit_code': result.returncode, 'command': cmd,
               'uf2': str(uf2) if passed else None,
               'sha256': hashlib.sha256(uf2.read_bytes()).hexdigest() if passed else None}
        results.append(row)
        (output / 'results.json').write_text(json.dumps(results, indent=2) + '\n')
        print(f'{"PASS" if passed else "FAIL"} {name}', flush=True)
    raise SystemExit(not all(r['passed'] for r in results))


if __name__ == '__main__':
    main()
