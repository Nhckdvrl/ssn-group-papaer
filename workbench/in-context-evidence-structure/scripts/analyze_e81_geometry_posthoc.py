"""POST-HOC output geometry: orientation, contrast size, and shared bias."""
import argparse
import json
from pathlib import Path
import numpy as np
from analyze_e58 import interval


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('directory')
    a = ap.parse_args()
    d = Path(a.directory)
    rows = [json.loads(x) for x in (d / 'behavior.jsonl').read_text().splitlines()]
    signs = np.array([r['signs'][:2] for r in rows])
    ci = lambda x: interval(x, seed=810, nboot=4000)
    out = {'status': 'POST-HOC metric interpretation, not a new mechanism or deployable calibration',
           'definition': 'b=(z_A+z_B)/2; s=gold_sign_A*(z_A-z_B)/2. Paired accuracy=0.5*[1{s+b>0}+1{s-b>0}].',
           'conditions': {}, 'contrasts': {}}
    values = {}
    for k in rows[0]['scores']:
        z = np.array([r['scores'][k] for r in rows])
        s = (z[:, :2] - z[:, 2:]) * signs / 2
        b = (z[:, :2] + z[:, 2:]) / 2
        accuracy = .5 * ((s+b > 0).astype(float) + (s-b > 0).astype(float))
        exact = (z * np.array([r['signs'] for r in rows]) > 0).mean(1)
        assert np.array_equal(accuracy.mean(1), exact)
        values[k] = dict(signed_source_contrast=s.mean(1), abs_shared_bias=np.abs(b).mean(1),
                         fraction_both_correct=(s>np.abs(b)).mean(1), fraction_both_wrong=(s < -np.abs(b)).mean(1),
                         source_orientation=(s>0).mean(1))
        out['conditions'][k] = {name: ci(v) for name,v in values[k].items()}
    for layout in (0,1):
        pre = f'D{layout}.'
        for mode in ['mass','within','both','source_flip','full_attention']:
            out['contrasts'][pre+mode+'.minus_native'] = {
                name:ci(v-values[pre+'native'][name]) for name,v in values[pre+mode].items()}
    out['contrasts']['layout.native'] = {
        name:ci(v-values['D0.native'][name]) for name,v in values['D1.native'].items()}
    (d/'output_geometry_posthoc.json').write_text(json.dumps(out,indent=2))
    print(json.dumps({k:out['contrasts'][k] for k in ['layout.native','D0.full_attention.minus_native','D1.source_flip.minus_native']},indent=2))


if __name__=='__main__':
    main()
