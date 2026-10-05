#!/usr/bin/env python3
"""Render each real board adapter, offline after its pinned dependencies are present."""
import argparse
import copy
from pathlib import Path
import subprocess
import tempfile
import yaml
from keymap_drawer.config import Config

ROOT = Path(__file__).resolve().parents[1]
LAYERS = ['Base', 'Nav', 'Num', 'Sys', 'Magic']


def generate(workspace, destination):
    config = yaml.safe_load((ROOT / 'draw/config.yaml').read_text())
    helpers = workspace / 'zmk-helpers/include'
    layout = workspace / 'zmk/app/boards/arm/glove80/glove80-layouts.dtsi'
    if not (helpers / 'zmk-helpers/helper.h').is_file() or not layout.is_file():
        raise SystemExit('Missing dependencies: initialize west or follow README drawing setup.')
    config['parse_config']['zmk_keycode_map'] = Config().parse_config.zmk_keycode_map | config['parse_config']['zmk_keycode_map']
    config['parse_config']['zmk_additional_includes'] = [str(helpers)]
    destination.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        cfg = Path(tmp) / 'config.yaml'
        cfg.write_text(yaml.safe_dump(config, allow_unicode=True))
        for board, count in [('urchin', 34), ('glove80', 80)]:
            names = LAYERS[:4 if board == 'urchin' else 5]
            output = destination / f'{board}.yaml'
            subprocess.run(['keymap', '-c', str(cfg), 'parse', '-z', str(ROOT / f'config/{board}.keymap'),
                            '-l', *names, '-o', str(output)], check=True)
            data = yaml.safe_load(output.read_text())
            # Override online layout lookup: Glove80 uses its firmware geometry;
            # Urchin is a matrix-order schematic, not a claimed physical outline.
            data.pop('layout', None)
            if list(data['layers']) != names or any(len(v) != count for v in data['layers'].values()):
                raise SystemExit(f'{board}: unexpected layer names or binding count')
            for combo in data['combos']:
                if not all(0 <= p < count for p in combo['p']) or not set(combo['l']) <= set(names):
                    raise SystemExit(f'{board}: invalid combo positions or layers')
            output.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))
            geometry = ['-d', str(layout)] if board == 'glove80' else [
                '--ortho-layout', '{split: true, rows: 3, columns: 5, thumbs: 2}']
            subprocess.run(['keymap', '-c', str(cfg), 'draw', str(output), *geometry,
                            '--keys-only', '-o', str(destination / f'{board}.svg')], check=True)
            # Separate combo cards otherwise omit layer scopes. Annotate cards only;
            # keep the generated YAML's original key semantics and layer restrictions.
            cards = copy.deepcopy(data)
            for combo in cards['combos']:
                key = combo['k'] if isinstance(combo['k'], dict) else {'t': combo['k']}
                if key.get('h'):
                    raise SystemExit('Combo card hold legend is occupied; update scope annotation placement.')
                combo['k'] = key | {'h': '/'.join(combo['l'])}
            card_file = Path(tmp) / 'cards.yaml'
            card_file.write_text(yaml.safe_dump(cards, sort_keys=False, allow_unicode=True))
            card_config = copy.deepcopy(config)
            card_config['draw_config'].update(shrink_wide_legends=14,
                svg_extra_style='text.hold { font-size: 8px; }',
                footer_text='Combo card bottom = active layers • IevgeniiB/zmk-config')
            card_cfg = Path(tmp) / 'cards-config.yaml'
            card_cfg.write_text(yaml.safe_dump(card_config, allow_unicode=True))
            subprocess.run(['keymap', '-c', str(card_cfg), 'draw', str(card_file), *geometry,
                            '--combos-only', '-o', str(destination / f'{board}-combos.svg')], check=True)
            print(f'{board}: {len(names)} layers, {count} keys/layer, {len(data["combos"])} combos')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True, help='west workspace with zmk and zmk-helpers')
    parser.add_argument('--check', action='store_true', help='fail if committed diagrams or parsed data are stale')
    args = parser.parse_args()
    if args.check:
        with tempfile.TemporaryDirectory() as tmp:
            generated = Path(tmp)
            generate(args.workspace.resolve(), generated)
            stale = [p.name for p in generated.iterdir()
                     if not (ROOT / 'draw' / p.name).is_file() or p.read_bytes() != (ROOT / 'draw' / p.name).read_bytes()]
            if stale:
                raise SystemExit('Stale generated files: ' + ', '.join(sorted(stale)))
    else:
        generate(args.workspace.resolve(), ROOT / 'draw')


if __name__ == '__main__':
    main()
