"""Post-hoc E85 model from discovery singles, frozen before confirmation.

No joint discovery responses are used to estimate model parameters.
This predicts mean cue effects, not per-query next-token distributions.
"""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
from e84_reader_features import output_components


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('output')
    a = ap.parse_args()
    src = Path(a.source)
    rows = [json.loads(x) for x in (src/'behavior.jsonl').read_text().splitlines()]
    signs = np.array([r['signs'] for r in rows])
    assert len(rows) == 32 and json.loads((src/'run.json').read_text())['args']['seed'] == 85001
    rng = np.random.default_rng(851)
    indices = rng.integers(0,len(rows),(4000,len(rows)))
    out = dict(status='POST-HOC discovery model; frozen before independent confirmation',
               n_discovery_contexts=32, source_behavior_sha256=hashlib.sha256((src/'behavior.jsonl').read_bytes()).hexdigest(),
               script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), predictions={},
               scope='Mean field/code effect under joint native-cache intervention; not full algorithm or accuracy.',
               limitations=['Identity and mapping patch donors change contextualized K/V, not isolated semantic variables.',
                            'Mean gain composition need not describe all contexts or all pathways.'])
    for layout in (0,1):
        for cue in ['field','code']:
            vals = []
            for mode in ['full_base','name_K','label_KV']:
                z = np.array([r['scores'][f'D{layout}.{mode}'] for r in rows])
                vals.append(output_components(z,signs)[cue].mean(1))
            b,n,m = [v.mean() for v in vals]
            bb,nn,mm = [v[indices].mean(1) for v in vals]
            assert b > .1 and bb.min() > .05
            out['predictions'][f'D{layout}.{cue}'] = dict(
                base=float(b),name=float(n),mapping=float(m),
                name_ratio=float(n/b),mapping_ratio=float(m/b),
                product=dict(mean=float(n*m/b),ci95=np.quantile(nn*mm/bb,[.025,.975]).tolist()),
                additive=dict(mean=float(n+m-b),ci95=np.quantile(nn+mm-bb,[.025,.975]).tolist()))
    Path(a.output).write_text(json.dumps(out,indent=2))
    print(json.dumps(out['predictions'],indent=2))


if __name__ == '__main__':
    main()
