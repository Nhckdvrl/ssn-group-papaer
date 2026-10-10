"""Evaluate a frozen post-hoc discovery model on E85's independent run.

The constants come only from discovery. No confirmation singles are fitted.
Uncertainty in discovery estimates and confirmation means is kept separate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval
from e84_reader_features import output_components


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('forecast')
    ap.add_argument('confirmation')
    ap.add_argument('--discovery', default='results/e85/qwen3_discovery')
    a = ap.parse_args()
    frozen_path, directory = Path(a.forecast), Path(a.confirmation)
    frozen_bytes = frozen_path.read_bytes()
    forecast = json.loads(frozen_bytes)
    discovery = Path(a.discovery)
    assert hashlib.sha256((discovery/'behavior.jsonl').read_bytes()).hexdigest() == forecast['source_behavior_sha256']
    old_run = json.loads((discovery/'run.json').read_text())
    run = json.loads((directory/'run.json').read_text())
    assert old_run['args']['n'] == 32 and old_run['args']['seed'] == 85001
    assert run['args']['n'] == 64 and run['args']['seed'] == 185001
    assert run['source_hashes'] == old_run['source_hashes']
    assert max(run['control'].values()) <= .01
    rows = [json.loads(x) for x in (directory/'behavior.jsonl').read_text().splitlines()]
    assert len(rows) == 64
    signs = np.array([r['signs'] for r in rows])
    ci = lambda v: interval(v, seed=851, nboot=4000)
    comparisons, product_losses, additive_losses = {}, [], []
    for layout in (0, 1):
        raw = np.array([r['scores'][f'D{layout}.joint'] for r in rows])
        components = output_components(raw, signs)
        for cue in ['field', 'code']:
            key = f'D{layout}.{cue}'
            actual = components[cue].mean(1)
            pred = forecast['predictions'][key]
            p, ad = pred['product']['mean'], pred['additive']['mean']
            lp, la = (actual-p)**2, (actual-ad)**2
            product_losses.append(lp)
            additive_losses.append(la)
            comparisons[key] = dict(actual=ci(actual), frozen_product=pred['product'],
                                    frozen_additive=pred['additive'],
                                    actual_minus_product=ci(actual-p),
                                    actual_minus_additive=ci(actual-ad),
                                    product_mse=ci(lp), additive_mse=ci(la),
                                    product_minus_additive_mse=ci(lp-la))
    product_loss = np.stack(product_losses).mean(0)
    additive_loss = np.stack(additive_losses).mean(0)
    out = dict(forecast_sha256=hashlib.sha256(frozen_bytes).hexdigest(),
               confirmation_behavior_sha256=hashlib.sha256((directory/'behavior.jsonl').read_bytes()).hexdigest(),
               validation_script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               fitting='None on confirmation. Absolute discovery predictions are held fixed.',
               comparisons=comparisons,
               primary=dict(product_mse=ci(product_loss), additive_mse=ci(additive_loss),
                            product_minus_additive_mse=ci(product_loss-additive_loss)),
               limitations=['Four mean cue effects, not a full distribution or per-query mechanism.',
                            'Product model was proposed after observing discovery joint effects.',
                            'Independent contexts use the same schema and vocabulary distribution.',
                            'Bootstrap intervals for frozen estimates and confirmation sampling are separate.'])
    (directory/'gate_validation.json').write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))


if __name__ == '__main__':
    main()
