#!/usr/bin/env python3
"""Compare drawer parsing to each half's compiled devicetree (bindings and combos)."""
import argparse
import subprocess
import sys
import struct
import tempfile
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]


def bindings(dt, prop):
    cells = iter(struct.unpack(f'>{len(prop.value) // 4}I', prop.value))
    result = []
    for phandle in cells:
        node = dt.phandle2node[phandle]
        count = node.props['#binding-cells'].to_num()
        result.append((tuple(node.labels), tuple(next(cells) for _ in range(count))))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workspace', type=Path, required=True)
    parser.add_argument('--build-root', type=Path, required=True)
    args = parser.parse_args()
    ws = args.workspace.resolve()
    sys.path.insert(0, str(ws / 'zephyr/scripts/dts/python-devicetree/src'))
    from devicetree.dtlib import DT
    targets = [('glove80', 'glove80_lh-firmware'), ('glove80', 'glove80_rh-firmware'),
               ('urchin', 'nice_nano_v2-urchin_left'), ('urchin', 'nice_nano_v2-urchin_right')]
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        cfg = tmp / 'config.yaml'
        cfg.write_text(yaml.safe_dump({'parse_config': {
            'skip_binding_parsing': True,
            'zmk_additional_includes': [str(ws / 'zmk-helpers/include')]}}))
        for board, target in targets:
            compiled = DT(str(args.build_root / target / 'zephyr/zephyr.dts'))
            out = tmp / 'raw.yaml'
            subprocess.run(['keymap', '-c', str(cfg), 'parse', '-z', str(ROOT / f'config/{board}.keymap'),
                            '-o', str(out)], check=True)
            raw = yaml.safe_load(out.read_text())
            layers = list(raw['layers'].values())
            actual_layers = list(compiled.get_node('/keymap').nodes.values())
            if len(layers) != len(actual_layers):
                raise SystemExit(f'{target}: layer count differs')
            # Compile the parser's symbolic bindings with the actual ZMK headers.
            # Stub only behavior declarations; names and numeric arguments must match.
            declarations = []
            for node in compiled.node_iter():
                if node.labels and '#binding-cells' in node.props:
                    labels = ': '.join(node.labels) + ':'
                    declarations.append(f'{labels} b{len(declarations)} {{ #binding-cells = <{node.props["#binding-cells"].to_num()}>; }};')
            text = ''.join(f'#include <dt-bindings/zmk/{name}.h>\n' for name in ['keys', 'bt', 'outputs', 'rgb'])
            text += '/dts-v1/;\n/ {\n' + '\n'.join(declarations)
            for i, layer in enumerate(layers):
                text += f'\nl{i} {{ bindings = <' + ' '.join(layer) + '>; };'
            for i, combo in enumerate(raw['combos']):
                text += f'\nc{i} {{ bindings = <{combo["k"]}>; }};'
            text += '\n};\n'
            source = tmp / 'parsed.dts'
            result = subprocess.run(['cc', '-E', '-P', '-x', 'assembler-with-cpp', '-I', str(ws / 'zmk/app/include'), '-'],
                                    input=text, text=True, capture_output=True, check=True)
            source.write_text(result.stdout)
            parsed = DT(str(source))
            for i, actual in enumerate(actual_layers):
                expected = bindings(parsed, parsed.get_node(f'/l{i}').props['bindings'])
                observed = bindings(compiled, actual.props['bindings'])
                if expected != observed:
                    raise SystemExit(f'{target}: binding mismatch on layer {i}')
            actual_combos = list(compiled.get_node('/combos').nodes.values())
            if len(raw['combos']) != len(actual_combos):
                raise SystemExit(f'{target}: combo count differs')
            for i, (combo, actual) in enumerate(zip(raw['combos'], actual_combos)):
                expected = bindings(parsed, parsed.get_node(f'/c{i}').props['bindings'])
                observed = bindings(compiled, actual.props['bindings'])
                if (expected != observed or combo['p'] != actual.props['key-positions'].to_nums()
                        or [int(x) for x in combo['l']] != actual.props['layers'].to_nums()):
                    raise SystemExit(f'{target}: combo mismatch at {actual.path}')
            print(f'PASS {target}: every layer binding and all {len(actual_combos)} combo bindings/positions/scopes match compiled DTS')


if __name__ == '__main__':
    main()
