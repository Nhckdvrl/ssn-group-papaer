"""Complete the predeclared natural-versus-fixed partner contrasts and paired CIs.

The original numerical driver and analyzer stay frozen. This CPU-only report
fills the natural A/B-minus-P contrasts named in the original experiment card.
"""
import json
from pathlib import Path
import numpy as np
import e160_analyze as core

ROOT=core.ROOT/'retry_1'


def main():
    plan=json.loads((ROOT/'plan.json').read_text());manifest=json.loads((ROOT/'manifest.json').read_text())
    budget=json.loads((ROOT/'budget.json').read_text())
    if manifest['status']!='complete' or any(r['status']!='complete' for r in budget['attempts']):raise ValueError('Completed retry required')
    if core.sha(manifest['raw']['path'])!=manifest['raw']['sha256']:raise ValueError('Raw differs')
    with np.load(manifest['raw']['path'],allow_pickle=False) as file:a={k:file[k] for k in file.files}
    core.validate(a)
    results={}
    fields=('gold','answer_tokens','answer_chars')
    metrics={key:core.scores(a[key],*(a[f] for f in fields)) for key in (
        'clamped_candidate_loglikelihood','natural_candidate_loglikelihood','without_shared_candidate_loglikelihood')}
    for name in metrics['natural_candidate_loglikelihood']:
        sign=-1 if name.endswith('accuracy') else 1
        natural=sign*(metrics['without_shared_candidate_loglikelihood'][name]-metrics['natural_candidate_loglikelihood'][name])
        fixed=sign*(metrics['without_shared_candidate_loglikelihood'][name]-metrics['clamped_candidate_loglikelihood'][name][:,0])
        stats=lambda x:core.stats(x,a['subject'])
        results[name]={'natural':[stats(natural[i]-natural[0]) for i in (1,2)],
                       'fixed_producer_P':[stats(fixed[i]-fixed[0]) for i in (1,2)],
                       'fixed_minus_natural':[stats((fixed[i]-fixed[0])-(natural[i]-natural[0])) for i in (1,2)]}
    report={'experiment':'E160','status':'complete','kind':'predeclared natural-versus-fixed partner contrasts; CPU reporting completion',
        'raw_sha256':manifest['raw']['sha256'],'plan_sha256':core.sha(ROOT/'plan.json'),
        'source_sha256':core.sha(__file__),'frozen_statistics_sha256':core.sha(core.__file__),
        'registration':'E160 card at 55960d57, readouts: natural partner effects, fixed-producer-P effects, and their difference',
        'consumer_contrasts':['A_minus_P','B_minus_P'],'metrics':results,'new_model_forwards':0}
    (ROOT/'natural_vs_fixed_partner_effects.json').write_text(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False)+'\n')
    print('Complete paired natural and fixed partner contrasts')


if __name__=='__main__':main()
