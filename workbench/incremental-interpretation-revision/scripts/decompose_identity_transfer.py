"""POST-HOC E31: actor contrasts of preregistered named J cells.

Reuses every registered cohort; no new inference or annotation.
"""
import argparse
import json
from pathlib import Path
from analyze_source_ablation import stat
from data import sha


def analyze(summary):
    source = json.loads(summary.read_text())
    out = dict(experiment='E31',
               analysis_status='POST-HOC actor/predicate identity contrasts of preregistered named J cells; behavioral account, not latent decomposition',
               units='bits', summary_sha256=sha(summary),
               analysis_code_sha256=sha(Path(__file__)), contrasts={})
    for cohort, rows in source['probability']['per_family'].items():
        values = {}
        for marker in ('same_began', 'different_began'):
            vector = {r['verb_family']: r[f'J/{marker}/same_actor/named'] - r[f'J/{marker}/other_actor/named'] for r in rows}
            values[marker] = vector
            out['contrasts'][f'{cohort}/actor_match/{marker}'] = stat(vector)
        interaction = {f: values['same_began'][f] - values['different_began'][f] for f in values['same_began']}
        out['contrasts'][f'{cohort}/actor_by_predicate_interaction'] = stat(interaction)
    return out


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--summary', type=Path, required=True)
    p.add_argument('--out', type=Path, required=True)
    a = p.parse_args()
    a.out.write_text(json.dumps(analyze(a.summary), indent=2)+'\n')
